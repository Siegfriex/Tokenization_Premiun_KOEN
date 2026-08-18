"""PRE-NB09 독립 감사 하네스 — Claude-A.

B가 PRE-NB09 protocol을 동결하면, 그 protocol을 **audit spec**(JSON) 하나로 옮겨적고
이 스크립트를 돌린다. 스크립트는 spec이 선언한 것만 계산한다. 변수 목록도, 임계값도,
참조 수준도 여기에 하드코딩돼 있지 않다 — 전부 spec에서 온다.

설계 원칙
---------
1. **Spec이 없으면 실행되지 않는다.** 기본 변수 목록이 없으므로, spec을 주지 않고 돌리면
   fail-closed로 멈춘다. 감사자가 피감사자의 사양을 대신 발명할 수 없다.
2. **모델을 적합하지 않는다.** 계수도, p-value도, R²도 생성하지 않는다. rank·조건수·
   VIF/GVIF는 전부 Gram 행렬에서 유도한다 (`§10` 참조).
3. **결정론적.** 표본추출 없음, 시드 없음. 전집단 2-pass 스트리밍.
4. **규약을 명시한다.** 조건수의 절편 포함 여부처럼 정의가 갈리는 지점은 spec이 선언하고
   결과에 그대로 되적는다 (G5 감사 note `A-01`의 재발 방지).

실행
----
    python scripts/audit_pre_nb09.py <spec.json> <out.json>
    python scripts/audit_pre_nb09.py --emit-schema        # spec JSON schema를 출력
    python scripts/audit_pre_nb09.py --self-test <spec>   # 알려진 기준선으로 하네스 검증

일곱 가지 검사 (지시서 §3)
--------------------------
    C1  exact predictor column inventory
    C2  outcome leakage check
    C3  matrix rank
    C4  standardized condition number
    C5  VIF / GVIF
    C6  same-construct structural relationship
    C7  block nesting consistency
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import duckdb
import numpy as np

# ---------------------------------------------------------------------------
# spec 계약
# ---------------------------------------------------------------------------

SPEC_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "PRE-NB09 audit spec",
    "description": (
        "피감사 protocol을 기계가 읽을 수 있게 옮겨적은 것. 이 파일의 모든 값은 "
        "protocol 문서에서 그대로 와야 하며, 감사자가 임의로 채우지 않는다."
    ),
    "type": "object",
    "required": [
        "spec_id", "protocol_id", "protocol_commit", "base_main_sha",
        "artifacts", "spine", "cohort", "columns", "models", "outcomes",
        "leakage", "families", "nesting", "conventions", "thresholds",
    ],
    "additionalProperties": False,
    "properties": {
        "spec_id": {"type": "string"},
        "protocol_id": {"type": "string"},
        "protocol_commit": {"type": "string", "description": "결과보다 먼저 동결된 protocol commit"},
        "base_main_sha": {"type": "string"},
        "artifacts": {
            "type": "object",
            "description": "논리 이름 -> {path, sha256}. 감사 시작 전에 재해시한다.",
            "additionalProperties": {
                "type": "object",
                "required": ["path", "sha256"],
                "properties": {"path": {"type": "string"}, "sha256": {"type": "string"}},
            },
        },
        "spine": {"type": "string", "description": "cohort를 정의하는 artifact의 논리 이름"},
        "cohort": {
            "type": "object",
            "required": ["id_column", "expected_n", "expected_pair_set_md5"],
            "properties": {
                "id_column": {"type": "string"},
                "expected_n": {"type": "integer"},
                "expected_pair_set_md5": {"type": "string"},
            },
        },
        "columns": {
            "type": "object",
            "description": "설계행렬에 들어갈 수 있는 모든 항. 여기 없는 항은 어떤 모형에도 못 들어간다.",
            "additionalProperties": {
                "type": "object",
                "required": ["kind", "sql"],
                "properties": {
                    "kind": {"enum": ["continuous", "categorical"]},
                    "sql": {"type": "string", "description": "artifact alias를 쓰는 SQL 식"},
                    "artifact": {"type": "string"},
                    "physical_column": {"type": ["string", "null"]},
                    "derived_from": {"type": "string", "description": "파생항이면 근거 조항"},
                    "reference_rule": {
                        "enum": ["largest_realized_level", "declared"],
                        "description": "categorical 전용",
                    },
                    "reference_level": {"type": ["string", "null"]},
                },
            },
        },
        "models": {
            "type": "object",
            "description": "모형 이름 -> columns의 키 목록 (절편은 자동, 여기 적지 않는다)",
            "additionalProperties": {"type": "array", "items": {"type": "string"}},
        },
        "outcomes": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["sql", "models"],
                "properties": {
                    "sql": {"type": "string"},
                    "models": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "leakage": {
            "type": "object",
            "required": ["excluded", "identities"],
            "properties": {
                "excluded": {
                    "type": "array",
                    "description": "구조적으로 배제된 물리 열과 그 사유",
                    "items": {
                        "type": "object",
                        "required": ["column", "reason", "klass"],
                        "properties": {
                            "column": {"type": "string"},
                            "reason": {"type": "string"},
                            "klass": {"type": "string"},
                        },
                    },
                },
                "identities": {
                    "type": "array",
                    "description": "배제를 정당화하는 항등식. 각각 전집단에서 측정한다.",
                    "items": {
                        "type": "object",
                        "required": ["name", "sql", "max_abs_error"],
                        "properties": {
                            "name": {"type": "string"},
                            "sql": {"type": "string", "description": "오차를 반환하는 스칼라 식"},
                            "max_abs_error": {"type": "number", "description": "허용 상한"},
                        },
                    },
                },
            },
        },
        "families": {
            "type": "object",
            "description": "same-construct 가족 -> columns 키 목록. 가족 내부만 검사한다.",
            "additionalProperties": {"type": "array", "items": {"type": "string"}},
        },
        "nesting": {
            "type": "object",
            "required": ["chains", "mutually_exclusive"],
            "properties": {
                "chains": {
                    "type": "array",
                    "description": "각 사슬은 왼쪽이 오른쪽의 진부분집합이어야 한다",
                    "items": {"type": "array", "items": {"type": "string"}},
                },
                "mutually_exclusive": {
                    "type": "array",
                    "description": "한 모형 안에 공존하면 안 되는 열 집합",
                    "items": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "conventions": {
            "type": "object",
            "required": ["condition_number_includes_intercept", "spearman_tie_handling",
                         "standardize_dummies"],
            "properties": {
                "condition_number_includes_intercept": {"type": "boolean"},
                "spearman_tie_handling": {"enum": ["midrank", "competition"]},
                "standardize_dummies": {"type": "boolean"},
            },
        },
        "thresholds": {
            "type": "object",
            "required": ["rank_deficient", "condition_number", "vif", "abs_spearman"],
            "properties": {
                "rank_deficient": {"const": "HARD_FAIL"},
                "condition_number": {"type": "number"},
                "vif": {"type": "number"},
                "abs_spearman": {"type": "number"},
            },
        },
    },
}


class SpecError(RuntimeError):
    """spec이 계약을 만족하지 않는다 — fail-closed."""


def load_spec(path: Path) -> dict[str, Any]:
    spec = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in SPEC_SCHEMA["required"] if k not in spec]
    if missing:
        raise SpecError(f"SPEC_INCOMPLETE: missing top-level keys {missing}")
    unknown = [k for k in spec if k not in SPEC_SCHEMA["properties"]]
    if unknown:
        raise SpecError(f"SPEC_UNKNOWN_KEYS: {unknown}")
    for model, cols in spec["models"].items():
        bad = [c for c in cols if c not in spec["columns"]]
        if bad:
            raise SpecError(f"SPEC_UNDECLARED_COLUMN: model {model} references {bad}")
    for fam, cols in spec["families"].items():
        bad = [c for c in cols if c not in spec["columns"]]
        if bad:
            raise SpecError(f"SPEC_UNDECLARED_COLUMN: family {fam} references {bad}")
    for name, oc in spec["outcomes"].items():
        bad = [m for m in oc["models"] if m not in spec["models"]]
        if bad:
            raise SpecError(f"SPEC_UNKNOWN_MODEL: outcome {name} references {bad}")
    return spec


# ---------------------------------------------------------------------------
# 실행 엔진
# ---------------------------------------------------------------------------

class Harness:
    def __init__(self, spec: dict[str, Any], root: Path, batch: int = 200_000) -> None:
        self.spec = spec
        self.root = root
        self.batch = batch
        self.con = duckdb.connect(config={
            "memory_limit": "3GB", "threads": 6,
            "temp_directory": "/tmp/claude-1000/duckdb_audit",
        })
        self.findings: list[dict[str, Any]] = []
        self.hard_fail: list[str] = []

    # -- helpers ------------------------------------------------------------
    def _finding(self, check: str, status: str, detail: Any) -> None:
        self.findings.append({"check": check, "status": status, "detail": detail})
        if status == "HARD_FAIL":
            self.hard_fail.append(f"{check}: {detail}")

    def _from_clause(self) -> str:
        arts = self.spec["artifacts"]
        spine = self.spec["spine"]
        idc = self.spec["cohort"]["id_column"]
        parts = [f"read_parquet('{arts[spine]['path']}') {spine}"]
        for name, a in arts.items():
            if name == spine:
                continue
            parts.append(f"join read_parquet('{a['path']}') {name} using ({idc})")
        return "from " + "\n".join(parts)

    # -- C0 prerequisites ---------------------------------------------------
    def check_artifacts_and_cohort(self) -> None:
        from tokenization_premium.hashing import sha256_file  # noqa: PLC0415

        for name, a in self.spec["artifacts"].items():
            p = self.root / a["path"]
            if not p.exists():
                self._finding("C0_artifact_identity", "HARD_FAIL", f"{name} missing at {a['path']}")
                continue
            actual = sha256_file(p)
            ok = actual == a["sha256"]
            self._finding("C0_artifact_identity", "PASS" if ok else "HARD_FAIL",
                          {"artifact": name, "expected": a["sha256"], "actual": actual})

        idc = self.spec["cohort"]["id_column"]
        spine = self.spec["spine"]
        spath = self.spec["artifacts"][spine]["path"]
        n, dn = self.con.execute(
            f"select count(*), count(distinct {idc}) from read_parquet('{spath}')").fetchone()
        exp = self.spec["cohort"]["expected_n"]
        self._finding("C0_cohort_n", "PASS" if n == exp == dn else "HARD_FAIL",
                      {"n": n, "distinct": dn, "expected": exp})

        md5 = self.con.execute(
            f"select md5(string_agg({idc}, '' order by {idc})) from read_parquet('{spath}')"
        ).fetchone()[0]
        exp_md5 = self.spec["cohort"]["expected_pair_set_md5"]
        self._finding("C0_pair_set_md5", "PASS" if md5 == exp_md5 else "HARD_FAIL",
                      {"actual": md5, "expected": exp_md5})

        for name, a in self.spec["artifacts"].items():
            if name == spine:
                continue
            j = self.con.execute(
                f"select count(*) from read_parquet('{spath}') s "
                f"join read_parquet('{a['path']}') b using ({idc})").fetchone()[0]
            self._finding("C0_join_preserves_n", "PASS" if j == exp else "HARD_FAIL",
                          {"artifact": name, "joined": j, "expected": exp})

    # -- C1 predictor inventory --------------------------------------------
    def check_column_inventory(self) -> dict[str, list[str]]:
        """spec이 선언한 모든 항이 물리적으로 존재하고 평가 가능한지 확인한다."""
        declared = self.spec["columns"]
        used = sorted({c for cols in self.spec["models"].values() for c in cols})
        unused = sorted(set(declared) - set(used))
        if unused:
            self._finding("C1_declared_but_unused", "NOTE", unused)

        for key, meta in declared.items():
            try:
                self.con.execute(
                    f"select {meta['sql']} as v {self._from_clause()} limit 1").fetchone()
                self._finding("C1_column_evaluable", "PASS", key)
            except Exception as exc:  # noqa: BLE001
                self._finding("C1_column_evaluable", "HARD_FAIL", {"column": key, "error": str(exc)})

        # 물리 열이 선언됐다면 실제 스키마에 있는지 확인
        for key, meta in declared.items():
            phys, art = meta.get("physical_column"), meta.get("artifact")
            if not phys or not art:
                continue
            cols = {r[0] for r in self.con.execute(
                f"describe select * from read_parquet('{self.spec['artifacts'][art]['path']}')"
            ).fetchall()}
            self._finding("C1_physical_column_exists", "PASS" if phys in cols else "HARD_FAIL",
                          {"column": key, "physical": phys, "artifact": art})
        return {"used": used, "unused": unused}

    # -- C2 outcome leakage -------------------------------------------------
    def check_leakage(self) -> None:
        """구조적 검사만 한다. 사영/적합 기반 검사는 계수·적합통계를 만들므로 하지 않는다."""
        lk = self.spec["leakage"]
        declared_phys = {m.get("physical_column") for m in self.spec["columns"].values()}
        for item in lk["excluded"]:
            present = item["column"] in declared_phys
            self._finding("C2_excluded_stays_out", "HARD_FAIL" if present else "PASS",
                          {"column": item["column"], "klass": item["klass"],
                           "reason": item["reason"]})

        for ident in lk["identities"]:
            err = self.con.execute(
                f"select max(abs({ident['sql']})) {self._from_clause()}").fetchone()[0]
            ok = err is not None and err <= ident["max_abs_error"]
            self._finding("C2_identity_holds", "PASS" if ok else "HARD_FAIL",
                          {"identity": ident["name"], "max_abs_error": err,
                           "tolerance": ident["max_abs_error"]})

        for oname, oc in self.spec["outcomes"].items():
            for m in oc["models"]:
                overlap = [c for c in self.spec["models"][m]
                           if self.spec["columns"][c]["sql"].strip() == oc["sql"].strip()]
                self._finding("C2_outcome_not_on_rhs", "HARD_FAIL" if overlap else "PASS",
                              {"outcome": oname, "model": m, "overlap": overlap})

    # -- design matrix ------------------------------------------------------
    def build_universe(self) -> tuple[list[str], dict[str, list[str]], set[str]]:
        """categorical을 실현 수준에 따라 dummy로 펼치고 열 우주를 만든다."""
        spec = self.spec
        universe: list[str] = []
        expand: dict[str, list[str]] = {}
        continuous: set[str] = set()
        for key in sorted({c for cols in spec["models"].values() for c in cols}):
            meta = spec["columns"][key]
            if meta["kind"] == "continuous":
                universe.append(key)
                continuous.add(key)
                expand[key] = [key]
                continue
            rows = self.con.execute(
                f"select {meta['sql']} lv, count(*) n {self._from_clause()} "
                "group by 1 order by n desc, lv").fetchall()
            if meta.get("reference_rule") == "declared":
                ref = meta["reference_level"]
                if ref not in [r[0] for r in rows]:
                    self._finding("C1_declared_reference_realized", "HARD_FAIL",
                                  {"column": key, "reference": ref})
                    ref = rows[0][0]
            else:
                ref = rows[0][0]
            self._finding("C1_reference_level", "PASS",
                          {"column": key, "reference": ref,
                           "rule": meta.get("reference_rule", "largest_realized_level"),
                           "levels": [{"level": lv, "n": n} for lv, n in rows]})
            dummies = [f"{key}::{lv}" for lv, _ in rows if lv != ref]
            expand[key] = dummies
            universe.extend(dummies)
        return universe, expand, continuous

    def gram(self, universe: list[str], expand: dict[str, list[str]]) -> tuple[int, np.ndarray, np.ndarray]:
        """전집단 2-pass로 평균과 중심화 교차곱을 누적한다. 모형은 적합하지 않는다."""
        spec = self.spec
        sel: list[str] = []
        for key in sorted({c for cols in spec["models"].values() for c in cols}):
            meta = spec["columns"][key]
            if meta["kind"] == "continuous":
                sel.append(f"({meta['sql']})::DOUBLE as \"{key}\"")
            else:
                for d in expand[key]:
                    lv = d.split("::", 1)[1].replace("'", "''")
                    sel.append(
                        f"(case when ({meta['sql']}) = '{lv}' then 1.0 else 0.0 end) as \"{d}\"")
        query = "select " + ",\n  ".join(sel) + "\n" + self._from_clause()
        p = len(universe)

        def stream(fn):
            reader = self.con.execute(query).fetch_record_batch(self.batch)
            n = 0
            while True:
                try:
                    b = reader.read_next_batch()
                except StopIteration:
                    break
                if b.num_rows == 0:
                    break
                z = np.empty((b.num_rows, p), dtype=np.float64)
                for j, name in enumerate(universe):
                    z[:, j] = b.column(b.schema.get_field_index(name)).to_numpy(
                        zero_copy_only=False)
                fn(z)
                n += b.num_rows
            return n

        tot = np.zeros(p)
        nonfinite = np.zeros(p, dtype=np.int64)

        def pass1(z):
            bad = ~np.isfinite(z)
            if bad.any():
                nonfinite[:] += bad.sum(axis=0)
            tot[:] += z.sum(axis=0)

        n_rows = stream(pass1)
        if nonfinite.sum():
            self._finding("C0_nonfinite", "HARD_FAIL",
                          {universe[i]: int(nonfinite[i]) for i in range(p) if nonfinite[i]})
        else:
            self._finding("C0_nonfinite", "PASS", 0)
        mean = tot / n_rows

        cross = np.zeros((p, p))

        def pass2(z):
            zc = z - mean
            cross[:, :] += zc.T @ zc

        stream(pass2)
        return n_rows, mean, cross

    # -- C3/C4/C5 -----------------------------------------------------------
    def model_diagnostics(self, model: str, cols: list[str], universe: list[str],
                          expand: dict[str, list[str]], continuous: set[str],
                          n: int, mean: np.ndarray, cross: np.ndarray,
                          corr: np.ndarray, sd: np.ndarray) -> dict[str, Any]:
        idx = {c: i for i, c in enumerate(universe)}
        design = [d for c in cols for d in expand[c]]
        k = [idx[d] for d in design]
        p = len(design)
        conv = self.spec["conventions"]
        sub_cross, sub_mean, sub_sd = cross[np.ix_(k, k)], mean[k], sd[k]
        is_cont = np.array([d in continuous or conv["standardize_dummies"] for d in design])
        scale = np.where(is_cont, sub_sd, 1.0)
        mu = np.where(is_cont, 0.0, sub_mean)

        cz = sub_cross / np.outer(scale, scale)
        second = cz + n * np.outer(mu, mu)
        if conv["condition_number_includes_intercept"]:
            g = np.empty((p + 1, p + 1))
            g[0, 0] = n
            g[0, 1:] = n * mu
            g[1:, 0] = n * mu
            g[1:, 1:] = second
        else:
            g = second
        ev = np.clip(np.linalg.eigvalsh(g), 0.0, None)
        sv = np.sqrt(ev)[::-1]
        tol = max(g.shape[0], n) * np.finfo(float).eps * sv[0]
        rank = int((sv > tol).sum())
        cond = float(sv[0] / sv[-1]) if sv[-1] > 0 else float("inf")

        rm = corr[np.ix_(k, k)]
        vif = np.diag(np.linalg.inv(rm))
        gvif: dict[str, Any] = {}
        for c in cols:
            if self.spec["columns"][c]["kind"] != "categorical":
                continue
            bi = [design.index(d) for d in expand[c]]
            oi = [i for i in range(p) if i not in bi]
            if not bi or not oi:
                continue
            sb, lb = np.linalg.slogdet(rm[np.ix_(bi, bi)])
            sz, lz = np.linalg.slogdet(rm[np.ix_(oi, oi)])
            sf, lf = np.linalg.slogdet(rm)
            val = float(np.exp(lb + lz - lf)) if min(sb, sz, sf) > 0 else None
            gvif[c] = {"df": len(bi), "gvif": val,
                       "gvif_1_2df": None if val is None else float(val ** (1 / (2 * len(bi))))}

        expected_rank = g.shape[0]
        deficiency = expected_rank - rank
        if deficiency:
            self._finding("C3_rank", "HARD_FAIL", {"model": model, "p": expected_rank, "rank": rank})
        else:
            self._finding("C3_rank", "PASS", {"model": model, "p": expected_rank, "rank": rank})

        th = self.spec["thresholds"]
        if cond >= th["condition_number"]:
            self._finding("C4_condition_number", "REVIEW_TRIGGER",
                          {"model": model, "value": cond, "threshold": th["condition_number"]})
        else:
            self._finding("C4_condition_number", "PASS", {"model": model, "value": cond})

        vmax = float(vif.max())
        gmax = max([b["gvif_1_2df"] for b in gvif.values() if b["gvif_1_2df"] is not None],
                   default=0.0)
        if max(vmax, gmax) >= th["vif"]:
            self._finding("C5_vif_gvif", "REVIEW_TRIGGER",
                          {"model": model, "max_vif": vmax, "max_gvif_1_2df": gmax,
                           "threshold": th["vif"]})
        else:
            self._finding("C5_vif_gvif", "PASS", {"model": model, "max_vif": vmax})

        return {
            "design_columns": design,
            "p_with_intercept": expected_rank,
            "rank": rank,
            "rank_deficiency": deficiency,
            "condition_number": cond,
            "condition_number_includes_intercept": conv["condition_number_includes_intercept"],
            "max_vif": vmax,
            "vif": {design[i]: float(vif[i]) for i in range(p)},
            "gvif": gvif,
        }

    # -- C6 -----------------------------------------------------------------
    def check_families(self) -> dict[str, Any]:
        conv = self.spec["conventions"]["spearman_tie_handling"]
        th = self.spec["thresholds"]["abs_spearman"]
        out: dict[str, Any] = {}
        for fam, cols in self.spec["families"].items():
            pairs: dict[str, float] = {}
            for a, b in itertools.combinations(cols, 2):
                sa = self.spec["columns"][a]["sql"]
                sb = self.spec["columns"][b]["sql"]
                if conv == "midrank":
                    q = (f"with base as (select ({sa}) a, ({sb}) b {self._from_clause()}), "
                         "num as (select a, b, row_number() over (order by a) ra, "
                         "row_number() over (order by b) rb from base), "
                         "r as (select avg(ra) over (partition by a) x, "
                         "avg(rb) over (partition by b) y from num) "
                         "select corr(x, y) from r")
                else:
                    q = (f"with base as (select ({sa}) a, ({sb}) b {self._from_clause()}), "
                         "r as (select rank() over (order by a) x, rank() over (order by b) y "
                         "from base) select corr(x, y) from r")
                pairs[f"{a} ~ {b}"] = self.con.execute(q).fetchone()[0]
            worst = max(pairs, key=lambda k: abs(pairs[k])) if pairs else None
            trig = bool(worst and abs(pairs[worst]) >= th)
            out[fam] = {"pairs": pairs, "max_abs_rho_pair": worst,
                        "max_abs_rho": abs(pairs[worst]) if worst else None, "trigger": trig}
            self._finding("C6_same_construct", "REVIEW_TRIGGER" if trig else "PASS",
                          {"family": fam, "pair": worst,
                           "rho": pairs[worst] if worst else None, "threshold": th})
        return out

    # -- C7 -----------------------------------------------------------------
    def check_nesting(self) -> None:
        models = {m: set(c) for m, c in self.spec["models"].items()}
        for chain in self.spec["nesting"]["chains"]:
            for lo, hi in zip(chain, chain[1:], strict=False):
                if lo not in models or hi not in models:
                    self._finding("C7_nesting", "HARD_FAIL", {"chain": chain, "unknown": [lo, hi]})
                    continue
                ok = models[lo] < models[hi]
                self._finding("C7_nesting", "PASS" if ok else "HARD_FAIL",
                              {"subset": lo, "superset": hi,
                               "missing_from_superset": sorted(models[lo] - models[hi]),
                               "added": sorted(models[hi] - models[lo])})
        for group in self.spec["nesting"]["mutually_exclusive"]:
            g = set(group)
            for m, cols in models.items():
                both = sorted(g & cols)
                ok = len(both) <= 1
                self._finding("C7_mutual_exclusion", "PASS" if ok else "HARD_FAIL",
                              {"model": m, "group": sorted(g), "co_occurring": both})

    # -- driver -------------------------------------------------------------
    def run(self) -> dict[str, Any]:
        self.check_artifacts_and_cohort()
        inventory = self.check_column_inventory()
        self.check_leakage()
        self.check_nesting()

        universe, expand, continuous = self.build_universe()
        n, mean, cross = self.gram(universe, expand)
        cov = cross / (n - 1)
        sd = np.sqrt(np.diag(cov))
        if (sd == 0).any():
            zero = [universe[i] for i in range(len(universe)) if sd[i] == 0]
            self._finding("C1_zero_variance", "HARD_FAIL", zero)
            corr = np.full_like(cov, np.nan)
        else:
            self._finding("C1_zero_variance", "PASS", [])
            corr = cov / np.outer(sd, sd)

        models: dict[str, Any] = {}
        for m, cols in self.spec["models"].items():
            models[m] = self.model_diagnostics(m, cols, universe, expand, continuous,
                                               n, mean, cross, corr, sd)
        families = self.check_families()

        statuses = [f["status"] for f in self.findings]
        verdict = ("PRE_NB09_AUDIT_HARD_FAIL" if "HARD_FAIL" in statuses
                   else "PRE_NB09_AUDIT_PASS_WITH_REVIEW" if "REVIEW_TRIGGER" in statuses
                   else "PRE_NB09_AUDIT_PASS")
        return {
            "harness": "audit_pre_nb09",
            "spec_id": self.spec["spec_id"],
            "protocol_id": self.spec["protocol_id"],
            "protocol_commit": self.spec["protocol_commit"],
            "base_main_sha": self.spec["base_main_sha"],
            "N": n,
            "conventions": self.spec["conventions"],
            "thresholds": self.spec["thresholds"],
            "inventory": inventory,
            "models": models,
            "families": families,
            "findings": self.findings,
            "hard_fail": self.hard_fail,
            "verdict": verdict,
            "model_fitted": False,
            "coefficient_produced": False,
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="PRE-NB09 independent audit harness")
    ap.add_argument("spec", nargs="?", help="audit spec JSON (피감사 protocol의 기계 판독본)")
    ap.add_argument("out", nargs="?", help="결과 JSON 출력 경로")
    ap.add_argument("--emit-schema", action="store_true", help="spec JSON schema를 출력하고 종료")
    ap.add_argument("--self-test", action="store_true",
                    help="알려진 기준선 spec으로 하네스 자체를 검증한다")
    ap.add_argument("--expect", help="self-test 기대값 JSON")
    args = ap.parse_args()

    if args.emit_schema:
        print(json.dumps(SPEC_SCHEMA, indent=2, ensure_ascii=False))
        return 0

    if not args.spec:
        print("PRE_NB09_AUDIT_HARNESS: spec이 없으면 실행하지 않는다 (fail-closed).\n"
              "피감사 protocol이 동결된 뒤 그 사양을 spec JSON으로 옮겨적고 다시 실행하라.\n"
              "  python scripts/audit_pre_nb09.py --emit-schema", file=sys.stderr)
        return 2

    from tokenization_premium.paths import PROJECT_ROOT  # noqa: PLC0415

    spec = load_spec(Path(args.spec))
    result = Harness(spec, PROJECT_ROOT).run()

    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=1, ensure_ascii=False,
                                             default=float), encoding="utf-8")

    print(f"\nverdict = {result['verdict']}   N = {result['N']:,}")
    print(f"{'model':8s} {'p':>4s} {'rank':>5s} {'def':>4s} {'cond':>12s} {'maxVIF':>12s}")
    for m, d in result["models"].items():
        print(f"{m:8s} {d['p_with_intercept']:4d} {d['rank']:5d} {d['rank_deficiency']:4d}"
              f" {d['condition_number']:12.4f} {d['max_vif']:12.4f}")
    trig = [f for f in result["findings"] if f["status"] == "REVIEW_TRIGGER"]
    print(f"\nreview triggers: {len(trig)}")
    for f in trig:
        print(f"  {f['check']}: {json.dumps(f['detail'], ensure_ascii=False, default=float)}")
    if result["hard_fail"]:
        print("\nHARD FAIL:")
        for h in result["hard_fail"]:
            print(f"  {h}")

    if args.self_test and args.expect:
        expect = json.loads(Path(args.expect).read_text(encoding="utf-8"))
        bad: list[str] = []
        for m, exp in expect["models"].items():
            got = result["models"][m]
            for key, tol in (("rank", 0.0), ("p_with_intercept", 0.0),
                             ("condition_number", 1e-6), ("max_vif", 1e-6)):
                a, b = got[key], exp[key]
                d = abs(a - b) if tol == 0 else abs(a - b) / max(abs(b), 1e-300)
                if d > tol:
                    bad.append(f"{m}.{key}: got {a!r} expected {b!r} (diff {d:.3e})")
        for fam, exp in expect.get("families", {}).items():
            got = result["families"][fam]["max_abs_rho"]
            if abs(got - exp) > 1e-9:
                bad.append(f"family {fam}: got {got!r} expected {exp!r}")
        print("\nSELF_TEST =", "PASS" if not bad else "FAIL")
        for b in bad:
            print("  ", b)
        return 1 if bad else 0

    return 1 if result["hard_fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
