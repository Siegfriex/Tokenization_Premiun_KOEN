"""G3 token audit sample (N=100) — SSOT §14.2(4) token byte inspection.

결정적 표본에 pair_id / token ids / decoded token bytes(hex) / roundtrip을 담는다.
raw KO/EN 문장은 저장하지 않는다 (공개 저장소 위생). 산출물은 local-only.
"""

from __future__ import annotations

import datetime as dt
import json
from zoneinfo import ZoneInfo

import duckdb

from tokenization_premium.hashing import sha256_file
from tokenization_premium.paths import PROJECT_ROOT
from tokenization_premium.tokenizer_measurement import (
    TOKENIZER_CONFIG_SHA256,
    decoded_token_bytes,
    load_o200k_base_offline,
)

KST = ZoneInfo("Asia/Seoul")
TOK = PROJECT_ROOT / "data/registry/TOKEN_O200K_BASE_v001.parquet"
REP = PROJECT_ROOT / "data/registry/REP_FEATURES_v002.parquet"
PAIR = PROJECT_ROOT / "data/registry/PAIR_REGISTRY_v002.parquet"
CACHE = PROJECT_ROOT / ".runtime/tiktoken-cache"
OUT = PROJECT_ROOT / ".runtime/tok-full/TOKEN_AUDIT_SAMPLE_v001.json"
MANIFEST = PROJECT_ROOT / "outputs/manifests/TOKEN_AUDIT_SAMPLE_MANIFEST_v001.json"
SALT = "TOKEN_AUDIT_v001"
PER_GROUP = 100

con = duckdb.connect()
con.execute("SET memory_limit='5GB'")
con.execute("SET threads=8")
T, R, P = (f"read_parquet('{p.as_posix()}')" for p in (TOK, REP, PAIR))
con.execute(f"CREATE OR REPLACE VIEW j AS SELECT t.*, p.domain, p.length_stratum, "
            f"p.translation_direction, p.logical_corpus, r.ko_script_type_count, "
            f"r.ko_latin_share, r.ko_symbol_other_share, r.ko_codepoint_count "
            f"FROM {T} t JOIN {P} p USING (pair_id) JOIN {R} r USING (pair_id)")

# SSOT §14.2 / §16.3 취지: domain, 길이, mixed script, 희귀 Unicode, TP 양극단을 덮는다.
GROUPS = [
    ("domain_general", "domain = 'general'", "stable"),
    ("domain_other", "domain = 'other'", "stable"),
    ("domain_dialogue", "domain = 'dialogue'", "stable"),
    ("domain_technology", "domain = 'technology'", "stable"),
    ("shortest", "TRUE", "ko_codepoint_count ASC"),
    ("longest", "TRUE", "ko_codepoint_count DESC"),
    ("mixed_script", "ko_script_type_count >= 3", "ko_latin_share DESC"),
    ("rare_unicode", "ko_symbol_other_share > 0", "ko_symbol_other_share DESC"),
    ("tp_highest", "TRUE", "token_premium DESC"),
    ("tp_lowest", "TRUE", "token_premium ASC"),
]

chosen: dict[str, str] = {}
for name, where, order in GROUPS:
    order_sql = f"md5(pair_id || '{SALT}')" if order == "stable" else f"{order}, md5(pair_id || '{SALT}')"
    excl = ""
    if chosen:
        ids = ",".join(f"'{p}'" for p in chosen)
        excl = f" AND pair_id NOT IN ({ids})"
    rows = con.execute(
        f"SELECT pair_id FROM j WHERE {where}{excl} ORDER BY {order_sql} LIMIT 10").fetchall()
    for (pid,) in rows:
        chosen[pid] = name

while len(chosen) < PER_GROUP:
    ids = ",".join(f"'{p}'" for p in chosen)
    rows = con.execute(
        f"SELECT pair_id FROM j WHERE pair_id NOT IN ({ids}) "
        f"ORDER BY md5(pair_id || '{SALT}') LIMIT {PER_GROUP - len(chosen)}").fetchall()
    if not rows:
        break
    for (pid,) in rows:
        chosen[pid] = "stable_hash_backfill"

ids = ",".join(f"'{p}'" for p in chosen)
detail = con.execute(f"""
SELECT pair_id, ko_token_ids, en_token_ids, ko_token_count, en_token_count,
       token_premium, log_token_premium, code_point_ratio, byte_density_ratio,
       compression_penalty, identity_abs_error, roundtrip_ok,
       domain, length_stratum, translation_direction, logical_corpus
FROM j WHERE pair_id IN ({ids}) ORDER BY md5(pair_id || '{SALT}')""").fetchdf()
con.close()

encoding = load_o200k_base_offline(CACHE)
records = []
for _, row in detail.iterrows():
    records.append({
        "pair_id": row["pair_id"],
        "sample_reason": chosen[row["pair_id"]],
        "domain": row["domain"], "length_stratum": row["length_stratum"],
        "translation_direction": row["translation_direction"], "logical_corpus": row["logical_corpus"],
        "ko_token_count": int(row["ko_token_count"]), "en_token_count": int(row["en_token_count"]),
        "token_premium": float(row["token_premium"]),
        "log_token_premium": float(row["log_token_premium"]),
        "code_point_ratio": float(row["code_point_ratio"]),
        "byte_density_ratio": float(row["byte_density_ratio"]),
        "compression_penalty": float(row["compression_penalty"]),
        "identity_abs_error": float(row["identity_abs_error"]),
        "roundtrip_ok": bool(row["roundtrip_ok"]),
        "ko_token_ids_head": [int(v) for v in list(row["ko_token_ids"])[:32]],
        "en_token_ids_head": [int(v) for v in list(row["en_token_ids"])[:32]],
        "ko_token_bytes_head": decoded_token_bytes(row["ko_token_ids"], encoding=encoding),
        "en_token_bytes_head": decoded_token_bytes(row["en_token_ids"], encoding=encoding),
    })

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

reasons: dict[str, int] = {}
for r in records:
    reasons[r["sample_reason"]] = reasons.get(r["sample_reason"], 0) + 1
manifest = {
    "artifact_id": "TOKEN_AUDIT_SAMPLE_MANIFEST_v001",
    "generated_kst": dt.datetime.now(tz=KST).isoformat(timespec="seconds"),
    "spec_ref": "SSOT §14.2(4) token byte representation; §31 G3 audit sample token bytes inspection",
    "source_artifact": {"path": "data/registry/TOKEN_O200K_BASE_v001.parquet",
                        "sha256": sha256_file(TOK)},
    "tokenizer_config_sha256": TOKENIZER_CONFIG_SHA256,
    "sampling_salt": SALT,
    "n": len(records),
    "sample_reason_counts": reasons,
    "coverage": {k: {str(a): int(b) for a, b in
                     detail[k].value_counts().sort_index().items()}
                 for k in ("domain", "length_stratum", "translation_direction", "logical_corpus")},
    "roundtrip_ok_all": all(r["roundtrip_ok"] for r in records),
    "max_identity_abs_error": max(r["identity_abs_error"] for r in records),
    "token_bytes_encoding": "decode_single_token_bytes -> hex, head 32 tokens per side",
    "raw_text_included": False,
    "artifact": {"path": str(OUT.relative_to(PROJECT_ROOT)), "sha256": sha256_file(OUT),
                 "distribution": "LOCAL_ONLY"},
}
MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
print(f"token audit sample n={len(records)}")
print(f"  reasons  {reasons}")
print(f"  roundtrip all ok       {manifest['roundtrip_ok_all']}")
print(f"  max identity abs error {manifest['max_identity_abs_error']:.3e}")
print(f"  coverage domain        {manifest['coverage']['domain']}")
print(f"  coverage length        {manifest['coverage']['length_stratum']}")
print(f"\nsample   {OUT.relative_to(PROJECT_ROOT)}  (local only)")
print(f"manifest {MANIFEST.relative_to(PROJECT_ROOT)}")
