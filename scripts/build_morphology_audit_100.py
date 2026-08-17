"""Director manual morphology audit pack (N=100) 생성.

Decision: RD-20260817-D02D03-CONFORMANCE-01 (Addendum §20-§21)

corrected pilot v002(N=1,000)에서 중복 없이 100건을 뽑는다.
  A. domain balanced        40  (populated domain 각 10)
  B. metric extremes        40  (8개 group × 5)
  C. structural stress      20  (5개 범주 × 4)
중복 제거 후 stable-hash backfill로 정확히 100건을 채운다.

산출물:
  ssot/HumanLebeled/MORPHOLOGY_AUDIT_100_v001/
    README.md                                    판정 기준 + baseline metric (추적)
    [HUMAN]_MORPHOLOGY_AUDIT_100_v001.xlsx       LOCAL ONLY (원문 포함, 커밋 금지)
  outputs/manual_audit/MORPHOLOGY_AUDIT_100_SAMPLING_KEY_v001.csv   machine key (원문 없음)
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from zoneinfo import ZoneInfo

import duckdb
import pandas as pd

from tokenization_premium.hashing import sha256_file
from tokenization_premium.paths import PROJECT_ROOT

KST = ZoneInfo("Asia/Seoul")
PILOT = PROJECT_ROOT / ".runtime/nb04-pilot-v002/MORPH_FEATURES_PILOT_v002.parquet"
REP_V2 = PROJECT_ROOT / "data/registry/REP_FEATURES_v002.parquet"
PAIR = PROJECT_ROOT / "data/registry/PAIR_REGISTRY_v002.parquet"
AUDIT_REQUEST_DIR = PROJECT_ROOT / "ssot/HumanLebeled/MORPHOLOGY_AUDIT_100_v001"
WORKBOOK = AUDIT_REQUEST_DIR / "[HUMAN]_MORPHOLOGY_AUDIT_100_v001.xlsx"
KEY_CSV = PROJECT_ROOT / "outputs/manual_audit/MORPHOLOGY_AUDIT_100_SAMPLING_KEY_v001.csv"
MANIFEST = PROJECT_ROOT / "outputs/manifests/MORPHOLOGY_AUDIT_100_MANIFEST_v001.json"

TARGET_N = 100
SALT = "MORPH_AUDIT_100_v001"


def stable_rank(pair_id: str) -> str:
    """재실행해도 동일한 결정적 순서를 주는 stable hash."""
    return hashlib.md5(f"{pair_id}{SALT}".encode()).hexdigest()  # noqa: S324 - 순서 결정용, 보안용 아님


def load_frame() -> pd.DataFrame:
    """pilot v002 + strata + surface feature + 원문을 하나의 frame으로 모은다."""
    con = duckdb.connect()
    con.execute("SET memory_limit='4GB'")
    con.execute("SET threads=4")
    try:
        df = con.execute(
            "SELECT m.pair_id, m.morpheme_sequence, m.eojeol_count, m.morpheme_count, "
            "  m.particle_count, m.ending_count, m.deriv_affix_count, m.morpheme_density, "
            "  m.particle_ratio, m.ending_ratio, m.deriv_affix_ratio, m.function_morpheme_ratio, "
            "  m.analysis_warning_flag, m.analysis_warning_reason, "
            "  p.logical_corpus, p.translation_direction, p.domain, p.length_stratum, "
            "  p.ko_text_analysis AS ko_text, "
            "  r.ko_latin_share, r.ko_digit_share, r.ko_punctuation_share, r.ko_codepoint_count "
            f"FROM read_parquet('{PILOT.as_posix()}') m "
            f"JOIN read_parquet('{PAIR.as_posix()}') p USING (pair_id) "
            f"JOIN read_parquet('{REP_V2.as_posix()}') r USING (pair_id)"
        ).fetchdf()
    finally:
        con.close()
    df["stable_rank"] = df["pair_id"].map(stable_rank)
    df["has_irregular_affix"] = df["morpheme_sequence"].map(
        lambda seq: any("-" in m["pos"] and m["pos"].split("-")[0] in {"XSN", "XSV", "XSA"} for m in seq))
    return df


def take(df: pd.DataFrame, chosen: dict[str, str], reason: str, n: int,
         *, by: str | None = None, ascending: bool = False) -> None:
    """아직 선택되지 않은 행에서 n건을 고르고 선정 사유를 기록한다 (중복 없음)."""
    pool = df[~df["pair_id"].isin(chosen)]
    if pool.empty:
        return
    order = [by, "stable_rank"] if by else ["stable_rank"]
    ascending_flags = [ascending, True] if by else [True]
    for pair_id in pool.sort_values(order, ascending=ascending_flags).head(n)["pair_id"]:
        chosen[pair_id] = reason


def build_sample(df: pd.DataFrame) -> dict[str, str]:
    """A/B/C 설계로 뽑고 중복 제거 후 stable-hash backfill로 정확히 100건을 만든다."""
    chosen: dict[str, str] = {}

    # --- A. domain balanced 40 -------------------------------------------------
    domains = [d for d in sorted(df["domain"].dropna().unique())]
    per_domain = 40 // max(1, len(domains))
    for domain in domains:
        take(df[df["domain"] == domain], chosen, f"A_domain_{domain}", per_domain)

    # --- B. metric extremes 40 -------------------------------------------------
    extremes = [
        ("B_density_bottom", "morpheme_density", True),
        ("B_density_top", "morpheme_density", False),
        ("B_particle_top", "particle_ratio", False),
        ("B_ending_top", "ending_ratio", False),
        ("B_deriv_affix_top", "deriv_affix_ratio", False),
        ("B_morpheme_count_top", "morpheme_count", False),
        ("B_eojeol_bottom", "eojeol_count", True),
        ("B_eojeol_top", "eojeol_count", False),
    ]
    for reason, column, ascending in extremes:
        take(df, chosen, reason, 5, by=column, ascending=ascending)

    # --- C. structural stress 20 ----------------------------------------------
    stress = [
        ("C_mixed_latin", df[df["ko_latin_share"] > 0], "ko_latin_share", False),
        ("C_digit_unit", df[df["ko_digit_share"] > 0], "ko_digit_share", False),
        ("C_punctuation", df[df["ko_punctuation_share"] > 0], "ko_punctuation_share", False),
        ("C_short_dialogue", df[df["domain"] == "dialogue"], "eojeol_count", True),
        ("C_long_technology", df[df["domain"] == "technology"], "eojeol_count", False),
    ]
    for reason, pool, column, ascending in stress:
        take(pool, chosen, reason, 4, by=column, ascending=ascending)

    # --- 선호 조건: XSA-I 등 irregular affix 사례를 반드시 포함시킨다 -------------
    take(df[df["has_irregular_affix"]], chosen, "D_irregular_affix_case", 4)

    # --- 선호 조건: length_stratum Q1-Q5 각 5건 이상 --------------------------
    for stratum in sorted(df["length_stratum"].dropna().unique()):
        present = sum(1 for pid in chosen if df.loc[df["pair_id"] == pid, "length_stratum"].iloc[0] == stratum)
        if present < 5:
            take(df[df["length_stratum"] == stratum], chosen, f"D_stratum_fill_{stratum}", 5 - present)

    # --- 선호 조건: 주요 direction 대표성 --------------------------------------
    for direction in sorted(df["translation_direction"].dropna().unique()):
        present = sum(
            1 for pid in chosen
            if df.loc[df["pair_id"] == pid, "translation_direction"].iloc[0] == direction)
        if present < 5:
            take(df[df["translation_direction"] == direction], chosen,
                 f"D_direction_fill_{direction}", 5 - present)

    # --- 최종: 초과분은 stable-hash 순으로 절단, 부족분은 backfill --------------
    if len(chosen) > TARGET_N:
        keep = sorted(chosen, key=stable_rank)[:TARGET_N]
        chosen = {pid: chosen[pid] for pid in keep}
    while len(chosen) < TARGET_N:
        before = len(chosen)
        take(df, chosen, "E_stable_hash_backfill", TARGET_N - len(chosen))
        if len(chosen) == before:
            break
    return chosen


def render_sequence(sequence) -> str:
    """형태소 sequence를 사람이 읽을 수 있는 'form/POS' 문자열로 만든다."""
    return " ".join(f"{m['form']}/{m['pos']}" for m in sequence)


if __name__ == "__main__":
    started = dt.datetime.now(tz=KST)
    KEY_CSV.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_REQUEST_DIR.mkdir(parents=True, exist_ok=True)

    frame = load_frame()
    print(f"pilot pool: {len(frame):,} rows  domains={sorted(frame['domain'].dropna().unique())}")
    chosen = build_sample(frame)
    print(f"selected: {len(chosen)} unique pair_ids")

    sample = frame[frame["pair_id"].isin(chosen)].copy()
    sample["sample_reason"] = sample["pair_id"].map(chosen)
    sample = sample.sort_values("stable_rank").reset_index(drop=True)
    sample.insert(0, "no", range(1, len(sample) + 1))
    sample["kiwi_analysis"] = sample["morpheme_sequence"].map(render_sequence)

    reason_counts = sample["sample_reason"].value_counts().sort_index()
    print("\nsample_reason 분포:")
    for reason, count in reason_counts.items():
        print(f"  {reason:34s} {count:>3}")
    print("\ncoverage:")
    for column in ("domain", "length_stratum", "translation_direction", "logical_corpus"):
        counts = sample[column].value_counts().sort_index().to_dict()
        print(f"  {column:22s} {counts}")
    print(f"  irregular affix cases  {int(sample['has_irregular_affix'].sum())}")

    # ---- workbook (LOCAL ONLY: 원문 포함) --------------------------------------
    audit = sample[["no", "pair_id", "ko_text", "kiwi_analysis"]].rename(
        columns={"ko_text": "한국어", "kiwi_analysis": "Kiwi 분석결과"})
    audit["O/X"] = ""

    metrics = sample[[
        "no", "pair_id", "logical_corpus", "translation_direction", "domain", "length_stratum",
        "eojeol_count", "morpheme_count", "particle_count", "ending_count", "deriv_affix_count",
        "morpheme_density", "particle_ratio", "ending_ratio", "deriv_affix_ratio",
        "function_morpheme_ratio", "analysis_warning_flag", "analysis_warning_reason",
        "has_irregular_affix", "sample_reason",
    ]].copy()

    rubric = pd.DataFrame({
        "항목": [
            "판정 대상", "O 기준", "X 기준", "판정 시 주의 1", "판정 시 주의 2", "판정 시 주의 3",
            "morpheme_density 정의", "particle/ending/deriv_affix ratio 정의",
            "조사(J*)", "어미(E*)", "파생접사", "zero-morpheme 규약", "참고",
        ],
        "내용": [
            "Kiwi 형태소 분할과 POS 태그가 해당 한국어 문장에 대해 타당한가",
            "분할 경계와 품사 부착이 모두 타당함 (사소한 대안 분석 여지는 O로 본다)",
            "명백한 오분할, 명백한 오품사, 또는 문장 의미를 왜곡하는 분석",
            "tokenizer/BPE 경계와 무관하다 — 형태소 분석만 본다",
            "고유명사 미등록으로 인한 분할은 analyzer 한계이며 그 자체로 X가 아니다",
            "표기 오류가 있는 원문에서 analyzer가 최선의 분석을 했다면 X가 아니다",
            "MorphemeCount / EojeolCount  (SSOT §13.6)",
            "각 Count / MorphemeCount  (SSOT §13.7)",
            "base tag가 J로 시작하는 태그",
            "base tag가 E로 시작하는 태그",
            "base tag가 XSN / XSV / XSA (XSA-I 등 irregular variant 포함)",
            "형태소가 0개면 pair를 유지하고 warning을 기록하며 ratio는 null (대체 분모 금지)",
            "analyzer: Kiwi kiwipiepy 0.23.2 / model 0.23.0, custom dictionary 미사용",
        ],
    })

    rejudge = pd.DataFrame(columns=[
        "pair_id", "한국어", "Kiwi 분석결과", "기존 O/X", "재판정 O/X", "주요 사유", "재판정 근거", "신뢰도"])

    with pd.ExcelWriter(WORKBOOK, engine="openpyxl") as writer:
        audit.to_excel(writer, sheet_name="audit", index=False)
        metrics.to_excel(writer, sheet_name="참고_메트릭", index=False)
        rubric.to_excel(writer, sheet_name="기준", index=False)
        rejudge.to_excel(writer, sheet_name="X_재판정", index=False)

    # ---- machine key (원문 없음, 추적 가능) ------------------------------------
    key = metrics.copy()
    key["stable_rank"] = sample["stable_rank"]
    key.to_csv(KEY_CSV, index=False, encoding="utf-8")

    # ---- 100/100 exact set equality 검증 ---------------------------------------
    workbook_ids = set(audit["pair_id"])
    key_ids = set(key["pair_id"])
    exact_equal = workbook_ids == key_ids and len(workbook_ids) == TARGET_N
    print(f"\nworkbook ids {len(workbook_ids)} / key ids {len(key_ids)} / "
          f"exact set equality: {exact_equal}")

    payload = {
        "artifact_id": "MORPHOLOGY_AUDIT_100_MANIFEST_v001",
        "decision_id": "RD-20260817-D02D03-CONFORMANCE-01",
        "generated_kst": started.isoformat(timespec="seconds"),
        "source_pilot": {"path": str(PILOT.relative_to(PROJECT_ROOT)), "sha256": sha256_file(PILOT),
                         "rows": int(len(frame))},
        "target_n": TARGET_N,
        "selected_n": int(len(sample)),
        "sampling_salt": SALT,
        "sampling_design": {
            "A_domain_balanced": 40, "B_metric_extremes": 40, "C_structural_stress": 20,
            "D_preference_fills": "irregular affix / length stratum / direction 대표성",
            "E_backfill": "stable md5(pair_id||salt) 순서",
            "replacement": "without replacement (중복 제거 후 backfill)",
        },
        "sample_reason_counts": {str(k): int(v) for k, v in reason_counts.items()},
        "coverage": {
            column: {str(k): int(v) for k, v in sample[column].value_counts().sort_index().items()}
            for column in ("domain", "length_stratum", "translation_direction", "logical_corpus")
        },
        "irregular_affix_cases": int(sample["has_irregular_affix"].sum()),
        "workbook": {
            "path": str(WORKBOOK.relative_to(PROJECT_ROOT)),
            "sha256": sha256_file(WORKBOOK),
            "sheets": ["audit", "참고_메트릭", "기준", "X_재판정"],
            "distribution": "LOCAL_ONLY_CONTAINS_RAW_KO_TEXT_DO_NOT_COMMIT",
        },
        "sampling_key": {"path": str(KEY_CSV.relative_to(PROJECT_ROOT)), "sha256": sha256_file(KEY_CSV),
                         "contains_raw_text": False},
        "exact_set_equality_100": bool(exact_equal),
        "status": "READY_FOR_DIRECTOR_MANUAL_AUDIT",
    }
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"\nworkbook  {WORKBOOK.relative_to(PROJECT_ROOT)}  sha {payload['workbook']['sha256']}")
    print(f"key       {KEY_CSV.relative_to(PROJECT_ROOT)}  sha {payload['sampling_key']['sha256']}")
    print(f"manifest  {MANIFEST.relative_to(PROJECT_ROOT)}")
    if not exact_equal:
        raise SystemExit("FAIL: workbook/key 100건 exact set equality 불일치")
