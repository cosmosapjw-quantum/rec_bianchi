#!/usr/bin/env python3
"""Independent source-free auditor for REC V2 collision/geometry physics.

Uses csv/decimal-looking f64 only, no REI source solver or NumPy dependency.
Rechecks each of the 46080 ORIGINAL H/He matter-cell rows, bounds and signs.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path

SIGMA_C = 6.6524587051e-25 * 29979245800.0
N = 46080
FIELDS=("node","source_proper_volume_cm3",
  "Ne160_lower","Ne160_upper","Ne161V2_lower","Ne161V2_upper",
  "Gamma160_lower_s_inv","Gamma160_upper_s_inv",
  "Gamma161_frozen_lower_s_inv","Gamma161_frozen_upper_s_inv",
  "Gamma161_expanded_lower_s_inv","Gamma161_expanded_upper_s_inv",
  "delta_chem_lower_s_inv","delta_chem_upper_s_inv",
  "delta_geometry_lower_s_inv","delta_geometry_upper_s_inv",
  "delta_total_lower_s_inv","delta_total_upper_s_inv")

def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for x in iter(lambda:f.read(1<<20),b""):
            h.update(x)
    return h.hexdigest()
def must(condition,label):
    if not condition:raise AssertionError("REC197_INDEPENDENT_"+label)
def near(a,b,eps=3e-14):
    return abs(a-b)<=eps*max(abs(a),abs(b),1e-300)
def audit(root:Path,destination:Path):
    root,destination=Path(root),Path(destination)
    must(not destination.exists(),"REFUSE_OVERWRITE")
    src=json.loads((root/"SCIENCE_RESULT.json").read_text())
    csvpath=root/"ORIGINAL_F05_V2_THOMSON_GEOMETRY_46080.csv.gz"
    must(digest(csvpath)==src["source_csv_sha256"],"SCIENTIFIC_SOURCE_CSV_HASH")
    must(src["cells"]==N and src["source_original_26event_reintegrated"] is False,
         "ORIGINAL_SOURCE_SCOPE")
    must(src["owner_accepted_tick161"] is False and src["production"]=="HOLD",
         "FALSE_TICK161_ACCEPT")
    must(src["original_tar_sha256"]==
         "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b",
         "TAR_HASH")
    must(src["v2_npz_sha256"]==
         "c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823",
         "V2_SHA")
    must(src["native_source_frozen_volume_over_microtick"],"NOT_FROZEN_SOURCE")
    dt=src["source_microtick_seconds"]
    hlo,hhi=src["native_source_H_s_inv_interval"]
    must(0<dt and 0<hlo<=hhi,"GEOMETRIC_CLOCK")
    fmin=math.exp(-3*hhi*dt)
    fmax=math.exp(-3*hlo*dt)
    flo,fhi=src["expansion_volume_inverse_factor_interval"]
    must(near(fmin,flo) and near(fmax,fhi) and 0<flo<=fhi<1,
         "SOURCE_CONDITIONAL_EXPANSION_FACTOR")
    counts={k:{"definite_increase":0,"definite_decrease":0,"undetermined":0}
            for k in ("native_chemistry","with_expansion")}
    flip=0
    Ne0lo,Ne0hi,Ne1lo,Ne1hi,vol=[],[],[],[],[]
    normal_lambda_count=0
    with gzip.open(csvpath,"rt",encoding="ascii",newline="") as fp:
        reader=csv.DictReader(fp)
        must(tuple(reader.fieldnames)==FIELDS,"SOURCE_SCHEMA")
        for row in reader:
            j=int(row["node"])
            must(j==normal_lambda_count,"ORIGINAL_ORDER")
            normal_lambda_count+=1
            (v,n0lo,n0hi,n1lo,n1hi,g0lo,g0hi,g1lo,g1hi,
             gelo,gehi,dclo,dchi,dglo,dghi,dtlo,dthi)=(float(row[k]) for k in FIELDS[1:])
            must(all(math.isfinite(a) for a in
              (v,n0lo,n0hi,n1lo,n1hi,g0lo,g0hi,g1lo,g1hi,gelo,gehi,
               dclo,dchi,dglo,dghi,dtlo,dthi)),
               "NONFINITE_ORIGINAL_CELL")
            must(v>0 and 0<n0lo<=n0hi and 0<n1lo<=n1hi,
                 "ORIGINAL_SOURCE_CELL_CONE")
            for lo,hi in ((g0lo,g0hi),(g1lo,g1hi),(gelo,gehi),
                          (dclo,dchi),(dglo,dghi),(dtlo,dthi)):
                must(lo<=hi,"INTERVAL_ORDER")
            # Independently from source producer, recompute the photon collision
            # physical coefficient and expansion branch on the original proper V.
            for got,actual in ((g0lo,SIGMA_C*n0lo/v),(g0hi,SIGMA_C*n0hi/v),
                               (g1lo,SIGMA_C*n1lo/v),(g1hi,SIGMA_C*n1hi/v),
                               (gelo,g1lo*flo),(gehi,g1hi*fhi),
                               (dclo,g1lo-g0hi),(dchi,g1hi-g0lo),
                               (dglo,g1hi*(flo-1)),(dghi,g1lo*(fhi-1)),
                               (dtlo,gelo-g0hi),(dthi,gehi-g0lo)):
                must(near(got,actual,4e-14),"INDEPENDENT_COLLISION_FORMULA")
            must(dghi<0,"EXPANSION_REDUCES_COLLISION_RATE")
            # Exact additive identity, contained by independently widened
            # intervals. This is not an original continuum error estimate.
            tol=5e-15*max(g0hi,g1hi)
            must(dclo+dglo<=dtlo+tol and
                 dchi+dghi>=dthi-tol,"ADDITIVE_ENCLOSURE")
            for key,lo,hi in (("native_chemistry",dclo,dchi),
                              ("with_expansion",dtlo,dthi)):
                if lo>0:k="definite_increase"
                elif hi<0:k="definite_decrease"
                else:k="undetermined"
                counts[key][k]+=1
            if dclo>0 and dthi<0:flip+=1
            vol.append(v)
            Ne0lo.append(n0lo);Ne0hi.append(n0hi)
            Ne1lo.append(n1lo);Ne1hi.append(n1hi)
    must(normal_lambda_count==N,"SOURCE_46080")
    must(counts==src["physical_sign_classes"],"SIGN_CATEGORY_PARITY")
    must(flip==src["chem_increase_to_geometry_decrease_strict_cells"],
         "STRICT_SIGN_REVERSAL_COUNT")
    Vtot=math.fsum(vol)
    must(Vtot>0,"SOURCE_VOLUME_SUM")
    mean_0=[SIGMA_C*math.fsum(x)/Vtot for x in (Ne0lo,Ne0hi)]
    mean_f=[SIGMA_C*math.fsum(x)/Vtot for x in (Ne1lo,Ne1hi)]
    mean_e=[mean_f[0]*flo,mean_f[1]*fhi]
    for label,calc,expected in (
      ("mean160",mean_0,src["volume_weighted_Gamma160_s_inv"]),
      ("mean161f",mean_f,src["volume_weighted_Gamma161_frozen_s_inv"]),
      ("mean161e",mean_e,src["volume_weighted_Gamma161_expanded_s_inv"])):
        must(all(near(a,b,2e-13) for a,b in zip(calc,expected)),label)
    must(src["REI_canonical_DAG"]=="28/88" and
         src["REC_H5_physical_DAG"]=="0/313","CENTRAL_DAG_NO_FALSE_PROMOTION")
    result={"schema":"REC197_SOURCE_FREE_THOMSON_GEOMETRY_FULL_CELL_AUDIT_V1",
            "cells_checked":N,"data_sha256":digest(csvpath),
            "source_frozen_physical_volume":"VERIFIED_SOURCE",
            "original_and_V2_source_provenance":"SOURCE_LOCKED",
            "full_cell_physical_rate_and_geometry":"PASS",
            "additive_signed_collision_decomposition":"PASS",
            "strict_sign_reversals":flip,
            "count_chem":counts["native_chemistry"],
            "count_expanding":counts["with_expansion"],
            "source_chem_and_geometry_independence":"TWO_DIFFERENT_EXPLICIT_PHYSICAL_ASSUMPTIONS",
            "actual_Bianchi_null_ray_or_observed_CMB":"NOT_COMPUTED",
            "original_F05_tick161":"NOT_ACCEPTED",
            "REI_canonical_DAG":"28/88",
            "REC_H5_physical_DAG":"0/313"}
    destination.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"REC197_46080_SOURCE_CONDITIONAL_THOMSON_AUDIT_PASS",
      "rows":N,"strict_flips":flip,"source_sha":result["data_sha256"]}),flush=True)
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--results",required=True,type=Path)
    p.add_argument("--audit",required=True,type=Path)
    x=p.parse_args();audit(x.results,x.audit)
