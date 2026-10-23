"""Three predeclared risk-directed cases; root runs this under run_bounded.py.

No solver, C compilation, original LINE02 runner, history integration, or IVP.
All artifacts are written below this reviewer's directory. Primary arrays are
reused as independent native-C references; their preparation is never rerun.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time
import traceback

START_WALL = time.perf_counter()
START_CPU = resource.getrusage(resource.RUSAGE_SELF)
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[name] = "1"
sys.dont_write_bytecode = True

import mpmath as mp
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("REC_HISTORY_UNIT_ROOT",
                          HERE.parent / "rec_bianchi/research/rec_history_boundary_20261023")).resolve()
DONOR = ROOT.parent / "rec_line_native_owner_20261023"
PRIMARY = ROOT / "results/attempt001"
sys.path.insert(0, str(ROOT / "code"))
import history_boundary as hb

mp.mp.dps = 80
EPS = np.finfo(float).eps
LYA_FACT = 4.662899067555897e15


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    out = Path(args.output).resolve()
    if HERE not in out.parents:
        raise ValueError("review output must remain in the reviewer's directory")
    out.mkdir(parents=True, exist_ok=False)
    checks, cases, arrays = [], [], {}

    def check(case, name, value, **evidence):
        checks.append(dict(case=case, name=name, passed=bool(value), **evidence))

    def compare(case, name, value, reference, gross, tolerance):
        a, b, g = np.asarray(value), np.asarray(reference), np.asarray(gross)
        scale = np.maximum(np.abs(g), 1e-300)
        difference = np.abs(a-b)
        ratio = float(np.max(difference/scale))
        check(case, name, np.all(np.isfinite(a)) and np.all(difference <= tolerance*scale),
              maximum_scaled_error=ratio, tolerance=float(tolerance),
              maximum_absolute_error=float(np.max(difference)))

    identities = {str(path): sha(path) for path in (
        Path(__file__), ROOT/"FROZEN_CONTRACT.md", ROOT/"PREEXEC_ADDENDUM.md",
        ROOT/"code/history_boundary.py", PRIMARY/"SUMMARY.json", PRIMARY/"raw_arrays.npz",
        DONOR/"inputs/ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv",
        DONOR/"results/attempt001/PREPARED_BLOCKS.npz")}
    if identities[str(ROOT/"FROZEN_CONTRACT.md")] != "dc0e109608edddf458489066be4a1bae83bd2d89134535f2a0303c4c5efbcf35":
        raise ValueError("frozen contract identity changed")
    if identities[str(ROOT/"code/history_boundary.py")] != "f0858a0ef231c62cf29c8d03ca769d3e9f8539a7809f890be5f4e22aa5fa0600":
        raise ValueError("review target differs from the independently inspected primary source")

    # Metadata audit only: the two statements are exact separate native lines.
    native = (DONOR/"vendor/hydrogen.c").read_bytes()
    source_lines = native.splitlines(keepends=True)
    concatenated = (PRIMARY/"native_oracle/rhs_real_statements.cfrag").read_bytes()
    components = []
    pieces = []
    for prefix in (b"sr[0]     =", b"sr[1]     ="):
        matches = [(i+1, line) for i, line in enumerate(source_lines)
                   if line.lstrip().startswith(prefix)]
        if len(matches) != 1:
            raise ValueError("native statement identity is not unique")
        line_number, piece = matches[0]
        pieces.append(piece)
        components.append(dict(source_line=line_number, source_byte_offset=native.index(piece),
                               bytes=len(piece), sha256=hashlib.sha256(piece).hexdigest(),
                               exact_individual_substring=True))
    if b"".join(pieces) != concatenated:
        raise ValueError("retained statement concatenation differs from literal native lines")
    supplement = dict(status="PASS_PROVENANCE", original_BUILD_preserved=True,
                      hydrogen_c_sha256=hashlib.sha256(native).hexdigest(),
                      combined_fragment_sha256=hashlib.sha256(concatenated).hexdigest(),
                      contiguous_substring=concatenated in native,
                      interpretation="Two noncontiguous byte-identical original source lines concatenated in source order",
                      components=components)
    (out/"SOURCE_STATEMENT_SUPPLEMENT.json").write_text(json.dumps(supplement, indent=2)+"\n")

    # Read the snapshot independently; no production parser is used for oracles.
    meta, real_source = {}, np.zeros(2)
    virtual = np.zeros((311, 13))
    with (DONOR/"inputs/ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv").open(newline="") as handle:
        for row in csv.reader(handle):
            if row[0] == "META":
                meta[row[1]] = float(row[2])
            elif row[0] == "REAL":
                real_source[int(row[1])] = float(row[3])
            elif row[0] == "VIRTUAL":
                virtual[int(row[1])] = list(map(float, row[2:]))
    source = np.r_[real_source, virtual[:, 7]]
    incoming0 = np.r_[virtual[:, 1], meta["Dfplus_Lya"], meta["Dfplus_Lyb"]]
    x1s, nH, H = map(mp.mpf, (meta["x1s"], meta["nH_cm3"], meta["H_sInv"]))
    native_rate_mp = mp.mpf(LYA_FACT)*H/nH/x1s
    frozen = hb.load_frozen(DONOR/"inputs/ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv",
                            DONOR/"results/attempt001/PREPARED_BLOCKS.npz")
    with np.load(PRIMARY/"raw_arrays.npz", allow_pickle=False) as saved:
        du = saved["frozen_direction2"].copy()
        c_rhs = saved["frozen_rhs2"][1].copy()
        dX = saved["frozen_states2"][0].copy()
        c_outgoing_tangent = saved["frozen_outgoing2"][3].copy()
    fatal = None
    try:
        # Case 1: one stored finite-opacity direction, rotated to complex values.
        # Separate real/imaginary checks prevent a large baseline masking a lost
        # or cast-away imaginary component. No additional solve is performed.
        case = "complex_finite_source_and_outgoing"
        cases.append(dict(id=case, tau=2.0, reference="primary direction 2 native-C RHS/outgoing", dense_solves=0))
        baseline = source.copy()
        baseline[1] = float(mp.mpf(source[1])+3*native_rate_mp*x1s*
                            (mp.exp(-mp.mpf(2))*(-1))*mp.mpf(incoming0[311]))
        complex_source = frozen.source_at(incoming0+1j*du, tau=2.0)
        check(case, "complex_source_dtype", np.iscomplexobj(complex_source))
        compare(case, "source_real_baseline", complex_source.real, baseline,
                np.abs(source)+np.abs(baseline), 128*EPS)
        compare(case, "source_imaginary_native_C", complex_source.imag, c_rhs,
                np.abs(c_rhs), 128*EPS)
        complex_out = frozen.outgoing_jvp(1j*dX, 1j*du, tau=2.0)
        check(case, "complex_outgoing_dtype_and_zero_real", np.iscomplexobj(complex_out)
              and np.all(complex_out.real == 0))
        compare(case, "outgoing_imaginary_native_C", complex_out.imag, c_outgoing_tangent,
                np.abs(c_outgoing_tangent), 5e-9)
        arrays.update(complex_source=complex_source, complex_source_real_reference=baseline,
                      complex_source_imaginary_reference=c_rhs, complex_outgoing=complex_out,
                      complex_outgoing_imaginary_reference=c_outgoing_tangent)

        # Case 2: tau=0 must remove the entire direct Ly-alpha diagonal/source
        # pair, retain all other source rows, and copy the incoming line exactly.
        case = "transparent_direct_Lya_pair"
        cases.append(dict(id=case, tau=0.0, Lya_incoming_multiplier=1.75, dense_solves=0))
        incoming = incoming0.copy()
        incoming[311] *= 1.75
        expected = source.copy()
        expected[1] = float(mp.mpf(source[1])-3*native_rate_mp*x1s*mp.mpf(incoming0[311]))
        actual = frozen.source_at(incoming, tau=0.0)
        compare(case, "source_pair_removed", actual, expected,
                np.abs(source)+np.abs(expected), 128*EPS)
        other = np.arange(313) != 1
        check(case, "other_source_rows_exact", np.array_equal(actual[other], source[other]))
        increment = frozen.source_increment(incoming-incoming0, tau=0.0)
        check(case, "Lya_input_coefficient_exact_zero", np.all(increment == 0.0))
        original_M, transparent_M = frozen.Mstar(), frozen.Mstar(0.0)
        delta_M = transparent_M-original_M
        delta_M[1,1] = 0.0
        check(case, "other_matrix_entries_exact", np.all(delta_M == 0.0))
        diag_reference = float(mp.mpf(original_M[1,1])-native_rate_mp)
        compare(case, "direct_diagonal_removed", transparent_M[1,1], diag_reference,
                abs(original_M[1,1])+abs(diag_reference), 128*EPS)
        output = frozen.outgoing(frozen.X0, incoming, tau=0.0)
        check(case, "transparent_outgoing_exact", output[311] == incoming[311])
        arrays.update(transparent_source=actual, transparent_source_reference=expected,
                      transparent_source_increment=increment)

        # Case 3: an admitted negative incoming departure exercises the optional
        # physical reference across JVP and ledger APIs. Both source and input
        # absolute occupations are positive; no clipping is permitted.
        case = "signed_incoming_physical_reference"
        base = 2.0**-40
        state = np.array([-base, -1.125*base, .75, .3, 1.4])
        direction = np.array([.2*base, -.3*base, .01, .02, -.03])
        reference_occupation = 2*base
        cases.append(dict(id=case, state=state.tolist(), direction=direction.tolist(),
                          reference_occupation=reference_occupation, dense_solves=0))
        admitted = hb.boundary_jvp(*state, *direction, reference_occupation=reference_occupation)
        def expression(t):
            din,xr,g,tau,q = [mp.mpf(float(state[k]))+t*mp.mpf(float(direction[k]))
                             for k in range(5)]
            return din+(xr/(3*g)-din)*(-mp.expm1(-tau/q))
        oracle = mp.diff(expression, mp.mpf(0))
        din,xr,g,tau,q = map(mp.mpf, state)
        dd,dx,dg,dt,dq = map(mp.mpf, direction)
        transmission, absorption = mp.exp(-tau/q), -mp.expm1(-tau/q)
        source_departure = xr/(3*g)
        gross = float(abs(transmission*dd)+abs(absorption*dx/(3*g))+
                      abs(absorption*source_departure*dg/g)+
                      abs((source_departure-din)*transmission*dt/q)+
                      abs((source_departure-din)*transmission*tau*dq/q**2))
        compare(case, "signed_JVP_mp80", admitted, float(oracle), gross, 5e-9)
        try:
            hb.boundary_jvp(*state, *direction)
        except ValueError as exc:
            check(case, "zero_reference_rejects_same_state", str(exc) == "NEGATIVE_ABSOLUTE_OCCUPATION")
        else:
            check(case, "zero_reference_rejects_same_state", False)
        ledger = hb.line_ledger(state[0],state[1],state[2],state[3],float(nH),float(H),state[4],
                                reference_occupation=reference_occupation)
        # Independent atomic-side normalization; nH cancels analytically.
        atomic_r0 = mp.mpf(LYA_FACT)*H/nH/g
        rate_ref = nH*mp.mpf(1e6)*atomic_r0*q*absorption*(xr-3*g*din)
        rate_gross = nH*mp.mpf(1e6)*atomic_r0*q*absorption*(abs(xr)+3*g*abs(din))
        compare(case, "signed_ledger_atomic_rate_mp80", ledger["R"], float(rate_ref),
                float(rate_gross), 128*EPS)
        arrays["signed_JVP_and_rate"] = np.array([admitted,float(oracle),gross,ledger["R"],float(rate_ref),float(rate_gross)])
    except Exception as exc:
        fatal = dict(type=type(exc).__name__, message=str(exc))
        (out/"exception.log").write_text(traceback.format_exc())
    np.savez_compressed(out/"raw_arrays.npz", **arrays)
    (out/"checks.json").write_text(json.dumps(checks, indent=2, allow_nan=False)+"\n")
    (out/"cases.json").write_text(json.dumps(cases, indent=2, allow_nan=False)+"\n")
    usage = resource.getrusage(resource.RUSAGE_SELF)
    summary = dict(status="PASS_SCOPED" if fatal is None and len(cases)==3 and all(c["passed"] for c in checks)
                   else "FAILED_PRESERVED", fatal=fatal, cases=len(cases), case_cap=3,
                   reviewer_allocation_cap=4, checks=len(checks), failed=[c for c in checks if not c["passed"]],
                   dense_rhs_solves=0, C_compilations=0, old_LINE02_reruns=0, new_IVP=0,
                   CPU_seconds=usage.ru_utime+usage.ru_stime-START_CPU.ru_utime-START_CPU.ru_stime,
                   wall_seconds=time.perf_counter()-START_WALL, peak_rss_KiB=usage.ru_maxrss,
                   mpmath_digits=80, identities_sha256=identities,
                   physical_history_calibration="INPUT_DEPENDENT_UNCALIBRATED",
                   execution_accounting="Use root run_bounded receipt for cumulative inclusive charge")
    (out/"SUMMARY.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n")
    print(json.dumps(summary, indent=2, allow_nan=False))
    return 0 if summary["status"] == "PASS_SCOPED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
