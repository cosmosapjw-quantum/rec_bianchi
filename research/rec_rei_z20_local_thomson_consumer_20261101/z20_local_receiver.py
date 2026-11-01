#!/usr/bin/env python3
"""Read-only local (one-sided z=20) Thomson clock/opacity receiver witness.

This is NOT a native REI line-of-sight integrator. No Bianchi primordial
history, no REI IVP, no z>20 shear extrapolation and no canonical node claim.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import sys
from pathlib import Path

SHEAR_REL = "research/rec_r3c_rei_bridge_20261015/SHEAR_BACK_EXTRAPOLATION.json"
SHEAR_BLOB_SHA1 = "7a5b76f618ae47b500f56a8084c2a15829ba184e"
SOURCE_PARENT_HEAD = "ba283bf2262396b9a5ac14867caffd78f8469b99"
REI_SCENARIO_SHA256 = "07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696"
Z_BOUNDARY = 20.0
MU_VALUES = (0.0, 0.5, 1.0)
Q_VALUES = (-0.01, -0.005, 0.0, 0.005, 0.01)


def blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def lrs_ray_redshift_ratio(
    mean_redshift: float,
    reference_redshift: float,
    photon_direction_ref: tuple[float, float, float],
    beta_at_ref: tuple[float, float, float],
    beta_at_event: tuple[float, float, float],
) -> float:
    """Exact Bianchi-I geometric-optics E(event)/E(ref) from constant p_i.

    Valid for supplied metric histories, but NO actual high-z Bianchi beta_i
    history is present or inferred here. Not used for physical output rows.
    """
    if not (mean_redshift >= reference_redshift >= 0):
        raise ValueError("invalid ordered mean redshifts")
    if any(not math.isfinite(t) for t in
           (*photon_direction_ref, *beta_at_ref, *beta_at_event)):
        raise ValueError("invalid direction/beta")
    if abs(sum(v*v for v in photon_direction_ref) - 1) > 1e-12:
        raise ValueError("photon reference direction is not unit normalized")
    if abs(sum(beta_at_ref)) > 1e-12 or abs(sum(beta_at_event)) > 1e-12:
        raise ValueError("trace-free Bianchi beta_i required")
    return (1+mean_redshift)/(1+reference_redshift) * math.sqrt(sum(
        photon_direction_ref[i]**2 *
        math.exp(2*(beta_at_ref[i]-beta_at_event[i])) for i in range(3)
    ))


def read_z20_shear_cases(repo: Path) -> list[dict]:
    payload = (repo/SHEAR_REL).read_bytes()
    if blob_sha1(payload) != SHEAR_BLOB_SHA1:
        raise ValueError("original original-REI shear source blob identity drift")
    obj = json.loads(payload)
    if (obj["schema"] != "rec.rei.formal_shear_backextrapolation.v1"
        or obj["accepted_physical_zbar_range"] != [4.0,20.0]
        or obj["extrapolated_to_primordial_epoch"] !=
        "COUNTERFACTUAL_NOT_PHYSICALLY_ADMITTED"):
        raise ValueError("source shear authority/domain drift")
    rows = [r for r in obj["rows"] if
            r["zbar_formal"] == Z_BOUNDARY and r["within_REI_physical_domain"]]
    cases = sorted(rows, key=lambda r: r["q_ref"])
    if len(cases) != len(Q_VALUES):
        raise ValueError("missing source-authentic z20 shear cases")
    for case, q in zip(cases, Q_VALUES):
        if case["q_ref"] != q or not case["directional_monotone_redshift"]:
            raise ValueError("z20 q source case drift")
        if abs(case["ratio_shear_squared_to_hflrw_squared"]-q*q)>1e-13:
            raise ValueError("z20 shear/H_FLRW source identity drift")
        sH = q / math.sqrt(1+q*q)
        if abs(case["signed_sigma_over_H"]-sH)>1e-13:
            raise ValueError("z20 dimensionless shear identity drift")
        if abs(case["H_parallel_over_H"]-(1+2*sH))>1e-13:
            raise ValueError("z20 H_parallel geometrical identity drift")
        if abs(case["H_perp_over_H"]-(1-sH))>1e-13:
            raise ValueError("z20 H_perp geometrical identity drift")
    return cases


def local_clock_opacity(
    gamma_thomson_s_inv: float,
    H_flrw_s_inv: float,
    q_ref: float,
    mu_parallel: float,
    source_case: dict,
) -> dict:
    """At z20 ONLY: Hbar=sqrt(H_F^2+s^2), s=q H_F; Hray=sum_i n_i² H_i.

    Units: gamma & H are s^-1, dτ/d ln(1+z_ray) dimensionless.
    The forward-ln(a) derivative of the lookback tau(20,z) is NEGATIVE.
    """
    if not all(math.isfinite(x) for x in
               (gamma_thomson_s_inv, H_flrw_s_inv, q_ref, mu_parallel)):
        raise ValueError("non-finite local opacity input")
    if gamma_thomson_s_inv <= 0 or H_flrw_s_inv <= 0:
        raise ValueError("nonpositive physical rate or H")
    if not 0 <= mu_parallel <= 1:
        raise ValueError("mu must represent a physical direction cosine magnitude")
    if source_case["q_ref"] != q_ref or source_case["zbar_formal"] != Z_BOUNDARY:
        raise ValueError("source q/redshift mismatch: no extrapolation")
    Hbar = H_flrw_s_inv*math.sqrt(1+q_ref*q_ref)
    Hperp = Hbar*source_case["H_perp_over_H"]
    Hparallel = Hbar*source_case["H_parallel_over_H"]
    Hray = (1-mu_parallel*mu_parallel)*Hperp + mu_parallel*mu_parallel*Hparallel
    if min(Hbar,Hperp,Hparallel,Hray) <= 0:
        raise ValueError("nonmonotone directional redshift: cannot use local clock")
    return {
        "Hbar_s_inv": Hbar,
        "Hray_s_inv": Hray,
        "mean_clock_dtaudln1pz": gamma_thomson_s_inv/Hbar,
        "forward_lna_dtaudln_a": -gamma_thomson_s_inv/Hbar,
        "ray_clock_dtaudln1pz_ray": gamma_thomson_s_inv/Hray,
        "ray_over_mean_clock_ratio": Hbar/Hray,
    }


def compute(repo: Path, out: Path) -> dict:
    # Import exact source-locked original HyRec reader from unchanged parent PR187.
    sys.path.insert(0,str(repo/"research/rec_rei_hyrec_primordial_screen_20261101"))
    from original_hyrec_screen import (prepare,hubble,C_M_S,SIGMA_T_M2,
                                      NATIVE_C_STDOUT_SHA256)
    boundary, history, prepared = prepare(repo)  # includes 8001 native C row check
    if (boundary["rei_scenario_sha256"] != REI_SCENARIO_SHA256
        or history[0]["zbar"] != 20):
        raise ValueError("real original REI boundary identity drift")
    cases = read_z20_shear_cases(repo)
    donor_ne = history[0]["ne_m3"]
    original_ne = boundary["published_rei_approximate_initial"]["electron_density_m3"]
    if abs(donor_ne/boundary["hyrec_full_conditional_projection"]
           ["electron_density_m3"]-1)>3e-14:
        raise ValueError("donor conditional recipient n_e mismatch")
    HF = hubble(Z_BOUNDARY)
    header=["zbar","q_ref","mu_parallel","ne_owner","ne_m3","gamma_T_s_inv",
            "H_F_s_inv","Hbar_s_inv","Hray_s_inv","d_tau_d_abs_ln_a",
            "signed_d_tau_d_ln_a","d_tau_d_ln1p_zray",
            "ray_to_mean_opacity_ratio","source_validity"]
    rows=[]
    for case in cases:
        q = case["q_ref"]
        for mu in MU_VALUES:
            for owner,ne in (("REC_NATIVE_HYREC_CONDITIONAL",donor_ne),
                             ("REI_ORIGINAL_APPROXIMATE_IC",original_ne)):
                gam = C_M_S*SIGMA_T_M2*ne
                v = local_clock_opacity(gam,HF,q,mu,case)
                rows.append([20,q,mu,owner,ne,gam,HF,
                             v["Hbar_s_inv"],v["Hray_s_inv"],
                             v["mean_clock_dtaudln1pz"],
                             v["forward_lna_dtaudln_a"],
                             v["ray_clock_dtaudln1pz_ray"],
                             v["ray_over_mean_clock_ratio"],
                             "LOCAL_Z20_ONLY_NOT_HIGHZ_BIANCHI_HISTORY"])
    q0 = next(c for c in cases if c["q_ref"]==0)
    source_q0 = local_clock_opacity(C_M_S*SIGMA_T_M2*donor_ne,HF,0,0,q0)
    source_parity = abs(source_q0["mean_clock_dtaudln1pz"] /
                        history[0]["dtaudlna"] - 1)
    donor_over_rei = donor_ne/original_ne-1
    if source_parity > 2e-12:
        raise ValueError("q0 original optical-depth clock parity failed")
    if abs(donor_over_rei-boundary["donor_minus_baseline"]
           ["optical_depth_rate_fractional"])>2e-13:
        raise ValueError("donor/recipient boundary mismatch")
    out.mkdir(parents=True,exist_ok=True)
    path=out/"REC_REI_Z20_LOCAL_RAY_CLOCK_OPACITY.csv"
    with path.open("w",encoding="ascii",newline="") as f:
        w=csv.writer(f,lineterminator="\n")
        w.writerow(header)
        for row in rows:
            w.writerow([format(v,".17g") if isinstance(v,float) else v for v in row])
    payload={
        "schema":"rec.rei.z20_local_thomson_ray_clock.v1",
        "parent_head":SOURCE_PARENT_HEAD,
        "original_HyRec_C_stdout_sha256":NATIVE_C_STDOUT_SHA256,
        "original_shear_git_blob_sha1":SHEAR_BLOB_SHA1,
        "original_shear_domain":[4,20],
        "REI_AXBI_scenario_sha256":REI_SCENARIO_SHA256,
        "source_primordial_FLRW_rows_reused":len(history),
        "new_source_evolved_states":0,
        "new_local_operator_rows":len(rows),
        "zbar_boundary":20,
        "z20_original_REC_donor_ne_m3":donor_ne,
        "z20_original_REI_baseline_ne_m3":original_ne,
        "z20_donor_over_baseline_differential_opacity_fraction":donor_over_rei,
        "z20_q0_source_rate_parity_relative":source_parity,
        "z20_H_FLRW_s_inv":HF,
        "negative_signed_forward_lna_derivative":True,
        "local_Bianchi_ray_monotonic":all(c["directional_monotone_redshift"] for c in cases),
        "high_z_Bianchi_shear_extension":"FORBIDDEN_SOURCE_OUT_OF_DOMAIN",
        "actual_native_REI_Thomson_CMB_LoS_receiver":"NOT_IDENTIFIED_IN_TRACKED_REI_PYTHON_SOURCE",
        "full_observer_z0_optical_depth":"NOT_COMPUTED_NO_ADMITTED_LOWER_SEGMENT",
        "F05_original_acceptance":"BLOCKED_UNCHANGED",
        "REI_canonical":"28/88",
        "REI_working":"33/88",
        "REI_physical_fast":"4/7",
        "REC_H5":"0/313",
        "canonical_delta":0,
        "source_ownership":"REC_READ_ONLY_LOCAL_OPERATOR",
        "source_adoption":"NOT_ADOPTED",
        "production":"HOLD",
        "merge":False,
        "new_native_REI_IVPs":0,
        "new_native_HyRec_C_executions":0,
        "csv_sha256":hashlib.sha256(path.read_bytes()).hexdigest()
    }
    (out/"SCIENCE_STATUS.json").write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n",
                                           encoding="ascii")
    return payload


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    x=p.parse_args()
    print(json.dumps(compute(x.repo.resolve(),x.out.resolve()),sort_keys=True))
