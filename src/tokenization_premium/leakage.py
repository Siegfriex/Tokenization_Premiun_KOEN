"""PRE-NB10 leakage-group construction and LR-01 boundary checks.

Pure functions only — no IO, no artifact reads. The heavy full-population pass lives in a runner
script; everything decision-bearing lives here so it can be unit-tested without the 3.8M-row job.

Contract: `ssot_nb10/01_PRE_NB10_GROUPING_CONTRACT_v001.md`.
Authority: SSOT §23.2 · `LR-01` · `CR-FAST-G5-SPLIT-RELOCATION-01`.

Two pairs share a leakage group if they share a normalised KO text or a normalised EN text,
transitively. Assignment is a deterministic hash of the frozen group id — no outcome value ever
participates.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Mapping, Sequence

HOLDOUT = "HOLDOUT"
TRAIN = "TRAIN"

_NON_ALNUM = re.compile(r"[^0-9a-z가-힣]")


class LeakageBoundaryViolation(RuntimeError):
    """An enforced group key crosses the train/holdout boundary. HARD FAIL."""


def normalise_text(text: str) -> str:
    """Tier-2 normalisation: casefold, then drop every non-alphanumeric character.

    Deliberately model-free. Absorbs case, punctuation and whitespace variants and nothing else.
    """
    return _NON_ALNUM.sub("", text.lower())


def text_key(text: str, *, normalised: bool) -> str:
    """Stable hash of one side's text under the chosen tier."""
    payload = normalise_text(text) if normalised else text
    return hashlib.md5(payload.encode("utf-8")).hexdigest()  # noqa: S324 - grouping key, not a credential


class _DisjointSet:
    """Union-find with path compression. Small and explicit so the grouping is auditable."""

    def __init__(self) -> None:
        self._parent: dict[str, str] = {}

    def add(self, item: str) -> None:
        self._parent.setdefault(item, item)

    def find(self, item: str) -> str:
        root = item
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[item] != root:
            self._parent[item], item = root, self._parent[item]
        return root

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self._parent[ra] = rb


def build_groups(rows: Iterable[tuple[str, str, str]]) -> dict[str, str]:
    """Connected components over (pair_id, ko_key, en_key).

    Returns pair_id -> group_id. The group id is the component root's pair id, which is stable for
    a fixed input ordering; callers that need order-independence should canonicalise afterwards with
    :func:`canonical_group_ids`.
    """
    ds = _DisjointSet()
    pair_ids: list[str] = []
    for pair_id, ko_key, en_key in rows:
        pair_ids.append(pair_id)
        for node in (pair_id, f"K:{ko_key}", f"E:{en_key}"):
            ds.add(node)
        ds.union(pair_id, f"K:{ko_key}")
        ds.union(pair_id, f"E:{en_key}")
    return {pid: ds.find(pid) for pid in pair_ids}


def canonical_group_ids(groups: Mapping[str, str]) -> dict[str, str]:
    """Re-key each component by its lexicographically smallest member.

    Makes the grouping independent of input order, so the split reproduces regardless of how the
    cohort was scanned.
    """
    members: dict[str, list[str]] = {}
    for pair_id, root in groups.items():
        members.setdefault(root, []).append(pair_id)
    canonical = {root: min(m) for root, m in members.items()}
    return {pair_id: canonical[root] for pair_id, root in groups.items()}


def group_sizes(groups: Mapping[str, str]) -> dict[str, int]:
    sizes: dict[str, int] = {}
    for group_id in groups.values():
        sizes[group_id] = sizes.get(group_id, 0) + 1
    return sizes


def assign_split(group_id: str, salt: str, holdout_share: float) -> str:
    """Deterministic, outcome-blind holdout assignment for one group.

    `uint64(sha256(salt || group_id)[:8]) / 2**64 < holdout_share`. Consumes the group id and the
    frozen salt and nothing else — no outcome, no feature, no model output.
    """
    if not 0.0 < holdout_share < 1.0:
        raise ValueError(f"holdout_share must be in (0,1), got {holdout_share!r}")
    digest = hashlib.sha256(f"{salt}{group_id}".encode()).digest()
    draw = int.from_bytes(digest[:8], "big") / 2**64
    return HOLDOUT if draw < holdout_share else TRAIN


def assign_all(groups: Mapping[str, str], salt: str, holdout_share: float) -> dict[str, str]:
    """Assign every pair via its group, so a group can never be split."""
    per_group = {g: assign_split(g, salt, holdout_share) for g in set(groups.values())}
    return {pair_id: per_group[g] for pair_id, g in groups.items()}


def crossing_keys(assignment: Mapping[str, str], key_of: Mapping[str, str]) -> list[str]:
    """Keys whose members land on both sides of the boundary. Empty list means no leakage."""
    seen: dict[str, set[str]] = {}
    for pair_id, side in assignment.items():
        key = key_of.get(pair_id)
        if key is None:
            continue
        seen.setdefault(key, set()).add(side)
    return sorted(k for k, sides in seen.items() if len(sides) > 1)


def assert_no_crossing(
    assignment: Mapping[str, str],
    enforced: Mapping[str, Mapping[str, str]],
) -> dict[str, int]:
    """Run every enforced key family. Raises on the first violation; returns all-zero counts on pass.

    `enforced` maps a check name to a pair_id -> key mapping. A check with no crossings contributes
    a zero; any crossing is a HARD FAIL and stops the split.
    """
    counts: dict[str, int] = {}
    for name, key_of in enforced.items():
        crossings = crossing_keys(assignment, key_of)
        counts[name] = len(crossings)
        if crossings:
            raise LeakageBoundaryViolation(
                f"LR01_VIOLATION [{name}]: {len(crossings)} key(s) cross the boundary; "
                f"first offenders {crossings[:3]}"
            )
    return counts


def holdout_share(assignment: Mapping[str, str]) -> float:
    total = len(assignment)
    if total == 0:
        raise ValueError("empty assignment")
    return sum(1 for side in assignment.values() if side == HOLDOUT) / total


def assert_assignment_complete(assignment: Mapping[str, str], expected_pair_ids: Sequence[str]) -> None:
    """Every cohort row assigned exactly once, to a known side, with nothing extra."""
    expected = set(expected_pair_ids)
    if len(expected) != len(expected_pair_ids):
        raise LeakageBoundaryViolation("DUPLICATE_PAIR_ID_IN_COHORT")
    missing = expected - set(assignment)
    extra = set(assignment) - expected
    if missing or extra:
        raise LeakageBoundaryViolation(
            f"ASSIGNMENT_INCOMPLETE: {len(missing)} missing, {len(extra)} unexpected"
        )
    bad = {s for s in assignment.values()} - {TRAIN, HOLDOUT}
    if bad:
        raise LeakageBoundaryViolation(f"UNKNOWN_SPLIT_LABEL {sorted(bad)}")


def assert_share_within_band(assignment: Mapping[str, str], low: float = 0.15, high: float = 0.20) -> float:
    """SSOT §23.2 final-holdout band."""
    share = holdout_share(assignment)
    if not low <= share <= high:
        raise LeakageBoundaryViolation(
            f"HOLDOUT_SHARE_OUT_OF_BAND: {share:.4f} not in [{low}, {high}]"
        )
    return share
