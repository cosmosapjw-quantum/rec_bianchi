"""Explicit-map numerical experiment; NOT authenticated physical deposition.

Reuse the existing COM component. Independent oracle: scalar Fraction sums.
"""
from __future__ import annotations
import argparse
import dataclasses
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
BASE = "b97e9f399d865d9e1bf4467c063393aa5e72d282"
CORE = "src/full_bianchi_hyrec/trajectory/com_source_deposition.py"
CORE_BLOB = "a3662cf399f14b7148d880266825be12baf934a0"
ALLOWED = {"scripts/probe_rec_donor02b_deposition.py",
           ".github/workflows/rec-donor02b-deposition-probe.yml",
           "docs/research/rec_donor02b_deposition/README.md",
           "docs/research/rec_donor02b_deposition/CLOSEOUT.json"}


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def exact_action(B, mu, rates, density):
    return [[density / mu[i] * sum(B[i][s] * rates[s][q] for s in range(len(rates)))
             for q in range(len(rates[0]))] for i in range(len(mu))]


def floats(matrix):
    return [[float(x) for x in row] for row in matrix]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    out = parser.parse_args().out.resolve()
    if out == ROOT or ROOT in out.parents:
        raise RuntimeError("OUTPUT_MUST_BE_OUTSIDE_WORKTREE")
    out.mkdir(parents=True, exist_ok=False)
    head = git("rev-parse", "HEAD")
    assert head == os.environ.get("EXPECTED_HEAD", head), "WRONG_HEAD"
    subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", BASE, head], check=True)
    assert git("rev-parse", "HEAD:src") == git("rev-parse", BASE + ":src")
    assert git("hash-object", CORE) == CORE_BLOB
    changed = set(git("diff", "--name-only", BASE, head).splitlines())
    assert changed and changed <= ALLOWED, sorted(changed)
    assert not git("status", "--porcelain", "--untracked-files=all"), "DIRTY_BEFORE"
    subprocess.run(["git", "-C", str(ROOT), "diff", "--check", BASE, head], check=True)
    import numpy as np
    from full_bianchi_hyrec.trajectory.com_source_deposition import COMSourceDepositionPlan

    # These SI magnitudes and ratios are exactly representable, manufactured
    # inputs. They are not cosmological parameters or atomic-source data.
    n = F(2**20)
    mu = (F(2**21), F(2**22), F(2**23))
    eu = F(1, 2**60)
    E, Es = (eu, 2*eu, 3*eu), (F(3,2)*eu, F(5,2)*eu)
    B = ((F(1,2), F(0)), (F(1,2), F(1,2)), (F(0), F(1,2)))
    B2 = ((F(3,4), F(1,4)), (F(0), F(0)), (F(1,4), F(3,4)))
    R = ((F(2), F(-1)), (F(4), F(3)))
    dR = ((F(1), F(2)), (F(-2), F(1)))

    def make_plan(matrix, name):
        return COMSourceDepositionPlan(
            mode_measure_m3=[float(x) for x in mu],
            cell_energy_J=[float(x) for x in E], source_energy_J=[float(x) for x in Es],
            number_fractions=floats(matrix), angular_weights=[0.5, 0.5],
            directions=[[0.,0.,1.], [0.,0.,-1.]],
            measure_id="manufactured-dyadic-density-measure/v1", map_id=name)

    plan, alternate = make_plan(B, "manufactured-map-A/v1"), make_plan(B2, "manufactured-map-B/v1")
    records = []
    na = nj = 0
    for scale_n in (F(1,2), F(1), F(2)):
        for scale_r in (F(-1), F(0), F(1,2), F(2)):
            rr = tuple(tuple(scale_r*x for x in row) for row in R)
            nn = n*scale_n
            oracle = exact_action(B, mu, rr, nn)
            tr = tuple(tuple(nn*dR[s][q]+nn/4*rr[s][q] for q in range(2)) for s in range(2))
            joracle = exact_action(B, mu, tr, F(1))
            a = plan.apply(floats(rr), float(nn))
            j = plan.jvp(floats(rr), floats(dR), float(nn), float(nn/4))
            for i in range(3):
                for q in range(2):
                    assert F.from_float(float(a[i,q])) == oracle[i][q], "ACTION_ORACLE"
                    assert F.from_float(float(j[i,q])) == joracle[i][q], "JVP_ORACLE"
                    na += 1
                    nj += 1
            records.append({"density_scale": str(scale_n), "rate_scale": str(scale_r),
                            "action_s_inv": a.tolist(), "jvp_s_inv": j.tolist()})
    a = plan.apply(floats(R), float(n))
    j = plan.jvp(floats(R), floats(dR), float(n), float(n/4))
    np.testing.assert_array_equal(a, [[.5,-.25],[.75,.25],[.25,.1875]])
    np.testing.assert_array_equal(j, [[.375,.4375],[.0625,.4375],[-.0625,.109375]])
    moments = []
    for p in (plan, alternate):
        aa = p.apply(floats(R), float(n))
        for q in range(2):
            nl = sum(mu[i]*F.from_float(float(aa[i,q])) for i in range(3))
            nr = n*sum(R[s][q] for s in range(2))
            el = sum(E[i]*mu[i]*F.from_float(float(aa[i,q])) for i in range(3))
            er = n*sum(Es[s]*R[s][q] for s in range(2))
            assert nl == nr and el == er
            moments.append({"map": p.map_id, "angle": q,
                            "number_residual": "0", "energy_residual": "0"})
        np.testing.assert_array_equal(p.photon_power_four_vector(aa),
                                      p.source_power_four_vector(floats(R), float(n)))
    a2 = alternate.apply(floats(R), float(n))
    assert not np.array_equal(a, a2), "MAP_NONIDENTIFIABILITY_WITNESS_LOST"
    assert a[0,1] < 0, "SIGNED_RATE_PROJECTED"
    wrong_no_density = np.array(floats(exact_action(B, mu, R, F(1))))
    wrong_twice = a * (float(n)/plan.mode_measure_m3[:,None])
    assert not np.array_equal(a, wrong_no_density)
    assert not np.array_equal(a, wrong_twice)
    # Full dmu/mu=1/2 derivative differs from the intentionally fixed-map core.
    omitted = -a/2
    full_j = j+omitted
    assert np.max(np.abs(omitted)) > 0
    rejected = []

    def must_reject(label, operation):
        try:
            operation()
        except (ValueError, FloatingPointError, TypeError):
            rejected.append(label)
        else:
            raise AssertionError("INVALID_ACCEPTED:"+label)

    must_reject("zero_measure", lambda: dataclasses.replace(plan, mode_measure_m3=[0.,4.,8.]))
    must_reject("number_partition", lambda: dataclasses.replace(plan, number_fractions=[[.75,0],[.5,.5],[0,.5]]))
    must_reject("energy_moment", lambda: dataclasses.replace(plan, number_fractions=[[.75,0],[.25,.5],[0,.5]]))
    must_reject("nonfinite_rate", lambda: plan.apply([[float("nan"),0.],[0.,0.]], float(n)))
    must_reject("wrong_rate_shape", lambda: plan.apply([[1.],[2.]], float(n)))
    must_reject("boolean_density", lambda: plan.apply(floats(R), True))
    try:
        import sympy as sp
        ns,dn,ms,dm,br,dbr = sp.symbols("n dn mu dmu br dbr", nonzero=True)
        eps = sp.symbols("eps")
        expr = (ns+eps*dn)*(br+eps*dbr)/(ms+eps*dm)
        residual = sp.simplify(sp.diff(expr,eps).subs(eps,0)
                               - ((dn*br+ns*dbr)/ms-ns*br*dm/ms**2))
        assert residual == 0
        symbolic = {"executed": True, "sympy": sp.__version__, "full_measure_derivative_residual": "0"}
    except ImportError as exc:
        symbolic = {"executed": False, "status": "OPTIONAL_TOOL_UNAVAILABLE", "detail": str(exc)}

    data = {
        "schema": "rec-donor02b-explicit-map-probe/v1",
        "classification": "PASS_BOUNDED_EXPLICIT_MAP_COMPONENT_PROBE_NOT_PHYSICAL_ADMISSION",
        "source_head": head, "source_tree": git("rev-parse", "HEAD^{tree}"),
        "base": BASE, "core_blob": CORE_BLOB, "production_tree_unchanged": True,
        "changed_paths": sorted(changed), "python": sys.version, "platform": platform.platform(),
        "numpy": np.__version__, "input_class": "MANUFACTURED_DYADIC_SI_DATA",
        "tolerance": "EXACT_FOR_THIS_FINITE_DYADIC_CORPUS_ONLY",
        "action_scalar_checks": na, "jvp_scalar_checks": nj,
        "max_action_residual": 0.0, "max_jvp_residual": 0.0,
        "density_m3": float(n), "measure_m3": [float(x) for x in mu], "energy_scale_j": float(eu),
        "B": floats(B), "alternate_B": floats(B2), "packet_rates_per_H_s": floats(R),
        "action_s_inv": a.tolist(), "fixed_map_jvp_s_inv": j.tolist(),
        "alternate_action_s_inv": a2.tolist(), "map_difference_max_s_inv": float(np.max(np.abs(a-a2))),
        "moment_residuals": moments, "invalid_inputs_rejected": rejected,
        "normalization_mutants_detected": ["omit_n_H", "apply_n_H_over_mu_twice"],
        "omitted_moving_measure_term_s_inv": omitted.tolist(),
        "full_measure_tangent_formula_only": full_j.tolist(), "symbolic": symbolic,
        "optional_executables": {x: shutil.which(x) for x in ("octave","sage","Singular","lean","lake")},
        "claim_boundary": {"physical_source_authenticated": False,
            "resolved_authority_adapter_implemented": False, "physical_deposition_map_selected": False,
            "provider_admitted": False, "moving_map_jvp_implemented": False, "claim": "NO_PASS_REC_PHYSICAL_SPLIT"}}
    (out/"corpus.json").write_text(json.dumps(records, indent=2)+"\n")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        for name, series, title in (
            ("map_ambiguity.png", ((a,"map A"),(a2,"map B")),
             "Same number/energy moments, different occupation rates"),
            ("moving_measure_term.png", ((j,"fixed measure JVP"),(full_j,"including dmu/mu=1/2")),
             "Fixed-measure and moving-measure derivatives")):
            fig, ax = plt.subplots(figsize=(8,4.5))
            for values, label in series:
                ax.plot(np.arange(a.size), values.reshape(-1), "o-", label=label)
            ax.set_xlabel("Flattened (target mode, angle) index")
            ax.set_ylabel("Occupation rate / tangent [s^-1]")
            ax.set_title(title)
            ax.legend()
            fig.tight_layout()
            fig.savefig(out/name, dpi=160)
            plt.close(fig)
        data["plot_generation"] = "TWO_PNG_FILES"
    except ImportError:
        data["plot_generation"] = "OPTIONAL_MATPLOTLIB_UNAVAILABLE"
    data["rendered_visual_audit"] = "NOT_PERFORMED"
    data["clean_worktree"] = not bool(git("status", "--porcelain", "--untracked-files=all"))
    assert data["clean_worktree"], "DIRTY_AFTER"
    (out/"RESULT.json").write_text(json.dumps(data, indent=2, sort_keys=True)+"\n")
    files = sorted(p for p in out.iterdir() if p.is_file())
    (out/"SHA256SUMS").write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest()+"  "+p.name+"\n" for p in files))
    print(json.dumps(data, sort_keys=True))


if __name__ == "__main__":
    main()
