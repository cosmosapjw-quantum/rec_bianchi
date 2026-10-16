"""Source-native H-only steady-temperature continuation from reviewed U3.

The input is the accepted U3 j=382 checkpoint. No C trajectory enters the
Python state update. The endpoint diagnostic in U3 is deliberately discarded.
"""
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
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology, saha_xH1s, tm_steady_K

START_J = 382
START_IZ = 18605
MAX_EXTRA_ACCEPTED = 2048
MAX_FULL_EVALUATIONS = 8192
MAX_COMMON_SAMPLES = 64
RT_LIMIT_J = 10972
DXHII_MAX = 3.0e-4
DLNT_MAX = 5.0e-4
U3_STOP_NPZ_SHA256 = "97e54b568191a037f03822472972008952ee6c0eaedf486367d0c29f1c9bbe8b"
U3_STOP_JSON_SHA256 = "7b86be4d2e9c4a3aa53047a20b4408bf2a52be33a94e53a9ee6987ba73b7f12b"
U3_VERIFICATION_SHA256 = "8ed9aa4ac0c570fadf3f80f83b13c528056b5f4cadcd713c92b5b5031af4e082"
CHECKPOINT_FIELDS = {
    "global_iz", "z", "xH1s", "xHII", "xHeII", "xe", "Tm_K", "post_saha",
    "hydrogen_rhs_dln_a", "helium_rhs_dln_a", "virtual_out", "average_virtual",
    "lyman_out", "matrix_residual", "source_branch_h_only", "helium_cutoff_crossed",
    "hydrogen_post_saha_off_crossed",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_reviewed_u3_stop(npz: Path, sidecar: Path, verification: Path) -> dict[str, np.ndarray]:
    """Require the exact reviewed accepted state and all causal photon columns."""
    got = (sha256(npz), sha256(sidecar), sha256(verification))
    expected = (U3_STOP_NPZ_SHA256, U3_STOP_JSON_SHA256, U3_VERIFICATION_SHA256)
    if got != expected:
        raise ValueError(f"REVIEWED_U3_IDENTITY_MISMATCH:{got!r}")
    meta = json.loads(Path(sidecar).read_text())
    report = json.loads(Path(verification).read_text())
    if (meta.get("phase") != "STOP" or meta.get("accepted_extra") != 374 or
            meta.get("npz_sha256") != U3_STOP_NPZ_SHA256 or
            report.get("status") != "EVENT_TWO_STEPS_COMPLETE" or
            report.get("python_accepted_extra") != 374):
        raise ValueError("U3_REVIEWED_STOP_SEMANTICS_MISMATCH")
    with np.load(npz, allow_pickle=False) as source:
        if set(source.files) != CHECKPOINT_FIELDS:
            raise ValueError("U3_CHECKPOINT_FIELD_SET_MISMATCH")
        a = {k: np.array(source[k], copy=True) for k in source.files}
    if (a["global_iz"].shape != (START_J+1,) or
            a["virtual_out"].shape != (NVIRT, START_J) or
            a["average_virtual"].shape != (NVIRT, START_J) or
            a["lyman_out"].shape != (3, START_J) or
            a["hydrogen_rhs_dln_a"].shape != (START_J,) or
            int(a["global_iz"][-1]) != START_IZ or
            not bool(a["post_saha"][-1]) or
            float(a["xHeII"][-1]) != 0.0 or
            not np.array_equal(a["global_iz"], np.arange(18223, START_IZ+1))):
        raise ValueError("U3_CHECKPOINT_START_STATE_MISMATCH")
    for key in ("z", "xH1s", "xHII", "xHeII", "xe", "Tm_K", "virtual_out", "average_virtual", "lyman_out", "hydrogen_rhs_dln_a"):
        if not np.all(np.isfinite(a[key])):
            raise ValueError(f"U3_CHECKPOINT_NONFINITE:{key}")
    return a


def classify_stop_status(status: str, event_j: int | None, after: int) -> str:
    """Preserve source event progress when a bounded run ends mid-transition."""
    if (status == "BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED" and
            event_j is not None and after < 2):
        return "HOLD_NEXT_STAGE_REQUIRED:EVENT_TWO_STEPS_INCOMPLETE"
    return status


def continue_hydrogen_steady(
    checkpoint: dict[str, np.ndarray], c: HyRec2012Cosmology, source,
    *, common_input_oracle: Callable, max_extra_accepted: int = MAX_EXTRA_ACCEPTED,
    checkpoint_callback: Callable[[dict], None] | None = None,
) -> dict:
    if not callable(common_input_oracle):
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
    accepted=START_J; full_evals=0; samples=[]; common_max={"rhs":0.,"virtual":0.,"average":0.,"lyman":0.}
    event_j=None; after=0; status="BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED"
    event_samples: set[int] = set()
    fixed_samples={382,383,384} | {START_J+128*k for k in range(1,17)}
    endpoint_diagnostic=None

    def emit(phase, failure=None):
        if checkpoint_callback is None: return
        n=accepted
        checkpoint_callback({"phase":phase,"accepted_extra":n-START_J,
            **{k:nodes[k][:n+1].copy() for k in node_names},
            "hydrogen_rhs_dln_a":rhs[:n].copy(),"virtual_out":vout[:,:n].copy(),
            "average_virtual":avgout[:,:n].copy(),"lyman_out":lyout[:,:n].copy(),
            "matrix_residual":residual[:n].copy(),"full_evaluations":full_evals,
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
        while accepted-START_J<max_extra_accepted:
            j=accepted; iz=int(nodes["global_iz"][j]); z=float(nodes["z"][j])
            tr=c.T0_K*(1.+z)
            if j+1>=RT_LIMIT_J:
                status="HOLD_NEXT_STAGE_REQUIRED:RT_TABLE_BOUNDARY"; break
            if 1.-float(nodes["Tm_K"][j])/tr>=DLNT_MAX:
                status="HOLD_NEXT_STAGE_REQUIRED:THERMAL_BOUNDARY"; break
            if not (0.<float(nodes["xe"][j])<1.): raise FloatingPointError(f"HYDROGEN_STATE_DOMAIN:j={j}")
            out=evaluate(j,float(nodes["xe"][j]),float(nodes["Tm_K"][j]),
                         sample=(j in fixed_samples or j in event_samples))
            rhs[j]=float(out.dxHII_dln_a); residual[j]=float(out.normalized_matrix_residual)
            vout[:,j]=out.outgoing_virtual; avgout[:,j]=out.average_virtual; lyout[:,j]=out.outgoing_lyman
            nextj=j+1; nodes["global_iz"][nextj]=iz+1
            nodes["z"][nextj]=c.redshift(iz+1); zn=float(nodes["z"][nextj])
            if bool(nodes["post_saha"][j]):
                q=saha_xH1s(c,0.,zn)
                qprime=(1.+zn)*(saha_xH1s(c,0.,zn-.5)-saha_xH1s(c,0.,zn+.5))
                Tn=c.T0_K*(1.+zn)
                def probe(hii): return float(evaluate(nextj,hii,Tn).dxHII_dln_a)
                h0=1.-q; delta=.01*q
                if not (0.<delta<h0 and h0+delta<1.): raise ArithmeticError("POST_SAHA_PROBE_DOMAIN")
                f0=probe(h0); jac=(probe(h0+delta)-probe(h0-delta))/(2.*delta)
                if not math.isfinite(jac) or jac==0.: raise ArithmeticError("POST_SAHA_JACOBIAN")
                x1=q+(qprime+f0)/jac
                nodes["xH1s"][nextj]=x1; nodes["xe"][nextj]=1.-x1
                nodes["post_saha"][nextj]=abs(x1-q)<=DXHII_MAX
            else:
                nodes["xe"][nextj]=float(nodes["xe"][j])+SOURCE_DLNA*(1.25*rhs[j]-.25*rhs[j-2])
                nodes["xH1s"][nextj]=1.-nodes["xe"][nextj]
                nodes["post_saha"][nextj]=False
            nodes["xHII"][nextj]=nodes["xe"][nextj]; nodes["xHeII"][nextj]=0.
            nodes["Tm_K"][nextj]=tm_steady_K(c,float(nodes["xe"][nextj]),zn,c.hubble_s(zn))
            if not all(math.isfinite(float(nodes[k][nextj])) for k in ("xe","xH1s","Tm_K")):
                raise FloatingPointError(f"NONFINITE_ACCEPTED_STATE:j={j}")
            if not (0.<float(nodes["xe"][nextj])<1. and 0.<float(nodes["Tm_K"][nextj])<=c.T0_K*(1.+zn)):
                raise FloatingPointError(f"NONPHYSICAL_ACCEPTED_STATE:j={j}")
            accepted=nextj
            if bool(nodes["post_saha"][j]) and not bool(nodes["post_saha"][nextj]):
                if event_j is None:
                    event_j=nextj
                    event_samples.update((event_j,event_j+1,event_j+2))
                    if j not in samples:
                        evaluate(j,float(nodes["xe"][j]),float(nodes["Tm_K"][j]),sample=True)
                    emit("EVENT")
            elif event_j is not None: after+=1
            if (accepted-START_J)%128==0: emit(f"ACCEPTED_{accepted-START_J:04d}")
            if event_j is not None and after>=2:
                status="EVENT_TWO_STEPS_COMPLETE"; break
        status=classify_stop_status(status,event_j,after)
        if status=="EVENT_TWO_STEPS_COMPLETE":
            j=accepted; tr=c.T0_K*(1.+float(nodes["z"][j]))
            if j>=RT_LIMIT_J:
                status="HOLD_NEXT_STAGE_REQUIRED:RT_TABLE_BOUNDARY"
            elif 1.-float(nodes["Tm_K"][j])/tr>=DLNT_MAX:
                status="HOLD_NEXT_STAGE_REQUIRED:THERMAL_BOUNDARY"
            else:
                out=evaluate(j,float(nodes["xe"][j]),float(nodes["Tm_K"][j]),sample=True)
                endpoint_diagnostic={"j":j,"rhs":float(out.dxHII_dln_a),
                                     "matrix_residual":float(out.normalized_matrix_residual),
                                     "committed":False}
                emit("ENDPOINT_DIAGNOSTIC")
        emit("STOP")
    except BaseException as exc:
        emit("EXCEPTION",{"type":type(exc).__name__,"message":str(exc),"last_accepted_j":accepted})
        raise
    n=accepted
    return {"status":status,"event_j":event_j,"branch_steps_after_event":after,
        "accepted_extra":n-START_J,"full_evaluations":full_evals,"samples":samples,
        "common_max":common_max,"endpoint_diagnostic":endpoint_diagnostic,
        "nodes":{k:nodes[k][:n+1] for k in node_names},
        "hydrogen_rhs_dln_a":rhs[:n],"matrix_residual":residual[:n],
        "virtual_out":vout[:,:n],"average_virtual":avgout[:,:n],"lyman_out":lyout[:,:n]}
