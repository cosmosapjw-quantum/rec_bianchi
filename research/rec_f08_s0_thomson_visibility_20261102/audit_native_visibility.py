#!/usr/bin/env python3
"""Independent source-free physical auditor of original F08 S0 Thomson visibility.

Unlike the producer's exact affine-electron analytical integration, this code
uses two-point Gauss quadrature over the source-native S0 gas time steps.
It does not import the producing code or original BASS Rust stage code.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path

C=29979245800.0
SIGMA=6.6524587051e-25
CS=C*SIGMA
STEPS=160
NR=128
DT=625000000.0
DONOR="75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843"
QSRC="a6bcc931865db54402eb44727afe13d74b4ea40cf6f1c3b08acda239678c2d92"
PAIR="0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8"
BRANCHES=("S0_BI","S0_FLRW")
MODES=("CHARACTERISTIC","ORIGINAL_HAT")
def digest(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def fail(cond,name):
    if not cond:raise AssertionError("REC198_INDEPENDENT_"+name)
def relative(a,b,limit=2e-12):
    return abs(a-b)<=limit*max(abs(a),abs(b),1e-300)

def gauss_segment(ta,tb,tk,h,x0,x1,nH0,theta):
    """Two independent Gauss–Legendre nodes for the same source-affine gas path."""
    if tb==ta:return 0.0
    L=tb-ta
    g=1/math.sqrt(3)
    out=0.0
    for u in (0.5-0.5*g,0.5+0.5*g):
        t=ta+L*u
        frac=(t-tk)/h
        xe=x0+(x1-x0)*frac
        out+=nH0*math.exp(-theta*t)*xe
    return CS*L*0.5*out

def read_source(source):
    authority=json.loads((source/"SOURCE_AUTHORITY.json").read_text())
    fail(authority["bass_donor_trajectory_sha256"]==DONOR,"DONOR_SOURCE_AUTHORITY")
    fail(authority["original_rei_F08_source_pair_sha256"]==PAIR,"SOURCE_REI_PAIR")
    fail(digest(source/"F08_ORIGINAL_NATIVE_GAS_640.csv.gz")==DONOR,"DONOR_TRAJ_HASH")
    fail(digest(source/"F08_ORIGINAL_SOURCE_Q128.csv")==QSRC,"NATIVE_RAYS_HASH")
    q=[]
    with (source/"F08_ORIGINAL_SOURCE_Q128.csv").open(newline="") as f:
        for j,r in enumerate(csv.DictReader(f)):
            fail(int(r["ray"])==j,"RAY_INDEX")
            vec=tuple(float(r[k]) for k in ("qx","qy","qz"))
            fail(abs(math.fsum(x*x for x in vec)-1)<3e-15,"RAY_UNIT")
            q.append(vec)
    fail(len(q)==NR,"128_SOURCE_RAYS")
    trj={(b,k):[] for b in BRANCHES for k in MODES}
    with gzip.open(source/"F08_ORIGINAL_NATIVE_GAS_640.csv.gz","rt",newline="") as f:
        for r in csv.DictReader(f):
            key=(r["branch"],r["model"])
            fail(key in trj,"ORIGINAL_NATIVE_GAS_BRANCH")
            trj[key].append(r)
    for key,rows in trj.items():
        rows.sort(key=lambda x:int(x["step"]))
        fail(len(rows)==STEPS and
             all(int(row["step"])==i+1 and float(row["proper_t_s"])==(i+1)*DT
                 for i,row in enumerate(rows)),"ORIGINAL_PROPER_CLOCK")
    return authority,trj,q

def erates(a,rows):
    f=a["original_source_He_H_number"]
    gas=[a["original_source_initial_HII"]+f*(a["original_source_initial_HeII"]+2*a["original_source_initial_HeIII"])]
    for r in rows:
        xh=float(r["xHII"])
        xhe=float(r["xHeII"])
        x3=float(r["xHeIII"])
        fail(0<=xh<=1 and 0<=xhe<=1 and 0<=x3<=1 and xhe+x3<=1,"NATIVE_GAS_CONE")
        gas.append(xh+f*(xhe+2*x3))
    return gas

def geodesic_z(q,H,t,T):
    def g(s):return math.sqrt(math.fsum(u*u*math.exp(-2*h*s) for u,h in zip(q,H)))
    return g(t)/g(T)-1
def geodesic_h(q,H,t):
    w=[u*u*math.exp(-2*h*t) for u,h in zip(q,H)]
    return math.fsum(h*a for a,h in zip(w,H))/math.fsum(w)
def read_csv_gz(p):
    with gzip.open(p,"rt",newline="") as f:return list(csv.DictReader(f))

def audit(unit:Path,results:Path,out:Path):
    unit,results,out=map(Path,(unit,results,out))
    fail(not out.exists(),"NO_OVERWRITE_AUDIT")
    a,trj,q=read_source(unit/"source_inputs")
    j=json.loads((results/"SCIENCE_RESULT.json").read_text())
    fail(j["source_original_128_rays"]==NR and
         j["physical_gas_trajectory_rows_from_donor"]==640 and
         j["F08_original_full_interval_owner_status"]=="HOLD",
         "ORIGINAL_SCOPE")
    fail(j["F05_original_26event_source_used"] is False,"NO_FALSE_F05_SPLICE")
    gasfile=results/"ORIGINAL_F08_S0_4MODE_644_TEMPORAL_THOMSON.csv.gz"
    rayfile=results/"ORIGINAL_F08_S0_128RAY_1536_REDSHIFT_VISIBILITY.csv.gz"
    fail(digest(gasfile)==j["original_time_source_thomson_csv_sha256"],"GAS_DATA_BYTES")
    fail(digest(rayfile)==j["original_ray_source_visibility_csv_sha256"],"RAY_DATA_BYTES")
    trows=read_csv_gz(gasfile)
    rrows=read_csv_gz(rayfile)
    fail(len(trows)==644 and len(rrows)==1536,"RESULT_SIZE")
    T=STEPS*DT
    groups={(b,k):[] for b in BRANCHES for k in MODES}
    for r in trows:
        key=(r["branch"],r["model"])
        fail(key in groups,"TEMPORAL_GROUP")
        groups[key].append(r)
    raygroups={(b,k):[] for b in BRANCHES for k in MODES}
    for r in rrows:
        key=(r["branch"],r["model"])
        fail(key in raygroups,"RAY_GROUP")
        raygroups[key].append(r)
    min_z=min(geodesic_z(v,tuple(a["H_per_s"][b]),0,T) for b in BRANCHES for v in q)
    fail(relative(min_z,j["ray_source_redshift_support_min"],1e-13),"RAY_SUPPORT")
    results_by_model={}
    flux_checks=0
    for b in BRANCHES:
      H=tuple(float(x) for x in a["H_per_s"][b])
      theta=math.fsum(H)
      nH0=a["original_source_initial_nH_cm3"]
      for kind in MODES:
        key=(b,kind)
        xs=erates(a,trj[key])
        tail=[0.0]*(STEPS+1)
        inc=[gauss_segment(i*DT,(i+1)*DT,i*DT,DT,xs[i],xs[i+1],nH0,theta)
             for i in range(STEPS)]
        for i in range(STEPS-1,-1,-1):
            tail[i]=math.fsum([inc[i],tail[i+1]])
        actual=sorted(groups[key],key=lambda r:int(r["step"]))
        fail(len(actual)==STEPS+1,"COMPLETE_TEMPORAL_HISTORY")
        for k,r in enumerate(actual):
            t=k*DT
            fail(int(r["step"])==k and float(r["proper_t_s"])==t,"TIME_ORDER")
            ne=nH0*math.exp(-theta*t)*xs[k]
            gamma=ne*CS
            pairs=(
                ("x_e_per_H",xs[k]),("proper_nH_cm3",nH0*math.exp(-theta*t)),
                ("proper_ne_cm3",ne),("Gamma_T_s_inv",gamma),
                ("tau_to_source_horizon",tail[k]),
                ("survival_no_Thomson",math.exp(-tail[k])),
                ("visibility_per_proper_s",gamma*math.exp(-tail[k])))
            for label,expected in pairs:
                fail(relative(float(r[label]),expected,5e-12),label)
            if k>0:
                incr=float(r["delta_tau_from_previous_step"])
                fail(relative(incr,inc[k-1],5e-12),"STEP_SOURCE_TAU")
                prob=math.exp(-tail[k])*(-math.expm1(-inc[k-1]))
                fail(relative(float(r["source_step_scattering_probability"]),prob,5e-12),
                     "STEP_PROBABILITY")
            flux_checks+=1
        # Conditional collision probability must integrate to source total
        Ptotal=-math.expm1(-tail[0])
        Psum=math.fsum(float(r["source_step_scattering_probability"]) for r in actual)
        fail(relative(Ptotal,Psum,4e-12),"ACTUAL_VISIBILITY_NORMALIZATION")
        fail(relative(j["model_results"][b+"_"+kind]["total_Thomson_tau_t0_to_T"],tail[0]),
             "TOTAL_NATIVE_GAS_TAU")
        for r in raygroups[key]:
            idx=int(r["ray"])
            frac=float(r["target_fraction"])
            z=float(r["source_photon_redshift"])
            t=float(r["emission_t_s"])
            fail(0<=idx<NR and 0<t<T and frac in (.25,.5,.75),"SOURCE_RAY_TARGET")
            v=q[idx]
            fail(relative(z,min_z*frac,5e-12) and
                 abs(geodesic_z(v,H,t,T)-z)<2e-14,"SOURCE_PHOTON_REDSHIFT")
            heff=geodesic_h(v,H,t)
            fail(relative(heff,float(r["H_ray_s_inv"]),5e-12),"NULL_PHOTON_CLOCK")
            k=min(STEPS-1,int(t/DT))
            x=xs[k]+(xs[k+1]-xs[k])*((t-k*DT)/DT)
            ne=nH0*math.exp(-theta*t)*x
            gamma=CS*ne
            tpart=gauss_segment(t,(k+1)*DT,k*DT,DT,xs[k],xs[k+1],nH0,theta)
            tau=math.fsum([tpart,tail[k+1]])
            expected=gamma*math.exp(-tau)/((1+z)*heff)
            for name,value in (
                 ("proper_n_e_cm3",ne),("Gamma_T_s_inv",gamma),
                 ("tau_to_receiver",tau),
                 ("probability_scattering_to_receiver",-math.expm1(-tau)),
                 ("visibility_per_unit_source_ray_redshift",expected)):
                fail(relative(float(r[name]),value,8e-12),name)
            flux_checks+=1
        vals=[float(r["tau_to_receiver"]) for r in raygroups[key]]
        for f in (.25,.5,.75):
            subset=[float(r["tau_to_receiver"]) for r in raygroups[key]
                    if float(r["target_fraction"])==f]
            spread=(max(subset)-min(subset))/(math.fsum(subset)/len(subset))
            got=j["ray_angular_redshift_opacity_spread"][b+"_"+kind+":fraction="+str(f)]["relative_tau_spread"]
            fail(relative(spread,got,5e-12),"ANGULAR_BIANCHI_VISIBILITY")
            if b=="S0_FLRW":
                fail(spread<5e-11,"FLRW_ZERO_SHEAR_ISOTROPIC")
            else:
                fail(.01<spread<.03,"BI_DIRECTIONAL_REDSHIFT_EFFECT")
        results_by_model[b+"_"+kind]=tail[0]
    # source-selected actual 160 original source steps, observer at final tick
    fail(j["REI_canonical_DAG"]=="28/88" and
         j["REC_H5_physical_DAG"]=="0/313" and j["production"]=="HOLD",
         "FALSE_OWNER_NODE_ACCEPTANCE")
    receipt={
        "schema":"REC198_SOURCE_FREE_ORIGINAL_F08_S0_THOMSON_VISIBILITY_AUDIT_V1",
        "source_donor_sha256":DONOR,
        "source_q_sha256":QSRC,
        "source_trajectories":640,
        "time_rows_verified":644,
        "ray_rows_verified":1536,
        "physical_scalar_checks":flux_checks,
        "independent_integrator":"TWO_POINT_GAUSS_LEGENDRE_NOT_SOURCE_ANALYTIC_SERIES",
        "original_photon_ray_redshift":"CHECKED_ALL_RAYS",
        "native_gas_thomson_time_integral":"SOURCE_AFFINE_PHYSICAL_MODEL_PASS",
        "conditional_ray_visibility":"SOURCE_MATCHED_ALL_RAY_ROWS_PASS",
        "source_FLRW_zero_shear_direction":"PASS",
        "original_F08_owner_interval_acceptance":"HOLD",
        "REI_canonical_DAG":"28/88",
        "REC_H5_physical_DAG":"0/313",
        "full_bass_original_native_Rust_chemistry_reexecuted":False,
        "original_F05_26event_material_source_used":False,
        "donor_model_tau":results_by_model,
    }
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"SOURCE_F08_S0_NATIVE_THOMSON_FULL_AUDIT_PASS",
      "time_rows":644,"ray_rows":1536,"checks":flux_checks,
      "model_tau":results_by_model},sort_keys=True))
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--unit",required=True,type=Path)
    p.add_argument("--results",required=True,type=Path)
    p.add_argument("--audit",required=True,type=Path)
    a=p.parse_args()
    audit(a.unit,a.results,a.audit)
