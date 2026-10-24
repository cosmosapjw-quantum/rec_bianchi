"""Bounded source-native h/2 hydrogen and thermal continuation from reviewed U4.

The accepted Python photon columns and hydrogen state are the sole evolving
history.  Native C is used by the separate verifier as a same-grid oracle.
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
    populate_original_full_atomic,
)
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import (
    DLNA, HyRec2012Cosmology, tm_steady_K,
)
from full_bianchi_hyrec.trajectory.primordial_2012_refined_u4_exit import original_rt_stop_index
from full_bianchi_hyrec.trajectory.primordial_2012_thermal_transition import source_thermal_rhs

CHECKPOINT_SHA256 = "7ad1476c78d08218e42ac616dc43d03dd8eb232c44bfb66a8f20a237dcce6943"
START_IZ = 38452
RT_IZ = 36446
PREFIX_COLUMNS = 2006
MAX_EXTRA_ACCEPTED = 20000
MAX_FULL_EVALUATIONS = 20000
DLNT_MAX = 5.e-4


def load_frozen_checkpoint(path: Path) -> dict:
    if hashlib.sha256(path.read_bytes()).hexdigest() != CHECKPOINT_SHA256:
        raise ValueError("REVIEWED_H2_U4_CHECKPOINT_SHA_MISMATCH")
    with np.load(path, allow_pickle=False) as a:
        if set(a.files) != {"states_json", "steps_json", "virtual_out", "average_virtual", "lyman_out"}:
            raise ValueError("REVIEWED_H2_U4_CHECKPOINT_FIELDS")
        states = tuple(json.loads(str(v)) for v in a["states_json"])
        steps = tuple(json.loads(str(v)) for v in a["steps_json"])
        v = np.array(a["virtual_out"], copy=True)
        avg = np.array(a["average_virtual"], copy=True)
        ly = np.array(a["lyman_out"], copy=True)
    if (len(states) != 1246 or len(steps) != 1245 or
            states[-1]["iz"] != START_IZ or states[-1]["post_saha"] or
            states[-1]["xHeII"] != 0. or states[-1]["branch"] != "H_ONLY"):
        raise ValueError("REVIEWED_H2_U4_CHECKPOINT_STAGE")
    if ([steps[-2]["input_iz"], steps[-1]["input_iz"]] != [38450, 38451] or
            [steps[-2]["hydrogen_rhs"], steps[-1]["hydrogen_rhs"]] !=
            [-0.4919330230209214, -0.45204486161530666]):
        raise ValueError("REVIEWED_H2_U4_CHECKPOINT_RHS_TAIL")
    for values, shape in ((v, (NVIRT, PREFIX_COLUMNS)),
                          (avg, (NVIRT, PREFIX_COLUMNS)), (ly, (3, PREFIX_COLUMNS))):
        if values.shape != shape or not np.all(np.isfinite(values)):
            raise ValueError("REVIEWED_H2_U4_CHECKPOINT_SPECTRUM")
    return {"state": states[-1], "temperature_tail": [s["Tm_K"] for s in states[-4:]],
            "rhs_tail": (steps[-2]["hydrogen_rhs"], steps[-1]["hydrogen_rhs"]),
            "virtual_out": v, "average_virtual": avg, "lyman_out": ly}


@dataclass(frozen=True)
class U5ThermalResult:
    states: tuple[dict, ...]
    steps: tuple[dict, ...]
    virtual_out: np.ndarray
    average_virtual: np.ndarray
    lyman_out: np.ndarray
    event: dict | None
    full_evaluations: int
    status: str
    rt_stop_iz: int


def integrate_u5_thermal(checkpoint: dict, c: HyRec2012Cosmology, source,
                         *, max_extra_accepted: int = MAX_EXTRA_ACCEPTED,
                         max_full_evaluations: int = MAX_FULL_EVALUATIONS,
                         observer: Callable | None = None,
                         on_accept: Callable | None = None) -> U5ThermalResult:
    if not 1 <= max_extra_accepted <= MAX_EXTRA_ACCEPTED:
        raise ValueError("EXTRA_ACCEPTED_CAP")
    if not 1 <= max_full_evaluations <= MAX_FULL_EVALUATIONS:
        raise ValueError("FULL_EVALUATION_CAP")
    if DLNA != 8.49e-5/2. or c.izH0 != RT_IZ:
        raise ValueError("H2_GRID_OR_RT_START")
    s0 = dict(checkpoint["state"])
    if (s0["iz"] != START_IZ or s0["post_saha"] or s0["xHeII"] != 0. or
            abs(s0["z"]-c.redshift(START_IZ)) > 2.e-12):
        raise ValueError("CHECKPOINT_SOURCE_STAGE")
    if len(checkpoint["temperature_tail"]) != 4:
        raise ValueError("CHECKPOINT_TEMPERATURE_MEMORY")
    rt_stop = original_rt_stop_index(c)
    cap = PREFIX_COLUMNS+max_extra_accepted
    virtual = np.full((NVIRT,cap),np.nan)
    average = np.full((NVIRT,cap),np.nan)
    lyman = np.full((3,cap),np.nan)
    virtual[:,:PREFIX_COLUMNS] = checkpoint["virtual_out"]
    average[:,:PREFIX_COLUMNS] = checkpoint["average_virtual"]
    lyman[:,:PREFIX_COLUMNS] = checkpoint["lyman_out"]
    table = _canonical_twophoton_table(source.table.archive_path)
    states = [s0]
    steps = []
    t_tail = list(checkpoint["temperature_tail"])
    d_h_prev2,d_h_prev = map(float,checkpoint["rhs_tail"])
    d_t_prev2 = d_t_prev = None
    event = None
    evaluations = 0

    for extra in range(max_extra_accepted):
        s = states[-1]
        g = s["iz"]
        z = s["z"]
        j = g-RT_IZ
        if j >= rt_stop-RT_IZ:
            return U5ThermalResult(tuple(states),tuple(steps),virtual[:,:j].copy(),
                average[:,:j].copy(),lyman[:,:j].copy(),event,evaluations,
                "HOLD_NEXT_STAGE_REQUIRED:RT_TABLE_BOUNDARY",rt_stop)
        tr = c.T0_K*(1.+z)
        tm = s["Tm_K"]
        delta = 1.-tm/c.T0_K/(1.+z)
        if event is None and delta >= DLNT_MAX:
            # At input g, t_tail is [T(g-3),...,T(g)]. The original
            # history.c initializes both secants before the coupled step.
            d_t_prev2 = (t_tail[2]-t_tail[0])/2./DLNA
            d_t_prev = (t_tail[3]-t_tail[1])/2./DLNA
            event = {"type":"THERMAL_SWITCH","input_iz":g,"input_col":j,
                     "delta":delta,"thermal_seed_prev2":d_t_prev2,
                     "thermal_seed_prev":d_t_prev}
        coupled = event is not None
        if coupled and (8.617343e-5*tr/c.fsR/c.fsR/c.meR <= .004 or tm/tr <= .1):
            return U5ThermalResult(tuple(states),tuple(steps),virtual[:,:j].copy(),
                average[:,:j].copy(),lyman[:,:j].copy(),event,evaluations,
                "HOLD_NEXT_STAGE_REQUIRED:THERMAL_TABLE_OR_RATIO_BOUNDARY",rt_stop)
        if not 0. < s["xe"] < 1. or not 0. < tm <= tr:
            raise ArithmeticError(f"SOURCE_STATE_DOMAIN:{g}")
        if not (PREFIX_COLUMNS <= j < cap and np.all(np.isfinite(virtual[:,:j]))
                and np.all(np.isfinite(lyman[:,:j]))):
            raise ArithmeticError(f"UNACCEPTED_PHOTON_HISTORY_READ:{j}")
        incoming = causal_incoming_from_accepted_histories(
            energies_eV=table.energy_eV,virtual_history=virtual[:,:j],
            lyman_history=lyman[:,:j],z_start=c.redshift(RT_IZ),iz=j,
            z_face=z,dlna=DLNA,shear_q=0.)
        source_tm = math.nextafter(tm,0.) if tm == tr else tm
        snap = populate_original_full_atomic(source,z=z,xHII=s["xe"],xe=s["xe"],
            Tm_K=source_tm,incoming_virtual=incoming.virtual_distortion[0],
            incoming_lyman=incoming.lya_lyb_incoming_distortion[0])
        out = complete_original_full_atomic(snap)
        evaluations += 1
        if evaluations > max_full_evaluations:
            raise RuntimeError("FULL_EVALUATION_CAP")
        if (not math.isfinite(out.dxHII_dln_a) or
                not math.isfinite(out.normalized_matrix_residual) or
                out.normalized_matrix_residual > 2.e-10):
            raise ArithmeticError(f"FULL_SOURCE_OR_SCHUR:{g}")
        if observer is not None:
            observer(g,z,s["xe"],source_tm,virtual[:,:j],lyman[:,:j],out)
        virtual[:,j] = out.outgoing_virtual
        average[:,j] = out.average_virtual
        lyman[:,j] = out.outgoing_lyman
        d_h = out.dxHII_dln_a
        # Match the source predictor operand order literally.
        xe_out = s["xe"]+DLNA*(1.25*d_h-.25*d_h_prev2)
        zout = c.redshift(g+1)
        if coupled:
            d_t = source_thermal_rhs(c,s["xe"],tm,z)
            tm_out = tm+DLNA*(1.25*d_t-.25*d_t_prev2)
            d_t_prev2,d_t_prev = d_t_prev,d_t
        else:
            d_t = None
            tm_out = tm_steady_K(c,xe_out,zout,c.hubble_s(zout))
        if not all(math.isfinite(x) for x in (xe_out,tm_out)) or not 0.<xe_out<1.:
            raise ArithmeticError(f"NONPHYSICAL_ACCEPTED_NODE:{g+1}")
        state={"iz":g+1,"z":zout,"xH1s":1.-xe_out,"xHII":xe_out,
               "xHeII":0.,"xe":xe_out,"Tm_K":tm_out,
               "post_saha":False,"branch":"H_ONLY"}
        step={"input_iz":g,"output_iz":g+1,"branch":"H_ONLY",
              "hydrogen_rhs":d_h,"thermal_rhs":d_t,
              "schur_residual":out.normalized_matrix_residual,
              "photon_col":j,"coupled":coupled}
        states.append(state)
        steps.append(step)
        t_tail = (t_tail+[tm_out])[-4:]
        d_h_prev2,d_h_prev=d_h_prev,d_h
        if on_accept is not None:
            on_accept(state,step,out)
        if coupled and g >= event["input_iz"]+1:
            break
    cols=PREFIX_COLUMNS+len(steps)
    status=("THERMAL_EVENT_TWO_STEPS_COMPLETE" if event and
            len(steps) >= event["input_iz"]-START_IZ+2 else
            "HOLD_CAP_BEFORE_THERMAL_EVENT_PLUS_TWO")
    return U5ThermalResult(tuple(states),tuple(steps),virtual[:,:cols].copy(),
                           average[:,:cols].copy(),lyman[:,:cols].copy(),
                           event,evaluations,status,rt_stop)
