"""Source-native steady to coupled thermal transition from reviewed U4."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Callable

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import SOURCE_DLNA, causal_incoming_from_accepted_histories
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    NVIRT, _canonical_twophoton_table, populate_original_full_atomic,
    complete_original_full_atomic,
)
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology, tm_steady_K

START_J = 1004
START_IZ = 19227
MAX_EXTRA_ACCEPTED = 8192
MAX_FULL_EVALUATIONS = 8320
MAX_COMMON_SAMPLES = 64
RT_LIMIT_J = 10972
DXHII_MAX = 3.0e-4
DLNT_MAX = 5.0e-4
U4_STOP_NPZ_SHA256 = "52fe05bd8ca0f82cc5dd523a29773a0ce76faa40688dbee9dba06ed5f310bcca"
U4_STOP_JSON_SHA256 = "e3c740628c207e438e78e281404a849c7a062316d4284be7ed789f41474bf83b"
U4_VERIFICATION_SHA256 = "81ead9051470bf1b9c89b605ea55a2e40f04462d00eb9e39392f214b08f4ca83"
CHECKPOINT_FIELDS = {
    "global_iz", "z", "xH1s", "xHII", "xHeII", "xe", "Tm_K", "post_saha",
    "hydrogen_rhs_dln_a", "virtual_out", "average_virtual",
    "lyman_out", "matrix_residual",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_reviewed_u4_stop(npz: Path, sidecar: Path, verification: Path) -> dict[str, np.ndarray]:
    """Require the exact reviewed accepted state and all causal photon columns."""
    got = (sha256(npz), sha256(sidecar), sha256(verification))
    expected = (U4_STOP_NPZ_SHA256, U4_STOP_JSON_SHA256, U4_VERIFICATION_SHA256)
    if got != expected:
        raise ValueError(f"REVIEWED_U4_IDENTITY_MISMATCH:{got!r}")
    meta = json.loads(Path(sidecar).read_text())
    report = json.loads(Path(verification).read_text())
    if (meta.get("phase") != "STOP" or meta.get("accepted_extra") != 622 or
            meta.get("npz_sha256") != U4_STOP_NPZ_SHA256 or
            report.get("status") != "EVENT_TWO_STEPS_COMPLETE" or
            report.get("accepted_extra") != 622):
        raise ValueError("U4_REVIEWED_STOP_SEMANTICS_MISMATCH")
    with np.load(npz, allow_pickle=False) as source:
        if set(source.files) != CHECKPOINT_FIELDS:
            raise ValueError("U4_CHECKPOINT_FIELD_SET_MISMATCH")
        a = {k: np.array(source[k], copy=True) for k in source.files}
    if (a["global_iz"].shape != (START_J+1,) or
            a["virtual_out"].shape != (NVIRT, START_J) or
            a["average_virtual"].shape != (NVIRT, START_J) or
            a["lyman_out"].shape != (3, START_J) or
            a["hydrogen_rhs_dln_a"].shape != (START_J,) or
            int(a["global_iz"][-1]) != START_IZ or
            bool(a["post_saha"][-1]) or
            float(a["xHeII"][-1]) != 0.0 or
            not np.array_equal(a["global_iz"], np.arange(18223, START_IZ+1))):
        raise ValueError("U4_CHECKPOINT_START_STATE_MISMATCH")
    for key in ("z", "xH1s", "xHII", "xHeII", "xe", "Tm_K", "virtual_out", "average_virtual", "lyman_out", "hydrogen_rhs_dln_a"):
        if not np.all(np.isfinite(a[key])):
            raise ValueError(f"U4_CHECKPOINT_NONFINITE:{key}")
    return a


def classify_stop_status(status: str, event_j: int | None, after: int) -> str:
    """Preserve source event progress when a bounded run ends mid-transition."""
    if (status == "BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED" and
            event_j is not None and after < 2):
        return "HOLD_NEXT_STAGE_REQUIRED:EVENT_TWO_STEPS_INCOMPLETE"
    return status


def source_thermal_rhs(c: HyRec2012Cosmology, xe: float, tm: float, z: float) -> float:
    """Exact source branch and cgs-to-K/s coefficient of rec_dTmdlna."""
    tr=c.T0_K*(1.+z)
    if tr/tm-1. < 1.e-10:
        return -tr
    gamma=(c.fsR*c.fsR/(c.meR*c.meR*c.meR)*4.91466895548409e-22
           *tr*tr*tr*tr*xe/(1.+xe+c.fHe))
    return -2.*tm+gamma*(tr-tm)/c.hubble_s(z)


def continue_thermal_transition(
    checkpoint: dict[str, np.ndarray], c: HyRec2012Cosmology, source,
    *, common_input_oracle: Callable, max_extra_accepted: int = MAX_EXTRA_ACCEPTED,
    checkpoint_callback: Callable[[dict], None] | None = None,
) -> dict:
    if not callable(common_input_oracle) or not callable(getattr(common_input_oracle,"thermal_rhs",None)):
        raise ValueError("COMMON_INPUT_C_ORACLE_REQUIRED")
    if not (1 <= max_extra_accepted <= MAX_EXTRA_ACCEPTED):
        raise ValueError("EXTRA_ACCEPTED_CAP_INVALID")
    table = _canonical_twophoton_table(source.table.archive_path)
    ncap = START_J + max_extra_accepted
    node_names = ("global_iz", "z", "xH1s", "xHII", "xHeII", "xe", "Tm_K", "post_saha")
    nodes = {k: np.empty(ncap+1, dtype=checkpoint[k].dtype) for k in node_names}
    for k in node_names: nodes[k][:START_J+1] = checkpoint[k]
    vout = np.full((NVIRT,ncap),np.nan); avgout=np.full((NVIRT,ncap),np.nan)
    lyout=np.full((3,ncap),np.nan); rhs=np.full(ncap,np.nan); residual=np.full(ncap,np.nan)
    for target,key in ((vout,"virtual_out"),(avgout,"average_virtual"),(lyout,"lyman_out")):
        target[:,:START_J]=checkpoint[key]
    rhs[:START_J]=checkpoint["hydrogen_rhs_dln_a"]
    residual[:START_J]=checkpoint["matrix_residual"]
    thermal_rhs=np.full(ncap,np.nan)
    thermal_prev_after=np.full(ncap,np.nan)
    thermal_prev2_after=np.full(ncap,np.nan)
    accepted=START_J; full_evals=0; samples=[]; common_max={"rhs":0.,"thermal_rhs":0.,"virtual":0.,"average":0.,"lyman":0.}
    event_j=None; after=0; status="BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED"
    event_samples: set[int] = set()
    fixed_samples={START_J,START_J+1} | {START_J+256*k for k in range(1,33)}
    endpoint_diagnostic=None
    thermal_prev=None; thermal_prev2=None; thermal_seeds=None

    def emit(phase, failure=None):
        if checkpoint_callback is None: return
        n=accepted
        checkpoint_callback({"phase":phase,"accepted_extra":n-START_J,
            **{k:nodes[k][:n+1].copy() for k in node_names},
            "hydrogen_rhs_dln_a":rhs[:n].copy(),"virtual_out":vout[:,:n].copy(),
            "average_virtual":avgout[:,:n].copy(),"lyman_out":lyout[:,:n].copy(),
            "matrix_residual":residual[:n].copy(),"thermal_rhs_dln_a":thermal_rhs[:n].copy(),
            "thermal_prev_after":thermal_prev_after[:n].copy(),
            "thermal_prev2_after":thermal_prev2_after[:n].copy(),
            "full_evaluations":full_evals,"thermal_prev":thermal_prev,
            "thermal_prev2":thermal_prev2,"thermal_seeds":thermal_seeds,
            "event_j":event_j,"branch_steps_after_event":after,"samples":tuple(samples),
            "common_max":dict(common_max),"endpoint_diagnostic":endpoint_diagnostic,
            "failure":failure})

    def evaluate(j, hii, temp, sample=False):
        nonlocal full_evals
        if full_evals >= MAX_FULL_EVALUATIONS: raise RuntimeError("HOLD_NEXT_STAGE_REQUIRED:FULL_EVALUATION_CAP")
        if j >= RT_LIMIT_J: raise RuntimeError("HOLD_NEXT_STAGE_REQUIRED:RT_TABLE_BOUNDARY")
        if j<2:
            fv=np.zeros(NVIRT); fl=np.zeros(2)
        else:
            inc=causal_incoming_from_accepted_histories(
                energies_eV=table.energy_eV,virtual_history=vout[:,:j],
                lyman_history=lyout[:,:j],z_start=float(nodes["z"][0]),iz=j,
                z_face=float(nodes["z"][j]),dlna=SOURCE_DLNA,shear_q=0.)
            fv=inc.virtual_distortion[0]; fl=inc.lya_lyb_incoming_distortion[0]
        tr=c.T0_K*(1.+float(nodes["z"][j])); t=float(temp)
        if t==tr: t=math.nextafter(t,0.)
        snap=populate_original_full_atomic(source,z=float(nodes["z"][j]),xHII=float(hii),
            xe=float(hii),Tm_K=t,incoming_virtual=fv,incoming_lyman=fl)
        out=complete_original_full_atomic(snap); full_evals+=1
        if not math.isfinite(float(out.dxHII_dln_a)):
            raise ArithmeticError(f"NONFINITE_FULL_RHS:j={j}")
        if (not math.isfinite(float(out.normalized_matrix_residual)) or
                out.normalized_matrix_residual>2e-10):
            raise ArithmeticError(f"SCHUR_RESIDUAL:j={j}")
        for label,values,shape in (("virtual",out.outgoing_virtual,(NVIRT,)),
                                   ("average",out.average_virtual,(NVIRT,)),
                                   ("lyman",out.outgoing_lyman,(3,))):
            if np.asarray(values).shape!=shape or not np.all(np.isfinite(values)):
                raise ArithmeticError(f"NONFINITE_FULL_PHOTON:j={j}:channel={label}")
        if sample and j not in samples:
            if len(samples)>=MAX_COMMON_SAMPLES: raise RuntimeError("HOLD_NEXT_STAGE_REQUIRED:COMMON_INPUT_SAMPLE_CAP")
            ref=common_input_oracle(j,float(nodes["z"][j]),float(hii),0.,t,vout[:,:j],lyout[:,:j])
            samples.append(j)
            if not math.isfinite(float(ref["rhs"])):
                raise ArithmeticError(f"NONFINITE_COMMON_INPUT_C_RHS:j={j}")
            r=abs(out.dxHII_dln_a-float(ref["rhs"]))/max(1.,abs(float(ref["rhs"])))
            if not math.isfinite(r): raise ArithmeticError(f"NONFINITE_COMMON_INPUT_RHS_RATIO:j={j}")
            common_max["rhs"]=max(common_max["rhs"],r)
            if r>2e-10: raise ArithmeticError(f"COMMON_INPUT_RHS_PARITY:j={j}:scaled={r}")
            t_py=source_thermal_rhs(c,float(hii),t,float(nodes["z"][j]))
            t_c=float(common_input_oracle.thermal_rhs(float(hii),t,float(nodes["z"][j])))
            t_scaled=abs(t_py-t_c)/max(1.,abs(t_c))
            if not math.isfinite(t_scaled) or t_scaled>2e-10:
                raise ArithmeticError(f"COMMON_INPUT_THERMAL_RHS_PARITY:j={j}:scaled={t_scaled}")
            common_max["thermal_rhs"]=max(common_max["thermal_rhs"],t_scaled)
            tr_ev=8.617343e-5*tr
            fbbv=1./np.expm1(table.energy_eV/tr_ev)
            line_e=np.array((10.198714553953742,12.087365397278509,12.748393192442178))
            fbbl=1./np.expm1(line_e/tr_ev)
            for label,p,bb in (("virtual",out.outgoing_virtual,fbbv),
                               ("average",out.average_virtual,fbbv),("lyman",out.outgoing_lyman,fbbl)):
                q=np.asarray(ref[label],dtype=float)
                tol=1e-7*np.maximum(abs(p),abs(q))+1e-10*bb
                ratio=abs(p-q)/tol
                if not np.all(np.isfinite(ratio)) or np.any(ratio>1):
                    raise ArithmeticError(f"COMMON_INPUT_PHOTON_PARITY:j={j}:kind={label}")
                common_max[label]=max(common_max[label],float(np.max(ratio)))
        return out

    emit("START")
    try:
        while accepted-START_J < max_extra_accepted:
            j=accepted; iz=int(nodes["global_iz"][j]); z=float(nodes["z"][j])
            tr=c.T0_K*(1.+z); tm=float(nodes["Tm_K"][j])
            delta=1.-tm/tr
            if event_j is None and delta >= DLNT_MAX:
                event_j=j
                if j<3: raise ArithmeticError("THERMAL_SEED_PREHISTORY_MISSING")
                thermal_prev2=(float(nodes["Tm_K"][j-1])-float(nodes["Tm_K"][j-3]))/(2.*SOURCE_DLNA)
                thermal_prev=(float(nodes["Tm_K"][j])-float(nodes["Tm_K"][j-2]))/(2.*SOURCE_DLNA)
                thermal_seeds={"prev2":thermal_prev2,"prev":thermal_prev,"event_j":j,
                               "delta":delta}
                event_samples.update((j-1,j,j+1))
                if j-1 not in samples:
                    evaluate(j-1,float(nodes["xe"][j-1]),
                             float(nodes["Tm_K"][j-1]),sample=True)
                emit("EVENT")
            if j >= RT_LIMIT_J:
                status="HOLD_NEXT_STAGE_REQUIRED:RT_TABLE_BOUNDARY"; break
            if event_j is not None and (8.617343e-5*tr/(c.fsR*c.fsR*c.meR)<=0.004
                                        or tm/tr<=0.1):
                status="HOLD_NEXT_STAGE_REQUIRED:THERMAL_TABLE_OR_RATIO_BOUNDARY"; break
            if not (0.<float(nodes["xe"][j])<1. and 0.<tm<=tr):
                raise FloatingPointError(f"HYDROGEN_THERMAL_STATE_DOMAIN:j={j}")
            out=evaluate(j,float(nodes["xe"][j]),tm,
                         sample=(j in fixed_samples or j in event_samples))
            rhs[j]=float(out.dxHII_dln_a); residual[j]=float(out.normalized_matrix_residual)
            vout[:,j]=out.outgoing_virtual; avgout[:,j]=out.average_virtual
            lyout[:,j]=out.outgoing_lyman
            nextj=j+1; nodes["global_iz"][nextj]=iz+1
            nodes["z"][nextj]=c.redshift(iz+1); zn=float(nodes["z"][nextj])
            nodes["xe"][nextj]=float(nodes["xe"][j])+SOURCE_DLNA*(1.25*rhs[j]-.25*rhs[j-2])
            nodes["xH1s"][nextj]=1.-nodes["xe"][nextj]
            nodes["xHII"][nextj]=nodes["xe"][nextj]
            nodes["xHeII"][nextj]=0.
            nodes["post_saha"][nextj]=False
            if event_j is None:
                nodes["Tm_K"][nextj]=tm_steady_K(c,float(nodes["xe"][nextj]),zn,c.hubble_s(zn))
            else:
                g=source_thermal_rhs(c,float(nodes["xe"][j]),tm,z)
                if not math.isfinite(g): raise ArithmeticError(f"NONFINITE_THERMAL_RHS:j={j}")
                thermal_rhs[j]=g
                nodes["Tm_K"][nextj]=tm+SOURCE_DLNA*(1.25*g-.25*thermal_prev2)
                thermal_prev2,thermal_prev=thermal_prev,g
                thermal_prev_after[j]=thermal_prev
                thermal_prev2_after[j]=thermal_prev2
                after+=1
            if not all(math.isfinite(float(nodes[k][nextj])) for k in ("xe","xH1s","Tm_K")):
                raise FloatingPointError(f"NONFINITE_ACCEPTED_STATE:j={j}")
            if not (0.<float(nodes["xe"][nextj])<1. and
                    0.<float(nodes["Tm_K"][nextj])<=c.T0_K*(1.+zn)):
                raise FloatingPointError(f"NONPHYSICAL_ACCEPTED_STATE:j={j}")
            accepted=nextj
            if (accepted-START_J)%256==0: emit(f"ACCEPTED_{accepted-START_J:04d}")
            if event_j is not None:
                emit(f"COUPLED_{after}")
                if after>=2:
                    status="THERMAL_EVENT_TWO_STEPS_COMPLETE"; break
        status=classify_stop_status(status,event_j,after)
        emit("STOP")
    except BaseException as exc:
        emit("EXCEPTION",{"type":type(exc).__name__,"message":str(exc),"last_accepted_j":accepted})
        raise
    n=accepted
    return {"status":status,"event_j":event_j,"branch_steps_after_event":after,
        "accepted_extra":n-START_J,"full_evaluations":full_evals,"samples":samples,
        "common_max":common_max,"endpoint_diagnostic":endpoint_diagnostic,
        "thermal_seeds":thermal_seeds,"thermal_prev":thermal_prev,
        "thermal_prev2":thermal_prev2,
        "nodes":{k:nodes[k][:n+1] for k in node_names},
        "hydrogen_rhs_dln_a":rhs[:n],"thermal_rhs_dln_a":thermal_rhs[:n],
        "thermal_prev_after":thermal_prev_after[:n],
        "thermal_prev2_after":thermal_prev2_after[:n],
        "matrix_residual":residual[:n],"virtual_out":vout[:,:n],
        "average_virtual":avgout[:,:n],"lyman_out":lyout[:,:n]}
