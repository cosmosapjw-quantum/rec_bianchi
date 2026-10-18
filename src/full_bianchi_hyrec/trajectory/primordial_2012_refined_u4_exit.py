"""Continue reviewed h/2 Python FULL history through H post-Saha exit.

Only the reviewed h/2 accepted checkpoint is imported.  The native C history
is an external same-grid oracle and does not furnish any Python state.
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
    DLNA, DXHII_MAX, HyRec2012Cosmology, saha_xH1s, tm_steady_K,
)

CHECKPOINT_SHA256 = "70274c9631b33e4ed1c4b8761608cd9ce22f82d96b0afbcb36c0e786e2c04c6d"
START_IZ = 37207
RT_IZ = 36446
PREFIX_COLUMNS = 761
MAX_EXTRA_ACCEPTED = 4096
MAX_FULL_EVALUATIONS = 16384
DLNT_MAX = 5e-4


def load_frozen_checkpoint(path: Path) -> dict:
    if hashlib.sha256(path.read_bytes()).hexdigest() != CHECKPOINT_SHA256:
        raise ValueError("REVIEWED_H2_CONTINUATION_CHECKPOINT_SHA_MISMATCH")
    with np.load(path, allow_pickle=False) as archive:
        if set(archive.files) != {"states_json", "steps_json", "virtual_out", "average_virtual", "lyman_out"}:
            raise ValueError("REVIEWED_H2_CHECKPOINT_FIELDS")
        states = tuple(json.loads(str(s)) for s in archive["states_json"])
        steps = tuple(json.loads(str(s)) for s in archive["steps_json"])
        virtual = np.array(archive["virtual_out"], copy=True)
        average = np.array(archive["average_virtual"], copy=True)
        lyman = np.array(archive["lyman_out"], copy=True)
    if len(states) != 754 or len(steps) != 753 or states[-1]["iz"] != START_IZ:
        raise ValueError("REVIEWED_H2_CHECKPOINT_INDEX")
    if any(a.shape != shape or not np.all(np.isfinite(a)) for a, shape in (
        (virtual, (NVIRT, PREFIX_COLUMNS)), (average, (NVIRT, PREFIX_COLUMNS)),
        (lyman, (3, PREFIX_COLUMNS)))):
        raise ValueError("REVIEWED_H2_CHECKPOINT_PHOTONS")
    if states[-1]["branch"] != "H_ONLY" or not states[-1]["post_saha"] or states[-1]["xHeII"] != 0.:
        raise ValueError("REVIEWED_H2_CHECKPOINT_STAGE")
    if [steps[-2]["input_iz"], steps[-1]["input_iz"]] != [37205, 37206]:
        raise ValueError("REVIEWED_H2_CHECKPOINT_RHS_INDICES")
    if [steps[-2]["hydrogen_rhs"], steps[-1]["hydrogen_rhs"]] != [
        -0.2140541132585438, -0.06964592995647713]:
        raise ValueError("REVIEWED_H2_CHECKPOINT_RHS_TAIL")
    return {"state": states[-1], "rhs_tail": (
        steps[-2]["hydrogen_rhs"], steps[-1]["hydrogen_rhs"]),
        "virtual_out": virtual, "average_virtual": average, "lyman_out": lyman}


def original_rt_stop_index(c: HyRec2012Cosmology) -> int:
    """Translate history.c::rec_set_derived_params Pion/RT-stop loop."""
    z = 900.
    pion = 1.
    while pion > .01 and z > 0.:
        tr = 8.617343e-5*c.T0_K*(1.+z)/c.fsR/c.fsR/c.meR
        n_h = 1.e-6*c.nH0_m3*(1.+z)**3
        rl = 4.662899067555897e15*(c.fsR*c.fsR*c.meR)**3*c.hubble_s(z)/n_h
        t4 = tr/(8.617343e-5*1.e4)
        alpha = (c.fsR/c.meR)**2*4.309e-13*t4**(-.6166)/(1.+.6703*t4**.5300)
        beta4 = (3.016103031869581e21*(c.fsR*c.meR)**3*tr*math.sqrt(tr)
                 *math.exp(-.25*13.598286071938324/tr)*alpha)
        decay = 8.2206*c.fsR**8*c.meR
        pion = beta4/(3.*rl+decay+beta4)
        z -= 10.
    nzrt = math.floor(2.+math.log(8001./(1.+z))/DLNA)-c.izH0
    return c.izH0+nzrt


@dataclass(frozen=True)
class U4ExitResult:
    states: tuple[dict, ...]
    steps: tuple[dict, ...]
    virtual_out: np.ndarray
    average_virtual: np.ndarray
    lyman_out: np.ndarray
    event: dict | None
    full_evaluations: int
    status: str
    rt_stop_iz: int


def integrate_u4_exit(checkpoint: dict, c: HyRec2012Cosmology, source,
                      *, max_extra_accepted: int = MAX_EXTRA_ACCEPTED,
                      max_full_evaluations: int = MAX_FULL_EVALUATIONS,
                      observer: Callable | None = None,
                      on_accept: Callable | None = None) -> U4ExitResult:
    if not 1 <= max_extra_accepted <= MAX_EXTRA_ACCEPTED:
        raise ValueError("EXTRA_ACCEPTED_CAP")
    if not 1 <= max_full_evaluations <= MAX_FULL_EVALUATIONS:
        raise ValueError("FULL_EVALUATION_CAP")
    if DLNA != 8.49e-5/2 or c.izH0 != RT_IZ:
        raise ValueError("H2_GRID_OR_RT_START")
    s0 = dict(checkpoint["state"])
    if s0["iz"] != START_IZ or not s0["post_saha"] or s0["xHeII"] != 0.:
        raise ValueError("CHECKPOINT_STAGE_OR_INDEX")
    if abs(s0["z"]-c.redshift(START_IZ)) > 2.e-12:
        raise ValueError("CHECKPOINT_REDSHIFT")
    if abs(s0["xe"]-s0["xHII"]) > 5.e-13 or abs(s0["xH1s"]+s0["xHII"]-1.) > 5.e-13:
        raise ArithmeticError("CHECKPOINT_SPECIES_LEDGER")
    rt_stop = original_rt_stop_index(c)
    n = PREFIX_COLUMNS+max_extra_accepted+1
    virtual = np.full((NVIRT,n), np.nan)
    average = np.full((NVIRT,n), np.nan)
    lyman = np.full((3,n), np.nan)
    virtual[:,:PREFIX_COLUMNS] = checkpoint["virtual_out"]
    average[:,:PREFIX_COLUMNS] = checkpoint["average_virtual"]
    lyman[:,:PREFIX_COLUMNS] = checkpoint["lyman_out"]
    table = _canonical_twophoton_table(source.table.archive_path)
    states = [s0]
    steps = []
    d_h_prev2, d_h_prev = map(float, checkpoint["rhs_tail"])
    evaluations = 0
    event = None

    def rhs(g: int, xhii: float, tm: float, *, z_override: float | None = None):
        nonlocal evaluations
        if evaluations >= max_full_evaluations:
            raise RuntimeError("FULL_EVALUATION_CAP")
        j = g-RT_IZ
        if j < PREFIX_COLUMNS or j >= n:
            raise ArithmeticError("PHOTON_COLUMN_BOUNDS")
        if np.any(~np.isfinite(virtual[:,:j])) or np.any(~np.isfinite(lyman[:,:j])):
            raise ArithmeticError(f"UNACCEPTED_PHOTON_HISTORY_READ:{j}")
        z = c.redshift(g) if z_override is None else z_override
        incoming = causal_incoming_from_accepted_histories(
            energies_eV=table.energy_eV, virtual_history=virtual[:,:j],
            lyman_history=lyman[:,:j], z_start=c.redshift(RT_IZ), iz=j,
            z_face=z, dlna=DLNA, shear_q=0.)
        if tm == c.T0_K*(1.+z):
            tm = math.nextafter(tm, 0.)
        snap = populate_original_full_atomic(
            source, z=z, xHII=xhii, xe=xhii, Tm_K=tm,
            incoming_virtual=incoming.virtual_distortion[0],
            incoming_lyman=incoming.lya_lyb_incoming_distortion[0])
        out = complete_original_full_atomic(snap)
        evaluations += 1
        if (not math.isfinite(out.dxHII_dln_a) or
                not 0. <= out.normalized_matrix_residual <= 2.e-10):
            raise ArithmeticError(f"FULL_SOURCE_OR_SCHUR:{g}")
        if observer is not None:
            observer(g,z,xhii,tm,virtual[:,:j],lyman[:,:j],out)
        return out

    for extra in range(max_extra_accepted):
        s = states[-1]
        g = s["iz"]
        z = s["z"]
        j = g-RT_IZ
        # history.c outer thermal loop and inner RT model selection are both
        # evaluated at the accepted input before any source/column write.
        if not 1.-s["Tm_K"]/c.T0_K/(1.+z) < DLNT_MAX:
            raise RuntimeError(f"HOLD_THERMAL_STAGE_BEFORE_ENDPOINT:{g}")
        if not j < rt_stop-RT_IZ:
            raise RuntimeError(f"HOLD_RT_STAGE_BEFORE_ENDPOINT:{g}")
        current = rhs(g,s["xe"],s["Tm_K"])
        virtual[:,j] = current.outgoing_virtual
        average[:,j] = current.average_virtual
        lyman[:,j] = current.outgoing_lyman
        d_h = current.dxHII_dln_a
        zout = c.redshift(g+1)
        if s["post_saha"]:
            zprobe = (1.+z)*math.exp(-DLNA)-1.
            q = saha_xH1s(c,0.,zprobe)
            dq = (1.+zprobe)*(saha_xH1s(c,0.,zprobe-.5)-saha_xH1s(c,0.,zprobe+.5))
            X = 1.-q
            tr = c.T0_K*(1.+zprobe)
            f0 = rhs(g+1,X,tr,z_override=zprobe).dxHII_dln_a
            delta = .01*q
            fp = rhs(g+1,X+delta,tr,z_override=zprobe).dxHII_dln_a
            fm = rhs(g+1,X-delta,tr,z_override=zprobe).dxHII_dln_a
            jac = (fp-fm)/(2*delta)
            if not math.isfinite(jac) or jac == 0.:
                raise ArithmeticError(f"POST_SAHA_JACOBIAN:{g+1}")
            x1 = q+(dq+f0)/jac
            post_next = abs(x1-q) <= DXHII_MAX
            xe_out = 1.-x1
        else:
            xe_out = s["xe"]+DLNA*(1.25*d_h-.25*d_h_prev2)
            x1 = 1.-xe_out
            post_next = False
        if not all(math.isfinite(x) for x in (xe_out,x1)) or not 0. <= xe_out <= 1.:
            raise ArithmeticError(f"NONPHYSICAL_ACCEPTED_NODE:{g+1}")
        tm_out = tm_steady_K(c,xe_out,zout,c.hubble_s(zout))
        state = {"iz":g+1,"z":zout,"xH1s":x1,"xHII":1.-x1,
                 "xHeII":0.,"xe":xe_out,"Tm_K":tm_out,
                 "post_saha":post_next,"branch":"H_ONLY"}
        if abs(state["xH1s"]+state["xHII"]-1.) > 5.e-13 or abs(state["xe"]-state["xHII"]) > 5.e-13:
            raise ArithmeticError(f"SPECIES_LEDGER:{g+1}")
        step = {"input_iz":g,"output_iz":g+1,"branch":"H_ONLY",
                "hydrogen_rhs":d_h,"helium_rhs":math.nan,
                "schur_residual":current.normalized_matrix_residual,"photon_col":j}
        states.append(state)
        steps.append(step)
        if on_accept is not None:
            on_accept(state,step,current)
        d_h_prev2,d_h_prev = d_h_prev,d_h
        if event is None and s["post_saha"] and not post_next:
            event = {"type":"HYDROGEN_POST_SAHA_OFF","iz":g+1,"after_steps":extra+1}
        if event is not None and g+1 >= event["iz"]+2:
            break
    status = "EVENT_PLUS_TWO" if event and states[-1]["iz"] == event["iz"]+2 else "CAP_BEFORE_EVENT_PLUS_TWO"
    cols = PREFIX_COLUMNS+len(steps)
    return U4ExitResult(tuple(states),tuple(steps),virtual[:,:cols].copy(),
                        average[:,:cols].copy(),lyman[:,:cols].copy(),
                        event,evaluations,status,rt_stop)
