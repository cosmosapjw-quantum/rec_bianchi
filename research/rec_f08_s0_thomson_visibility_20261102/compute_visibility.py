#!/usr/bin/env python3
"""Actual original REI F08 S0 BASS-native H/He history -> Thomson visibility along null rays.

Time-dependent, 160 original proper steps and 128 original q directions,
for two BASS prescribed geometries × characteristic/fixed-hat photon
spectral representations. Thomson unscattered-hazard postprocessing.
No new 26-event F05 IVP, no synthetic owner admission or present-day CMB.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math
from pathlib import Path

C=29979245800.0
SIGMA=6.6524587051e-25
RATE=C*SIGMA
STEPS=160
RAYS=128
SOURCE_DT=625000000.0
MODELS=("CHARACTERISTIC","ORIGINAL_HAT")
BRANCHES=("S0_BI","S0_FLRW")
SOURCE_DONOR_SHA="75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843"
SOURCE_Q_SHA="a6bcc931865db54402eb44727afe13d74b4ea40cf6f1c3b08acda239678c2d92"
F08_PAIR="0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8"
REC_PARENT="ab71106999cb90d8be2435818511aca2c4ca2993"
BASS_PARENT="b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6"

def sha(path:Path)->str:
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):
            h.update(b)
    return h.hexdigest()

def must(test:bool,label:str):
    if not test:raise ValueError("REC198_F08_S0_"+label)

def exact_moments(lam:float)->tuple[float,float]:
    """A=∫exp(-lam s)ds, B=∫s exp(-lam s)ds, 0≤s≤1.

    Powers computed by recurrence to avoid cancellation at S0 lam 1.875e-5.
    """
    must(math.isfinite(lam) and lam>=0,"BAD_EXPANSION_LAMBDA")
    if lam>=0.1:
        e=math.exp(-lam)
        return -math.expm1(-lam)/lam,(-math.expm1(-lam)-lam*e)/(lam*lam)
    A=B=0.0
    p=1.0
    for k in range(16):
        A+=p/(k+1)
        B+=p/(k+2)
        p*=(-lam)/(k+1)
    must(A>0 and B>0,"NONPOSITIVE_MOMENTS")
    return A,B

def xe(xh:float,xheii:float,xheiii:float,fhe:float)->float:
    must(all(math.isfinite(x) for x in (xh,xheii,xheiii,fhe)) and
         0<=xh<=1 and 0<=xheii<=1 and 0<=xheiii<=1 and
         xheii+xheiii<=1+1e-13 and fhe>0,"INVALID_NATIVE_H_HE")
    return xh+fhe*(xheii+2*xheiii)

def integrate_segment(ta:float,tb:float,tk:float,h:float,x0:float,x1:float,
                      nH0:float,theta:float)->float:
    """Analytic Thomson exposure on a subinterval of ONE actual source step.

    x_e linearly interpolated between source native endpoints;
    n_H=nH0 exp(-theta*t) exactly the BASS native source prescription.
    """
    must(h>0 and theta>=0 and nH0>0 and tb>=ta and
         tk-1e-5<=ta<=tb<=tk+h+1e-5,"BAD_SEGMENT_DOMAIN")
    if tb==ta:return 0.0
    fa=(ta-tk)/h
    fb=(tb-tk)/h
    xa=x0+(x1-x0)*fa
    xb=x0+(x1-x0)*fb
    length=tb-ta
    A,B=exact_moments(theta*length)
    v=RATE*nH0*math.exp(-theta*ta)*length*(xa*A+(xb-xa)*B)
    must(math.isfinite(v) and v>=0,"NEGATIVE_THOMSON_TAU")
    return v

def g_ray(q:tuple[float,float,float],H:tuple[float,float,float],t:float)->float:
    return math.sqrt(math.fsum(qi*qi*math.exp(-2*hi*t) for qi,hi in zip(q,H)))
def source_redshift(q,H,t,receive):
    return g_ray(q,H,t)/g_ray(q,H,receive)-1.0
def H_ray(q,H,t):
    nums=[qi*qi*math.exp(-2*hi*t) for qi,hi in zip(q,H)]
    return math.fsum(hi*x for hi,x in zip(H,nums))/math.fsum(nums)
def invert_source_redshift(q,H,z,receive):
    must(z>0 and source_redshift(q,H,0.0,receive)>z,"REDSHIFT_OUTSIDE_SOURCE_SUPPORT")
    left,right=0.0,receive
    for _ in range(70):
        mid=(left+right)/2
        if source_redshift(q,H,mid,receive)>z:left=mid
        else:right=mid
    return (left+right)/2

def gather_source_data(base:Path):
    base=Path(base)
    source=base/"source_inputs"
    authority=json.loads((source/"SOURCE_AUTHORITY.json").read_text())
    must(authority["frozen_trajectory_sha256"]==SOURCE_DONOR_SHA
         and authority["original_source_q128_sha256"]==SOURCE_Q_SHA
         and authority["original_rei_F08_source_pair_sha256"]==F08_PAIR,
         "SOURCE_AUTHORITY")
    must(authority["bass_donor_head"]==BASS_PARENT,"BASS_PARENT")
    donor=source/"F08_ORIGINAL_NATIVE_GAS_640.csv.gz"
    qp=source/"F08_ORIGINAL_SOURCE_Q128.csv"
    must(sha(donor)==SOURCE_DONOR_SHA and sha(qp)==SOURCE_Q_SHA,"SOURCE_BYTES_CHANGED")
    must(authority["source_proper_dt_s"]==SOURCE_DT
         and authority["steps_per_model"]==STEPS
         and authority["directions"]==RAYS,"SOURCE_PROPER_CLOCK")
    H={b:tuple(authority["H_per_s"][b]) for b in BRANCHES}
    must(H["S0_BI"]==(1.01e-14,9.9e-15,1e-14)
         and H["S0_FLRW"]==(1e-14,1e-14,1e-14),"ORIGINAL_SOURCE_H")
    q=[]
    with qp.open(newline="") as f:
        for i,r in enumerate(csv.DictReader(f)):
            must(int(r["ray"])==i,"RAY_ORDER")
            v=tuple(float(r[x]) for x in ("qx","qy","qz"))
            must(abs(math.fsum(y*y for y in v)-1)<4e-15,"RAY_UNIT")
            q.append(v)
    must(len(q)==RAYS,"SOURCE_Q128")
    grouped={(b,k):[] for b in BRANCHES for k in MODELS}
    with gzip.open(donor,"rt",newline="") as f:
        for row in csv.DictReader(f):
            key=(row["branch"],row["model"])
            must(key in grouped,"UNKNOWN_BASS_NATIVE_MODEL")
            grouped[key].append(row)
    must(sum(map(len,grouped.values()))==640,"NATIVE_640")
    for key,rows in grouped.items():
        rows.sort(key=lambda r:int(r["step"]))
        must(len(rows)==STEPS and
             all(int(r["step"])==i+1 and float(r["proper_t_s"])==(i+1)*SOURCE_DT
                 for i,r in enumerate(rows)),"SOURCE_PROPER_TIME_"+str(key))
        # Native H/He cells are in proton-normalized number fractions,
        # different from original F05 46,080 material particle counts.
        must(all(float(r["xHII"])>=0 and float(r["stage_native_residual"])<=1e-15
                 for r in rows),"SOURCE_NATIVE_ROOT")
    return authority,H,q,grouped

def source_time_states(authority,rows):
    init=xe(authority["original_source_initial_HII"],
            authority["original_source_initial_HeII"],
            authority["original_source_initial_HeIII"],
            authority["original_source_He_H_number"])
    return [init]+[xe(float(r["xHII"]),float(r["xHeII"]),float(r["xHeIII"]),
                      authority["original_source_He_H_number"]) for r in rows]

def run(base:Path,out:Path):
    base,out=Path(base).resolve(),Path(out).resolve()
    must(not out.exists(),"NO_OVERWRITE_SCIENCE")
    source,Hlist,q,donor=gather_source_data(base)
    horizon=STEPS*SOURCE_DT
    min_z=min(source_redshift(v,Hlist[b],0.0,horizon) for b in BRANCHES for v in q)
    must(0<min_z<0.02,"SOURCE_REDSHIFT_HORIZON")
    targets=[(p,min_z*p) for p in (0.25,0.5,0.75)]
    out.mkdir(parents=True)
    timepath=out/"ORIGINAL_F08_S0_4MODE_644_TEMPORAL_THOMSON.csv.gz"
    raypath=out/"ORIGINAL_F08_S0_128RAY_1536_REDSHIFT_VISIBILITY.csv.gz"
    time_head=("branch","model","step","proper_t_s",
               "x_e_per_H","proper_nH_cm3","proper_ne_cm3",
               "Gamma_T_s_inv","tau_to_source_horizon","survival_no_Thomson",
               "visibility_per_proper_s",
               "delta_tau_from_previous_step",
               "source_step_scattering_probability")
    ray_head=("branch","model","ray","target_fraction","source_photon_redshift",
              "emission_t_s","receiver_t_s","lookback_s","H_ray_s_inv",
              "proper_n_e_cm3","Gamma_T_s_inv",
              "tau_to_receiver","probability_scattering_to_receiver",
              "visibility_per_unit_source_ray_redshift",
              "qx","qy","qz")
    summaries={}
    time_rows=[]
    ray_rows=[]
    for b in BRANCHES:
        H=Hlist[b]
        theta=math.fsum(H)
        nH0=source["original_source_initial_nH_cm3"]
        for model in MODELS:
            key=b+"_"+model
            x=source_time_states(source,donor[(b,model)])
            inc=[integrate_segment(i*SOURCE_DT,(i+1)*SOURCE_DT,i*SOURCE_DT,
                      SOURCE_DT,x[i],x[i+1],nH0,theta) for i in range(STEPS)]
            tau=[0.0]*(STEPS+1)
            for i in range(STEPS-1,-1,-1):
                tau[i]=math.fsum([inc[i],tau[i+1]])
            must(0<tau[0]<1e-3 and tau[-1]==0
                 and all(tau[i]>tau[i+1] for i in range(STEPS)),
                 "SOURCE_TAU_MONOTONIC_"+key)
            totalprob=-math.expm1(-tau[0])
            step_prob=math.fsum(math.exp(-tau[i+1])*(-math.expm1(-inc[i])) for i in range(STEPS))
            must(abs(step_prob-totalprob)<2e-20,"SOURCE_VISIBILITY_NORMALIZATION")
            for i in range(STEPS+1):
                t=i*SOURCE_DT
                nH=nH0*math.exp(-theta*t)
                ne=nH*x[i]
                gamma=RATE*ne
                p_scatter=(math.exp(-tau[i])*(-math.expm1(-inc[i-1])) if i else 0.0)
                time_rows.append((b,model,i,t,x[i],nH,ne,gamma,tau[i],
                   math.exp(-tau[i]),gamma*math.exp(-tau[i]),
                   inc[i-1] if i else 0.0,p_scatter))
            def tau_time(t):
                if t>=horizon:return 0.0
                i=min(STEPS-1,int(t/SOURCE_DT))
                remain=integrate_segment(t,(i+1)*SOURCE_DT,i*SOURCE_DT,
                                         SOURCE_DT,x[i],x[i+1],nH0,theta)
                return math.fsum([remain,tau[i+1]])
            def ne_time(t):
                i=min(STEPS-1,int(t/SOURCE_DT))
                frac=(t-i*SOURCE_DT)/SOURCE_DT
                return nH0*math.exp(-theta*t)*(x[i]+(x[i+1]-x[i])*frac)
            for ray,v in enumerate(q):
                for f,zstar in targets:
                    te=invert_source_redshift(v,H,zstar,horizon)
                    red=source_redshift(v,H,te,horizon)
                    hr=H_ray(v,H,te)
                    ne=ne_time(te)
                    gamma=RATE*ne
                    Tdepth=tau_time(te)
                    must(0<te<horizon and hr>0 and Tdepth>0
                         and abs(red-zstar)<3e-15,"SOURCE_RAY_DOMAIN")
                    ray_rows.append((b,model,ray,f,red,te,horizon,horizon-te,
                       hr,ne,gamma,Tdepth,-math.expm1(-Tdepth),
                       gamma*math.exp(-Tdepth)/((1+red)*hr),*v))
            summaries[key]={
              "true_source_chemistry_steps":STEPS,
              "original_s0_photon_directions":RAYS,
              "total_Thomson_tau_t0_to_T":tau[0],
              "total_scattering_probability":totalprob,
              "source_temporal_visibility_probability_sum":step_prob,
              "final_xe_per_H":x[-1],
              "initial_xe_per_H":x[0],
              "original_native_chemistry_root_max":max(float(z["stage_native_residual"])
                                                     for z in donor[(b,model)]),
              "total_source_native_ne_time_end_cm3":nH0*math.exp(-theta*horizon)*x[-1],
              "source_Thomson_time_interpolant":"PIECEWISE_AFFINE_XE_WITH_EXACT_NATIVE_EXPONENTIAL_NH",
            }
    must(len(time_rows)==4*(STEPS+1) and len(ray_rows)==4*RAYS*len(targets),
         "REAL_NATIVE_SOURCE_RESULT_ROWS")
    def write(path,header,rows):
        with path.open("xb") as handle:
            with gzip.GzipFile(fileobj=handle,mode="wb",filename="",mtime=0,compresslevel=6) as z:
                with io.TextIOWrapper(z,encoding="ascii",newline="",write_through=True) as s:
                    w=csv.writer(s,lineterminator="\n")
                    w.writerow(header)
                    for row in rows:
                        w.writerow([v if isinstance(v,str) or isinstance(v,int)
                                    else format(float(v),".17e") for v in row])
    write(timepath,time_head,time_rows)
    write(raypath,ray_head,ray_rows)
    spread={}
    for b in BRANCHES:
        for model in MODELS:
            key=b+"_"+model
            for f,zstar in targets:
                vals=[r[11] for r in ray_rows if r[0]==b and r[1]==model and r[3]==f]
                gamma_vals=[r[13] for r in ray_rows if r[0]==b and r[1]==model and r[3]==f]
                mean=math.fsum(vals)/len(vals)
                spread[f"{key}:fraction={f}"]={
                   "source_z_target":zstar,
                   "min_tau":min(vals),
                   "max_tau":max(vals),
                   "relative_tau_spread":(max(vals)-min(vals))/mean,
                   "mean_tau":mean,
                   "max_visibility_per_z":max(gamma_vals),
                   "min_visibility_per_z":min(gamma_vals)}
                if b=="S0_FLRW":
                    must(spread[f"{key}:fraction={f}"]["relative_tau_spread"] < 5e-11,
                         "FLRW_RAY_ISOTROPIC")
                else:
                    must(spread[f"{key}:fraction={f}"]["relative_tau_spread"] > 1e-5,
                         "BI_RAY_REDSHIFT_ANISOTROPY")
    summary={
      "schema":"REC198_SOURCE_PAIRED_F08_S0_NATIVE_TIME_DEPENDENT_THOMSON_VISIBILITY_V1",
      "rec_parent_head":REC_PARENT,
      "bass_original_native_donor_head":BASS_PARENT,
      "original_rei_F08_S0_pair_sha256":F08_PAIR,
      "native_source_trajectory_sha256":SOURCE_DONOR_SHA,
      "native_source_q128_sha256":SOURCE_Q_SHA,
      "original_source_H_per_s":Hlist,
      "source_Hubble_expansion_for_density_s_inv":{
          b:math.fsum(Hlist[b]) for b in BRANCHES},
      "source_initial_n_H_cm3":source["original_source_initial_nH_cm3"],
      "source_initial_HII_HeII_HeIII":[source["original_source_initial_HII"],
                                      source["original_source_initial_HeII"],
                                      source["original_source_initial_HeIII"]],
      "source_helium_number_per_hydrogen":source["original_source_He_H_number"],
      "native_source_dt_s":SOURCE_DT,
      "source_horizon_T_s":horizon,
      "source_original_128_rays":RAYS,
      "physical_gas_trajectory_rows_from_donor":640,
      "time_visibility_rows":len(time_rows),
      "ray_visibility_rows":len(ray_rows),
      "ray_source_redshift_support_min":min_z,
      "ray_source_redshift_fraction_targets":targets,
      "model_results":summaries,
      "ray_angular_redshift_opacity_spread":spread,
      "original_time_source_thomson_csv_sha256":sha(timepath),
      "original_ray_source_visibility_csv_sha256":sha(raypath),
      "scientific_claim":"ACTUAL_NATIVE_F08_GAS_HISTORY_EXACT_RAY_REDSHIFT_CONDITIONAL_THOMSON_HAZARD",
      "interpolation_scope":"PIECEWISE_AFFINE_NATIVE_GAS_XE_NOT_ORIGINAL_FULL_IVP_DENSE_OUTPUT",
      "F08_original_full_interval_owner_status":"HOLD",
      "F05_original_26event_source_used":False,
      "new_accepted_REI_owner_nodes":0,
      "REI_canonical_DAG":"28/88",
      "REI_working_DAG":"33/88",
      "PhysicalFast_DAG":"4/7",
      "REC_H5_physical_DAG":"0/313",
      "source_nonnegligible_Klein_Nishina_or_thermal_corrections":"NOT_APPLIED_LEADING_THOMSON_ONLY",
      "production":"HOLD",
    }
    (out/"SCIENCE_RESULT.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"REC198_NATIVE_128RAY_SOURCE_THOMSON_VISIBILITY_COMPUTED",
            "donor_rows":640,"gas_rows":len(time_rows),"ray_rows":len(ray_rows),
            "tau0":{k:float(v["total_Thomson_tau_t0_to_T"]) for k,v in summaries.items()},
            "BI_spread":{k:v["relative_tau_spread"] for k,v in spread.items()
                         if k.startswith("S0_BI")},
            "hash_gas":summary["original_time_source_thomson_csv_sha256"],
            "hash_ray":summary["original_ray_source_visibility_csv_sha256"]},sort_keys=True))
    return summary

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--unit",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    run(a.unit,a.out)
