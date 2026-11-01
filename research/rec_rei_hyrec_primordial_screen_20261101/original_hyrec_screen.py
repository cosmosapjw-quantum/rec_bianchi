#!/usr/bin/env python3
"""REC-owned original HyRec2012 q=0 primordial Thomson optical screen.

Inputs are immutable REC original HyRec2012 FULL H+He C results already matched
to the *conditional* REI AXBI z=20 scenario. REI's astrophysical reionization
history, F05/26-event owner and production state are never modified.

No original HyRec C, REI native IVP, Bianchi optical path or CMB transfer is run.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path

SOURCE_REL = "research/rec_r3c_rei_bridge_20261015/HYREC_FLRW_Z20_TO_1600.csv"
BOUNDARY_REL = "research/rec_r3c_rei_bridge_20261015/REI_CONDITIONAL_BOUNDARY.json"
SOURCE_GIT_BLOB = "2b50008c744d9cb241d9985a4bf6ce8bcf83e09a"
BOUNDARY_GIT_BLOB = "89cdfc766e2e613760d84274812f2b4432373354"
NATIVE_C_STDOUT_SHA256 = "6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400"
REI_AXBI_SCENARIO_SHA256 = "07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696"
N_ROWS = 1581
Z_MIN = 20
Z_MAX = 1600
C_M_S = 299792458.0
SIGMA_T_M2 = 6.6524587321e-29
H100_S_INV = 1.0e7 / 3.0856775814913673e24
H = 0.674
OMEGA_M = 0.315
OMEGA_R = 0.000092
OMEGA_L = 1.0 - OMEGA_M - OMEGA_R
ORIGINAL_LIMIT = 2.0e-4

def git_blob_hash(payload: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") + b"\x00" + payload).hexdigest()

def assert_original_source_bytes(source: bytes, boundary: bytes) -> dict:
    if git_blob_hash(source) != SOURCE_GIT_BLOB:
        raise ValueError("SOURCE_ORIGINAL_HYREC_CSV_BLOB_IDENTITY_MISMATCH")
    if git_blob_hash(boundary) != BOUNDARY_GIT_BLOB:
        raise ValueError("SOURCE_ORIGINAL_REI_BOUNDARY_BLOB_IDENTITY_MISMATCH")
    info = json.loads(boundary)
    if (info["schema"] != "rec.rei.primordial_reference_boundary.v1"
        or float(info["zbar"]) != 20.0
        or info["source_sha256"] != NATIVE_C_STDOUT_SHA256
        or info["rei_scenario_sha256"] != REI_AXBI_SCENARIO_SHA256
        or info["decision"] != "REI_REFERENCE_COUNTERFACTUAL_NOT_ADOPTED"):
        raise ValueError("SOURCE_PROVENANCE_OR_REI_ADOPTION_DRIFT")
    return info

def read_original_history(source: bytes) -> list[dict[str, float]]:
    text = source.decode("ascii")
    reader = csv.DictReader(io.StringIO(text))
    keys = ["zbar","xe_per_H","Tgas_K","ne_m3","dtaudlna","u_th_J_m3"]
    if reader.fieldnames != keys:
        raise ValueError("original HyRec history field contract changed")
    rows = [{k:float(row[k]) for k in keys} for row in reader]
    if len(rows) != N_ROWS:
        raise ValueError("original HyRec history is incomplete")
    # Original SOURCE file runs backward 1600 -> 20. This is not a new calculation.
    for index, row in enumerate(rows):
        z = Z_MAX-index
        if (row["zbar"] != float(z) or
            not all(math.isfinite(v) for v in row.values()) or
            not 0 < row["xe_per_H"] <= 1.2 or
            not all(row[k]>0 for k in keys if k not in ("zbar",))):
            raise ValueError("original source history grid/nonphysical value")
    return rows[::-1]

def hubble(z:float) -> float:
    if z < 0.0 or not math.isfinite(z):
        raise ValueError("invalid homogeneous redshift")
    return H * H100_S_INV * math.sqrt(
        OMEGA_M*(1+z)**3 + OMEGA_R*(1+z)**4 + OMEGA_L)

def cumulative_simpson_38(f:list[float]) -> list[float]:
    """Unit-grid composite 1/3 Simpson with 3/8 final interval for odd n>=3.

    At the single first interval, local quadratic interpolation from the first
    three frozen source samples is used. This is a smooth-source quadrature,
    not a validated bound on HyRec physics or the true continuum integral.
    """
    if len(f)<4 or not all(v>=0 and math.isfinite(v) for v in f):
        raise ValueError("invalid positive opacity input")
    out=[0.0]
    for n in range(1,len(f)):
        if n==1:
            v=(5*f[0]+8*f[1]-f[2])/12
        elif n%2==0:
            v=out[n-2]+(f[n-2]+4*f[n-1]+f[n])/3
        else:
            v=out[n-3]+3*(f[n-3]+3*f[n-2]+3*f[n-1]+f[n])/8
        if v<=out[-1]:
            raise ValueError("unexpected nonmonotone physical optical depth")
        out.append(v)
    return out

def cumulative_trapezoid(f:list[float]) -> list[float]:
    out=[0.]
    for n in range(1,len(f)):
        out.append(out[-1]+.5*(f[n-1]+f[n]))
    return out

def two_step_composite_simpson(f:list[float],endpoint_index:int,step:int) -> float:
    if endpoint_index% (2*step):
        raise ValueError("Simpson composite endpoint not on requested grid")
    ans=0.0
    for j in range(0,endpoint_index,2*step):
        ans+=step*(f[j]+4*f[j+step]+f[j+2*step])/3
    return ans

def prepare(repo:Path):
    source=(repo/SOURCE_REL).read_bytes()
    boundary=(repo/BOUNDARY_REL).read_bytes()
    info=assert_original_source_bytes(source,boundary)
    rows=read_original_history(source)
    donor=info["hyrec_full_conditional_projection"]
    original=info["published_rei_approximate_initial"]
    root=rows[0]
    for key,a,b in (
      ("HyRec_xe",root["xe_per_H"],donor["electron_fraction_per_H"]),
      ("HyRec_T",root["Tgas_K"],donor["temperature_K"]),
      ("HyRec_ne",root["ne_m3"],donor["electron_density_m3"]),
      ("HyRec_opacity",root["dtaudlna"],donor["thomson_optical_depth_rate_per_ln_a"])
    ):
        if abs(a-b)>2e-14*max(1.0,abs(a),abs(b)):
            raise ValueError("REC z20 original donor boundary mismatch: "+key)

    z20_nH = root["ne_m3"] / root["xe_per_H"]
    if abs(z20_nH/info["normalization_mismatch"]["nH_REI_m3"]-1)>3e-14:
        raise ValueError("REC/REI recipient hydrogen normalization mismatch")
    x0=root["xe_per_H"]
    kappa=[]
    kappa_frozen=[]
    parity=[]
    for r in rows:
        z=r["zbar"]
        rate=C_M_S*SIGMA_T_M2*r["ne_m3"]/hubble(z)
        check=abs(rate/r["dtaudlna"]-1)
        parity.append(check)
        if check>2e-12:
            raise ValueError("original Thomson opacity from n_e/H mismatches source")
        kappa.append(r["dtaudlna"]/(1+z))
        # Comparison only: artificial freeze of primordial electron fraction,
        # not evolution or a substitute for HyRec at z>20.
        frozen_ne=z20_nH*((1+z)/21.0)**3*x0
        kappa_frozen.append(C_M_S*SIGMA_T_M2*frozen_ne/hubble(z)/(1+z))
    tau=cumulative_simpson_38(kappa)
    tau_frozen=cumulative_simpson_38(kappa_frozen)
    trap=cumulative_trapezoid(kappa)
    survival=[math.exp(-x) for x in tau]
    visibility=[kappa[i]*survival[i] for i in range(len(tau))]
    return info,rows,dict(kappa=kappa,kappa_frozen=kappa_frozen,tau=tau,
                          tau_frozen=tau_frozen,trap=trap,
                          survival=survival,visibility=visibility,
                          opacity_parity_max_relative=max(parity),
                          z20_nH_rei_m3=z20_nH)

def run(repo:Path,out:Path) -> dict:
    info,rows,q=prepare(repo)
    out.mkdir(parents=True,exist_ok=True)
    tau=q["tau"];vis=q["visibility"]
    maxindex=max(range(len(vis)),key=lambda i:vis[i])
    tau_one=next(i for i,v in enumerate(tau) if v>=1)
    z_tau_one=Z_MIN+tau_one-1+(1-tau[tau_one-1])/(tau[tau_one]-tau[tau_one-1])
    controls={}
    for z in [100,600,1100,1600]:
        j=z-Z_MIN
        controls[str(z)]={
         "source_simpson_tau":tau[j],
         "coarse_step2_tau":two_step_composite_simpson(q["kappa"],j,2),
         "source_trapezoid_tau":q["trap"][j],
        }
        if j%8==0:
            controls[str(z)]["coarse_step4_tau"]=two_step_composite_simpson(q["kappa"],j,4)
    checkpoints=[]
    for z in [20,30,40,50,60,80,100,150,200,300,400,500,600,800,1000,1100,1200,1400,1600]:
        j=z-Z_MIN
        checkpoints.append({
         "zbar":z,"original_HyRec_xe_per_H":rows[j]["xe_per_H"],
         "tau_REC_from_z20":tau[j],
         "transmission_REC_from_z20":q["survival"][j],
         "tau_if_xe_frozen_at_z20":q["tau_frozen"][j],
         "relative_tau_native_vs_frozen":None if z==20 else tau[j]/q["tau_frozen"][j]-1,
        })
    output=out/"ORIGINAL_HYREC_TO_REI_PRIMORDIAL_THOMSON_1581.csv.gz"
    header=["zbar","original_HyRec_xe_per_H","original_Tgas_K","receiver_ne_m3",
        "H_FLRW_s_inv","gamma_Thomson_s_inv","d_tau_dln_a","d_tau_dz",
        "tau_REC_20_to_z","transmission_REC_20_to_z","visibility_REC_per_z",
        "tau_frozen_xe20_control","delta_tau_native_minus_frozen"]
    with output.open("wb") as f:
        with gzip.GzipFile(fileobj=f,mode="wb",filename="",mtime=0,compresslevel=8) as gz:
            with io.TextIOWrapper(gz,encoding="ascii",newline="") as stream:
                writer=csv.writer(stream);writer.writerow(header)
                for i,r in enumerate(rows):
                    values=[r["zbar"],r["xe_per_H"],r["Tgas_K"],r["ne_m3"],
                        hubble(r["zbar"]),C_M_S*SIGMA_T_M2*r["ne_m3"],
                        r["dtaudlna"],q["kappa"][i],
                        tau[i],q["survival"][i],vis[i],q["tau_frozen"][i],
                        tau[i]-q["tau_frozen"][i]]
                    writer.writerow([format(v,".17g") for v in values])
    if q["opacity_parity_max_relative"]>2e-12:
        raise ValueError("original source Thomson parity not met")
    if abs(q["trap"][-1]-tau[-1])/tau[-1]>1e-6:
        raise ValueError("composite-quadrature control mismatch")
    if abs(q["kappa"][0]-info["hyrec_full_conditional_projection"]["thomson_optical_depth_rate_per_ln_a"]/21)>1e-17:
        raise ValueError("original donor boundary opacity broken")
    visibility_norm=cumulative_simpson_38(vis)[-1]
    if abs(visibility_norm-(1-q["survival"][-1]))>1e-5:
        raise ValueError("visibility probability normalization fails")

    result={
      "schema":"rec.rei.original_hyrec_primordial_thomson_screen.v1",
      "source_git_blob_sha1":SOURCE_GIT_BLOB,
      "source_native_HyRec2012_C_stdout_sha256":NATIVE_C_STDOUT_SHA256,
      "source_boundary_git_blob_sha1":BOUNDARY_GIT_BLOB,
      "recipient_reference_REI_AXBI_sha256":REI_AXBI_SCENARIO_SHA256,
      "boundary_decision":"ORIGINAL_REI_REFERENCE_IC_UNCHANGED",
      "donor_adoption":"NOT_ADOPTED",
      "reference_clock":"mean FLRW zbar; NOT observed-direction redshift",
      "source_scope":"ORIGINAL_HYREC2012_FLRW_FULL_H_HE_PRIMORDIAL_Z20_TO_Z1600",
      "receiver_scope":"conditional REC-owned primordial Thomson screen above z20; NO_REI_NATIVE_IGM_F05_CONSUMER",
      "z20":rows[0],
      "source_rows":len(rows),"new_model_rows":len(rows),
      "source_Hubble_parameters":{"h":H,"Om":OMEGA_M,"Or":OMEGA_R,"OL":OMEGA_L},
      "c_m_s":C_M_S,"sigmaT_m2":SIGMA_T_M2,
      "opacity_parity_max_relative":q["opacity_parity_max_relative"],
      "source_helium_species_handling":"native total free x_e includes He early; late z20 x_HII=xe projected only conditionally",
      "original_REI_baseline_at_z20":info["published_rei_approximate_initial"],
      "original_donor_at_z20":info["hyrec_full_conditional_projection"],
      "relative_ne_donor_minus_rei_at_z20":info["donor_minus_baseline"]["ne_m3"]/info["published_rei_approximate_initial"]["electron_density_m3"],
      "nH_recipient_m3_at_z20":q["z20_nH_rei_m3"],
      "tau_z20_to_z1600":tau[-1],
      "transmission_z20_to_z1600":q["survival"][-1],
      "visibility_peak_source_grid_zbar":int(rows[maxindex]["zbar"]),
      "visibility_peak_per_redshift":vis[maxindex],
      "tau_one_crossing_linear_interpolation_zbar":z_tau_one,
      "visibility_quadrature_normalization":visibility_norm,
      "visibility_expected_integral":1-q["survival"][-1],
      "quadrature_comparison":controls,"selected_source_outputs":checkpoints,
      "output_file":output.name,"output_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
      "source_initial_ionizing_photon_stock":"REI_ASTROPHYSICAL_0_STAYS_ZERO",
      "physical_completed_REI_first_F05":False,
      "REI_canonical":"28/88","REI_working":"33/88","REI_fast":"4/7",
      "REC_physical_H5":"0/313","canonical_delta":0,
      "producer_code_owned_by":"cosmosapjw-quantum/rec_bianchi",
      "source_owner_switch":False,"new_igm_IVP":0,"new_primordial_IVP":0,
      "production":"HOLD","no_merge":True,"auto_next_node":False,
      "scientific_claim":"Original source-owned primordial FLRW Thomson screen/conditional REI z20 boundary only; NOT a Bianchi IGM accepted history or complete CMB optical depth",
    }
    (out/"SCIENCE_STATUS.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    with (out/"REC_REI_SOURCE_PHYSICS_WITNESS.csv").open("w",encoding="ascii",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(["zbar","xe","Tgas_K","tau_REC_20_z","visibility_per_z","tau_frozen_control"])
        for z in [20,30,50,100,200,400,600,800,1000,1100,1600]:
            j=z-Z_MIN
            writer.writerow([z,*[format(a,".17g") for a in (rows[j]["xe_per_H"],rows[j]["Tgas_K"],tau[j],vis[j],q["tau_frozen"][j])]])
    print(json.dumps({k:result[k] for k in ["source_rows","opacity_parity_max_relative","tau_z20_to_z1600","visibility_peak_source_grid_zbar","tau_one_crossing_linear_interpolation_zbar","output_sha256","REI_canonical","REC_physical_H5"]},sort_keys=True))
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    opts=parser.parse_args()
    run(opts.repo.resolve(),opts.out.resolve())
