#!/usr/bin/env python3
"""Original REI 26-event F05 ACCEPTED tick0 -> tick160 Thomson matter history.
No original solver or REI owner mutations; no tick161 or optical-depth sky.
"""
from __future__ import annotations
import argparse
import csv
from decimal import Decimal, localcontext
import gzip
import hashlib
import io
import json
from pathlib import Path
import struct
import tarfile
import numpy as np

TAR_NAME="ORIGINAL_REI_F05_FIRST_INTERVAL_ACCEPTED160.tar.gz"
TAR_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
INIT_NAME="ORIGINAL_REI_F05_initial_material_state_z6.npz"
INIT_SHA="7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d"
FORCE_NAME="ORIGINAL_REI_F05_canonical_time_resolved_forcing_nodes.csv"
FORCE_SHA="9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268"
ORIGINAL_ARRAY_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
EXPECTED_STATE={
  "LOCAL_NEUTRAL_HAZARD_PRIMARY":"74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6",
  "RECOMBINATION_WEIGHTED_AUDITOR":"a93c9a5f3cf95521322dc033d14a24a0ed8d4ed44a823ccb39720b0434c73b0a",
  "SCRIPT_SELF_SHIELDING_AUDITOR":"3aaff7b8cc4be8664c2d81d617d205f85f6ff974b62460a69e3839760c2fcf9c"
}
MPC_CM=Decimal("3.085677581491367e24")
C=Decimal("29979245800")
SIGMA=Decimal("6.6524587051e-25")
N=46080
T160_HEX="0x1.6afb23f875d98p+39"
FIELDS=(
  "node",
  "source_proper_volume_cm3",
  "initial_tick0_n_e_cm3",
  "accepted_tick160_n_e_lower_cm3",
  "accepted_tick160_n_e_upper_cm3",
  "accepted_tick0_Thomson_rate_s_inv",
  "accepted_tick160_Thomson_rate_lower_s_inv",
  "accepted_tick160_Thomson_rate_upper_s_inv",
  "accepted_0_to_160_DeltaThomson_rate_lower_s_inv",
  "accepted_0_to_160_DeltaThomson_rate_upper_s_inv",
  "accepted_initial_H_electron_N",
  "accepted_initial_He_electron_N",
  "accepted_0_to_160_DeltaH_electron_lower_N",
  "accepted_0_to_160_DeltaH_electron_upper_N",
  "accepted_0_to_160_DeltaHe_electron_lower_N",
  "accepted_0_to_160_DeltaHe_electron_upper_N",
  "accepted_electron_change_sign_class"
)

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def fmt(d):
    return format(d,".17E")

def decode(data):
    if data[:8]!=b"REIADP1\x00":
        raise ValueError("BAD_REIADP1_MAGIC")
    length=struct.unpack_from("<Q",data,8)[0]
    end=16+length
    if end>=len(data):
        raise ValueError("REIADP1_HEADER_TRUNCATION")
    h=json.loads(data[16:end].decode("ascii"))
    expected={"schema":1,"array_order":["population_lower","population_upper",
              "log_temperature_lower","log_temperature_upper"],
              "byte_order":"little","dtype":"float64",
              "population_shape":[N,5],"log_temperature_shape":[N]}
    if any(h.get(k)!=v for k,v in expected.items()):
        raise ValueError("REIADP1_HEADER_SCHEMA_MISMATCH")
    if len(data)-end != ((2*N*5)+(2*N))*8:
        raise ValueError("REIADP1_ARRAY_LENGTH_DRIFT")
    a=np.frombuffer(data,dtype="<f8",count=12*N,offset=end)
    lo=a[:N*5].reshape(N,5)
    hi=a[N*5:2*N*5].reshape(N,5)
    loglo=a[10*N:11*N]
    loghi=a[11*N:12*N]
    if (np.any(lo<=0) or np.any(lo>hi) or np.any(loglo>loghi)
            or not np.isfinite(a).all()):
        raise ValueError("REIADP1_PHYSICAL_INTERVAL_INVALID")
    return h["metadata"],lo,hi,loglo,loghi,hashlib.sha256(data[end:]).hexdigest()

def verify_accepted_archive(path):
    if sha(path)!=TAR_SHA:
        raise ValueError("ORIGINAL_F05_ACCEPTED_ARCHIVE_SHA_DRIFT")
    with tarfile.open(path,"r:gz") as tar:
        timeline=[]
        previous={}
        for i,(left,right,depth) in enumerate(((0,64,0),(64,128,0),(128,160,1)),start=1):
            row=json.loads(tar.extractfile(f"history/accepted_{i:08d}.json").read())
            if (row.get("accepted_index")!=i or row.get("interval")!=
                {"depth":depth,"left_tick":left,"right_tick":right}):
                raise ValueError("ORIGINAL_ACCEPTED_HISTORY_INTERVAL_DRIFT")
            if row.get("classification")!="CANDIDATE_UNSEALED_LOCAL_EXECUTION":
                raise ValueError("ORIGINAL_ACCEPTED_HISTORY_PROVENANCE_DRIFT")
            for lane in EXPECTED_STATE:
                rr=row["lanes"][lane]
                if rr["classification"]!="PASS" or rr["scientific_accept"] is not True:
                    raise ValueError("ORIGINAL_ACCEPTED_LANE_NOT_PASS")
                if i>1 and rr["parent_state_sha256"]!=previous[lane]:
                    raise ValueError("ORIGINAL_ACCEPTED_PREDECESSOR_CHAIN_BROKEN")
                previous[lane]=rr["candidate_state"]["sha256"]
            timeline.append({"accepted_index":i,"left_tick":left,"right_tick":right,
                             "history_classification":row["classification"]})
        terminal=json.loads(tar.extractfile("data/results.json").read())
        if terminal.get("accepted_tick")!=160 or terminal.get("accepted_endpoints")!=3:
            raise ValueError("F05_ACCEPTED_STOP_TICK_NOT_160")
        if terminal.get("status")!="BLOCKED_MINIMUM_STEP":
            raise ValueError("ORIGINAL_F05_TERMINAL_BLOCKER_CHANGED")
        actual=None
        for lane,expected_sha in EXPECTED_STATE.items():
            name=f"checkpoints/generations/g-00000003-tick-000160/{lane}.state"
            data=tar.extractfile(name).read()
            if hashlib.sha256(data).hexdigest()!=expected_sha or previous[lane]!=expected_sha:
                raise ValueError("ORIGINAL_ACCEPTED_STATE_BYTE_IDENTITY_DRIFT")
            md,lo,hi,tlo,thi,array_sha=decode(data)
            if array_sha!=ORIGINAL_ARRAY_SHA:
                raise ValueError("ORIGINAL_NUMERIC_STATE_ARRAY_SHA_DRIFT")
            if (md.get("accepted_index")!=3 or md.get("endpoint_tick")!=160
                  or md.get("lane")!=lane):
                raise ValueError("ORIGINAL_STATE_OWNER_METADATA_DRIFT")
            if actual is None:
                actual=(lo.copy(),hi.copy(),tlo.copy(),thi.copy())
        return actual,timeline,terminal

def z_and_time(path):
    with path.open("r",newline="") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=85:
        raise ValueError("ORIGINAL_FORCE_85_NODES_DRIFT")
    group=[r for r in rows if r["interval_index"]=="0"]
    group.sort(key=lambda r:int(r["node_index"]))
    if len(group)!=17 or [int(r["node_index"]) for r in group]!=list(range(17)):
        raise ValueError("ORIGINAL_FIRST_INTERVAL_FORCING_ORDER_DRIFT")
    zs=[Decimal(r["z_mid"]) for r in group]
    if any(z!=Decimal("5.95") for z in zs):
        raise ValueError("NONCONSTANT_ORIGINAL_SOURCE_VOLUME")
    times=[float(r["time_s"]) for r in group]
    if any(b<=a for a,b in zip(times,times[1:])) or times[0]!=0.0:
        raise ValueError("ORIGINAL_PROPER_TIME_FORCING_DRIFT")
    t160=(times[-1]-times[0])*(160/131072)
    if t160.hex()!=T160_HEX:
        raise ValueError("ORIGINAL_TICK160_CLOCK_SHA_CONTRACT_DRIFT")
    return zs[0],Decimal.from_float(t160)

def input_sources(unit):
    unit=Path(unit).resolve()
    repo=unit.parents[1]
    original=repo/"research/rec_rei_f05_native_thomson_medium_20261101/source_inputs"
    path=unit/"source_inputs"/TAR_NAME
    initial=original/INIT_NAME
    forcing=original/FORCE_NAME
    if sha(initial)!=INIT_SHA or sha(forcing)!=FORCE_SHA:
        raise ValueError("ORIGINAL_FIRST_INTERVAL_MATERIAL_OR_CLOCK_SHA_DRIFT")
    state,timeline,terminal=verify_accepted_archive(path)
    z,t160=z_and_time(forcing)
    return initial,state,z,t160,timeline,terminal

def compute(unit,out):
    unit=Path(unit).resolve()
    out=Path(out).resolve()
    if out.exists() and any(out.iterdir()):
        raise FileExistsError("DO_NOT_OVERWRITE_EXISTING_SCIENCE")
    initial,states,z,t160,timeline,terminal=input_sources(unit)
    lo,hi,tlo,thi=states
    with np.load(initial,allow_pickle=False) as src:
        if np.asarray(src["W_node"]).shape!=(N,):
            raise ValueError("ORIGINAL_FIRST_INTERVAL_NODE_COUNT")
        weights=src["W_node"].copy()
        init=np.stack([src["N_HI"],src["N_HII"],src["N_HeI"],
                       src["N_HeII"],src["N_HeIII"]],axis=1)
    if (not np.isfinite(weights).all() or np.any(weights<=0)
          or not np.isfinite(init).all() or np.any(init<=0)):
        raise ValueError("ORIGINAL_INIT_PHYSICS_INVALID")
    if abs(float(np.sum(weights))-1.0)>2e-14:
        raise ValueError("ORIGINAL_NATIVE_WEIGHT_SUM_DRIFT")
    init_h=init[:,0]+init[:,1]
    init_he=np.sum(init[:,2:5],axis=1)
    if (not np.all(np.sum(lo[:,:2],axis=1)<=init_h) or
        not np.all(np.sum(hi[:,:2],axis=1)>=init_h) or
        not np.all(np.sum(lo[:,2:5],axis=1)<=init_he) or
        not np.all(np.sum(hi[:,2:5],axis=1)>=init_he)):
        raise ValueError("ACCEPTED_F05_NUCLEI_OUTSIDE_INTERVAL")
    temp=io.StringIO(newline="")
    writer=csv.writer(temp,lineterminator="\n");writer.writerow(FIELDS)
    with localcontext() as ctx:
        ctx.prec=90
        s={k:Decimal(0) for k in ["V","e0","e160lo","e160hi","H0","He0",
                 "dHlo","dHhi","dHelo","dHehi","q0","q160lo","q160hi",
                 "definite_gain_e0","definite_loss_e0","sign_ambiguous_e0"]}
        counts={"definite_gain":0,"definite_loss":0,"sign_ambiguous":0}
        all_rows=0
        for j in range(N):
            w=Decimal.from_float(float(weights[j]))
            V=w*(MPC_CM**3)/(Decimal(1)+z)**3
            h0=Decimal.from_float(float(init[j,1]))
            he0=Decimal.from_float(float(init[j,3]))+2*Decimal.from_float(float(init[j,4]))
            e0=h0+he0
            h160lo=Decimal.from_float(float(lo[j,1]))
            h160hi=Decimal.from_float(float(hi[j,1]))
            he160lo=Decimal.from_float(float(lo[j,3]))+2*Decimal.from_float(float(lo[j,4]))
            he160hi=Decimal.from_float(float(hi[j,3]))+2*Decimal.from_float(float(hi[j,4]))
            e160lo=h160lo+he160lo
            e160hi=h160hi+he160hi
            dHlo,dHhi=h160lo-h0,h160hi-h0
            dHelo,dHehi=he160lo-he0,he160hi-he0
            de_lo,de_hi=e160lo-e0,e160hi-e0
            if V<=0 or e0<=0 or e160lo<=0 or e160lo>e160hi or de_lo>de_hi:
                raise ValueError("ORIGINAL_ACCEPTED_ELECTRON_CONE_FAILURE")
            classif="definite_gain" if de_lo>0 else "definite_loss" if de_hi<0 else "sign_ambiguous"
            counts[classif]+=1
            s[classif+"_e0"]+=e0
            n0,nlo,nhi=e0/V,e160lo/V,e160hi/V
            g0,glo,ghi=C*SIGMA*n0,C*SIGMA*nlo,C*SIGMA*nhi
            dglo,dghi=glo-g0,ghi-g0
            writer.writerow([j,*[fmt(v) for v in
                   [V,n0,nlo,nhi,g0,glo,ghi,dglo,dghi,h0,he0,
                    dHlo,dHhi,dHelo,dHehi]],classif])
            s["V"]+=V;s["e0"]+=e0;s["e160lo"]+=e160lo;s["e160hi"]+=e160hi
            s["H0"]+=h0;s["He0"]+=he0
            s["dHlo"]+=dHlo;s["dHhi"]+=dHhi;s["dHelo"]+=dHelo;s["dHehi"]+=dHehi
            s["q0"]+=e0*e0/V;s["q160lo"]+=e160lo*e160lo/V;s["q160hi"]+=e160hi*e160hi/V
            all_rows+=1
        if all_rows!=N or sum(counts.values())!=N:
            raise ValueError("ORIGINAL_46080_SOURCE_ROWS_MISSING")
        dN=[s["e160lo"]-s["e0"],s["e160hi"]-s["e0"]]
        if dN[0]>dN[1] or dN[1]>=0:
            raise ValueError("ACCEPTED_GLOBAL_ELECTRON_CHANGE_NOT_NEGATIVE")
        mean_n0=s["e0"]/s["V"]
        mean_n160=[s["e160lo"]/s["V"],s["e160hi"]/s["V"]]
        g0=C*SIGMA*mean_n0
        g160=[C*SIGMA*x for x in mean_n160]
        dg=[x-g0 for x in g160]
        cl0=s["q0"]*s["V"]/s["e0"]**2
        cl160=[s["q160lo"]*s["V"]/s["e160hi"]**2,
               s["q160hi"]*s["V"]/s["e160lo"]**2]
        def interval(x):return [fmt(v) for v in x]
        result={
            "schema":"REC_REI_ORIGINAL_ACCEPTED_0_TO_160_THOMSON_MATERIAL_V1",
            "science_scope":"ORIGINAL_F05_SOURCE_ACCEPTED_MATERIAL_ENDPOINTS_NO_INTERPOLATED_IVP",
            "material_source_repo":"cosmosapjw-quantum/rei_bianchi",
            "material_archive_sha256":TAR_SHA,
            "source_initial_npz_sha256":INIT_SHA,
            "source_forcing_sha256":FORCE_SHA,
            "original_accepted_raw_arrays_sha256":ORIGINAL_ARRAY_SHA,
            "original_accepted_primary_state_sha256":EXPECTED_STATE["LOCAL_NEUTRAL_HAZARD_PRIMARY"],
            "accepted_intervals":timeline,
            "source_archive_terminal_status":terminal["status"],
            "official_accepted_tick":160,
            "source_total_ticks":131072,
            "source_volume_model":"W_node_MPC3_OVER_1PLUSZ_CUBED",
            "source_z_first_interval":str(z),
            "source_accepted_0_to_160_seconds":fmt(t160),
            "source_physical_cells":N,
            "source_shape_lanes":3,
            "source_independent_physical_realizations":1,
            "source_total_proper_volume_cm3":fmt(s["V"]),
            "initial_global_electron_number":fmt(s["e0"]),
            "accepted160_global_electron_number":interval([s["e160lo"],s["e160hi"]]),
            "accepted_global_electron_change_N":interval(dN),
            "accepted_0_to_160_relative_global_electron_change":interval([v/s["e0"] for v in dN]),
            "initial_volume_mean_electron_density_cm3":fmt(mean_n0),
            "accepted160_volume_mean_electron_density_cm3":interval(mean_n160),
            "initial_volume_mean_Thomson_rate_s_inv":fmt(g0),
            "accepted160_volume_mean_Thomson_rate_s_inv":interval(g160),
            "accepted_0_to_160_Delta_mean_Thomson_rate_s_inv":interval(dg),
            "accepted_0_to_160_mean_rate_secant_s_inv2":interval([x/t160 for x in dg]),
            "initial_electron_clumping":fmt(cl0),
            "accepted160_electron_clumping":interval(cl160),
            "accepted_0_to_160_Delta_electron_clumping":interval([x-cl0 for x in cl160]),
            "accepted_0_to_160_H_electron_delta_N":interval([s["dHlo"],s["dHhi"]]),
            "accepted_0_to_160_He_electron_delta_N":interval([s["dHelo"],s["dHehi"]]),
            "source_native_electron_change_classes":counts,
            "original_tick0_electron_inventory_fraction_in_definite_gain_cells":fmt(s["definite_gain_e0"]/s["e0"]),
            "original_tick0_electron_inventory_fraction_in_definite_loss_cells":fmt(s["definite_loss_e0"]/s["e0"]),
            "original_tick0_electron_inventory_fraction_in_ambiguous_cells":fmt(s["sign_ambiguous_e0"]/s["e0"]),
            "sigma_T_cm2":str(SIGMA),"c_cm_s":str(C),
            "new_native_F05_IVPs":0,
            "intermediate_accepted_64_128_states":"NOT_IN_ORIGINAL_SOURCE_ARCHIVE_NOT_FABRICATED",
            "continuous_thomson_optical_depth":"NOT_COMPUTED_FROM_TWO_ENDPOINTS",
            "observed_CMB_tau":"NOT_COMPUTED","observed_polarization":"NOT_COMPUTED",
            "F05_tick161":"NOT_ACCEPTED_V2_SHADOW_ONLY",
            "REI_canonical_DAG":"28/88","REI_working_DAG":"33/88",
            "REI_physical_fast_DAG":"4/7","REC_H5_physical_DAG":"0/313",
            "canonical_delta":0,"production":"HOLD","merge":False,
            "force_push":False,"tolerance_change":False,"auto_next":False,
            "numerical_status":"SOURCE_CONDITIONAL_BINARY64_ENDPOINTS_DECIMAL_AGGREGATES_NO_FORMAL_MPFR"
        }
    out.mkdir(parents=True,exist_ok=True)
    file=out/"ORIGINAL_ACCEPTED_F05_THOMSON_CHANGE_46080.csv.gz"
    with file.open("xb") as sink:
        with gzip.GzipFile(fileobj=sink,mode="wb",mtime=0,filename="",compresslevel=6) as g:
            g.write(temp.getvalue().encode("ascii"))
    result["source_physical_csv_gzip_sha256"]=sha(file)
    (out/"SCIENCE_RESULT.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({key:result[key] for key in
        ("initial_volume_mean_Thomson_rate_s_inv",
         "accepted160_volume_mean_Thomson_rate_s_inv",
         "accepted_0_to_160_Delta_mean_Thomson_rate_s_inv",
         "accepted_0_to_160_relative_global_electron_change",
         "source_native_electron_change_classes",
         "source_physical_csv_gzip_sha256")},sort_keys=True))
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--unit-root",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    compute(a.unit_root,a.out)
