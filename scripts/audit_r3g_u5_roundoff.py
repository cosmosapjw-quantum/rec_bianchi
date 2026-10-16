#!/usr/bin/env python3
"""Read-only, bounded audit of the preserved U5 first-failure trajectory."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
import resource
import sys
from decimal import Decimal, localcontext
from pathlib import Path

os.environ.update({k: "1" for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")})
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table
from full_bianchi_hyrec.trajectory.primordial_2012_helium import HyRec2012Cosmology
from full_bianchi_hyrec.trajectory.primordial_2012_helium import tm_steady_K
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import SOURCE_DLNA

START, END, EVENT = 1004, 8368, 8366
N = END - START
FAIL_PAIRS = [(2218, 8), (3017, 10), (3456, 11), (4046, 13), (4458, 12),
              (4489, 14), (4734, 11), (4835, 14), (4864, 14)]
INPUT_SHA = {
    "checkpoint_0032_stop.npz": "09e702caf0bc0ce0edb1ce629477669c55e59c7fff34cd7298d759613719528f",
    "checkpoint_0032_stop.json": "9fac62e0ae2edebb6f5ff42b0c73a7b1d4b5293cb5ac9bdd40971c9f7a5ee50d",
    "verification.json": "9453a59c6c2a19c4c3053e9b194e49cca30d736b7fee0849676f4329a41787a8",
    "native_oracle_stdout.csv": "5bc983967f1e0bd31149d9bac9c64c1201c8da2ca30bdb48905dcefdc05c2a90",
}
LIB_SHA = {"liboriginal_full_source.so": "db1e8dc1384bb5cd7d91c276174d8bb0e24402cf722e78f9febb7c591e43e27f",
           "liboriginal_history.so": "b7ca5e14b29ccb62d701ee501a4f95f788acc55e73e78a76789e5b83efcf1963"}
ZIP_SHA = "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def c_saved_arrays(path: Path) -> dict:
    """Parse the original stdout into fixed arrays; never hold millions of dicts."""
    row = np.full((N, 12), np.nan)
    v = np.full((N, 311), np.nan)
    a = np.full((N, 311), np.nan)
    l = np.full((N, 3), np.nan)
    seen = np.zeros((N, 3), dtype=np.int16)
    event = None
    end = None
    with path.open() as stream:
        for line in stream:
            f = line.rstrip("\n").split(",")
            tag = f[0]
            if tag == "U5STEP":
                j = int(f[1]); k = j - START
                if 0 <= k < N:
                    if math.isfinite(row[k, 0]): raise ValueError(f"DUPLICATE_C_STEP:{j}")
                    row[k] = [float(f[q]) for q in range(2, 14)]
                    # Thermal memory is saved separately because steady rows carry NaN.
            elif tag in ("V", "A", "L"):
                j = int(f[1]); k = j - START
                if 0 <= k < N:
                    b = int(f[2]); channel = {"V": 0, "A": 1, "L": 2}[tag]
                    target = (v, a, l)[channel]
                    if not (0 <= b < target.shape[1]) or math.isfinite(target[k, b]):
                        raise ValueError(f"DUPLICATE_OR_INVALID_C_SPECTRUM:{tag}:{j}:{b}")
                    target[k, b] = float(f[3]); seen[k, channel] += 1
            elif tag == "U5EVENT":
                event = [float(x) for x in f[1:]]
            elif tag == "U5END":
                end = f[1:]
            elif tag in ("META", "NODE", "STEP", "U4NODE", "U4STEP", "U4END", "END", "U5NODE"):
                pass
            else:
                raise ValueError(f"UNKNOWN_C_TAG:{tag}")
    if (not np.all(np.isfinite(row[:, [0,1,2,3,4,5,7,8,9]])) or
            not np.all(np.isfinite(row[-2:, [6,10,11]])) or
            not np.all(seen == (311, 311, 3))):
        raise ValueError("C_SAVED_ROWS_OR_SPECTRA_INCOMPLETE")
    if not all(np.all(np.isfinite(x)) for x in (v, a, l)):
        raise ValueError("C_NONFINITE_SPECTRUM")
    return {"row": row, "virtual": v, "average": a, "lyman": l, "event": event, "end": end}


def phi80(tau: float) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = 80
        t = Decimal.from_float(tau)
        return +(Decimal(1) - (Decimal(1) - (-t).exp()) / t)


def require_expected_failures(failures: dict[str, list[tuple[int,int]]]) -> None:
    if failures["virtual"] or failures["lyman"] or failures["average"] != FAIL_PAIRS:
        raise ValueError(f"UNEXPECTED_PHOTON_FAILURE_COORDINATES:{failures}")


def require_bound(raw_difference: float, original_tolerance: float,
                  propagated_bound: float) -> None:
    if not all(math.isfinite(v) and v>=0 for v in
               (raw_difference,original_tolerance,propagated_bound)):
        raise ValueError("NONFINITE_DIAGNOSTIC_BOUND")
    if raw_difference>original_tolerance+propagated_bound:
        raise ValueError("PHI_PROPAGATED_BUDGET")


def require_scaled_pair(actual: float, expected: float, limit: float, label: str) -> float:
    ratio=abs(actual-expected)/max(1.,abs(expected))
    if not math.isfinite(ratio) or ratio>limit:
        raise ValueError(f"{label}_PARITY")
    return ratio


def require_phi_domain(bin_index: int, tau: float) -> None:
    if not (bin_index<100 and 1e-6<tau<1e-4):
        raise ValueError("PHI_DIAGNOSTIC_DOMAIN")


def scalar_diagnostic(folder: Path, py: dict, saved_c: dict, cosmology,
                      energies: np.ndarray) -> list[dict]:
    """Re-evaluate only the nine failing bins on each owner's saved state."""
    from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
        causal_incoming_from_accepted_histories, _source_edges)
    from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
        populate_original_full_atomic, complete_original_full_atomic)
    from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
    from full_bianchi_hyrec.trajectory.primordial_2012_full_start import make_hmla_source
    from verify_r3g_full_start import FullSourceCOracle, z0

    for name, expected in LIB_SHA.items():
        if sha(folder/name) != expected: raise ValueError(f"PINNED_C_LIBRARY_SHA_MISMATCH:{name}")
    src = folder/"source_extract/HyRec"
    for name in ("Alpha_inf.dat", "R_inf.dat", "two_photon_tables.dat"):
        if not (src/name).is_file(): raise ValueError(f"C_SOURCE_TABLE_MISSING:{name}")
        member=json.loads((folder/"source_manifest.json").read_text())["source_members"]["HyRec/"+name]
        if sha(src/name)!=member: raise ValueError(f"C_SOURCE_TABLE_SHA_MISMATCH:{name}")
    table = OriginalHyRecPrimitiveRateTable.from_archive(ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
    source = make_hmla_source(cosmology, table)
    oracle = FullSourceCOracle(folder/"liboriginal_full_source.so",src,cosmology)
    lib=ctypes.CDLL(str(folder/"liboriginal_full_source.so")); pop=lib.rec_r3b_populate
    dbl=ctypes.c_double; ptr=ctypes.POINTER(dbl)
    pop.argtypes=[dbl]*6+[ptr]*14; pop.restype=None
    pointer=lambda arr: arr.ctypes.data_as(ptr)
    u=2.**-53
    output=[]
    c_v=np.zeros((311,END),dtype=float); c_l=np.zeros((3,END),dtype=float)
    c_v[:,START:END]=saved_c["virtual"].T
    c_l[:,START:END]=saved_c["lyman"].T
    # Earlier C columns 8..1003 are also in the native CSV and are parsed below.
    # The zero prefix 0..7 is usable only after the retarded-index proof.
    early_v=np.full((311,START),np.nan); early_l=np.full((3,START),np.nan)
    with (folder/"native_oracle_stdout.csv").open() as stream:
        for line in stream:
            if not line.startswith(("V,","L,")): continue
            f=line.rstrip("\n").split(","); j=int(f[1])
            if 8<=j<START:
                (early_v if f[0]=="V" else early_l)[int(f[2]),j]=float(f[3])
    if not np.all(np.isfinite(early_v[:,8:])) or not np.all(np.isfinite(early_l[:,8:])):
        raise ValueError("C_EARLY_SAVED_HISTORY_INCOMPLETE")
    c_v[:,:START]=np.nan_to_num(early_v,nan=0.0)
    c_l[:,:START]=np.nan_to_num(early_l,nan=0.0)
    srcidx,target_e,source_e=_source_edges(energies)
    for j,b in FAIL_PAIRS:
        k=j-START
        rowprev=saved_c["row"][k-1]
        c_state={"z":float(rowprev[1]),"xe":float(rowprev[3]),"tm":float(rowprev[4])}
        p_state={"z":float(py["z"][j]),"xe":float(py["xe"][j]),"tm":float(py["Tm_K"][j])}
        owned=[]
        for owner,state,hv,hl,raw in (
            ("Python",p_state,py["virtual_out"][:,:j],py["lyman_out"][:,:j],float(py["average_virtual"][b,j])),
            ("C",c_state,c_v[:,:j],c_l[:,:j],float(saved_c["average"][k,b]))):
            # All active C retarded interpolation pairs must lie in saved j>=8.
            eta_start=-math.log1p(z0(cosmology)); eta_face=-math.log1p(state["z"])
            eta_emit=eta_face-np.log(source_e/target_e)
            ix=(eta_emit-eta_start)/SOURCE_DLNA
            active=ix>=0
            if np.any(np.floor(ix[active])<8) or np.any(np.floor(ix[active])+1>j-1):
                raise ValueError(f"UNPROVEN_C_CAUSAL_PREFIX:{j}:{owner}")
            inc=causal_incoming_from_accepted_histories(
                energies_eV=energies,virtual_history=hv,lyman_history=hl,
                z_start=z0(cosmology),iz=j,z_face=state["z"],dlna=SOURCE_DLNA,shear_q=0.)
            incoming=inc.virtual_distortion[0]
            ly=inc.lya_lyb_incoming_distortion[0]
            tr=cosmology.T0_K*(1+state["z"])
            tm=math.nextafter(state["tm"],0.) if state["tm"]==tr else state["tm"]
            py_snap=populate_original_full_atomic(source,z=state["z"],xHII=state["xe"],
                xe=state["xe"],Tm_K=tm,incoming_virtual=incoming,incoming_lyman=ly)
            py_out=complete_original_full_atomic(py_snap)
            # Exactly one original C FULL and one original C populate per own input.
            c_full=oracle(j,state["z"],state["xe"],0.,tm,hv,hl)
            if owner=="Python":
                raw_channels=(py["virtual_out"][:,j],py["average_virtual"][:,j],py["lyman_out"][:,j])
            else:
                raw_channels=(saved_c["virtual"][k],saved_c["average"][k],saved_c["lyman"][k])
            tr_ev=8.617343e-5*tr
            bbv=1/np.expm1(energies/tr_ev)
            bbl=1/np.expm1(np.array((10.198714553953742,12.087365397278509,12.748393192442178))/tr_ev)
            for name,own,candidate,bb in zip(("virtual","average","lyman"),raw_channels,
                (c_full["virtual"],c_full["average"],c_full["lyman"]),(bbv,bbv,bbl)):
                all_tol=1e-7*np.maximum(np.abs(own),np.abs(candidate))+1e-10*bb
                if np.any(np.abs(own-candidate)>all_tol):
                    raise ValueError(f"C_FULL_OWN_INPUT_625_RECONSTRUCTION:{j}:{owner}:{name}")
            c_values=np.array([c_full["virtual"][b],c_full["average"][b],*c_full["lyman"]])
            fbb=1/math.expm1(float(energies[b])/(8.617343e-5*tr))
            tol=1e-7*max(abs(raw),abs(c_values[1]))+1e-10*fbb
            if abs(raw-c_values[1])>tol:
                raise ValueError(f"C_FULL_OWN_INPUT_RECONSTRUCTION:{j}:{owner}")
            # Check the Python snapshot against its own stored bin as well.
            if owner=="Python" and abs(raw-float(py_out.average_virtual[b]))>tol:
                raise ValueError(f"PYTHON_OWN_INPUT_RECONSTRUCTION:{j}")
            arrays=[np.empty(shape,dtype=float) for shape in ((2,2),(2,311),(2,311),(3,311),(2,),(311,),(311,),(2,),(2,),(2,),(2,),(311,))]
            # 14 pointer outputs: Trr, Trv, Tvr, Tvv, sr, sv, Dtau,
            # Alpha, DAlpha, Beta, xr, xv.  Two final extra arrays are not present.
            nH=cosmology.nH0_m3*1.e-6*(1+state["z"])**3
            tr_ev=8.617343e-5*tr; tm_ev=8.617343e-5*tm
            old=os.getcwd(); os.chdir(src)
            try:
                pop(state["xe"],state["xe"],nH,cosmology.hubble_s(state["z"]),tm_ev,tr_ev,
                    pointer(np.ascontiguousarray(incoming)),pointer(np.ascontiguousarray(ly)),
                    *[pointer(arr) for arr in arrays])
            finally: os.chdir(old)
            if owner=="Python":
                tau=float(py_snap.Dtau[b]); rv=py_snap.Trv; vr=py_snap.Tvr
                real=py_snap.instantaneous_schur_solution()[0]
            else:
                tau=float(arrays[6][b]); rv=arrays[1]; vr=arrays[2]; real=arrays[10]
            x1s=1-state["xe"]
            gamma=-float(rv[0,b]+rv[1,b])
            f=float(incoming[b])
            q=-(real[0]*vr[0,b]+real[1]*vr[1,b])/(x1s*gamma)-f
            require_phi_domain(b,tau)
            p64=1-(1-math.exp(-tau))/tau
            p80=phi80(tau)
            with localcontext() as ctx:
                ctx.prec=80
                a80=Decimal.from_float(f)+p80*Decimal.from_float(q)
            a64=f+p64*q
            bphi=u/tau+4*u
            if abs(p64-float(p80))>bphi: raise ValueError(f"PHI_ERROR_BOUND:{j}:{owner}")
            if abs(a64-raw)>tol: raise ValueError(f"DIAGONAL_IDENTITY_RECONSTRUCTION:{j}:{owner}")
            owned.append({"owner":owner,"tau":tau,"phi64":p64,"phi80":str(p80),
                          "incoming":f,"Q":q,"A64":a64,"A80":str(a80),"raw":raw,
                          "raw_reconstruction_absolute":abs(a64-raw),"phi_bound":bphi,
                          "retarded_min_active_index":int(np.min(np.floor(ix[active]))),
                          "c_full_own_average_ratio":abs(raw-c_values[1])/tol})
        p,c=owned
        tol=1e-7*max(abs(p["raw"]),abs(c["raw"]))+1e-10*fbb
        stable=abs(Decimal(p["A80"])-Decimal(c["A80"]))
        if stable>Decimal.from_float(tol): raise ValueError(f"PHI80_STABLE_REMAINDER:{j}:{b}")
        bound=(abs(p["Q"])*p["phi_bound"]+abs(c["Q"])*c["phi_bound"]+
               p["raw_reconstruction_absolute"]+c["raw_reconstruction_absolute"]+
               32*u*(abs(p["incoming"])+abs(p["phi64"]*p["Q"])+
                     abs(c["incoming"])+abs(c["phi64"]*c["Q"])))
        require_bound(abs(p["raw"]-c["raw"]),tol,bound)
        output.append({"j":j,"bin":b,"original_tolerance":tol,"stable_remainder_absolute":str(stable),
                       "propagated_bound":bound,"raw_absolute":abs(p["raw"]-c["raw"]),"owners":owned})
    return output


def audit(folder: Path) -> dict:
    folder = folder.resolve()
    for name, expected in INPUT_SHA.items():
        if sha(folder / name) != expected: raise ValueError(f"IMMUTABLE_INPUT_SHA_MISMATCH:{name}")
    if sha(ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip") != ZIP_SHA:
        raise ValueError("ORIGINAL_HYREC_ZIP_SHA_MISMATCH")
    source_manifest=json.loads((folder/"source_manifest.json").read_text())
    if source_manifest.get("source_zip_sha256")!=ZIP_SHA:
        raise ValueError("SAVED_SOURCE_MANIFEST_ZIP_MISMATCH")
    for name in ("hydrogen.c","helium.c","history.c","hyrec_params.h"):
        if source_manifest["source_c"][name] != source_manifest["source_members"]["HyRec/"+name]:
            raise ValueError(f"SAVED_SOURCE_MEMBER_MISMATCH:{name}")
    meta = json.loads((folder / "checkpoint_0032_stop.json").read_text())
    original = json.loads((folder / "verification.json").read_text())
    if (meta["phase"], meta["accepted_extra"], meta["event_j"], meta["branch_steps_after_event"]) != ("STOP", N, EVENT, 2):
        raise ValueError("SAVED_STOP_SEMANTICS_MISMATCH")
    if original.get("status") != "FAIL" or "row=2218 channel=average bin=8" not in original["first_failure"]["message"]:
        raise ValueError("ORIGINAL_VERIFIER_FAILURE_NOT_PRESERVED")
    with np.load(folder / "checkpoint_0032_stop.npz", allow_pickle=False) as handle:
        py = {key: np.array(handle[key], copy=True) for key in handle.files}
    if py["xe"].shape != (END+1,) or py["average_virtual"].shape != (311, END):
        raise ValueError("SAVED_PYTHON_SHAPE_MISMATCH")
    c = c_saved_arrays(folder / "native_oracle_stdout.csv")
    r = c["row"]
    j = np.arange(START, END)
    iz = py["global_iz"][START+1:END+1]
    if not np.array_equal(iz, r[:, 0].astype(np.int64)) or not np.all(~py["post_saha"][START:END+1]):
        raise ValueError("INDEX_OR_BRANCH_MISMATCH")
    state = {}
    for name, col, floor, limit in (("xH1s", 2, 1e-8, 5e-9), ("xHII", 3, 1e-8, 5e-9),
                                    ("xe", 3, 1e-8, 5e-9), ("Tm_K", 4, 1., 5e-10)):
        err = np.abs(py[name][START+1:END+1]-r[:, col])/np.maximum(np.abs(r[:, col]),floor)
        state[name] = float(np.max(err))
        if not np.all(np.isfinite(err)) or state[name] > limit: raise ValueError(f"STATE_PARITY:{name}")
    if not np.array_equal(py["xHeII"][START:END+1], np.zeros(N+1)):
        raise ValueError("HEII_NOT_ZERO")
    redshift_max = float(np.max(np.abs(py["z"][START+1:END+1]-r[:, 1])))
    if redshift_max > 2e-12: raise ValueError("REDSHIFT_PARITY")
    h_rhs = np.abs(py["hydrogen_rhs_dln_a"][START:END]-r[:,5])/np.maximum(1.,np.abs(r[:,5]))
    h_prev = np.abs(py["hydrogen_rhs_dln_a"][START:END]-r[:,8])/np.maximum(1.,np.abs(r[:,8]))
    h_prev2 = np.abs(py["hydrogen_rhs_dln_a"][START-1:END-1]-r[:,9])/np.maximum(1.,np.abs(r[:,9]))
    if np.max(h_rhs)>2e-7 or np.max(h_prev)>2e-8 or np.max(h_prev2)>2e-8:
        raise ValueError("HYDROGEN_RHS_OR_MEMORY_PARITY")
    # Scalar mutation guard shares the same fixed limits as the vector audit.
    require_scaled_pair(float(py["hydrogen_rhs_dln_a"][START]),float(r[0,5]),2e-7,"HYDROGEN_RHS")
    require_scaled_pair(float(py["hydrogen_rhs_dln_a"][START]),float(r[0,8]),2e-8,"HYDROGEN_MEMORY")
    h_recurrence = np.abs(py["xe"][START+1:END+1] - (py["xe"][START:END] + SOURCE_DLNA *
        (1.25*py["hydrogen_rhs_dln_a"][START:END]-.25*py["hydrogen_rhs_dln_a"][START-2:END-2])))
    if np.max(h_recurrence)>2e-15: raise ValueError("HYDROGEN_STEP_RECURRENCE")
    if c["event"] is None or int(c["event"][0]) != EVENT or c["end"] is None or c["end"][0] != "THERMAL_EVENT_TWO_STEPS_COMPLETE":
        raise ValueError("C_EVENT_OR_END_MISMATCH")
    if np.any(r[:EVENT-START,7] != 0) or np.any(r[EVENT-START:,7] != 1):
        raise ValueError("C_THERMAL_BRANCH_SEQUENCE")
    cosmology = HyRec2012Cosmology()
    delta = 1-py["Tm_K"][START:END+1]/(cosmology.T0_K*(1+py["z"][START:END+1]))
    if not (np.all(delta[:EVENT-START] < 5e-4) and delta[EVENT-START] >= 5e-4):
        raise ValueError("THERMAL_SWITCH_THRESHOLD")
    t_seeds = ((py["Tm_K"][EVENT-1]-py["Tm_K"][EVENT-3])/(2*SOURCE_DLNA),
               (py["Tm_K"][EVENT]-py["Tm_K"][EVENT-2])/(2*SOURCE_DLNA))
    if any(abs(x-y)/max(1,abs(y)) > 2e-8 for x,y in zip(t_seeds,c["event"][2:4])):
        raise ValueError("THERMAL_SEED_PARITY")
    if any(abs(x-y)/max(1,abs(y)) > 2e-8 for x,y in zip(t_seeds,(meta["thermal_seeds"]["prev2"],meta["thermal_seeds"]["prev"]))):
        raise ValueError("PYTHON_THERMAL_SEED_INCONSISTENT")
    t_rhs = np.abs(py["thermal_rhs_dln_a"][EVENT:END]-r[EVENT-START:,6])/np.maximum(1,np.abs(r[EVENT-START:,6]))
    if np.max(t_rhs)>2e-8: raise ValueError("THERMAL_RHS_PARITY")
    for step in range(START,EVENT):
        expected=tm_steady_K(cosmology,float(py["xe"][step+1]),float(py["z"][step+1]),
                             cosmology.hubble_s(float(py["z"][step+1])))
        if abs(float(py["Tm_K"][step+1])-expected)>2e-12:
            raise ValueError(f"PRE_EVENT_STEADY_TM:{step}")
    prev2=t_seeds[0]
    for step in range(EVENT,END):
        k=step-START
        g=float(py["thermal_rhs_dln_a"][step])
        if abs(float(py["thermal_prev_after"][step])-r[k,10])/max(1,abs(r[k,10]))>2e-8:
            raise ValueError(f"THERMAL_MEMORY_PREV:{step}")
        if abs(float(py["thermal_prev2_after"][step])-r[k,11])/max(1,abs(r[k,11]))>2e-8:
            raise ValueError(f"THERMAL_MEMORY_PREV2:{step}")
        candidate=py["Tm_K"][step]+SOURCE_DLNA*(1.25*py["thermal_rhs_dln_a"][step]-.25*prev2)
        if abs(py["Tm_K"][step+1]-candidate)>2e-12: raise ValueError(f"THERMAL_STEP_RECURRENCE:{step}")
        prev2=t_seeds[1] if step==EVENT else py["thermal_rhs_dln_a"][step-1]
    table = _canonical_twophoton_table(ROOT / "archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip")
    tr_ev = 8.617343e-5*cosmology.T0_K*(1+py["z"][START:END])
    energies={"virtual":table.energy_eV,"average":table.energy_eV,
              "lyman":np.array((10.198714553953742,12.087365397278509,12.748393192442178))}
    ratios={}; failures={}; counts={}
    for channel in ("virtual","average","lyman"):
        parr=py[("virtual_out" if channel=="virtual" else "average_virtual" if channel=="average" else "lyman_out")][:,START:END].T
        carr=c[channel]
        bb=1/np.expm1(energies[channel][None,:]/tr_ev[:,None])
        tol=1e-7*np.maximum(np.abs(parr),np.abs(carr))+1e-10*bb
        ratio=np.abs(parr-carr)/tol
        if not np.all(np.isfinite(ratio)): raise ValueError(f"NONFINITE_PHOTON_RATIO:{channel}")
        ratios[channel]=float(np.max(ratio)); counts[channel]=int(ratio.size)
        loc=np.argwhere(ratio>1)
        failures[channel]=[(int(START+k),int(b)) for k,b in loc]
    require_expected_failures(failures)
    details=scalar_diagnostic(folder,py,c,cosmology,table.energy_eV)
    return {"scope":"R3G-U5-ROUNDOFF-AUDIT-001","original_verification_status":"FAIL",
        "original_average_gate":"HOLD_ORIGINAL_TOLERANCE_NOT_MET",
        "state_causal_thermal_gate":"PASS","cancellation_diagnostic":"NUMERICALLY_CHECKED",
        "full_primordial_history":"NOT_ESTABLISHED","temporal_refinement":"NOT_RUN",
        "rei_activation":False,"status":"SCOPED_STATE_CAUSAL_THERMAL_PASS_AVERAGE_PHOTON_HOLD",
        "source_zip_sha256":ZIP_SHA,"saved_input_sha256":INPUT_SHA,
        "saved_source_manifest_sha256":sha(folder/"source_manifest.json"),
        "saved_c_library_sha256":LIB_SHA,
        "audit_script_sha256":sha(Path(__file__)),
        "accepted_rows":N,"first_j":START,"last_j":END-1,"event_j":EVENT,
        "state_max_scaled":state,"z_max_absolute":redshift_max,
        "hydrogen_rhs_max_scaled":float(np.max(h_rhs)),
        "hydrogen_memory_max_scaled":max(float(np.max(h_prev)),float(np.max(h_prev2))),
        "hydrogen_recurrence_max_absolute":float(np.max(h_recurrence)),
        "thermal_rhs_max_scaled":float(np.max(t_rhs)),
        "thermal_seeds":list(t_seeds),"photon_count":counts,
        "photon_max_tolerance_ratio":ratios,"photon_failure_pairs":failures,
        "matrix_residual_max":float(np.nanmax(py["matrix_residual"][START:END])),
        "nine_pair_diagnostic":details,
        "claim_ceiling":"q=0 original HyRec bounded saved U5 trajectory; nine average-spectrum failures remain original FAIL"}


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--folder",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    if a.report.exists(): raise SystemExit("REPORT_CREATE_ONLY")
    os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    resource.setrlimit(resource.RLIMIT_CPU,(110,110))
    report=audit(a.folder)
    with a.report.open("x") as out:
        json.dump(report,out,sort_keys=True,indent=2); out.write("\n")
    print(json.dumps(report,sort_keys=True))
    return 0

if __name__ == "__main__": raise SystemExit(main())
