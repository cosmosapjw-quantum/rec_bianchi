"""Opt-in R3P audit of the unchanged HyRec2012 U6 native stream.

Install explicitly as ``verifier.compare_native_stream = compare_native_stream``
from an externally source-bound launcher; importing this module changes no
verifier bindings, manifests, physical operators or resource caps.

The implementation follows ``verify_r3i_h2_u6_rt_boundary.compare_native_stream``.
Per-column scalar temperatures, per-step V/A blackbody factors and dispatch
maps are reused, with unchanged scalar libm and arithmetic association. Caches
are consulted only after the original order checks, and invalidated after a
caller guard or successful forensic hooks. Inputs are stable between those
synchronous boundaries, as in the original verifier. Added per-audit storage
is O(311); input rows are streamed and the two legacy C histories are retained
for independent-owner diagnostics.

The optional keyword-only prefix_auditor owns the first PV row and the same
enumerated iterator for the remaining prefix. It must consume exactly
PREFIX_COLUMNS*314 rows including the first, validate them in stream order,
fill cv/cl prefix columns and return total PV/PL counts and prefix_position.
Its guard calls must be at least as frequent as every 4096 consumed lines;
chunk guard timing is a separate accelerated-path contract. The first row
has already passed the outer guard and tag/stage checks. Callback exceptions
propagate unchanged. This module imports or compiles no accelerator.

Material input-contract correction: a nonfinite *Python prefix* value now
raises ``ArithmeticError("C_PREFIX_NONFINITE")``. The old prefix comparison
could accept NaN and infinity. Other parser behavior, including incidental
IndexError/ValueError diagnostics and ignored trailing fields, is retained.
No status, average-gate failure or historical hold is promoted.

``causal_link_count(table, j)`` is an optional separate drop-in. Its four-entry
LRU is keyed by normalized energy shape and exact bytes, so even an in-place
table mutation cannot reuse stale geometry. All original per-step delay and
past-only index checks remain; the frozen delay buffers are backed by bytes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
from types import MappingProxyType

import numpy as np

from verify_r3i_h2_u6_rt_boundary import (
    CHECKPOINT_SHA256, START_IZ, RT_IZ, PREFIX_COLUMNS, MAX_AVERAGE_FAILURES,
    KB_EV_K, LINE_EV, compare_state, checked_integrated_rhs_ratio,
    check_thermal_event_row, _owner, numerical_gates, sha, _source_edges,
)

_SPECTRAL_METRICS = MappingProxyType({"V": "virtual", "A": "average", "L": "lyman"})


@dataclass(frozen=True, eq=False)
class CausalGeometry:
    """An owned immutable delay vector, retaining the original count checks."""

    delays: np.ndarray = field(repr=False)

    def __post_init__(self):
        # bytes-backed storage cannot be made writeable via setflags and never
        # aliases a caller-owned array, unlike a read-only view of that array.
        delays = np.asarray(self.delays, dtype=np.float64)
        if delays.shape != (313,):
            raise ValueError("U6_CAUSAL_GEOMETRY_SHAPE")
        object.__setattr__(self, "delays", np.frombuffer(delays.tobytes(), dtype=np.float64))

    @classmethod
    def from_energies(cls, energies):
        _, dst, src = _source_edges(energies)
        return cls(np.log(src/dst)/4.245e-5)

    def __call__(self, j: int) -> int:
        delay = self.delays
        if not np.all(np.isfinite(delay)) or not np.all(delay>1.):
            raise ArithmeticError("U6_FREQUENCY_CAUSAL_SPACING")
        emit = j-delay
        active = emit>=0.
        if not np.all(np.floor(emit[active]).astype(np.int64)+1<=j-1):
            raise ArithmeticError(f"U6_FUTURE_PHOTON_INDEX:{j}")
        return len(delay)


@lru_cache(maxsize=4)
def _cached_causal_geometry(shape, energy_bytes):
    energies = np.frombuffer(energy_bytes, dtype=np.float64).reshape(shape)
    return CausalGeometry.from_energies(energies)


def causal_link_count(table, j: int) -> int:
    """Same signature and checks as the legacy audit, with bounded geometry reuse."""
    energies = np.asarray(table.energy_eV, dtype=np.float64)
    geometry = _cached_causal_geometry(energies.shape, energies.tobytes(order="C"))
    return geometry(j)


def compare_native_stream(path: Path, result, c, table, source, oracle,
                          source_dir: Path, evidence: Path,
                          guard, *, prefix_auditor=None) -> dict:
    """Audit the original stream with bounded scalar caches; see module contract.

    Original positional arguments, return fields, tolerances, scalar guards
    and forensic writes match the frozen verifier. The documented nonfinite
    Python-prefix fix is the only intentionally stricter input check.
    """
    n = len(result.steps)
    cv = np.full((311, PREFIX_COLUMNS+n), np.nan)
    cl = np.full((3, PREFIX_COLUMNS+n), np.nan)
    maxima = {k: 0. for k in ("xe", "Tm_K", "hydrogen_rhs", "thermal_rhs",
                               "virtual", "average", "lyman")}
    counts = {k: 0 for k in ("PARAM", "HE", "NODE", "THERMAL_EVENT",
                             "PV", "PL", "BASE", "STEP", "V", "A", "L", "END")}
    failures = []
    c_input = None
    c_step_input = None
    end = None
    prefix_position = 0
    spectral_position = 0
    spectral_arrays = {"V": result.virtual_out, "A": result.average_virtual,
                       "L": result.lyman_out}
    spectral_metrics = _SPECTRAL_METRICS
    prefix_column = spectral_index = None
    prefix_tr = spectral_tr = None
    spectral_blackbody = [None] * 311
    with path.open() as stream, (evidence/"average_diagnostics.jsonl").open("x") as diag, \
            (evidence/"average_raw_failures.jsonl").open("x") as raw:
        rows = enumerate(stream, 1)
        for line_no, line in rows:
            if line_no % 4096 == 0:
                guard("native_stream")
                # A caller guard may mutate its inputs. Invalidate only after
                # it returns, preserving the original first-failure boundary.
                prefix_column = spectral_index = None
                spectral_arrays.update(V=result.virtual_out, A=result.average_virtual,
                                       L=result.lyman_out)
            row = line.rstrip("\n").split(",")
            tag = row[0]
            if tag not in counts:
                raise ArithmeticError(f"UNKNOWN_C_RECORD:{tag}")
            if tag == "HE" and (counts["PARAM"] != 1 or counts["NODE"]):
                raise ArithmeticError("C_HE_STAGE_ORDER")
            if tag == "NODE" and counts["HE"] != 36447:
                raise ArithmeticError("C_NODE_STAGE_ORDER")
            if tag == "THERMAL_EVENT" and (counts["NODE"] != 1 or counts["PV"]):
                raise ArithmeticError("C_EVENT_STAGE_ORDER")
            if tag in ("PV","PL") and (counts["THERMAL_EVENT"] != 1 or counts["BASE"]):
                raise ArithmeticError("C_PREFIX_STAGE_ORDER")
            if tag in ("STEP","V","A","L") and counts["BASE"] != 1:
                raise ArithmeticError("C_STEP_STAGE_ORDER")
            if tag == "END" and (counts["STEP"] != n or spectral_position != n*625):
                raise ArithmeticError("C_END_STAGE_ORDER")
            counts[tag] += 1
            if tag == "PARAM":
                if counts[tag] != 1 or tuple(map(int, row[1:])) != (RT_IZ, 21943, 58389):
                    raise ArithmeticError("C_PARAM_GRID")
            elif tag == "HE":
                if int(row[1]) != counts[tag]-1 or counts[tag] > 36447:
                    raise ArithmeticError("C_HE_ORDER")
                if any(not math.isfinite(float(q)) for q in row[2:14]):
                    raise ArithmeticError("C_HE_NONFINITE")
            elif tag == "NODE":
                if counts[tag] != 1 or int(row[1]) != RT_IZ:
                    raise ArithmeticError("C_NODE_GRID")
            elif tag == "THERMAL_EVENT":
                if counts[tag] != 1:
                    raise ArithmeticError("C_PRIOR_THERMAL_EVENT")
                check_thermal_event_row(row,result.event)
            elif tag in ("PV", "PL"):
                if tag == "PV" and prefix_position == 0 and prefix_auditor is not None:
                    audited = prefix_auditor(
                        first=(line_no, line), rows=rows, result=result,
                        c=c, table=table, cv=cv, cl=cl, guard=guard)
                    # The first PV was already counted by the common dispatch.
                    # Replace with totals, rather than counting that row twice.
                    counts["PV"] = audited["PV"]
                    counts["PL"] = audited["PL"]
                    prefix_position = audited["prefix_position"]
                    prefix_column = spectral_index = None
                    spectral_arrays.update(V=result.virtual_out, A=result.average_virtual,
                                           L=result.lyman_out)
                    continue
                col, b = map(int, row[1:3])
                expected_tag = "PV" if prefix_position % 314 < 311 else "PL"
                expected_col, expected_bin = divmod(prefix_position, 314)
                if expected_tag == "PL": expected_bin -= 311
                if tag != expected_tag or col != expected_col or b != expected_bin:
                    raise ArithmeticError(f"C_PREFIX_ORDER:{prefix_position}")
                value = float(row[3])
                if not math.isfinite(value): raise ArithmeticError("C_PREFIX_NONFINITE")
                (cv if tag == "PV" else cl)[b, col] = value
                py = (result.virtual_out if tag == "PV" else result.lyman_out)[b, col]
                # Legacy abs(NaN) > tol and inf > inf can silently pass here.
                # Match the existing native-prefix nonfinite rejection.
                if not math.isfinite(py): raise ArithmeticError("C_PREFIX_NONFINITE")
                energy = table.energy_eV[b] if tag == "PV" else LINE_EV[b]
                # Order/index checks above precede every cache access.
                if prefix_column != col:
                    prefix_tr = KB_EV_K*c.T0_K*(1.+c.redshift(RT_IZ+col))
                    prefix_column = col
                tr = prefix_tr
                fbb = 1./math.expm1(float(energy)/tr)
                if abs(py-value) > 1.e-7*max(abs(py),abs(value))+1.e-10*fbb:
                    raise ArithmeticError(f"C_PREFIX_PARITY:{col}:{b}:{tag}")
                prefix_position += 1
            elif tag == "BASE":
                if counts[tag] != 1 or prefix_position != PREFIX_COLUMNS*314:
                    raise ArithmeticError("C_PREFIX_INCOMPLETE_AT_BASE")
                c_input = {"iz": int(row[1]), "z": float(row[2]),
                           "xH1s": float(row[3]), "xHII": float(row[4]),
                           "xHeII": float(row[5]), "xe": float(row[6]),
                           "Tm_K": float(row[7]), "post_saha": bool(int(row[8]))}
                compare_state(result.states[0], c_input, -1)
            elif tag == "STEP":
                i = counts[tag]-1
                if (int(row[1]) != i or i >= n or int(row[2]) != START_IZ+i+1 or
                        spectral_position != i*625):
                    raise ArithmeticError(f"C_STEP_ORDER:{i}")
                native = {"iz": int(row[2]), "z": float(row[3]),
                          "xH1s": float(row[4]), "xHII": float(row[5]),
                          "xHeII": float(row[6]), "xe": float(row[7]),
                          "Tm_K": float(row[8]), "post_saha": bool(int(row[11]))}
                if c_input is None: raise ArithmeticError("C_BASE_MISSING")
                compare_state(result.states[i+1], native, i)
                step = result.steps[i]
                if (step["input_iz"] != START_IZ+i or
                        step["photon_col"] != PREFIX_COLUMNS+i or
                        not step["coupled"] or int(row[10]) != 1):
                    raise ArithmeticError(f"C_COUPLED_STAGE:{i}")
                maxima["hydrogen_rhs"] = max(maxima["hydrogen_rhs"],
                    checked_integrated_rhs_ratio(step["hydrogen_rhs"],float(row[9]),2.e-7,i,"H"))
                maxima["thermal_rhs"] = max(maxima["thermal_rhs"],
                    checked_integrated_rhs_ratio(step["thermal_rhs"],float(row[12]),2.e-7,i,"T"))
                if not 0. <= step["schur_residual"] <= 2.e-10:
                    raise ArithmeticError(f"PY_SCHUR_RESIDUAL:{i}")
                for name, floor in (("xe",1.e-8),("Tm_K",1.)):
                    maxima[name] = max(maxima[name],
                        abs(result.states[i+1][name]-native[name])/max(abs(native[name]),floor))
                c_step_input = c_input
                c_input = native
            elif tag in ("V", "A", "L"):
                i,b = map(int,row[1:3])
                expected_step, position = divmod(spectral_position,625)
                expected_tag = "V" if position < 311 else "A" if position < 622 else "L"
                expected_bin = position if position < 311 else position-311 if position < 622 else position-622
                if tag != expected_tag or i != expected_step or b != expected_bin:
                    raise ArithmeticError(f"C_SPECTRAL_ORDER:{spectral_position}")
                j = PREFIX_COLUMNS+i
                value = float(row[3])
                py = spectral_arrays[tag][b,j]
                if not math.isfinite(value) or not math.isfinite(py):
                    raise ArithmeticError(f"C_SPECTRUM_NONFINITE:{i}:{tag}:{b}")
                if tag == "V": cv[b,j] = value
                if tag == "L": cl[b,j] = value
                energy = LINE_EV[b] if tag == "L" else table.energy_eV[b]
                if spectral_index != i:
                    spectral_tr = KB_EV_K*c.T0_K*(1.+result.states[i]["z"])
                    spectral_index = i
                    spectral_blackbody = [None] * 311
                tr = spectral_tr
                cached = spectral_blackbody[b] if tag == "A" else None
                if cached is not None and cached[0] == energy and cached[1] == tr:
                    # Keep the Python float produced by the same scalar libm
                    # expression, rather than recasting through a NumPy array.
                    fbb = cached[2]
                else:
                    fbb = 1./math.expm1(float(energy)/tr)
                if tag == "V":
                    spectral_blackbody[b] = (energy, tr, fbb)
                tol = 1.e-7*max(abs(py),abs(value))+1.e-10*fbb
                ratio = abs(py-value)/tol
                if not math.isfinite(ratio): raise ArithmeticError("C_SPECTRUM_RATIO_NONFINITE")
                if ratio > 1.:
                    if tag != "A" or len(failures) >= MAX_AVERAGE_FAILURES:
                        raise ArithmeticError(f"C_SPECTRUM_PARITY:{i}:{tag}:{b}:{ratio}")
                    if not (np.all(np.isfinite(cv[:,:j])) and np.all(np.isfinite(cl[:,:j]))):
                        raise ArithmeticError("C_OWNER_HISTORY_INCOMPLETE")
                    history_hashes={
                        "python_virtual_f64le":hashlib.sha256(np.ascontiguousarray(result.virtual_out[:,:j],dtype="<f8").tobytes()).hexdigest(),
                        "python_lyman_f64le":hashlib.sha256(np.ascontiguousarray(result.lyman_out[:,:j],dtype="<f8").tobytes()).hexdigest(),
                        "c_virtual_f64le":hashlib.sha256(np.ascontiguousarray(cv[:,:j],dtype="<f8").tobytes()).hexdigest(),
                        "c_lyman_f64le":hashlib.sha256(np.ascontiguousarray(cl[:,:j],dtype="<f8").tobytes()).hexdigest()}
                    raw_failure={"step":i,"input_iz":START_IZ+i,"bin":b,
                                 "python_raw":float(py),"c_raw":float(value),
                                 "original_gate_ratio":ratio,"accepted_history_sha256":history_hashes,
                                 "checkpoint_sha256":CHECKPOINT_SHA256,
                                 "common_binary_sha256":sha(Path(oracle.h.lib._name))}
                    raw.write(json.dumps(raw_failure,sort_keys=True)+"\n");raw.flush()
                    p = _owner("Python",result.states[i],result.virtual_out[:,:j],
                               result.lyman_out[:,:j],py,j=j,b=b,c=c,source=source,
                               table=table,oracle=oracle,source_dir=source_dir)
                    nowner = _owner("C",c_step_input,cv[:,:j],cl[:,:j],value,
                                    j=j,b=b,c=c,source=source,table=table,
                                    oracle=oracle,source_dir=source_dir)
                    gates = numerical_gates(p,nowner,fbb)
                    diagnostic = {**raw_failure,"owners":[p,nowner],**gates}
                    diag.write(json.dumps(diagnostic,sort_keys=True)+"\n")
                    diag.flush()
                    if (gates["original_gate"]["status"] != "FAIL" or
                            gates["decimal80_ieee_gate"]["status"] != "PASS"):
                        raise ArithmeticError(f"C_AVERAGE_DIAGNOSTIC_HOLD:{i}:{b}")
                    failures.append({"step":i,"bin":b,"original_gate":gates["original_gate"],
                                     "decimal80_ieee_gate":gates["decimal80_ieee_gate"]})
                    # Diagnostic hooks are another external-call boundary.
                    spectral_index = None
                    spectral_arrays.update(V=result.virtual_out, A=result.average_virtual,
                                           L=result.lyman_out)
                metric = spectral_metrics[tag]
                maxima[metric] = max(maxima[metric],ratio)
                spectral_position += 1
            elif tag == "END":
                end = {"status":row[1],"event_iz":int(row[2]),
                       "coupled":int(row[3]),"steps":int(row[4])}
    expected = {"PARAM":1,"HE":36447,"NODE":1,"THERMAL_EVENT":1,
                "PV":PREFIX_COLUMNS*311,"PL":PREFIX_COLUMNS*3,"BASE":1,
                "STEP":n,"V":n*311,"A":n*311,"L":n*3,"END":1}
    if counts != expected or spectral_position != n*625:
        raise ArithmeticError(f"C_COUNTS:{counts}:{expected}")
    if (end is None or end["status"] != result.status or end["event_iz"] != 53177 or
            end["coupled"] != n+2 or end["steps"] != n or
            not np.all(np.isfinite(cv)) or not np.all(np.isfinite(cl))):
        raise ArithmeticError(f"C_END_OR_HISTORY:{end}")
    return {"status":"PASS_PENDING_REVIEW","counts":counts,
            "spectral_fields":spectral_position,"causal_links":313*n,
            "maxima":maxima,"original_average_failures":failures,"end":end}
