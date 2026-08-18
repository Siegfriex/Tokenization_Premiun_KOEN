"""
/**
 * @purpose 동결 protocol의 실제 설계행렬 위에서만 identifiability / rank / 조건수 / VIF·GVIF /
 *          동일구성 상관을 측정한다. 어떤 모형도 적합하지 않고 어떤 계수도 산출하지 않는다.
 * @spec_ref ssot_g5/02_G5_DIAGNOSTIC_PROTOCOL_v001.md §4 §8 §9 §10 §11
 * @param 없음
 * @return outputs/reports/G5_IDENTIFIABILITY_v001.json,
 *         outputs/reports/G5_COLLINEARITY_v001.json,
 *         outputs/reports/G5_REALIZED_MODEL_CONTRACT_v001.json
 * @raises SystemExit(1) rank deficiency (HARD STOP)
 * @validation review trigger는 실패로 승격되지 않는다. VIF 단독으로 변수를 삭제하지 않는다.
 */
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
from scipy.linalg import qr
from scipy.stats import rankdata

from tokenization_premium.telemetry import RuntimeTelemetry

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime" / "g5"
MATRIX = RUNTIME / "analysis_matrix.parquet"
REPORTS = ROOT / "outputs" / "reports"
PROTOCOL_ID = "G5_DIAGNOSTIC_PROTOCOL_v001"
BASE_MAIN = "4eaa35e8437fc9013305c2b3fcf53133f2a0bddf"

COND_TRIGGER, VIF_TRIGGER, RHO_TRIGGER, NZV_FRACTION = 100.0, 20.0, 0.95, 0.001
CHUNK = 200_000

# ---- protocol §4 blocks, frozen ------------------------------------------------
M0_CONT = ["pair_log_size"]
M1_CONT = ["log_code_point_ratio", "log_byte_density_ratio", "delta_whitespace_density",
           "ko_latin_share", "ko_digit_share", "ko_punctuation_share", "ko_symbol_other_share",
           "en_hangul_share", "en_digit_share", "en_punctuation_share", "en_symbol_other_share",
           "ko_script_type_count", "ko_script_switch_count",
           "en_script_type_count", "en_script_switch_count"]
M2_CONT = ["morpheme_density", "particle_ratio", "ending_ratio", "deriv_affix_ratio"]
M2A_CONT = ["morpheme_density", "function_morpheme_ratio", "deriv_affix_ratio"]
M3_CONT = ["ko_chunk_count_log", "en_chunk_count_log",
           "ko_mean_chunk_bytes", "ko_p50_chunk_bytes", "ko_p90_chunk_bytes", "ko_max_chunk_bytes",
           "en_mean_chunk_bytes", "en_p50_chunk_bytes", "en_p90_chunk_bytes", "en_max_chunk_bytes",
           "ko_max_tokens_per_chunk", "en_max_tokens_per_chunk",
           "ko_chunk_type_share_number", "ko_chunk_type_share_punctuation",
           "ko_chunk_type_share_whitespace",
           "en_chunk_type_share_number", "en_chunk_type_share_punctuation",
           "en_chunk_type_share_whitespace"]

MODELS = {
    "M0":  M0_CONT,
    "M1":  M0_CONT + M1_CONT,
    "M2":  M0_CONT + M1_CONT + M2_CONT,
    "M2A": M0_CONT + M1_CONT + M2A_CONT,
    "M3":  M0_CONT + M1_CONT + M2_CONT + M3_CONT,
}
ALL_CONT = list(dict.fromkeys(sum(MODELS.values(), [])))
CATS = ["source_domain_cell", "translation_direction"]

FAMILIES = {
    "pair_scale": ["pair_log_size", "log_code_point_ratio"],
    "ko_script_comp": ["ko_latin_share", "ko_digit_share", "ko_punctuation_share",
                       "ko_symbol_other_share"],
    "en_script_comp": ["en_hangul_share", "en_digit_share", "en_punctuation_share",
                       "en_symbol_other_share"],
    "script_mixing": ["ko_script_type_count", "ko_script_switch_count",
                      "en_script_type_count", "en_script_switch_count"],
    "morphology": ["morpheme_density", "particle_ratio", "ending_ratio", "deriv_affix_ratio",
                   "function_morpheme_ratio"],
    "d05_chunk_scale": ["ko_chunk_count_log", "en_chunk_count_log"],
    "d05_chunk_bytes_ko": ["ko_mean_chunk_bytes", "ko_p50_chunk_bytes", "ko_p90_chunk_bytes",
                           "ko_max_chunk_bytes"],
    "d05_chunk_bytes_en": ["en_mean_chunk_bytes", "en_p50_chunk_bytes", "en_p90_chunk_bytes",
                           "en_max_chunk_bytes"],
    "d05_chunk_type_ko": ["ko_chunk_type_share_number", "ko_chunk_type_share_punctuation",
                          "ko_chunk_type_share_whitespace"],
    "d05_chunk_type_en": ["en_chunk_type_share_number", "en_chunk_type_share_punctuation",
                          "en_chunk_type_share_whitespace"],
    "d05_max_tokens": ["ko_max_tokens_per_chunk", "en_max_tokens_per_chunk"],
}


def _levels(cohort: dict, key: str) -> tuple[list[str], str]:
    counts = cohort[f"{key}_counts"]
    ref = cohort["reference_levels"][key]
    non_ref = [lv for lv in sorted(counts, key=lambda x: (-counts[x], x)) if lv != ref]
    return non_ref, ref


def main() -> int:
    cohort = json.loads((ROOT / "outputs" / "manifests"
                         / "ANALYSIS_COHORT_v001.json").read_text(encoding="utf-8"))
    n_rows = cohort["N"]
    cell_lv, cell_ref = _levels(cohort, "source_domain_cell")
    dir_lv, dir_ref = _levels(cohort, "translation_direction")
    dummies = ([f"cell::{lv}" for lv in cell_lv] + [f"dir::{lv}" for lv in dir_lv])
    design_cols = ALL_CONT + dummies                       # intercept는 별도 처리
    p_all = len(design_cols)
    idx = {c: i for i, c in enumerate(design_cols)}

    pf = pq.ParquetFile(MATRIX)
    read_cols = ALL_CONT + CATS

    def batches():
        for b in pf.iter_batches(batch_size=CHUNK, columns=read_cols):
            d = b.to_pydict()
            m = len(d[ALL_CONT[0]])
            X = np.empty((m, p_all), dtype=np.float64)
            for c in ALL_CONT:
                X[:, idx[c]] = np.asarray(d[c], dtype=np.float64)
            cell = np.asarray(d["source_domain_cell"], dtype=object)
            drc = np.asarray(d["translation_direction"], dtype=object)
            for lv in cell_lv:
                X[:, idx[f"cell::{lv}"]] = (cell == lv).astype(np.float64)
            for lv in dir_lv:
                X[:, idx[f"dir::{lv}"]] = (drc == lv).astype(np.float64)
            yield X

    # ---- pass 1: exact Gram, sums, min/max ------------------------------------
    with RuntimeTelemetry(run_id="G5_DIAG_PASS1", stage="GRAM", total=n_rows) as tel:
        G = np.zeros((p_all, p_all))
        s = np.zeros(p_all)
        vmin = np.full(p_all, np.inf)
        vmax = np.full(p_all, -np.inf)
        n = 0
        for X in batches():
            G += X.T @ X
            s += X.sum(axis=0)
            vmin = np.minimum(vmin, X.min(axis=0))
            vmax = np.maximum(vmax, X.max(axis=0))
            n += X.shape[0]
            tel.update(X.shape[0])
        tel1 = tel
    assert n == n_rows, f"row count drift {n} != {n_rows}"

    mean = s / n
    ss = np.diag(G) - n * mean**2                      # centred sum of squares
    sd = np.sqrt(np.maximum(ss, 0.0) / n)
    S = G - np.outer(s, s) / n                         # centred cross-products
    zero_var = [design_cols[i] for i in range(p_all) if sd[i] == 0.0]
    denom = np.where(sd > 0, sd, 1.0)
    corr = S / (n * np.outer(denom, denom))
    np.fill_diagonal(corr, 1.0)

    nzv = []
    for i, c in enumerate(design_cols):
        if c.startswith(("cell::", "dir::")):
            minority = min(s[i], n - s[i])
            if minority < NZV_FRACTION * n:
                nzv.append({"column": c, "minority_count": int(minority),
                            "fraction": minority / n})

    # ---- pass 2: streaming QR on the standardized design, per model -----------
    model_cols = {name: ["__intercept__"] + cont
                  + [f"cell::{lv}" for lv in cell_lv] + [f"dir::{lv}" for lv in dir_lv]
                  for name, cont in MODELS.items()}
    Rf: dict[str, np.ndarray | None] = dict.fromkeys(MODELS)

    with RuntimeTelemetry(run_id="G5_DIAG_PASS2", stage="QR", total=n_rows) as tel:
        for X in batches():
            m = X.shape[0]
            Z = np.empty((m, p_all + 1))
            Z[:, 0] = 1.0                                          # intercept, 표준화하지 않음
            for i, c in enumerate(design_cols):
                if c.startswith(("cell::", "dir::")):
                    Z[:, i + 1] = X[:, i]                           # dummy는 0/1 유지
                else:
                    Z[:, i + 1] = (X[:, i] - mean[i]) / (sd[i] if sd[i] > 0 else 1.0)
            zidx = {"__intercept__": 0, **{c: i + 1 for i, c in enumerate(design_cols)}}
            for name, cols in model_cols.items():
                B = Z[:, [zidx[c] for c in cols]]
                stack = B if Rf[name] is None else np.vstack([Rf[name], B])
                Rf[name] = qr(stack, mode="r")[0][:len(cols), :]
            tel.update(m)
        tel2 = tel

    eps = np.finfo(float).eps
    collinearity: dict = {}
    identifiability: dict = {}
    hard_fail: list[str] = []
    review: list[dict] = []

    for name, cols in model_cols.items():
        sv = np.linalg.svd(Rf[name], compute_uv=False)
        tol = max(n_rows, len(cols)) * eps * sv[0]
        rank = int((sv > tol).sum())
        p = len(cols)
        cond_std = float(sv[0] / sv[-1]) if sv[-1] > 0 else float("inf")

        nz = [c for c in cols if c != "__intercept__"]
        ii = [idx[c] for c in nz]
        Rm = corr[np.ix_(ii, ii)]
        try:
            vif = dict(zip(nz, np.diag(np.linalg.inv(Rm)), strict=True))
        except np.linalg.LinAlgError:
            vif = dict.fromkeys(nz, float("inf"))
        gvif = {}
        for block, pref in (("source_domain_cell", "cell::"), ("translation_direction", "dir::")):
            bi = [k for k, c in enumerate(nz) if c.startswith(pref)]
            zi = [k for k, c in enumerate(nz) if not c.startswith(pref)]
            if bi and zi:
                sgn_b, ld_b = np.linalg.slogdet(Rm[np.ix_(bi, bi)])
                sgn_z, ld_z = np.linalg.slogdet(Rm[np.ix_(zi, zi)])
                sgn_f, ld_f = np.linalg.slogdet(Rm)
                g = float(np.exp(ld_b + ld_z - ld_f)) if min(sgn_b, sgn_z, sgn_f) > 0 else None
                gvif[block] = {"gvif": g, "df": len(bi),
                               "gvif_1_2df": None if g is None else float(g ** (1 / (2 * len(bi))))}

        # raw-coding 조건수 (trigger 아님)
        Graw = G[np.ix_(ii, ii)]
        sv_raw = np.sqrt(np.maximum(np.linalg.eigvalsh(Graw), 0.0))
        cond_raw = float(sv_raw[-1] / sv_raw[0]) if sv_raw[0] > 0 else float("inf")

        vmax_c = max(vif.values())
        gmax = max([b["gvif_1_2df"] for b in gvif.values() if b["gvif_1_2df"] is not None],
                   default=None)
        collinearity[name] = {
            "p_with_intercept": p, "rank": rank, "rank_deficiency": p - rank,
            "full_rank": rank == p,
            "condition_number_standardized": cond_std,
            "condition_number_raw_coding_not_a_trigger": cond_raw,
            "max_vif": float(vmax_c),
            "top_vif": {k: float(v) for k, v in
                        sorted(vif.items(), key=lambda kv: -kv[1])[:6]},
            "gvif": gvif,
            "triggers": sorted(
                (["CONDITION_NUMBER >= 100 -> REPARAMETERIZATION_REVIEW"]
                 if cond_std >= COND_TRIGGER else [])
                + (["VIF >= 20 -> STRONG_REDUNDANCY_REVIEW"] if vmax_c >= VIF_TRIGGER else [])
                + (["GVIF^(1/2df) >= 20 -> STRONG_REDUNDANCY_REVIEW"]
                   if gmax is not None and gmax >= VIF_TRIGGER else [])),
        }
        if rank != p:
            hard_fail.append(f"{name}_RANK_DEFICIENT: p={p} rank={rank}")
        for t in collinearity[name]["triggers"]:
            review.append({"model": name, "trigger": t})

    # ---- same-construct Spearman ----------------------------------------------
    with RuntimeTelemetry(run_id="G5_DIAG_SPEARMAN", stage="RANK_CORR", total=n_rows) as tel:
        spearman = {}
        for fam, cols in FAMILIES.items():
            arr = pf.read(columns=cols).to_pydict()
            Rk = np.column_stack([rankdata(np.asarray(arr[c], dtype=np.float64), method="average")
                                  for c in cols])
            del arr
            C = np.corrcoef(Rk, rowvar=False)
            del Rk
            pairs = {f"{cols[i]} ~ {cols[j]}": float(C[i, j])
                     for i in range(len(cols)) for j in range(i + 1, len(cols))}
            mx = max(pairs.items(), key=lambda kv: abs(kv[1]))
            spearman[fam] = {"n_members": len(cols), "max_abs_rho": abs(mx[1]),
                             "max_abs_rho_pair": mx[0], "pairs": pairs,
                             "trigger": abs(mx[1]) >= RHO_TRIGGER}
            if abs(mx[1]) >= RHO_TRIGGER:
                review.append({"family": fam,
                               "trigger": "|rho| >= 0.95 -> REPRESENTATIVE_FEATURE_REVIEW"})
            tel.update(n_rows // len(FAMILIES))
        tel3 = tel

    # ---- identifiability --------------------------------------------------------
    sxd = cohort["source_by_domain"]
    sources = sorted({r["source_id"] for r in sxd})
    domains = sorted({r["domain"] for r in sxd})
    shared = [d for d in domains if len({r["source_id"] for r in sxd if r["domain"] == d}) > 1]
    cxd = cohort["cell_by_direction"]
    seen = {(r["source_domain_cell"], r["translation_direction"]): r["n"] for r in cxd}
    cells = sorted(cohort["source_domain_cell_counts"])
    dirs = sorted(cohort["translation_direction_counts"])
    empty = [{"source_domain_cell": c, "translation_direction": d}
             for c in cells for d in dirs if seen.get((c, d), 0) == 0]
    singleton = [{"source_domain_cell": c, "translation_direction": d, "n": seen[(c, d)]}
                 for c in cells for d in dirs if 0 < seen.get((c, d), 0) < 1000]

    identifiability = {
        "artifact_id": "G5_IDENTIFIABILITY_v001", "protocol_id": PROTOCOL_ID,
        "base_main_sha": BASE_MAIN, "N": n_rows,
        "source_levels": len(sources), "domain_levels": len(domains),
        "domains_shared_across_sources": shared,
        "source_domain_separately_identifiable": len(shared) == len(domains),
        "source_domain_verdict": ("COMPOSITE_CELL_CONTROL_ONLY" if len(shared) != len(domains)
                                  else "SEPARATELY_IDENTIFIABLE"),
        "source_by_domain": sxd,
        "cell_by_direction": cxd,
        "empty_cell_direction_combinations": empty,
        "near_singleton_cell_direction_combinations": singleton,
        "reference_levels": {"source_domain_cell": cell_ref, "translation_direction": dir_ref},
        "translation_direction_levels_retained": dirs,
        "sentence_type_zero_variance": cohort["sentence_type_zero_variance"],
        "logical_corpus_bijection": cohort["logical_corpus_bijection"],
        "zero_variance_design_columns": zero_var,
        "near_zero_variance_review": nzv,
        "rank_by_model": {k: {"p": v["p_with_intercept"], "rank": v["rank"],
                              "deficiency": v["rank_deficiency"]}
                          for k, v in collinearity.items()},
        "cell_direction_interaction": "NOT_ESTIMABLE_NOT_INTRODUCED" if empty else "NOT_INTRODUCED",
    }

    coll_out = {
        "artifact_id": "G5_COLLINEARITY_v001", "protocol_id": PROTOCOL_ID,
        "base_main_sha": BASE_MAIN, "N": n_rows,
        "trigger_thresholds": {"condition_number": COND_TRIGGER, "vif_gvif": VIF_TRIGGER,
                               "spearman_rho": RHO_TRIGGER,
                               "near_zero_variance_fraction": NZV_FRACTION},
        "trigger_semantics": "review trigger != failure; VIF alone never deletes a variable",
        "models": collinearity,
        "same_construct_spearman": spearman,
        "composition_status": "VALID (reference-coded; see cohort manifest closure errors)",
        "review_triggers": review,
    }

    contract = {
        "artifact_id": "G5_REALIZED_MODEL_CONTRACT_v001", "protocol_id": PROTOCOL_ID,
        "base_main_sha": BASE_MAIN,
        "outcome_A": "log_token_premium", "outcome_B": "log_compression_penalty",
        "outcome_A_matrix": "MODEL_MATRICES_BELOW",
        "outcome_B_matrix": "IDENTICAL_RHS_TO_OUTCOME_A",
        "outcome_B_note": ("SPEC-02: SSOT §18.2's illustrative form omits logCR/logBDR; the "
                           "approved common ladder includes them. Neither outcome can be "
                           "reconstructed from its own RHS."),
        "models": {name: {"continuous": cont,
                          "categorical": {"source_domain_cell": {"levels": len(cell_lv) + 1,
                                                                 "reference": cell_ref},
                                          "translation_direction": {"levels": len(dir_lv) + 1,
                                                                    "reference": dir_ref}},
                          "p_with_intercept": len(model_cols[name])}
                   for name, cont in MODELS.items()},
        "structural_removals": cohort["structural_identity_max_abs_error"],
        "column_summary": {c: {"mean": float(mean[idx[c]]), "sd": float(sd[idx[c]]),
                               "min": float(vmin[idx[c]]), "max": float(vmax[idx[c]])}
                           for c in design_cols},
        "runtime_telemetry": {k: {kk: vv for kk, vv in t.summary().items() if kk != "samples"}
                              for k, t in (("pass1_gram", tel1), ("pass2_qr", tel2),
                                           ("spearman", tel3))},
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    for fn, obj in (("G5_IDENTIFIABILITY_v001.json", identifiability),
                    ("G5_COLLINEARITY_v001.json", coll_out),
                    ("G5_REALIZED_MODEL_CONTRACT_v001.json", contract)):
        (REPORTS / fn).write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)
                                  + "\n", encoding="utf-8")

    print("model   p  rank  def   cond(std)     cond(raw)      maxVIF   triggers")
    for k, v in collinearity.items():
        print(f"{k:5s} {v['p_with_intercept']:3d} {v['rank']:5d} {v['rank_deficiency']:4d}"
              f" {v['condition_number_standardized']:11.2f} {v['condition_number_raw_coding_not_a_trigger']:13.2f}"
              f" {v['max_vif']:11.2f}   {len(v['triggers'])}")
    print("\nspearman max |rho| by family:")
    for k, v in spearman.items():
        print(f"  {v['max_abs_rho']:.4f} {'*' if v['trigger'] else ' '} {k:22s} {v['max_abs_rho_pair']}")
    print("\nhard_fail:", hard_fail)
    print("review triggers:", json.dumps(review, ensure_ascii=False))
    return 1 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main())
