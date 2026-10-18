"""Bounded continuation of the independently integrated HyRec h/2 FULL history.

The input is the immutable eight-column Python checkpoint, never a C state or
an h-grid photon field.  This module owns only the joint H+He to H-only event.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Callable

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
    causal_incoming_from_accepted_histories,
)
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    NVIRT, _canonical_twophoton_table, complete_original_full_atomic,
    populate_original_full_atomic,
)
from full_bianchi_hyrec.trajectory.primordial_2012_refined_start import (
    DLNA, DXHII_MAX, XHEII_MIN, HyRec2012Cosmology, helium_rhs,
    saha_xH1s, tm_steady_K,
)

CHECKPOINT_SHA256 = "a6fe8a9a9e6d32b99d5b567e62d87912fdf4d71aa7a9392b33fdf23c55b8416d"
PRODUCER_SHA256 = "82ea5c627fbb7a4e280fbb351c65f83cd6608364226aa643354bc8ab0f6435e0"
START_GLOBAL_INDEX = 36454
MAX_EXTRA_ACCEPTED = 4096
MAX_FULL_EVALUATIONS = 16384


def load_frozen_start(path: Path) -> dict[str, np.ndarray]:
    import hashlib
    if hashlib.sha256(path.read_bytes()).hexdigest() != CHECKPOINT_SHA256:
        raise ValueError("FROZEN_H2_CHECKPOINT_SHA_MISMATCH")
    with np.load(path, allow_pickle=False) as obj:
        data = {k: np.array(obj[k], copy=True) for k in obj.files}
    required = {"iz", "z", "xH1s", "xHII", "xHeII", "xe", "Tm_K",
                "helium_rhs_dln_a", "hydrogen_rhs_dln_a", "post_saha",
                "virtual_out", "average_virtual", "lyman_out", "matrix_residual"}
    if set(data) != required or data["iz"].tolist() != list(range(36446,36455)):
        raise ValueError("FROZEN_H2_CHECKPOINT_SHAPE_OR_INDEX")
    if any(data[k].shape != (9,) for k in ("z","xH1s","xHII","xHeII","xe","Tm_K","post_saha")):
        raise ValueError("FROZEN_H2_CHECKPOINT_NODE_SHAPE")
    if any(data[k].shape != (8,) for k in ("helium_rhs_dln_a","hydrogen_rhs_dln_a","matrix_residual")):
        raise ValueError("FROZEN_H2_CHECKPOINT_RHS_SHAPE")
    if data["virtual_out"].shape != (NVIRT,8) or data["average_virtual"].shape != (NVIRT,8) or data["lyman_out"].shape != (3,8):
        raise ValueError("FROZEN_H2_CHECKPOINT_SPECTRUM_SHAPE")
    if not all(np.all(np.isfinite(data[k])) for k in required if k != "post_saha"):
        raise ValueError("FROZEN_H2_CHECKPOINT_NONFINITE")
    if not np.all(data["post_saha"]):
        raise ValueError("FROZEN_H2_CHECKPOINT_BRANCH")
    return data


@dataclass(frozen=True)
class ContinuationResult:
    states: tuple[dict, ...]
    steps: tuple[dict, ...]
    virtual_out: np.ndarray
    average_virtual: np.ndarray
    lyman_out: np.ndarray
    event: dict | None
    full_evaluations: int
    status: str
    ledger_max: dict[str, float]


def integrate_continuation(
    checkpoint: dict[str,np.ndarray], c: HyRec2012Cosmology, source,
    *, max_extra_accepted: int = MAX_EXTRA_ACCEPTED,
    max_full_evaluations: int = MAX_FULL_EVALUATIONS,
    observer: Callable | None = None,
    on_accept: Callable | None = None,
) -> ContinuationResult:
    """Advance from global 36454 until first He cutoff or H post-Saha switch +2.

    `observer` receives each actually evaluated Python FULL atomic source input
    and its output.  It cannot change a state, branch, or photon column.
    """
    if not (1 <= max_extra_accepted <= MAX_EXTRA_ACCEPTED):
        raise ValueError("EXTRA_ACCEPTED_CAP")
    if not (1 <= max_full_evaluations <= MAX_FULL_EVALUATIONS):
        raise ValueError("FULL_EVALUATION_CAP")
    if DLNA != 8.49e-5/2 or int(checkpoint["iz"][-1]) != START_GLOBAL_INDEX:
        raise ValueError("CHECKPOINT_GRID_OR_INDEX")
    if not math.isclose(float(checkpoint["z"][-1]),c.redshift(START_GLOBAL_INDEX),abs_tol=2e-12):
        raise ValueError("CHECKPOINT_REDSHIFT")

    # One additional uncommitted column is addressable by the final
    # post-Saha next-node probe, but remains NaN throughout.
    cap = 8 + max_extra_accepted + 1
    virtual = np.full((NVIRT,cap), np.nan)
    average = np.full((NVIRT,cap), np.nan)
    lyman = np.full((3,cap), np.nan)
    virtual[:,:8] = checkpoint["virtual_out"]
    average[:,:8] = checkpoint["average_virtual"]
    lyman[:,:8] = checkpoint["lyman_out"]
    states = [{"iz": int(checkpoint["iz"][-1]),
               "z": float(checkpoint["z"][-1]),
               "xH1s":float(checkpoint["xH1s"][-1]),
               "xHII":float(checkpoint["xHII"][-1]),
               "xHeII":float(checkpoint["xHeII"][-1]),
               "xe":float(checkpoint["xe"][-1]),
               "Tm_K":float(checkpoint["Tm_K"][-1]),
               "post_saha":bool(checkpoint["post_saha"][-1]),
               "branch":"H_HE"}]
    steps: list[dict] = []
    d_he_prev2,d_he_prev = map(float,checkpoint["helium_rhs_dln_a"][-2:])
    d_h_prev2,d_h_prev = map(float,checkpoint["hydrogen_rhs_dln_a"][-2:])
    evaluations = 0
    event: dict | None = None
    ledger_max={"hydrogen_nuclei":0.,"helium_nuclei":0.,"electrons":0.}

    def check_ledgers(state: dict, where: str):
        vals=(state["xH1s"],state["xHII"],state["xHeII"],state["xe"])
        if not all(math.isfinite(float(v)) for v in vals):
            raise ArithmeticError(f"NONFINITE_SPECIES_LEDGER:{where}")
        if not (0. <= state["xH1s"] <= 1. and 0. <= state["xHII"] <= 1.
                and 0. <= state["xHeII"] <= c.fHe and 0. <= state["xe"] <= 1.+c.fHe):
            raise ArithmeticError(f"NEGATIVE_OR_SUPERUNITY_SPECIES:{where}")
        residuals={
            "hydrogen_nuclei":abs(state["xH1s"]+state["xHII"]-1.),
            "helium_nuclei":abs((c.fHe-state["xHeII"])+state["xHeII"]-c.fHe),
            "electrons":abs(state["xe"]-state["xHII"]-state["xHeII"]),
        }
        for name,val in residuals.items():
            if not math.isfinite(val) or val>5.e-13:
                raise ArithmeticError(f"SPECIES_LEDGER:{where}:{name}:{val:.17g}")
            ledger_max[name]=max(ledger_max[name],val)

    check_ledgers(states[0],"reviewed_checkpoint")
    table = _canonical_twophoton_table(source.table.archive_path)

    def rhs(global_j: int, xhii: float, xheii: float, tm: float,
            *, z_override: float | None = None):
        nonlocal evaluations
        if evaluations >= max_full_evaluations:
            raise RuntimeError("FULL_EVALUATION_CAP")
        j = global_j-36446
        if j < 0 or j >= cap or np.any(~np.isfinite(virtual[:,:j])) or np.any(~np.isfinite(lyman[:,:j])):
            raise ArithmeticError(f"UNACCEPTED_PHOTON_HISTORY_READ:{j}")
        z = c.redshift(global_j) if z_override is None else z_override
        if j < 2:
            incoming_v,incoming_l = np.zeros(NVIRT),np.zeros(2)
        else:
            incoming = causal_incoming_from_accepted_histories(
                energies_eV=table.energy_eV,virtual_history=virtual[:,:j],
                lyman_history=lyman[:,:j],z_start=c.redshift(36446),
                iz=j,z_face=z,dlna=DLNA,shear_q=0.)
            incoming_v = incoming.virtual_distortion[0]
            incoming_l = incoming.lya_lyb_incoming_distortion[0]
        tr = c.T0_K*(1.+z)
        if tm == tr:
            tm = math.nextafter(tm,0.)
        snap = populate_original_full_atomic(
            source,z=z,xHII=xhii,xe=xhii+xheii,Tm_K=tm,
            incoming_virtual=incoming_v,incoming_lyman=incoming_l)
        out = complete_original_full_atomic(snap)
        evaluations += 1
        residual=out.normalized_matrix_residual
        if (not math.isfinite(out.dxHII_dln_a) or not math.isfinite(residual)
                or residual<0. or residual>2.e-10):
            raise ArithmeticError(f"FULL_SOURCE_OR_SCHUR:{global_j}")
        if observer is not None:
            observer(global_j,z,xhii,xheii,tm,virtual[:,:j],lyman[:,:j],out)
        return out

    for extra in range(max_extra_accepted):
        s = states[-1]
        g = s["iz"]
        j = g-36446
        z = s["z"]
        zout = c.redshift(g+1)
        xhe_in = s["xHeII"]
        post = s["post_saha"]
        # Native history.c reevaluates this source stage condition at every
        # accepted input, including the two steps after a post-Saha event.
        branch = "H_HE" if xhe_in > XHEII_MIN else "H_ONLY"
        if branch == "H_HE":
            if xhe_in <= XHEII_MIN:
                raise ArithmeticError("H_HE_BRANCH_AFTER_HELIUM_CUTOFF")
            d_he = helium_rhs(c,s["xH1s"],xhe_in,c.hubble_s(z),z)
            xhe_out = xhe_in + DLNA*(1.25*d_he-0.25*d_he_prev2)
        else:
            d_he = math.nan
            xhe_out = 0.0
        # Current accepted FULL column is always source-owned at the input node.
        # At the H-only switch the source passes total xe as hydrogen xe_in.
        xh_source = s["xe"] if branch == "H_ONLY" else s["xHII"]
        current = rhs(g,xh_source,0.0 if branch == "H_ONLY" else xhe_in,s["Tm_K"])
        virtual[:,j] = current.outgoing_virtual
        average[:,j] = current.average_virtual
        lyman[:,j] = current.outgoing_lyman
        d_h = current.dxHII_dln_a
        if post:
            # history.c uses a one-step multiplicative zout inside its
            # post-Saha helper, then returns to the indexed source z grid
            # for the accepted output and steady-state Tm.
            zprobe=(1.+z)*math.exp(-DLNA)-1.
            q = saha_xH1s(c,xhe_out,zprobe)
            dq = (1.+zprobe)*(saha_xH1s(c,xhe_out,zprobe-0.5)
                              -saha_xH1s(c,xhe_out,zprobe+0.5))
            if xhe_out != 0.0:
                delta_he = .01*(c.fHe-xhe_out)
                dq += ((saha_xH1s(c,xhe_out+delta_he,zprobe)
                       -saha_xH1s(c,xhe_out-delta_he,zprobe))/(2*delta_he)
                       *helium_rhs(c,q,xhe_out,c.hubble_s(zprobe),zprobe))
            X = 1.-q
            tr = c.T0_K*(1.+zprobe)
            f0 = rhs(g+1,X,xhe_out,tr,z_override=zprobe).dxHII_dln_a
            delta_h = .01*q
            fp = rhs(g+1,X+delta_h,xhe_out,tr,z_override=zprobe).dxHII_dln_a
            fm = rhs(g+1,X-delta_h,xhe_out,tr,z_override=zprobe).dxHII_dln_a
            jac = (fp-fm)/(2*delta_h)
            if not math.isfinite(jac) or jac == 0:
                raise ArithmeticError(f"POST_SAHA_JACOBIAN:{g+1}")
            x1 = q+(dq+f0)/jac
            post_next = abs(x1-q) <= DXHII_MAX
            xe_out = (1.-x1)+xhe_out
        elif branch == "H_HE":
            xe_out = s["xHII"] + DLNA*(1.25*d_h-0.25*d_h_prev2)+xhe_out
            x1 = 1.-(xe_out-xhe_out)
            post_next = False
        else:
            xe_out = s["xe"] + DLNA*(1.25*d_h-0.25*d_h_prev2)
            x1 = 1.-xe_out
            post_next = False
        if not all(math.isfinite(v) for v in (xhe_out,x1,xe_out)) or not (0<=xe_out<=1+c.fHe):
            raise ArithmeticError(f"NONPHYSICAL_ACCEPTED_NODE:{g+1}")
        # Native H+He loop retains the residual HeII at its terminal node;
        # H-only loop treats the next output as xe=xHII, He neutral closure.
        tm_out = tm_steady_K(c,xe_out,zout,c.hubble_s(zout))
        out_state={"iz":g+1,"z":zout,"xH1s":x1,"xHII":1.-x1,
                   "xHeII":xhe_out,"xe":xe_out,"Tm_K":tm_out,
                   "post_saha":post_next,"branch":branch}
        check_ledgers(out_state,f"accepted:{g+1}:{branch}")
        states.append(out_state)
        steps.append({"input_iz":g,"output_iz":g+1,"branch":branch,
                      "hydrogen_rhs":d_h,"helium_rhs":d_he,
                      "schur_residual":current.normalized_matrix_residual,
                      "photon_col":j})
        if on_accept is not None:
            on_accept(out_state,steps[-1],current)
        d_h_prev2,d_h_prev = d_h_prev,d_h
        if branch == "H_HE":
            d_he_prev2,d_he_prev = d_he_prev,d_he
        if event is None:
            if xhe_out <= XHEII_MIN:
                event={"type":"HELIUM_CUTOFF","iz":g+1,"after_steps":extra+1}
            elif post and not post_next:
                event={"type":"HYDROGEN_POST_SAHA_OFF","iz":g+1,"after_steps":extra+1}
        if event is not None and g+1 >= event["iz"]+2:
            break
    ncols = len(steps)
    status = "EVENT_PLUS_TWO" if event and states[-1]["iz"] == event["iz"]+2 else "CAP_BEFORE_EVENT_PLUS_TWO"
    return ContinuationResult(tuple(states),tuple(steps),
        virtual[:,:8+ncols].copy(),average[:,:8+ncols].copy(),
        lyman[:,:8+ncols].copy(),event,evaluations,status,ledger_max)
