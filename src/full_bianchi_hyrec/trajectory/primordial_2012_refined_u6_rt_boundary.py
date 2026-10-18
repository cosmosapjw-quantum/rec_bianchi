"""Independent source-native h/2 FULL continuation to the RT/EMLA boundary.

Only accepted Python photon columns are input to the next atomic solve.  The
reviewed U5 thermal branch is latched; no thermal seed is reconstructed here.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Callable

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import causal_incoming_from_accepted_histories
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    NVIRT, _canonical_twophoton_table, complete_original_full_atomic,
    populate_original_full_atomic)
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import DLNA, HyRec2012Cosmology
from full_bianchi_hyrec.trajectory.primordial_2012_refined_u4_exit import original_rt_stop_index
from full_bianchi_hyrec.trajectory.primordial_2012_thermal_transition import source_thermal_rhs

CHECKPOINT_SHA256 = "7aeec545cfc028e870d51e07d1fe3f052bd770d1eb4537568f5faa889bf6752b"
START_IZ = 53179
RT_IZ = 36446
PREFIX_COLUMNS = 16733
MAX_EXTRA_ACCEPTED = 5210
MAX_FULL_EVALUATIONS = 5210
H_RHS_TAIL = (-0.056163878950571774, -0.0561296548568869)
T_RHS_TAIL = (-2280.408518685064, -2281.8526711832496)


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def load_frozen_checkpoint(path: Path) -> dict:
    if _sha(path) != CHECKPOINT_SHA256:
        raise ValueError("REVIEWED_H2_U5_CHECKPOINT_SHA_MISMATCH")
    with np.load(path, allow_pickle=False) as a:
        if set(a.files) != {"states_json", "steps_json", "virtual_out", "average_virtual", "lyman_out"}:
            raise ValueError("REVIEWED_H2_U5_CHECKPOINT_FIELDS")
        states = tuple(json.loads(str(v)) for v in a["states_json"])
        steps = tuple(json.loads(str(v)) for v in a["steps_json"])
        v = np.array(a["virtual_out"], copy=True)
        avg = np.array(a["average_virtual"], copy=True)
        ly = np.array(a["lyman_out"], copy=True)
    if (len(states) != 14728 or len(steps) != 14727 or
            states[-1]["iz"] != START_IZ or states[-1]["post_saha"] or
            states[-1]["xHeII"] != 0. or states[-1]["branch"] != "H_ONLY" or
            [steps[-2]["input_iz"], steps[-1]["input_iz"]] != [53177, 53178]):
        raise ValueError("REVIEWED_H2_U5_CHECKPOINT_STAGE")
    if (tuple(step["hydrogen_rhs"] for step in steps[-2:]) != H_RHS_TAIL or
            tuple(step["thermal_rhs"] for step in steps[-2:]) != T_RHS_TAIL or
            not all(step["coupled"] for step in steps[-2:])):
        raise ValueError("REVIEWED_H2_U5_CHECKPOINT_RHS_TAIL")
    for values, shape in ((v, (NVIRT, PREFIX_COLUMNS)),
                          (avg, (NVIRT, PREFIX_COLUMNS)), (ly, (3, PREFIX_COLUMNS))):
        if values.shape != shape or not np.all(np.isfinite(values)):
            raise ValueError("REVIEWED_H2_U5_CHECKPOINT_SPECTRUM")
    event_index = 53177-38452
    event_state = states[event_index]
    h = 4.245e-5
    event = {"input_iz": 53177,
             "delta": 1.-event_state["Tm_K"]/2.7255/(1.+event_state["z"]),
             "thermal_seed_prev2": (states[event_index-1]["Tm_K"]-states[event_index-3]["Tm_K"])/(2*h),
             "thermal_seed_prev": (states[event_index]["Tm_K"]-states[event_index-2]["Tm_K"])/(2*h)}
    if not 5.e-4 <= event["delta"] < 6.e-4:
        raise ValueError("REVIEWED_H2_U5_THERMAL_EVENT")
    return {"state": states[-1], "rhs_h_tail": H_RHS_TAIL,
            "rhs_t_tail": T_RHS_TAIL, "event": event, "virtual_out": v,
            "average_virtual": avg, "lyman_out": ly}


@dataclass(frozen=True)
class U6RTResult:
    states: tuple[dict, ...]
    steps: tuple[dict, ...]
    virtual_out: np.ndarray
    average_virtual: np.ndarray
    lyman_out: np.ndarray
    event: dict
    full_evaluations: int
    status: str
    rt_stop_iz: int


def integrate_u6_rt_boundary(checkpoint: dict, c: HyRec2012Cosmology, source,
                             *, max_extra_accepted: int = MAX_EXTRA_ACCEPTED,
                             max_full_evaluations: int = MAX_FULL_EVALUATIONS,
                             on_attempt: Callable | None = None,
                             observer: Callable | None = None,
                             on_accept: Callable | None = None) -> U6RTResult:
    if not 1 <= max_extra_accepted <= MAX_EXTRA_ACCEPTED:
        raise ValueError("EXTRA_ACCEPTED_CAP")
    if not 1 <= max_full_evaluations <= MAX_FULL_EVALUATIONS:
        raise ValueError("FULL_EVALUATION_CAP")
    if DLNA != 8.49e-5/2. or c.izH0 != RT_IZ:
        raise ValueError("H2_GRID_OR_RT_START")
    s0 = dict(checkpoint["state"])
    if (s0["iz"] != START_IZ or s0["post_saha"] or s0["xHeII"] != 0. or
            s0["branch"] != "H_ONLY" or
            abs(s0["z"]-c.redshift(START_IZ)) > 2.e-12):
        raise ValueError("CHECKPOINT_SOURCE_STAGE")
    if (tuple(checkpoint["rhs_h_tail"]) != H_RHS_TAIL or
            tuple(checkpoint["rhs_t_tail"]) != T_RHS_TAIL):
        raise ValueError("CHECKPOINT_PREDICTOR_MEMORY")
    rt_stop = original_rt_stop_index(c)
    if rt_stop != 58389 or START_IZ + MAX_EXTRA_ACCEPTED != rt_stop:
        raise ValueError("FROZEN_RT_BOUNDARY")
    cap = PREFIX_COLUMNS + max_extra_accepted
    virtual = np.full((NVIRT, cap), np.nan)
    average = np.full((NVIRT, cap), np.nan)
    lyman = np.full((3, cap), np.nan)
    virtual[:, :PREFIX_COLUMNS] = checkpoint["virtual_out"]
    average[:, :PREFIX_COLUMNS] = checkpoint["average_virtual"]
    lyman[:, :PREFIX_COLUMNS] = checkpoint["lyman_out"]
    table = _canonical_twophoton_table(source.table.archive_path)
    states = [s0]
    steps = []
    d_h_prev2, d_h_prev = H_RHS_TAIL
    d_t_prev2, d_t_prev = T_RHS_TAIL
    evaluations = 0
    for extra in range(max_extra_accepted):
        s = states[-1]
        g = s["iz"]
        j = g - RT_IZ
        if g >= rt_stop or j >= rt_stop-RT_IZ:
            raise ArithmeticError("EMLA_EVALUATION_PROHIBITED")
        z, tm, xe = s["z"], s["Tm_K"], s["xe"]
        tr = c.T0_K*(1.+z)
        if not 0. < xe < 1. or not 0. < tm <= tr:
            raise ArithmeticError(f"SOURCE_STATE_DOMAIN:{g}")
        if not (PREFIX_COLUMNS <= j < cap and np.all(np.isfinite(virtual[:, :j])) and
                np.all(np.isfinite(lyman[:, :j]))):
            raise ArithmeticError(f"UNACCEPTED_PHOTON_HISTORY_READ:{j}")
        if on_attempt is not None:
            on_attempt(g, z, xe, tm, j)
        incoming = causal_incoming_from_accepted_histories(
            energies_eV=table.energy_eV, virtual_history=virtual[:, :j],
            lyman_history=lyman[:, :j], z_start=c.redshift(RT_IZ), iz=j,
            z_face=z, dlna=DLNA, shear_q=0.)
        source_tm = math.nextafter(tm, 0.) if tm == tr else tm
        snap = populate_original_full_atomic(source, z=z, xHII=xe, xe=xe,
            Tm_K=source_tm, incoming_virtual=incoming.virtual_distortion[0],
            incoming_lyman=incoming.lya_lyb_incoming_distortion[0])
        out = complete_original_full_atomic(snap)
        evaluations += 1
        if (evaluations > max_full_evaluations or
                not math.isfinite(out.normalized_matrix_residual) or
                out.normalized_matrix_residual > 2.e-10):
            raise ArithmeticError(f"FULL_SOURCE_OR_CAP:{g}")
        if observer is not None:
            observer(g, z, xe, source_tm, virtual[:, :j], lyman[:, :j], out)
        virtual[:, j] = out.outgoing_virtual
        average[:, j] = out.average_virtual
        lyman[:, j] = out.outgoing_lyman
        d_h = out.dxHII_dln_a
        d_t = source_thermal_rhs(c, xe, tm, z)
        xe_out = xe + DLNA*(1.25*d_h-.25*d_h_prev2)
        tm_out = tm + DLNA*(1.25*d_t-.25*d_t_prev2)
        zout = c.redshift(g+1)
        if not all(math.isfinite(x) for x in (xe_out, tm_out)) or not 0. < xe_out < 1.:
            raise ArithmeticError(f"NONPHYSICAL_ACCEPTED_NODE:{g+1}")
        state = {"iz": g+1, "z": zout, "xH1s": 1.-xe_out,
                 "xHII": xe_out, "xHeII": 0., "xe": xe_out,
                 "Tm_K": tm_out, "post_saha": False, "branch": "H_ONLY"}
        step = {"input_iz": g, "output_iz": g+1, "branch": "H_ONLY",
                "hydrogen_rhs": d_h, "thermal_rhs": d_t,
                "schur_residual": out.normalized_matrix_residual,
                "photon_col": j, "coupled": True}
        states.append(state)
        steps.append(step)
        d_h_prev2, d_h_prev = d_h_prev, d_h
        d_t_prev2, d_t_prev = d_t_prev, d_t
        if on_accept is not None:
            on_accept(state, step, out)
    cols = PREFIX_COLUMNS + len(steps)
    status = ("RT_BOUNDARY_REACHED_NO_EMLA_EVALUATION" if
              states[-1]["iz"] == rt_stop else "HOLD_CAP_BEFORE_RT_BOUNDARY")
    return U6RTResult(tuple(states), tuple(steps), virtual[:, :cols].copy(),
                      average[:, :cols].copy(), lyman[:, :cols].copy(), checkpoint["event"],
                      evaluations, status, rt_stop)
