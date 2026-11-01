#!/usr/bin/env python3
"""Independent source-free full-row physics audit and exact ΔU product partition.

No source solver calls. This is an independent numerical audit of the
already generated true-source accepted endpoint data, not a second IVP.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path
import numpy as np

KB=1.380649e-16
C=29979245800.0
SIGMA=6.6524587051e-25
N=46080
KEYS=("source_volume_cm3","N_H","N_He","Ne_lower","Ne_upper",
      "T_lower_K","T_upper_K","B_lower_erg","B_upper_erg",
      "U_lower_erg","U_upper_erg","Gamma_lower_s_inv","Gamma_upper_s_inv")
IDX={x:i for i,x in enumerate(KEYS)}
TIMES=(0,64,128,160)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def must(x,what):
    if not x:raise AssertionError("REC195_SOURCE_FREE_"+what)
def total(x):return math.fsum(map(float,x))
def interval_mul(a,b,c,d):
    corners=np.stack((a*c,a*d,b*c,b*d))
    return corners.min(axis=0),corners.max(axis=0)

def audit(root:Path, outfile:Path):
    root=Path(root)
    p=root/"ORIGINAL_F05_REPLAY_0_64_128_160_46080.csv.gz"
    src=json.loads((root/"SCIENCE_RESULT.json").read_text())
    must(sha(p)==src["csv_sha256"],"CSV_BYTE_IDENTITY")
    must(src["physical_epochs"]==list(TIMES),"EPOCHS")
    must(src["total_rows"]==N*4,"SOURCE_ROWS")
    must(src["source_REI_PR363_sha"]==
         "abf83d4d883d5f311426b7f02cb001e70138ceb4","OWNER_HEAD")
    must(src["original_tar_sha256"]==
         "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b",
         "ORIGINAL_SOURCE_HASH")
    arr={}
    counts={}
    with gzip.open(p,"rt",encoding="ascii",newline="") as f:
        reader=csv.DictReader(f)
        must(tuple(reader.fieldnames)==("node","tick",*KEYS),"CSV_SCHEMA")
        rows={k:[] for k in TIMES}
        for row in reader:
            t=int(row["tick"])
            must(t in rows,"TIMESTAMP")
            must(int(row["node"])==len(rows[t]),"SOURCE_NODE_ORDER")
            vals=[float(row[k]) for k in KEYS]
            must(all(math.isfinite(x) and x>0 for x in vals),"PHYSICAL_POSITIVITY")
            rows[t].append(vals)
        for t in TIMES:
            must(len(rows[t])==N,"ALL_46080_ROWS_"+str(t))
            arr[t]=np.asarray(rows[t],dtype=np.float64)
            counts[str(t)]=len(rows[t])
    ref=arr[0]
    for t in TIMES:
        x=arr[t]
        for name in ("source_volume_cm3","N_H","N_He"):
            must(np.array_equal(ref[:,IDX[name]],x[:,IDX[name]]),
                 "CONSERVE_SOURCE_NUCLEI_VOLUME_"+name+"_"+str(t))
        n0,n1=x[:,IDX["Ne_lower"]],x[:,IDX["Ne_upper"]]
        t0,t1=x[:,IDX["T_lower_K"]],x[:,IDX["T_upper_K"]]
        b0,b1=x[:,IDX["B_lower_erg"]],x[:,IDX["B_upper_erg"]]
        u0,u1=x[:,IDX["U_lower_erg"]],x[:,IDX["U_upper_erg"]]
        g0,g1=x[:,IDX["Gamma_lower_s_inv"]],x[:,IDX["Gamma_upper_s_inv"]]
        for lower,upper in ((n0,n1),(t0,t1),(b0,b1),(u0,u1),(g0,g1)):
            must(np.all(lower<=upper),"BOUNDS_ORDER")
        V=x[:,IDX["source_volume_cm3"]]
        H=x[:,IDX["N_H"]];He=x[:,IDX["N_He"]]
        gamma_ref=[C*SIGMA*n0/V,C*SIGMA*n1/V]
        u_ref=[1.5*KB*(H+He+n0)*t0,1.5*KB*(H+He+n1)*t1]
        for actual,expect in zip((g0,g1,u0,u1),(*gamma_ref,*u_ref)):
            must(np.max(np.abs(actual-expect)/np.maximum(abs(expect),1e-300))<8e-15,
                 "INDEPENDENT_GAMMA_U_PHYSICS")
        d=src["point_physics"][str(t)]
        for lab,colname in (("Ne","Ne"),("B","B"),("U","U"),("Gamma","Gamma")):
            suffix="_lower" if lab=="Ne" else "_lower_erg"
            if lab=="Gamma":lo,hi=g0,g1
            elif lab=="Ne":lo,hi=n0,n1
            elif lab=="B":lo,hi=b0,b1
            else:lo,hi=u0,u1
            for val,seen in zip(d[lab],(total(lo),total(hi))):
                must(abs(val-seen)<=2e-14*max(abs(val),1e-300),
                     "GLOBAL_SOURCE_RECONSTRUCT_"+lab+"_"+str(t))
    partitions=[]
    for (left,right), expected in zip(((0,64),(64,128),(128,160)),
                                      src["interval_physics"]):
        x,y=arr[left],arr[right]
        def col(A,k):return A[:,IDX[k]]
        nlo,nhi=col(x,"Ne_lower"),col(x,"Ne_upper")
        mlo,mhi=col(y,"Ne_lower"),col(y,"Ne_upper")
        tlo,thi=col(x,"T_lower_K"),col(x,"T_upper_K")
        slo,shi=col(y,"T_lower_K"),col(y,"T_upper_K")
        N0=x[:,IDX["N_H"]]+x[:,IDX["N_He"]]
        anlo=N0+.5*(nlo+mlo)
        anhi=N0+.5*(nhi+mhi)
        dTlo,dThi=slo-thi,shi-tlo
        avgTlo,avgThi=.5*(tlo+slo),.5*(thi+shi)
        dNlo,dNhi=mlo-nhi,mhi-nlo
        ptl,pth=interval_mul(anlo,anhi,dTlo,dThi)
        pnl,pnh=interval_mul(avgTlo,avgThi,dNlo,dNhi)
        tpart=[1.5*KB*total(ptl),1.5*KB*total(pth)]
        npart=[1.5*KB*total(pnl),1.5*KB*total(pnh)]
        overall=expected["delta_U"]
        must(tpart[0]+npart[0]<=overall[0]*(1+1e-12) or
             tpart[0]+npart[0]<=overall[0]+2e-14*abs(overall[0]),
             "ENERGY_PARTITION_LOWER_CONTAINS_DELTA")
        must(tpart[1]+npart[1]>=overall[1]-(2e-14*abs(overall[1])),
             "ENERGY_PARTITION_UPPER_CONTAINS_DELTA")
        second=(expected["delta_Ne"],
                [total(dNlo),total(dNhi)])
        # Difference of two ~1e66 global sums loses relative bits in a
        # ~1e62 source increment; compare on the physical parent inventory
        # scale, NOT at an arbitrary relative precision of the tiny delta.
        source_inventory_scale=max(abs(total(nlo))+abs(total(mlo)),1.0)
        worst_source_scaled_discrepancy=max(abs(a-b)/source_inventory_scale
                                           for a,b in zip(*second))
        must(worst_source_scaled_discrepancy < 1e-14,
             "ELECTRON_SOURCE_DELTA_PARENT_SCALED")
        dt=expected["source_dt_seconds"]
        must(dt>0,"SOURCE_TIME")
        rate_u=[-expected["source_delta_U_secant_erg_s"][1],
                -expected["source_delta_U_secant_erg_s"][0]]
        rate_b=[-expected["source_delta_B_secant_erg_s"][1],
                -expected["source_delta_B_secant_erg_s"][0]]
        must(rate_u[0]>0 and rate_b[0]>0,"SIGNED_COOLING")
        partitions.append({
            "interval_ticks":[left,right],
            "thermal_temperature_work_interval_erg":tpart,
            "thermal_electron_number_work_interval_erg":npart,
            "source_delta_U_interval_erg":overall,
            "source_secular_thermal_cooling_rate_erg_s":rate_u,
            "source_secular_binding_discharge_rate_erg_s":rate_b,
            "temperature_definite_cool_cells":int(np.sum(shi<tlo)),
            "electron_definite_loss_cells":int(np.sum(mhi<nlo))})
    # Falsifiable distinct physical trend in three actual source intervals:
    # strict nonoverlap of thermal cooling (increasing), binding discharge
    # (decreasing) interval bounds.
    for x,y in zip(partitions,partitions[1:]):
        must(y["source_secular_thermal_cooling_rate_erg_s"][0] >
             x["source_secular_thermal_cooling_rate_erg_s"][1],
             "THERMAL_RATE_STAGING_INCREASING")
        must(y["source_secular_binding_discharge_rate_erg_s"][1] <
             x["source_secular_binding_discharge_rate_erg_s"][0],
             "BINDING_RATE_STAGING_DECREASING")
    out={
        "schema":"REC195_ORIGINAL_F05_SOURCE_PHYSICAL_TRAJECTORY_INDEPENDENT_AUDIT",
        "cell_rows_checked":4*N,
        "per_epoch_rows":counts,
        "source_csv_sha256":sha(p),
        "physical_rate_and_kinetic_energy_4_epoch_checks":"PASS",
        "source_H_He_volume_invariance":"PASS",
        "interval_kinetic_identity":"PASS_OUTER_BOXES",
        "strict_thermal_cooling_rate_acceleration":"PASS_3_NONOVERLAPPING_BOUNDS",
        "strict_binding_discharge_rate_deceleration":"PASS_3_NONOVERLAPPING_BOUNDS",
        "intervals":partitions,
        "scientific_scope":"SOURCE_ACCEPTED_DISCRETE_SECANT_NOT_CONTINUUM_DERIVATIVE_OR_NEW_OWNER_ACCEPTANCE",
        "REI_canonical_DAG":"28/88",
        "REC_H5_physical_DAG":"0/313",
    }
    if outfile.exists():raise FileExistsError("SOURCE_FREE_REFUSE_RESULT_OVERWRITE")
    outfile.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":"INDEPENDENT_SOURCE_FREE_SCIENCE_AUDIT_PASS",
            "rows":4*N,
            "thermal_loss_rates":[r["source_secular_thermal_cooling_rate_erg_s"] for r in partitions],
            "binding_discharge_rates":[r["source_secular_binding_discharge_rate_erg_s"] for r in partitions],
            "audit_json":str(outfile)},sort_keys=True))
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--results",type=Path,required=True)
    p.add_argument("--audit-out",type=Path,required=True)
    args=p.parse_args();audit(args.results,args.audit_out)
