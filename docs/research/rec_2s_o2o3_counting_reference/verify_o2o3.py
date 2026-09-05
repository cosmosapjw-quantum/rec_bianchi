"""생산 코드를 변경하지 않는 O2/O3 조건부 식 검산."""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction as F
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

import mpmath as mp
import sympy as sp

BASE = "e65ae5c211db4e3375e73410a404f0b23da084d4"
BASE_TREE = "e12a4ae4ed17859e4625f80fb0fa86e83a034036"
TRACE = "docs/research/original_hyrec_2s_input_trace"
PREFIX = "docs/research/rec_2s_o2o3_counting_reference"
ALLOWED = {f"{PREFIX}/RESEARCH_KO.md", f"{PREFIX}/DECISIONS.json",
           f"{PREFIX}/verify_o2o3.py", f"{PREFIX}/CLOSEOUT_KO.md",
           ".github/workflows/rec-2s-o2o3-research.yml"}
ROOT = Path(__file__).resolve().parents[3]


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def require(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    require(not out.is_relative_to(ROOT), "출력은 Git 밖이어야 한다")
    out.mkdir(parents=True, exist_ok=True)
    require(git("rev-parse", f"{BASE}^{{tree}}") == BASE_TREE, "기준 tree 불일치")
    subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", BASE, "HEAD"], check=True)
    require(not git("status", "--porcelain", "--untracked-files=all"), "시작 worktree 오염")
    delta = git("diff", "--name-status", BASE, "HEAD").splitlines()
    require(bool(delta), "연구 변경이 없다")
    for item in delta:
        status, path = item.split("\t", 1)
        require(status == "A" and path in ALLOWED, "허용되지 않은 변경: " + item)
    unchanged = {}
    for path in ("src", "tests", TRACE):
        unchanged[path] = git("rev-parse", f"HEAD:{path}")
        require(unchanged[path] == git("rev-parse", f"{BASE}:{path}"), "기존 바이트 변경: " + path)
    subprocess.run(["git", "-C", str(ROOT), "diff", "--check", BASE, "HEAD"], check=True)

    a, xu, xg, ft, fc = sp.symbols("a xu xg ft fc")
    u, v = sp.symbols("u v")
    C, D = a / (1-v), a*v / (1-v)
    native = C*xu-D*xg*ft
    full = C*xu*(1+ft)-D*xg*ft
    p = u/(1-u)
    du, bw, bp = xu-xg*u*v, xg*(ft-u), xg*(ft-p)
    da, dxu, dxg, dft, dfc = sp.symbols("da dxu dxg dft dfc")
    pair = a*(xu*(1+fc)*(1+ft)-xg*fc*ft)
    exact_jvp = sum(sp.diff(pair, z)*dz for z, dz in zip(
        (a,xu,xg,ft,fc), (da,dxu,dxg,dft,dfc)))
    stated_jvp = da*(xu*(1+fc)*(1+ft)-xg*fc*ft) + a*(
        (1+fc)*(1+ft)*dxu-fc*ft*dxg
        +(xu*(1+ft)-xg*ft)*dfc+(xu*(1+fc)-xg*fc)*dft)
    d, w, dd, dw = sp.symbols("d w dd dw")
    inv = d/xg+w
    inv_jvp = sp.diff(inv,d)*dd+sp.diff(inv,xg)*dxg+sp.diff(inv,w)*dw
    et, ec, G = sp.symbols("et ec G")
    E, theta, dE, dtheta = sp.symbols("E theta dE dtheta", positive=True)
    wr = sp.exp(-E/theta)
    residuals = {
        "stimulated_difference": full-native-C*xu*ft,
        "native_Wien_null": native.subs({xu:xg*u*v,ft:u}, simultaneous=True),
        "full_Planck_null": full.subs({xu:xg*u*v,ft:p}, simultaneous=True),
        "native_Planck_residual": native.subs({xu:xg*u*v,ft:p}, simultaneous=True)+C*xg*u*v*p,
        "full_Wien_residual": full.subs({xu:xg*u*v,ft:u}, simultaneous=True)-C*xg*u*v*u,
        "native_departure": C*du-D*bw-native,
        "mixed_reference_defect": C*du-D*bp-native-D*xg*(p-u),
        "corrected_reference": C*du-D*bp-D*xg*(p-u)-native,
        "full_pair_JVP": exact_jvp-stated_jvp,
        "inverse_reference_JVP": inv_jvp-(dd/xg-d*dxg/xg**2+dw),
        "Wien_reference_JVP": sp.diff(wr,E)*dE+sp.diff(wr,theta)*dtheta-wr*(-dE/theta+E*dtheta/theta**2),
        "atomic_plus_photon_energy": et*G+ec*G-(et+ec)*G,
        "two_leg_number": G+G-2*G,
        "wrong_double_energy_defect": 2*et*G-(et+ec)*G-(et-ec)*G,
    }
    reduced = {k:str(sp.factor(value)) for k,value in residuals.items()}
    require(all(value == "0" for value in reduced.values()), "기호 항등식 잔차")

    aa, ug, vg, ground = F(1), F(1,4), F(1,2), F(8,9)
    upper, cc, dc = ground*ug*vg, aa/(1-vg), aa*vg/(1-vg)
    pw = ug/(1-ug)
    def gn(f: F) -> F:
        return cc*upper-dc*ground*f
    def gf(f: F) -> F:
        return cc*upper*(1+f)-dc*ground*f
    witness = {"native_Wien":gn(ug), "full_Wien":gf(ug),
               "native_Planck":gn(pw), "full_Planck":gf(pw),
               "missing_reference_correction":dc*ground*(pw-ug)}
    require(witness == {"native_Wien":F(0), "full_Wien":F(1,18),
                       "native_Planck":-F(2,27), "full_Planck":F(0),
                       "missing_reference_correction":F(2,27)}, "유리수 반례 불일치")
    require(gf(ug) != gn(ug), "유도방출 누락이 검출되지 않음")
    require(dc*ground*(pw-ug) != 0, "기준장 보정 누락이 검출되지 않음")

    csv_path = ROOT / TRACE / "bins_2s.csv"
    raw = csv_path.read_bytes()
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    require(len(rows) == 140 and [int(r["b"]) for r in rows] == list(range(140)), "고정 채널 순서")
    e21 = F("10.198714553953742")
    energy_defects = [2*F(r["energy_eV_lexeme"])-e21 for r in rows]
    require(all(q > 0 for q in energy_defects), "두 배 배치 반례가 고에너지 영역에 있지 않음")
    require(all(r["original_bin_integral_status"] == "UNRESOLVED_ORIGINAL_INTEGRATION_REGION" for r in rows), "미결정 구간 상태 변경")
    mp.mp.dps = 80
    probes, summary = [], []
    max_residual = mp.mpf("0")
    for temperature in ("0.1", "0.3", "1.0"):
        th = mp.mpf(temperature)
        ratios = []
        for r in rows:
            energy = mp.mpf(r["energy_eV_lexeme"])
            uc = mp.exp(-energy/th)
            occ = 1/mp.expm1(energy/th)
            ratio = occ/(1+occ)
            error = abs(ratio-uc)
            max_residual = max(max_residual,error)
            require(error < mp.mpf("1e-70"), "80자리 점유수 항등식 잔차")
            ratios.append(ratio)
            probes.append({"b":int(r["b"]), "theta_eV":temperature,
                           "energy_eV":r["energy_eV_lexeme"],
                           "omission_over_full_forward":mp.nstr(ratio,40),
                           "identity_absolute_residual":mp.nstr(error,10)})
        summary.append({"theta_eV":temperature,
                        "minimum_forward_fraction":mp.nstr(min(ratios),30),
                        "maximum_forward_fraction":mp.nstr(max(ratios),30),
                        "net_rate_relative_error_bound":False})
    with (out/"FORWARD_FRACTION.csv").open("w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f,fieldnames=list(probes[0]))
        writer.writeheader(); writer.writerows(probes)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.4,4.6),layout="constrained")
    for temperature in ("0.1","0.3","1.0"):
        rr = [r for r in probes if r["theta_eV"] == temperature]
        ax.semilogy([float(r["energy_eV"]) for r in rr],
                    [float(r["omission_over_full_forward"]) for r in rr],
                    label=rf"$\Theta={temperature}\,\mathrm{{eV}}$")
    ax.set_xlabel(r"$E_t\ [\mathrm{eV}]$")
    ax.set_ylabel(r"$\Delta F_+/F_+=\exp(-E_t/\Theta)$")
    ax.legend(); ax.grid(True,which="both",alpha=0.25)
    fig.savefig(out/"FORWARD_FRACTION.png",dpi=160)
    fig.savefig(out/"FORWARD_FRACTION.svg")
    plt.close(fig)
    require(not git("status","--porcelain","--untracked-files=all"), "종료 worktree 오염")
    result = {
        "classification":"PASS_CONDITIONAL_O2_O3_RESEARCH_NOT_PHYSICAL_ADMISSION",
        "base_commit":BASE, "base_tree":BASE_TREE,
        "executed_commit":git("rev-parse","HEAD"), "executed_tree":git("rev-parse","HEAD^{tree}"),
        "workflow_sha":os.environ.get("GITHUB_SHA"), "event":os.environ.get("GITHUB_EVENT_NAME"),
        "run_id":os.environ.get("GITHUB_RUN_ID"), "run_attempt":os.environ.get("GITHUB_RUN_ATTEMPT"),
        "changed_paths":delta, "unchanged_subtrees":unchanged,
        "csv_git_blob":git("rev-parse",f"HEAD:{TRACE}/bins_2s.csv"), "csv_sha256":sha(csv_path),
        "script_sha256":sha(Path(__file__)),
        "symbolic_residuals":reduced, "symbolic_identity_count":len(reduced),
        "fraction_witness":{k:str(v) for k,v in witness.items()},
        "explicit_counterexamples_detected":3,
        "wrong_double_energy_min_eV_per_event":str(min(energy_defects)),
        "wrong_double_energy_max_eV_per_event":str(max(energy_defects)),
        "mpmath_dps":mp.mp.dps, "thermal_probe_count":len(probes),
        "thermal_summary":summary, "maximum_absolute_identity_residual":mp.nstr(max_residual,20),
        "environment":{"python":sys.version,"platform":platform.platform(),"sympy":sp.__version__,"mpmath":mp.__version__,"matplotlib":matplotlib.__version__},
        "clean_worktree":True, "figure_generated":True,
        "rendered_visual_audit":"NOT_PERFORMED_BY_SCRIPT",
        "source_implementation_tests_run":False, "native_C_executed":False,
        "historical_tests_recounted":False, "table_reextracted":False,
        "B":None,"mu":None,"owner_model_choice":None,
        "physical_source_authenticated":False,"provider_admitted":False,
        "claim":"NO_PASS_REC_PHYSICAL_SPLIT"}
    (out/"RESULT.json").write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    manifest = "".join(f"{sha(p)}  {p.name}\n" for p in sorted(out.iterdir()) if p.is_file() and p.name != "SHA256SUMS")
    (out/"SHA256SUMS").write_text(manifest,encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
