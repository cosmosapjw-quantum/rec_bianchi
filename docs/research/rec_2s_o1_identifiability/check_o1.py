"""O1의 자료 식별성만 검사한다. 생산 모듈·원본·과거 결과는 수정하지 않는다."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import zipfile

BASE = "dc9e9e9394eba314afa13e6db1b0811257e3be55"
BASE_TREE = "a12bdda27717a9b0f7a182e86bf6c3d081087ecc"
PREFIX = "docs/research/rec_2s_o1_identifiability/"
WORKFLOW = ".github/workflows/rec-2s-o1-identifiability.yml"
ZIP_PATH = "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"
ZIP_SHA = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
TABLE = "HyRec/two_photon_tables.dat"
TABLE_SHA = "93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9"
OWNER = "docs/research/original_hyrec_2s_input_trace/OWNER_REVIEW_CONTRACT.json"
PROPOSAL = "docs/research/rec_2s_o2o3_comparison/O2_O3_REVIEW_PROPOSAL.json"


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dump(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                               indent=2, allow_nan=False) + "\n", encoding="utf-8")


def product(a, b):
    out = [Q(0)] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i + j] += ai * bj
    return out


def integral(coefficients):
    return sum((v / (i + 1) for i, v in enumerate(coefficients)), Q(0))


def main(out: Path) -> None:
    root = Path(__file__).resolve().parents[3]
    out = out.resolve()
    if out == root or root in out.parents:
        raise ValueError("출력은 Git 작업공간 밖이어야 한다")
    out.mkdir(parents=True, exist_ok=True)
    result = {"classification": "RUNNING", "base_commit": BASE,
              "claim": "NO_PASS_REC_PHYSICAL_SPLIT", "physical_authentication": False,
              "owner_decision_changed": False, "provider_admitted": False}
    dump(out / "RESULT.json", result)
    try:
        assert git(root, "rev-parse", BASE + "^{tree}") == BASE_TREE
        subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", BASE, "HEAD"], check=True)
        assert not git(root, "status", "--porcelain", "--untracked-files=all")
        result.update(source_commit=git(root, "rev-parse", "HEAD"),
                      source_tree=git(root, "rev-parse", "HEAD^{tree}"),
                      source_parent=git(root, "rev-parse", "HEAD^"),
                      python=sys.version, platform=platform.platform())
        changed = git(root, "diff", "--name-only", BASE, "HEAD").splitlines()
        assert changed and all(p.startswith(PREFIX) or p == WORKFLOW for p in changed)
        subprocess.run(["git", "-C", str(root), "diff", "--check", BASE, "HEAD"], check=True)
        protected = ["src", "tests", "archive", OWNER, PROPOSAL]
        result["protected_objects"] = {}
        for name in protected:
            before = git(root, "rev-parse", BASE + ":" + name)
            after = git(root, "rev-parse", "HEAD:" + name)
            assert before == after
            result["protected_objects"][name] = after
        owner = json.loads((root / OWNER).read_text())
        assert all(x["status"] == "UNRESOLVED" for x in owner["required_owner_decisions"])
        proposal = json.loads((root / PROPOSAL).read_text())
        assert proposal["O2_proposal"]["selected_option"] is None
        assert proposal["O3_proposal"]["selected_field_law"] is None
        data = (root / ZIP_PATH).read_bytes()
        assert sha(data) == ZIP_SHA
        rows, hits = [], []
        with zipfile.ZipFile(root / ZIP_PATH) as z:
            assert sha(z.read(TABLE)) == TABLE_SHA
            for info in sorted(z.infolist(), key=lambda i: i.filename):
                if info.is_dir():
                    continue
                raw = z.read(info.filename)
                rows.append({"path": info.filename, "bytes": len(raw), "sha256": sha(raw)})
                suffix = Path(info.filename).suffix.lower()
                if suffix in (".c", ".h", ".py", ".f", ".f90", ".m", ".wl", ".wls", ".txt", ".md") or Path(info.filename).name.lower() == "makefile":
                    text = raw.decode("utf-8", errors="replace")
                    for number, line in enumerate(text.splitlines(), 1):
                        if any(token in line.lower() for token in ("two_photon_tables", "quadrature", "generate", "fopen(")):
                            hits.append({"path": info.filename, "line": number, "text": line})
        inventory = {"archive_sha256": ZIP_SHA, "table_sha256": TABLE_SHA,
                     "members": rows, "text_index": hits,
                     "scope": "구성원 전체 해시와 지정 텍스트 색인; 생성기 부재의 전면 증명 아님"}
        dump(out / "ARCHIVE_INVENTORY.json", inventory)
        print("ARCHIVE_INDEX_BEGIN", flush=True)
        print(json.dumps(inventory, ensure_ascii=False, sort_keys=True), flush=True)
        print("ARCHIVE_INDEX_END", flush=True)

        import sympy as s
        x = s.Symbol("x", real=True)
        e = s.Symbol("epsilon", positive=True)
        P = 6*x*x - 6*x + 1
        Phi = s.Rational(1,4) + x/2 - x*x/2
        symbolic = {}
        exact = {}
        def check(name, lhs, rhs):
            residual = s.simplify(lhs-rhs)
            symbolic[name] = str(residual)
            assert residual == 0, (name, residual)
        for sign, label in ((1, "plus"), (-1, "minus")):
            k = 1 + sign*e*P
            check(label+"_mass", s.integrate(k, (x,0,1)), 1)
            check(label+"_mean", s.integrate(x*k, (x,0,1)), s.Rational(1,2))
            check(label+"_second", s.integrate(x*x*k, (x,0,1)), s.Rational(1,3)+sign*e/30)
            check(label+"_source", s.integrate(k*Phi, (x,0,1)), s.Rational(1,3)-sign*e/60)
            m2 = s.integrate((x-s.Rational(1,2))**2*k, (x,0,1))
            check(label+"_taylor_remainder", s.integrate(k*Phi,(x,0,1))-Phi.subs(x,s.Rational(1,2)), -m2/2)
            kq = [Q(1)+Q(sign,2), Q(-3*sign), Q(3*sign)]
            fq = [Q(1,4), Q(1,2), Q(-1,2)]
            rate = integral(product(kq, fq))
            expected = Q(13,40) if sign == 1 else Q(41,120)
            assert integral(kq) == 1
            assert integral([Q(0)]+kq) == Q(1,2)
            assert rate == expected
            assert s.Rational(rate.numerator,rate.denominator) == s.integrate(k*Phi,(x,0,1)).subs(e,s.Rational(1,2))
            exact[label] = str(rate)
        check("second_moment_separation", s.integrate(2*e*P*x*x,(x,0,1)), e/15)
        check("source_separation", s.integrate(-2*e*P*Phi,(x,0,1)), e/30)
        check("noncentroid_linear_remainder", s.integrate(2*x*x,(x,0,1))-s.Rational(1,2), s.Rational(1,6))
        check("P_lower_bound", P+s.Rational(1,2), 6*(x-s.Rational(1,2))**2)
        check("P_upper_bound", 1-P, 6*x*(1-x))
        assert Q(exact["minus"])-Q(exact["plus"]) == Q(1,60)
        assert Q(3,8) != Q(exact["plus"]) and Q(3,8) != Q(exact["minus"])
        result.update(sympy=s.__version__, symbolic_residuals=symbolic,
                      fraction_rates=exact, source_separation="1/60",
                      midpoint_source="3/8", noncentroid_linear_remainder="1/6",
                      detected_mutants=["mass_and_centroid_determine_general_source", "discard_first_moment_without_centroid_evidence"],
                      archive_member_count=len(rows), archive_inventory_sha256=sha((out/"ARCHIVE_INVENTORY.json").read_bytes()),
                      changed_paths=changed, continuum_HyRec_error_claim=False,
                      physical_kernel_reconstructed=False, original_bin_intervals=None,
                      B=None, mu=None, old_O2_O3_checks_reexecuted=False,
                      original_C_or_history_executed=False, production_tests_executed=False,
                      local_runtime="container/Python: 프로세스 시작 전 ClientError",
                      wolfram="context: MCP SSE HTTP404; 평가 결과 없음")
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        xx = [i/200 for i in range(201)]
        fig, ax = plt.subplots(figsize=(6,4))
        for sign, label in ((1,r"$k_+$"),(-1,r"$k_-$")):
            ax.plot(xx,[1+sign*.5*(6*v*v-6*v+1) for v in xx],label=label)
        ax.set_xlabel(r"$x$"); ax.set_ylabel(r"$k_\pm(x)$")
        ax.legend(); fig.tight_layout()
        fig.savefig(out/"same_moments_different_source.png",dpi=160)
        fig.savefig(out/"same_moments_different_source.svg")
        plt.close(fig)
        result["figure_generated"] = True
        result["visual_audit"] = "NOT_PERFORMED"
        result["clean_worktree"] = not bool(git(root,"status","--porcelain","--untracked-files=all"))
        assert result["clean_worktree"]
        result["classification"] = "PASS_BOUNDED_O1_IDENTIFIABILITY_RESEARCH_NOT_PHYSICAL_ADMISSION"
        dump(out/"RESULT.json",result)
        manifest = "".join(sha(f.read_bytes())+"  "+f.name+"\n" for f in sorted(out.iterdir()) if f.is_file() and f.name != "SHA256SUMS")
        (out/"SHA256SUMS").write_text(manifest,encoding="utf-8")
        print("RESULT_JSON_BEGIN",flush=True)
        print(json.dumps(result,ensure_ascii=False,sort_keys=True),flush=True)
        print("RESULT_JSON_END",flush=True)
    except Exception as exc:
        result.update(classification="FAIL_O1_RESEARCH_EXECUTION", error_type=type(exc).__name__, error=str(exc))
        dump(out/"RESULT.json",result)
        raise


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    main(parser.parse_args().out)
