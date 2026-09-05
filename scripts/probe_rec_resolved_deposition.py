"""Bounded adapter validation. Never invokes the frozen REC-DONOR-02B main."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import runpy
import subprocess
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
BASE = "30576407d50e10b88a32b65a9510db61e4159e1b"
CORE = {
    "src/full_bianchi_hyrec/physical_source_authority.py": "6d4f39d48993c4715f5002ba068e8dcf98336be3",
    "src/full_bianchi_hyrec/trajectory/com_source_deposition.py": "a3662cf399f14b7148d880266825be12baf934a0",
    "scripts/probe_rec_donor02b_deposition.py": "fcfca64cd113800e2dee6a7a955c2c4453b53a84",
    "docs/research/rec_donor02b_deposition/CLOSEOUT.json": "812f1a841511fbaf8fe4f8d3dec222b3d1c8614d",
}
TEST = "tests/trajectory/test_rec_resolved_deposition.py"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def fixture():
    return runpy.run_path(str(ROOT / TEST))


def identities():
    d = fixture()
    _, binding, packet = d["case"]()
    a = binding.apply(packet, n_H_m3=d["N"])
    j = binding.jvp(packet, d["m"].PacketRates(d["DR"], d["layout"]()),
                    n_H_m3=d["N"], dn_H_m3=d["N"]/4)
    return {"source": a.receipt.source_identity, "plan": a.receipt.plan_identity,
            "action_input": a.receipt.input_identity, "action_output": a.receipt.result_identity,
            "jvp_input": j.receipt.input_identity, "jvp_output": j.receipt.result_identity}


def run_tests(out, label, selectors, env, prefix=None, expect_failure=False):
    xml = out / (label + ".xml")
    pytest_args = ["-q", "-p", "no:cacheprovider", "--junitxml="+str(xml), *selectors]
    if prefix is None:
        cmd = [sys.executable, "-m", "pytest", *pytest_args]
    else:
        cmd = [sys.executable, "-c", prefix + "\nimport pytest\nraise SystemExit(pytest.main("+repr(pytest_args)+"))"]
    run = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    log = run.stdout+run.stderr
    (out/(label+".log")).write_text(log)
    suites = ET.parse(xml).getroot().findall("testsuite") if xml.exists() else []
    totals = {k: sum(int(s.attrib.get(k, 0)) for s in suites)
              for k in ("tests", "failures", "errors", "skipped")}
    observed = re.search(r"(\d+) passed(?:, (\d+) subtests passed)?", log)
    result = {"command": cmd, "exit_code": run.returncode, "junit": totals,
              "pytest_passed": int(observed[1]) if observed else 0,
              "subtests_passed": int(observed[2] or 0) if observed else 0,
              "log": label+".log", "xml": xml.name}
    (out/(label+".json")).write_text(json.dumps(result, indent=2)+"\n")
    if expect_failure:
        assert run.returncode == 1 and totals["failures"] > 0 and totals["errors"] == 0, result
    else:
        assert run.returncode == 0 and totals["tests"] > 0 and not any(totals[k] for k in ("failures", "errors", "skipped")), result
    print(label, json.dumps(result), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    parser.add_argument("--identity-only", action="store_true")
    args = parser.parse_args()
    if args.identity_only:
        print(json.dumps(identities(), sort_keys=True))
        return
    if args.out is None:
        parser.error("--out required")
    out = args.out.resolve()
    if out == ROOT or ROOT in out.parents:
        raise ValueError("output must be outside Git worktree")
    out.mkdir(parents=True, exist_ok=False)
    assert not git("status", "--porcelain", "--untracked-files=all"), "DIRTY_SOURCE"
    head, tree = git("rev-parse", "HEAD"), git("rev-parse", "HEAD^{tree}")
    subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", BASE, head], check=True)
    for path, blob in CORE.items():
        assert git("hash-object", path) == blob, path
    allowed = {TEST, "src/full_bianchi_hyrec/resolved_deposition.py", "scripts/probe_rec_resolved_deposition.py"}
    changed = set(git("diff", "--name-only", BASE, head).splitlines())
    assert changed and all(p in allowed or p.startswith("docs/research/rec_resolved_deposition/") for p in changed)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=str(ROOT/"src"),
               MPLCONFIGDIR=str(out/"mplconfig"))
    os.environ["MPLCONFIGDIR"] = env["MPLCONFIGDIR"]
    tests = {
        "focused": run_tests(out, "focused", [TEST], env),
        "source_protocol": run_tests(out, "source-protocol", [
            "tests/trajectory/test_rec_donor01_typed_physical_source_red.py",
            "tests/trajectory/test_rec_donor02_source_safety.py"], env),
        "deposition_component": run_tests(out, "deposition-component", [
            "tests/trajectory/test_split_context_and_deposition.py", "-k",
            "number_energy or nonuniform_measure or fixed_map_jvp or invalid_deposition or bad_rate or plan_copies or validated_map or direction_guard or two_moment"], env),
    }
    import numpy as np
    import scipy
    import sympy as sp
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    d = fixture()
    _, binding, packet = d["case"]()
    n, dr = d["N"], d["m"].PacketRates(d["DR"], d["layout"]())
    action = binding.apply(packet, n_H_m3=n)
    jvp = binding.jvp(packet, dr, n_H_m3=n, dn_H_m3=n/4)
    alternate = d["m"].ResolvedDeposition(d["plan"](d["B2"]), d["layout"]()).apply(packet, n_H_m3=n)
    references = [d["exact"](d["B"], d["R"], n), d["exact"](d["B"], d["R"], n, d["DR"], n/4)]
    residuals = [np.array([[float(F(float(value))-ref[i][a]) for a, value in enumerate(row)]
                          for i, row in enumerate(result.values)])
                 for result, ref in zip((action, jvp), references)]
    assert all(not r.any() for r in residuals)
    delta = alternate.values-action.values
    assert np.max(np.abs(delta)) == .75
    ns, dns, mu, dmu, b, db, r, rr, eps = sp.symbols("n dn mu dmu b db r dr eps")
    fixed = sp.diff((ns+eps*dns)*b*(r+eps*rr)/mu, eps).subs(eps, 0)
    fixed_residual = sp.simplify(fixed-b*(ns*rr+dns*r)/mu)
    full = sp.diff((ns+eps*dns)*(b+eps*db)*(r+eps*rr)/(mu+eps*dmu), eps).subs(eps, 0)
    full_residual = sp.simplify(full-fixed-ns*db*r/mu+ns*b*r*dmu/mu**2)
    assert fixed_residual == full_residual == 0
    fresh_cmd = [sys.executable, str(Path(__file__).resolve()), "--identity-only"]
    fresh = [subprocess.check_output(fresh_cmd, cwd=ROOT, env=env, text=True) for _ in range(2)]
    assert fresh[0] == fresh[1]
    fig, axes = plt.subplots(3, 1, figsize=(7.2, 6.8), sharex=True, layout="constrained")
    for ax, residual, title in zip(axes[:2], residuals,
                                   ("Action minus exact reference", "Fixed-map JVP minus exact reference")):
        ax.axhline(0, color="0.7", lw=1)
        ax.scatter(range(6), residual.ravel(), color="#24598c", s=30, zorder=3)
        ax.set_yticks([0]); ax.set_ylabel(r"Residual [$s^{-1}$]")
        ax.set_title(title, fontsize=11)
        ax.text(.5, .70, "All six residuals are exactly zero", ha="center", transform=ax.transAxes, fontsize=10)
    axes[2].axhline(0, color="0.7", lw=1)
    axes[2].bar(range(6), delta.ravel(), color="#a0542a", width=.55)
    axes[2].set_ylabel(r"Difference [$s^{-1}$]")
    axes[2].set_title(r"Two maps: $A(B_2)-A(B)$; max absolute difference = 0.75 $s^{-1}$", fontsize=11)
    axes[2].set_xticks(range(6), ["0N", "0S", "1N", "1S", "2N", "2S"])
    axes[2].set_xlabel("Target index and angular channel (N: north, S: south)")
    fig.suptitle("Manufactured dyadic fixture: numerical deposition only", fontsize=12)
    fig.savefig(out/"reference_residual.png", dpi=160)
    plt.close(fig)
    mutants = [
        ("omit-density", "from full_bianchi_hyrec.trajectory.com_source_deposition import COMSourceDepositionPlan as P\no=P.apply\nP.apply=lambda self,r,n:o(self,r,1.)", "test_action_returns_execution_receipt_after_actual_plan"),
        ("double-conversion", "from full_bianchi_hyrec.trajectory.com_source_deposition import COMSourceDepositionPlan as P\no=P.apply\nP.apply=lambda self,r,n:o(self,r,n)*(n/self.mode_measure_m3[:,None])", "test_action_returns_execution_receipt_after_actual_plan"),
        ("omit-density-tangent", "from full_bianchi_hyrec.trajectory.com_source_deposition import COMSourceDepositionPlan as P\no=P.jvp\nP.jvp=lambda self,r,dr,n,dn:o(self,r,dr,n,0.)", "test_jvp_returns_density_and_fixed_map_execution_receipt"),
        ("ignore-layout", "from full_bianchi_hyrec.resolved_deposition import ResolvedDeposition as D\nD._require_packet=lambda self,r:None", "test_same_length_identity_or_order_mismatch_rejected"),
        ("omit-direction-identity", "import json\nfrom full_bianchi_hyrec.resolved_deposition import ResolvedDeposition as D\no=D.plan_payload_json.fget\ndef bad(self):\n v=json.loads(o(self)); v['arrays'].pop('directions'); return json.dumps(v,sort_keys=True,separators=(',',':'))\nD.plan_payload_json=property(bad)", "test_every_actual_plan_array_enters_identity[directions]"),
    ]
    mutation = {name: run_tests(out, "mutant-"+name, [TEST+"::"+test], env, prefix=code, expect_failure=True)
                for name, code, test in mutants}
    assert not git("status", "--porcelain", "--untracked-files=all"), "DIRTY_AFTER"
    for path, blob in CORE.items():
        assert git("hash-object", path) == blob, path
    result = {
        "schema": "rec-resolved-deposition-execution/v1",
        "classification": "PASS_BOUNDED_RESOLVED_NUMERICAL_DEPOSITION_ADAPTER",
        "claim": "NO_PASS_REC_PHYSICAL_SPLIT", "base_commit": BASE,
        "base_tree": git("rev-parse", BASE+"^{tree}"), "source_commit": head, "source_tree": tree,
        "tested_commit": head, "tested_tree": tree, "changed_paths": sorted(changed),
        "unchanged_core_blobs": CORE, "clean_source_before_and_after": True,
        "command": [sys.executable, *sys.argv], "exit_code": 0,
        "environment": {"python": sys.version, "platform": platform.platform(),
                        "numpy": np.__version__, "scipy": scipy.__version__, "sympy": sp.__version__,
                        "matplotlib": matplotlib.__version__, "pytest": __import__("pytest").__version__},
        "tests": tests, "oracle": {"method": "independent scalar Fraction sums", "action_max_residual": 0.,
           "jvp_max_residual": 0., "tested_domain": "B/B2 x isotropic/directional; 24 action + 24 JVP scalar comparisons in tests",
           "sympy_fixed_residual": str(fixed_residual), "sympy_full_formula_residual": str(full_residual)},
        "receipts": {"action": asdict(action.receipt), "jvp": asdict(jvp.receipt), "B2_action": asdict(alternate.receipt)},
        "arrays": {"action_s_inv": action.values.tolist(), "fixed_jvp_s_inv": jvp.values.tolist(),
                   "B2_action_s_inv": alternate.values.tolist(), "map_difference_s_inv": delta.tolist()},
        "fresh_process_command": fresh_cmd, "fresh_process_identities": [json.loads(s) for s in fresh],
        "targeted_mutations": mutation, "figure": "reference_residual.png",
        "visual_audit": "NOT_YET_PERFORMED", "physical_source_authenticated": False,
        "provider_admitted": False, "moving_map_or_event_jvp": False,
    }
    (out/"EXECUTION.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    (out/"SHA256SUMS").write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest()+"  "+p.name+"\n"
                                        for p in sorted(out.iterdir()) if p.is_file()))
    print(json.dumps({"classification": result["classification"], "source_commit": head, "source_tree": tree}), flush=True)


if __name__ == "__main__":
    main()
