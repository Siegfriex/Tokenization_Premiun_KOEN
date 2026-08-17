"""Corrected morphology pilot v002 (N=1,000) + superseded pilot 대조.

Decision: RD-20260817-D02D03-CONFORMANCE-01

동일 pair set에 대해 v001(defective) 대비 무엇이 정확히 얼마나 바뀌었는지 보인다.
Claude-B가 제시한 기대치와 exact 비교하며, 불일치 시 단순 FAIL로 끝내지 않고
pair/tag 수준 원인을 함께 출력한다.
"""

from __future__ import annotations

import datetime as dt
import json
from collections import Counter
from zoneinfo import ZoneInfo

import duckdb

from tokenization_premium.hashing import sha256_file
from tokenization_premium.memory_guard import MemoryGuard
from tokenization_premium.morphology import (
    MORPHOLOGY_CONFIG,
    MORPHOLOGY_CONFIG_SHA256,
    base_tag,
    execute_morphology_run,
)
from tokenization_premium.paths import PROJECT_ROOT

KST = ZoneInfo("Asia/Seoul")
REP_V2 = PROJECT_ROOT / "data/registry/REP_FEATURES_v002.parquet"
PAIR = PROJECT_ROOT / "data/registry/PAIR_REGISTRY_v002.parquet"
OLD_PILOT = PROJECT_ROOT / ".runtime/nb04-pilot/MORPH_FEATURES_PILOT_v001.parquet"
RUNTIME = PROJECT_ROOT / ".runtime/nb04-pilot-v002"
OUT = RUNTIME / "MORPH_FEATURES_PILOT_v002.parquet"
MANIFEST = PROJECT_ROOT / "outputs/manifests/MORPH_FEATURES_PILOT_MANIFEST_v002.json"

PILOT_N = 1_000
NUM_WORKERS = 24          # benchmark 선정값
ANALYSIS_BATCH = 2_500    # benchmark 선정값 (pilot N보다 크므로 단일 chunk)

# Claude-B가 제시한 corrected pilot 기대치 (동일 pair set 전제).
B_EXPECTED = {
    "particle_count_changed_rows": 0,
    "ending_count_changed_rows": 0,
    "xsa_irregular_token_occurrences": 8,
    "deriv_affix_total_old": 1692,
    "deriv_affix_total_new": 1700,
    "changed_pair_rows": 8,
}


def compare_with_superseded_pilot(con: duckdb.DuckDBPyConnection) -> dict:
    """v001 pilot과 동일 pair set인지 확인하고 count 단위 delta를 산출한다."""
    new = f"read_parquet('{OUT.as_posix()}')"
    old = f"read_parquet('{OLD_PILOT.as_posix()}')"

    only_new, only_old = con.execute(
        f"SELECT (SELECT count(*) FROM (SELECT pair_id FROM {new} EXCEPT SELECT pair_id FROM {old})),"
        f"       (SELECT count(*) FROM (SELECT pair_id FROM {old} EXCEPT SELECT pair_id FROM {new}))"
    ).fetchone()
    same_pair_set = only_new == 0 and only_old == 0

    # v001은 count를 저장하지 않고 ratio만 저장했으므로 ratio * morpheme_count로 복원한다.
    joined = (
        f"SELECT n.pair_id, n.morpheme_count AS new_mc, o.ko_morpheme_count AS old_mc, "
        f"  n.particle_count AS new_particle, "
        f"  CAST(round(o.ko_particle_ratio * o.ko_morpheme_count) AS BIGINT) AS old_particle, "
        f"  n.ending_count AS new_ending, "
        f"  CAST(round(o.ko_ending_ratio * o.ko_morpheme_count) AS BIGINT) AS old_ending, "
        f"  n.deriv_affix_count AS new_deriv, "
        f"  CAST(round(o.ko_deriv_affix_ratio * o.ko_morpheme_count) AS BIGINT) AS old_deriv, "
        f"  n.morpheme_density AS new_density, o.ko_morpheme_density AS old_density "
        f"FROM {new} n JOIN {old} o USING (pair_id)"
    )
    agg = con.execute(
        f"SELECT count(*), "
        f"  sum((new_mc <> old_mc)::INT), "
        f"  sum((new_particle <> old_particle)::INT), "
        f"  sum((new_ending <> old_ending)::INT), "
        f"  sum((new_deriv <> old_deriv)::INT), "
        f"  sum(old_deriv), sum(new_deriv), "
        f"  sum((abs(new_density - old_density) > 1e-12)::INT) "
        f"FROM ({joined})"
    ).fetchone()
    (rows, mc_changed, particle_changed, ending_changed, deriv_changed,
     old_deriv_total, new_deriv_total, density_changed) = agg

    changed_detail = con.execute(
        f"SELECT pair_id, old_deriv, new_deriv, new_deriv - old_deriv AS delta "
        f"FROM ({joined}) WHERE new_deriv <> old_deriv ORDER BY pair_id"
    ).fetchdf()

    return {
        "same_pair_set": bool(same_pair_set),
        "pair_ids_only_in_v002": int(only_new),
        "pair_ids_only_in_v001": int(only_old),
        "compared_rows": int(rows),
        "morpheme_count_changed_rows": int(mc_changed),
        "particle_count_changed_rows": int(particle_changed),
        "ending_count_changed_rows": int(ending_changed),
        "deriv_affix_count_changed_rows": int(deriv_changed),
        "morpheme_density_changed_rows": int(density_changed),
        "deriv_affix_total_old": int(old_deriv_total),
        "deriv_affix_total_new": int(new_deriv_total),
        "deriv_affix_total_delta": int(new_deriv_total - old_deriv_total),
        "changed_pairs": changed_detail.to_dict(orient="records"),
    }


def tag_evidence(con: duckdb.DuckDBPyConnection) -> dict:
    """pilot 전체의 tag 분포에서 irregular affix 발생을 직접 센다."""
    rows = con.execute(
        f"SELECT m.pos AS tag, count(*) AS n "
        f"FROM read_parquet('{OUT.as_posix()}'), unnest(morpheme_sequence) AS t(m) "
        f"GROUP BY m.pos ORDER BY n DESC"
    ).fetchall()
    raw = {tag: int(n) for tag, n in rows}
    irregular = {tag: n for tag, n in raw.items() if "-" in tag}
    xsa_irregular = {tag: n for tag, n in raw.items() if base_tag(tag) == "XSA" and "-" in tag}
    base_counts: Counter[str] = Counter()
    for tag, n in raw.items():
        base_counts[base_tag(tag)] += n
    unmapped = {
        tag: n for tag, n in sorted(raw.items())
        if not (base_tag(tag).startswith(("J", "E")) or base_tag(tag) in {"XSN", "XSV", "XSA"})
    }
    return {
        "distinct_raw_tags": len(raw),
        "distinct_base_tags": len(base_counts),
        "raw_tag_counts": dict(sorted(raw.items())),
        "irregular_tag_counts": dict(sorted(irregular.items())),
        "xsa_irregular_token_occurrences": sum(xsa_irregular.values()),
        "xsa_irregular_detail": dict(sorted(xsa_irregular.items())),
        "deriv_affix_family_counts": {
            tag: n for tag, n in sorted(raw.items()) if base_tag(tag) in {"XSN", "XSV", "XSA"}
        },
        "tags_outside_mapped_groups": len(unmapped),
        "unmapped_tag_note": "J*/E*/XS{N,V,A} 밖의 tag는 설계상 세 group 어디에도 매핑되지 않는다 (POS zoo 금지)",
    }


def distributions(con: duckdb.DuckDBPyConnection) -> dict:
    """corrected pilot의 주요 feature 분포를 요약한다."""
    q = con.execute(
        "SELECT "
        "  count(*), sum(analysis_warning_flag::INT), "
        "  min(eojeol_count), max(eojeol_count), avg(eojeol_count), "
        "  min(morpheme_count), max(morpheme_count), avg(morpheme_count), "
        "  min(morpheme_density), median(morpheme_density), max(morpheme_density), "
        "  min(particle_ratio), median(particle_ratio), max(particle_ratio), "
        "  min(ending_ratio), median(ending_ratio), max(ending_ratio), "
        "  min(deriv_affix_ratio), median(deriv_affix_ratio), max(deriv_affix_ratio), "
        "  sum((NOT isfinite(morpheme_density))::INT), "
        "  sum((particle_ratio IS NULL)::INT) "
        f"FROM read_parquet('{OUT.as_posix()}')"
    ).fetchone()
    keys = ["rows", "warning_rows", "eojeol_min", "eojeol_max", "eojeol_mean",
            "morpheme_min", "morpheme_max", "morpheme_mean",
            "density_min", "density_median", "density_max",
            "particle_min", "particle_median", "particle_max",
            "ending_min", "ending_median", "ending_max",
            "deriv_min", "deriv_median", "deriv_max",
            "nonfinite_density", "null_particle_ratio"]
    return {k: (float(v) if isinstance(v, float) else int(v)) for k, v in zip(keys, q, strict=True)}


if __name__ == "__main__":
    RUNTIME.mkdir(parents=True, exist_ok=True)
    OUT.unlink(missing_ok=True)
    OUT.with_suffix(".parquet.partial").unlink(missing_ok=True)
    run_id = "NB04_PILOT_V002_" + dt.datetime.now(tz=KST).strftime("%Y%m%dT%H%M%S")
    guard = MemoryGuard(run_id)
    boot = guard.sample()
    print(f"run_id={run_id}  MemAvailable={boot.mem_available_gib} GiB  swappiness={guard.swappiness}  "
          f"status={boot.status}")

    manifest = execute_morphology_run(
        project_root=PROJECT_ROOT,
        rep_features_v002_path=REP_V2,
        pair_registry_path=PAIR,
        output_path=OUT,
        runtime_dir=RUNTIME,
        run_id=run_id,
        run_mode="PILOT",
        limit=PILOT_N,
        num_workers=NUM_WORKERS,
        batch_rows=ANALYSIS_BATCH,
    )
    guard.sample()
    print(f"\npilot rows={manifest['output']['row_count']:,}  "
          f"{manifest['rows_per_sec']:,.1f} rows/s  warmup={manifest['warmup_sec']}s  "
          f"zero_morpheme={manifest['zero_morpheme_rows']}")

    con = duckdb.connect()
    try:
        comparison = compare_with_superseded_pilot(con)
        tags = tag_evidence(con)
        dist = distributions(con)
    finally:
        con.close()

    checks = {
        "particle_count_changed_rows": comparison["particle_count_changed_rows"],
        "ending_count_changed_rows": comparison["ending_count_changed_rows"],
        "xsa_irregular_token_occurrences": tags["xsa_irregular_token_occurrences"],
        "deriv_affix_total_old": comparison["deriv_affix_total_old"],
        "deriv_affix_total_new": comparison["deriv_affix_total_new"],
        "changed_pair_rows": comparison["deriv_affix_count_changed_rows"],
    }
    matched = {k: (checks[k] == B_EXPECTED[k]) for k in B_EXPECTED}

    print(f"\nsame pair set as superseded pilot: {comparison['same_pair_set']} "
          f"(only_v002={comparison['pair_ids_only_in_v002']}, only_v001={comparison['pair_ids_only_in_v001']})")
    print(f"morpheme_count changed rows: {comparison['morpheme_count_changed_rows']}  "
          f"(analysis 자체는 동일해야 하므로 0이 기대값)")
    print("\nClaude-B expectation check:")
    print(f"  {'metric':38s} {'expected':>10s} {'observed':>10s}  match")
    for key, expected in B_EXPECTED.items():
        print(f"  {key:38s} {expected:>10} {checks[key]:>10}  {'OK' if matched[key] else 'MISMATCH'}")

    if not all(matched.values()):
        print("\n  -- mismatch 원인 조사 --")
        print(f"  irregular tags observed: {tags['irregular_tag_counts']}")
        print(f"  deriv affix family    : {tags['deriv_affix_family_counts']}")
        print(f"  changed pairs         : {comparison['changed_pairs']}")

    print(f"\nchanged pairs ({len(comparison['changed_pairs'])}):")
    for row in comparison["changed_pairs"]:
        print(f"  {row['pair_id'][:28]}…  deriv {row['old_deriv']} -> {row['new_deriv']} "
              f"(delta {row['delta']:+d})")

    payload = {
        **manifest,
        "artifact_id": "MORPH_FEATURES_PILOT_MANIFEST_v002",
        "supersedes": "outputs/manifests/MORPH_FEATURES_PILOT_MANIFEST_v001.json",
        "morphology_config": MORPHOLOGY_CONFIG,
        "morphology_config_sha256": MORPHOLOGY_CONFIG_SHA256,
        "superseded_pilot": {
            "path": str(OLD_PILOT.relative_to(PROJECT_ROOT)),
            "sha256": sha256_file(OLD_PILOT),
            "status": "SUPERSEDED_BY_CONFORMANCE_DEFECT",
        },
        "comparison_with_superseded_pilot": comparison,
        "tag_evidence": tags,
        "distributions": dist,
        "claude_b_expectation": {"expected": B_EXPECTED, "observed": checks, "matched": matched,
                                 "all_matched": all(matched.values())},
        "memory_guard": guard.summary(),
        "selected_engine": {"num_workers": NUM_WORKERS, "analysis_batch": ANALYSIS_BATCH},
        "status": "CORRECTED_PILOT_COMPLETE_FULL_RUN_STILL_PROHIBITED",
    }
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"\nwrote {MANIFEST.relative_to(PROJECT_ROOT)}")
    print(f"pilot artifact sha256 {manifest['output']['sha256']}")
    print(f"ALL_B_EXPECTATIONS_MATCHED = {all(matched.values())}")
