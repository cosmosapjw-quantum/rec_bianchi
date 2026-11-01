#!/usr/bin/env python3
"""Original HyRec C no-UV residual-electron Thomson baseline, NOT real REI IGM.

Source: actual saved original native C H+He output, PR187 immutable reader.
Model: native q0 FLRW primordial history with astrophysical ionization DISABLED.
F08 S0 is a different electron, clock and photon owner and cannot be spliced.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import sys
from pathlib import Path

ROOT_IN_REPO = "research/rec_rei_native_hyrec_no_uv_floor_20261101"
PARENT = "research/rec_rei_hyrec_primordial_screen_20261101"
SCENARIO = ROOT_IN_REPO + "/REI_F08_S0_IMMUTABLE_SCENARIO.json"
S0_SHA256 = "c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1"
PARENT_OUTPUT_SHA256 = "879e51d67ab9a55be81a019a6bf08487ba425ab3bf97f30bc01cdda2825555a0"
SOURCE_PAIR_ID = "0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8"


def _parent(repo: Path):
    sys.path.insert(0, str(repo / PARENT))
    import original_hyrec_screen as src
    return src


def real_lowz_C(repo: Path, src, source_info: dict,
                highz_rows: list[dict[str,float]]) -> list[tuple[int, float, float]]:
    gz = (repo/src.NATIVE_C_GZIP_REL).read_bytes()
    if hashlib.sha256(gz).hexdigest() != src.NATIVE_C_GZIP_SHA256:
        raise ValueError("original native HyRec gzip SHA256 mismatch")
    payload = gzip.decompress(gz)
    if hashlib.sha256(payload).hexdigest() != src.NATIVE_C_STDOUT_SHA256:
        raise ValueError("original native HyRec stdout SHA256 mismatch")
    lines = payload.decode("ascii").splitlines()
    if len(lines) != 8001:
        raise ValueError("native C output must have 8001 original rows")
    seen = []
    tcmb0 = float(source_info["source_cosmology"]["T0_K"])
    for line in lines:
        part = line.split()
        if len(part) != 3:
            raise ValueError("native C stdout no longer has three columns")
        z, xe, ratio = map(float, part)
        if not all(math.isfinite(v) for v in (z,xe,ratio)):
            raise ValueError("nonfinite original native C source")
        if 0 <= z <= 20:
            if not (xe > 0 and ratio > 0 and int(z) == z):
                raise ValueError("invalid original native low-z source value")
            seen.append((int(z),xe,tcmb0*(1+z)*ratio))
    seen.reverse()
    if [r[0] for r in seen] != list(range(21)):
        raise ValueError("original native C low-z grid missing")
    if (seen[-1][1] != highz_rows[0]["xe_per_H"]
        or abs(seen[-1][2] / highz_rows[0]["Tgas_K"] - 1) > 3e-13):
        raise ValueError("original C z20 overlap source mismatch")
    return seen


def source_equal_F08(repo: Path, src, boundary: dict, highz: list[dict]) -> dict:
    raw = (repo/SCENARIO).read_bytes()
    if hashlib.sha256(raw).hexdigest() != S0_SHA256:
        raise ValueError("original REI F08 S0 scenario source identity mismatch")
    s=json.loads(raw)
    background=s["background"]
    initial=s["initial_state"]
    time=s["time"]
    source=s["source"]
    if (s["scenario_id"] != "REI_S0_PRIMARY_ONLY_CASE_A_BIANCHI_I_V1"
        or background["redshift"]["reference_z0"]!=10.0
        or initial["nH0_cm3"]!=0.0001
        or initial["fractions"]["HII"]!=0.9
        or initial["temperature_K"]!=50000.0
        or time["t_end_s"]!=1e13
        or source["energy_at_birth_ev"]!=13.7
        or initial["photon_number_per_H"]!=0.05):
        raise ValueError("REI F08 S0 immutable scenario semantics changed")
    f=initial["fractions"]
    x_s0=f["HII"]+initial["fHe"]*(f["HeII"]+2*f["HeIII"])
    ne_s0_m3=1e6*initial["nH0_cm3"]*x_s0
    ne_rec_m3=highz[0]["ne_m3"]
    h_s0=background["H_mean_per_s"]
    h_rec=src.hubble(20)
    # Independent physical-source equivalence requires much more than both
    # files calling their abscissa a redshift. Test actual dimensional states.
    same_initial_material = all((math.isclose(a,b,rel_tol=1e-12,abs_tol=0.)
        for a,b in ((ne_s0_m3,ne_rec_m3),
                    (h_s0,h_rec),
                    (x_s0,highz[0]["xe_per_H"]),
                    (initial["temperature_K"],highz[0]["Tgas_K"]))))
    same_initial_photon_owner=(initial["photon_number_per_H"]==0.0)
    background_is_fitted_cosmology=(background["redshift"]["interpretation"]
        != "Prescribed background label only; no Friedmann fit or cosmic initial history")
    valid_source_splice=bool(same_initial_material and same_initial_photon_owner
                             and background_is_fitted_cosmology)
    if valid_source_splice:
        raise ValueError("SOURCE_MATCH_GATE_LOGIC_REQUIRES_OWNER_INDEPENDENT_ADMISSION")
    summary={
        "F08_S0_source_pair_id":SOURCE_PAIR_ID,
        "source_equal_material_initial_conditions":same_initial_material,
        "source_equal_initial_ionizing_photons":same_initial_photon_owner,
        "F08_has_physical_Friedmann_clock":background_is_fitted_cosmology,
        "F08_S0_scenario_sha256":S0_SHA256,
        "F08_reference_z0":10.,
        "F08_reference_label_is_observed_cosmological_z":False,
        "F08_S0_xe_per_H_initial":x_s0,
        "F08_S0_ne_initial_m3":ne_s0_m3,
        "F08_S0_H_mean_per_s":h_s0,
        "F08_S0_Tgas_initial_K":initial["temperature_K"],
        "F08_S0_ionizing_photons_per_H_initial":initial["photon_number_per_H"],
        "REC_HyRec_ne_z20_m3":ne_rec_m3,
        "REC_HyRec_H_mean_z20_s_inv":h_rec,
        "REC_HyRec_Tgas_z20_K":highz[0]["Tgas_K"],
        "F08_to_REC_ne_ratio":ne_s0_m3/ne_rec_m3,
        "F08_to_REC_H_ratio":h_s0/h_rec,
        "F08_to_REC_T_ratio":initial["temperature_K"]/highz[0]["Tgas_K"],
        "F08_to_REC_xe_ratio":x_s0/highz[0]["xe_per_H"],
        "original_F08_same_source_and_clock_as_REC":False,
        "F08_OBSERVER_SKY_DIRECT_SPLICE":"REJECTED_PHYSICAL_SOURCE_MISMATCH"
    }
    return summary


def compute(repo: Path, out: Path) -> dict:
    src=_parent(repo)
    info, high, q=src.prepare(repo)
    low=real_lowz_C(repo,src,info,high)
    incompatible=source_equal_F08(repo,src,info,high)
    if not q["opacity_parity_max_relative"]<=2e-12:
        raise ValueError("source high-z thomson rate not reproduced")

    nH20=q["z20_nH_rei_m3"]
    def rate(z: int,xe: float):
        nH=nH20*((1+z)/21.0)**3
        ne=nH*xe
        return src.C_M_S*src.SIGMA_T_M2*ne/((1+z)*src.hubble(z))
    f_lo=[rate(z,xe) for z,xe,T in low]
    fx_lo=[rate(z,low[-1][1]) for z,xe,T in low]
    if abs(f_lo[-1]/q["kappa"][0]-1)>3e-13:
        raise ValueError("original source native z20 Thomson derivative not continuous")
    # Disjoint Simpson/3-8 segments; no accidental new Simpson panel crossing z20.
    tau_lo=src.cumulative_simpson_38(f_lo)
    tau_frozen=src.cumulative_simpson_38(fx_lo)
    tau_trap=src.cumulative_trapezoid(f_lo)
    tau0=tau_lo[-1]
    transmission=math.exp(-tau0)
    if tau0<=0 or not 0<transmission<1:
        raise ValueError("nonphysical noUV source scattering optical depth")

    header=("zbar","native_C_xe_per_H","native_C_Tgas_K","ne_REI_norm_m3",
            "H_FLRW_s_inv","GammaT_s_inv","d_tau_dz","tau_noUV_0_to_z",
            "transmission_noUV_0_to_z","visibility_noUV_per_z",
            "upstream_REC_tau_20_to_z","source_segment")
    newrows=[]
    g20_parity=0.
    for z,xe,T in low:
        ne=nH20*((1+z)/21.0)**3*xe
        f=f_lo[z]
        t=tau_lo[z]
        newrows.append([z,xe,T,ne,src.hubble(z),src.C_M_S*src.SIGMA_T_M2*ne,
                        f,t,math.exp(-t),f*math.exp(-t),0.,
                        "HYREC_C_NO_ASTRO_0_TO_20"])
    for i,row in enumerate(high[1:],1):
        z=int(row["zbar"])
        if z!=20+i:
            raise ValueError("highz original z source grid discontinuity")
        t=tau0+q["tau"][i]
        f=q["kappa"][i]
        survival=math.exp(-t)
        vis=f*survival
        original_g=q["visibility"][i]
        g20_parity=max(g20_parity,abs(vis-transmission*original_g))
        newrows.append([z,row["xe_per_H"],row["Tgas_K"],row["ne_m3"],
                        src.hubble(z),src.C_M_S*src.SIGMA_T_M2*row["ne_m3"],
                        f,t,survival,vis,q["tau"][i],
                        "HYREC_C_ORIGINAL_PR187_20_TO_1600"])
    if len(newrows)!=1601 or [x[0] for x in newrows]!=list(range(1601)):
        raise ValueError("duplicate or missing interval at source z20")
    highz_tau_parity=max(abs(newrows[20+i][7]-(tau0+q["tau"][i]))
                         for i in range(len(high)))
    if highz_tau_parity > 2e-13:
        raise ValueError("source cumulative opacity stitch parity drift")
    # The point z20 is solely from original C low branch with exact source parity.
    # Visibility normalization is only a numerical conservation check.
    g_all=[r[9] for r in newrows]
    integral=src.cumulative_simpson_38(g_all)[-1]
    expected=1-math.exp(-newrows[-1][7])
    if abs(integral-expected)>2e-5:
        raise ValueError("noUV source photon visibility conservation failed")
    maxindex=max(range(len(newrows)),key=lambda i:newrows[i][9])
    if maxindex!=1078:
        raise ValueError("original primordial source peak unexpectedly drifted")
    out.mkdir(parents=True,exist_ok=True)
    path=out/"ORIGINAL_NATIVE_C_NO_UV_THOMSON_0_TO_1600.csv.gz"
    with path.open("wb") as f:
        with gzip.GzipFile(fileobj=f,mode="wb",filename="",compresslevel=8,mtime=0) as gz:
            with io.TextIOWrapper(gz,encoding="ascii",newline="") as stream:
                writer=csv.writer(stream,lineterminator="\n")
                writer.writerow(header)
                for row in newrows:
                    writer.writerow([format(v,".17g") if isinstance(v,float) else v for v in row])
    result={
        "schema":"rec.rei.original_C_noUV_scattering_null_v1",
        "scope":"PURE_PRIMORDIAL_C_NO_ASTRO_IONIZATION_FLRW_Q0_NULL_ONLY",
        "original_C_stdout_sha256":src.NATIVE_C_STDOUT_SHA256,
        "original_C_stdout_8001_rows_reused":True,
        "original_highz_source_rows_reused":len(high),
        "original_highz_science_gzip_sha256":PARENT_OUTPUT_SHA256,
        "new_lowz_native_C_source_rows":len(low),
        "new_derived_source_null_rows":len(newrows),
        "new_evolved_IVPs":0,
        "unique_redshift_nodes":len(newrows),
        "tau_noUV_0_to_20":tau0,
        "tau_noUV_0_to_20_frozen_xe_z20_control":tau_frozen[-1],
        "tau_lowz_simpson_minus_trapezoid":tau0-tau_trap[-1],
        "tau_lowz_coarse_step2_simpson":src.two_step_composite_simpson(f_lo,20,2),
        "tau_noUV_0_to_1100":newrows[1100][7],
        "tau_noUV_0_to_1600":newrows[-1][7],
        "P_noUV_0_to_20":transmission,
        "P_noUV_0_to_1600":newrows[-1][8],
        "noUV_scatter_probability_0_to_20":1-transmission,
        "visibility_peak_zbar_noUV":maxindex,
        "z20_native_C_xe_per_H":low[-1][1],
        "z0_native_C_xe_per_H":low[0][1],
        "z0_native_C_Tgas_K":low[0][2],
        "z20_source_continuity_rate_rel":abs(f_lo[-1]/q["kappa"][0]-1),
        "highz_visibility_const_factor_max_abs":g20_parity,
        "highz_tau_addition_parity_max_abs":highz_tau_parity,
        "full_visibility_normalization_minus_expected":integral-expected,
        "true_REI_astrophysical_electron_history":"NOT_AVAILABLE_NOT_REPLACED",
        "original_REI_first_interval":"BLOCKED_TICK160_TO161_UNCHANGED",
        "original_REI_F08_receiver":"EXISTS_REI_PR349_BUT_SOURCE_MISMATCH",
        "original_REI_F08_source_equivalence":incompatible,
        "rei_canonical_DAG":"28/88",
        "rei_working_DAG":"33/88",
        "rei_physical_fast_DAG":"4/7",
        "rec_H5_physical_DAG":"0/313",
        "canonical_delta":0,
        "source_adoption":"NOT_ADOPTED",
        "production":"HOLD",
        "new_REI_IVPs":0,
        "no_merge":True,
        "no_force_push":True,
        "auto_next_node":False,
        "output_file":path.name,
        "output_sha256":hashlib.sha256(path.read_bytes()).hexdigest()
    }
    (out/"SCIENCE_STATUS.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="ascii")
    print(json.dumps({k:result[k] for k in
                      ("tau_noUV_0_to_20","tau_noUV_0_to_1100",
                       "noUV_scatter_probability_0_to_20",
                       "z20_source_continuity_rate_rel",
                       "output_sha256","rei_canonical_DAG","rec_H5_physical_DAG")},
                     sort_keys=True))
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    compute(a.repo.resolve(),a.out.resolve())
