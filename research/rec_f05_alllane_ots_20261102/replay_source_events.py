#!/usr/bin/env python3
"""True original F05 all-lane accepted-map replay + source event chemistry.

All source code/read inputs remain immutable. The only writable tree is --output.
The two missing audit shape lanes are source parity witnesses, not two new universes.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,math,subprocess,sys,tarfile
from pathlib import Path
import numpy as np

REC_PARENT="0f1f6dbd33a654a3dd49bc2d9dbe8854b572d235"
REI_OWNER="fab9429140038974a98f3ad3212036b0227e600e"
TAR_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
KERNEL_SHA="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
RECOMB="RECOMBINATION_WEIGHTED_AUDITOR"
SHIELD="SCRIPT_SELF_SHIELDING_AUDITOR"
FIRST64={RECOMB:"b9b1c383a3b697770528481f9cfa35989c61e17609c0100ef27b8c8cda337d9d",
         SHIELD:"31a763fdca76eb4d0b3fb03276342733dd1618bc2c7df22c3b00ba80691604fa"}
N=46080
EV_ERG=1.602176634e-12
K_B=1.380649e-16
CHI=np.array([0.,13.598434599702,0.,24.587389011,24.587389011+54.41776])
CHARGE=np.array([0.,1.,0.,1.,2.])
HNUC=np.array([1.,1.,0.,0.,0.])
HENUC=np.array([0.,0.,1.,1.,1.])
FIELDS=("dot_Ne_lo_s_inv","dot_Ne_hi_s_inv",
        "dot_B_lo_erg_s","dot_B_hi_erg_s",
        "ots_chemical_lo_erg_s","ots_chemical_hi_erg_s",
        "ots_heat_lo_erg_s","ots_heat_hi_erg_s",
        "ots_unresolved_lo_erg_s","ots_unresolved_hi_erg_s",
        "ots_escape_lo_erg_s","ots_escape_hi_erg_s",
        "primary_heat_lo_erg_s","primary_heat_hi_erg_s",
        "total_photoheat_lo_erg_s","total_photoheat_hi_erg_s")
FINAL_FIELDS=("original_total_U_rhs_lo_erg_s","original_total_U_rhs_hi_erg_s",
              "composition_U_work_lo_erg_s","composition_U_work_hi_erg_s",
              "temperature_only_U_term_lo_erg_s","temperature_only_U_term_hi_erg_s",
              "radiative_cooling_lo_erg_s","radiative_cooling_hi_erg_s",
              "expansion_cooling_lo_erg_s","expansion_cooling_hi_erg_s")
def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def require(ok,msg):
    if not ok:raise ValueError("REC196_ORIGINAL_F05_"+msg)
def load(name,path):
    sp=importlib.util.spec_from_file_location(name,path)
    require(sp is not None and sp.loader is not None,"IMPORT_NOT_FOUND")
    obj=importlib.util.module_from_spec(sp);sys.modules[name]=obj;sp.loader.exec_module(obj)
    return obj
def total(a):return math.fsum(map(float,np.asarray(a).ravel()))
def weighted_source(flux,weights):
    """Conservative signed interval sum of offdiagonal dest/source event fluxes."""
    require(flux.lo.shape==flux.hi.shape==(N,5,5),"ORIGINAL_EVENT_SHAPE")
    weights=np.asarray(weights,dtype=np.float64)
    d=weights[:,None]-weights[None,:]
    d=np.broadcast_to(d,flux.lo.shape)
    lower=np.sum(np.where(d>=0,d*flux.lo,d*flux.hi),axis=(1,2))
    upper=np.sum(np.where(d>=0,d*flux.hi,d*flux.lo),axis=(1,2))
    require(np.all(lower<=upper) and np.isfinite(lower).all() and np.isfinite(upper).all(),
            "FLUX_STOICHIOMETRY_INVALID")
    return lower,upper
def corners(a,b,c,d):
    x=np.stack((a*c,a*d,b*c,b*d))
    return x.min(axis=0),x.max(axis=0)
def event_fields(event):
    rate_ne=weighted_source(event.flux,CHARGE)
    rate_b=weighted_source(event.flux,CHI*EV_ERG)
    dh=weighted_source(event.flux,HNUC)
    dhe=weighted_source(event.flux,HENUC)
    require(np.all(dh[0]==0)&np.all(dh[1]==0)&np.all(dhe[0]==0)&np.all(dhe[1]==0),
            "H_HE_NUCLEAR_SOURCE")
    parts=[rate_ne,rate_b,
           (event.chemical_energy.lo,event.chemical_energy.hi),
           (event.resolved_heat.lo,event.resolved_heat.hi),
           (event.unresolved_energy.lo,event.unresolved_energy.hi),
           (event.escaped_energy.lo,event.escaped_energy.hi)]
    prim=event.photo_heat-event.resolved_heat
    parts.extend([(prim.lo,prim.hi),(event.photo_heat.lo,event.photo_heat.hi)])
    result=tuple(np.asarray(x,dtype=np.float64) for pair in parts for x in pair)
    require(len(result)==len(FIELDS) and all(x.shape==(N,) for x in result),
            "EVENT_FIELDS_SHAPE")
    require(all(np.isfinite(x).all() for x in result),"EVENT_NONFINITE")
    # This is the original OTS event identity, not a total gas energy closure.
    sum_ots=event.chemical_energy+event.resolved_heat+event.unresolved_energy+event.escaped_energy
    require(np.all(sum_ots.lo<=0)&np.all(sum_ots.hi>=0),"ORIGINAL_OTS_LEDGER")
    return result
def final_thermal(m,model,pop,logt,event,t):
    forcing=model.forcing_bounds(t,t)
    temp=m.iv.exp(logt)
    ctx=m.thermal_context(pop,forcing.volume_cm3,event.photo_heat,forcing.hubble_s_inv)
    tr=m.thermal_rhs(ctx,logt)
    expansion=ctx.expansion*temp
    cool=event.photo_heat-expansion-tr
    require(np.all(cool.lo>0)&np.all(cool.lo<=cool.hi),"ORIGINAL_PHYSICAL_COOLING")
    q=weighted_source(event.flux,CHARGE)
    correction_lo,correction_hi=corners(temp.lo,temp.hi,*q)
    correction_lo*=1.5*K_B;correction_hi*=1.5*K_B
    # The original thermal_root evolves total U, not T at fixed Ne.
    # Therefore source RHS = dot U; dot U_T = dot U - composition work.
    temp_only_lo=tr.lo-correction_hi
    temp_only_hi=tr.hi-correction_lo
    fields=(tr.lo,tr.hi,correction_lo,correction_hi,temp_only_lo,temp_only_hi,
            cool.lo,cool.hi,expansion.lo,expansion.hi)
    fields=tuple(np.asarray(x,dtype=np.float64) for x in fields)
    require(len(fields)==len(FINAL_FIELDS) and all(x.shape==(N,) for x in fields),
            "THERMAL_FIELDS_SHAPE")
    require(all(np.isfinite(x).all() for x in fields),"THERMAL_INVALID")
    return fields
def digest_numeric(fields):
    h=hashlib.sha256()
    for arr in fields:h.update(np.ascontiguousarray(arr,dtype="<f8").tobytes())
    return h.hexdigest()
def row_sums(fields,names):
    return {names[i]:total(a) for i,a in enumerate(fields)}
def assert_between(lo,hi,label):
    require(lo<=hi,"SUM_INTERVAL_"+label)
def run(rec,rei,private64,out):
    rec,rei,private64,out=map(lambda x:Path(x).resolve(),(rec,rei,private64,out))
    require(not out.exists(),"REFUSE_OVERWRITE_RESULT")
    require(subprocess.check_output(["git","-C",str(rei),"rev-parse","HEAD"],text=True).strip()==REI_OWNER,
            "REI_OWNER_HEAD_DRIFT")
    require(subprocess.run(["git","-C",str(rec),"merge-base","--is-ancestor",REC_PARENT,"HEAD"],
                           check=False).returncode==0,"REC_PARENT_DRIFT")
    parent=load("rec196_parent",rec/"research/rec_f05_accepted_trajectory_20261102/replay_and_measure.py")
    source=load("rec196_source",rei/"research/rei_f05_owner_original64_rust_20261101/execute_original64.py")
    require(sha(source.ARCHIVE)==TAR_SHA and sha(source.A/"adaptive_policy.py")==parent.ORIGINAL_POLICY_SHA,
            "ORIGINAL_TAR_POLICY_DRIFT")
    worker=source.module("rec196_owner_worker",source.A/"attempt_worker.py")
    require(sha(worker.KERNEL_PATH)==KERNEL_SHA,"ORIGINAL_SEALED_KERNEL_DRIFT")
    with tarfile.open(source.ARCHIVE,"r:gz") as z:
        receipts={}
        for ix,left,right in ((1,0,64),(2,64,128),(4,128,160)):
            row=json.load(z.extractfile(f"receipts/attempt_{ix:08d}_{left:06d}_{right:06d}.json"))
            require(row.get("action")=="ACCEPT" and row.get("classification")=="CANDIDATE_UNSEALED_LOCAL_EXECUTION",
                    "ORIGINAL_RECEIPT_STATUS")
            receipts[right]={p["lane"]:p["envelope"] for p in row["processes"]}
    for lane in FIRST64:
        for right in (64,128,160):
            e=receipts[right][lane]
            require(e["classification"]=="PASS" and e["scientific_accept"],"HISTORIC_LANE_NOT_PASS")
            if right==64: require(e["candidate_state"]["sha256"]==FIRST64[lane],"FIRST64_PARENT_HASH")
            if right==128: require(e["parent_state_sha256"]==FIRST64[lane],"FIRST128_CHAIN")
            if right==160: require(e["parent_state_sha256"]==receipts[128][lane]["candidate_state"]["sha256"],
                                   "FIRST160_CHAIN")
    worker.jax_guard.install_if_missing()
    m=worker._kernel()
    model=m.rim.ReducedIntervalModel.from_repo(rei)
    out.mkdir(parents=True)
    pub=out/"public";pub.mkdir()
    priv=out/"private";priv.mkdir()
    file=pub/"ORIGINAL_F05_NATIVE_SOURCE_EVENTS_184320.csv.gz"
    refhashes={}; lane_results={}; reference_state_arrays={}
    with file.open("xb") as fd:
      with gzip.GzipFile(fileobj=fd,filename="",mode="wb",mtime=0,compresslevel=6) as gz:
       with io.TextIOWrapper(gz,encoding="ascii",newline="",write_through=True) as txt:
        writer=csv.writer(txt,lineterminator="\n")
        writer.writerow(("node","interval_left_tick","interval_right_tick","sample","source_time_s",*FIELDS,*FINAL_FIELDS))
        for lane in (RECOMB,SHIELD):
            statepath=private64/f"{lane}.state"
            require(sha(statepath)==FIRST64[lane],"LOCKED_LANE64_STATE_SHA")
            base,y,logt,h,he=worker._context(m,lane)
            state=worker.state_io.read_state(statepath,expected_sha256=FIRST64[lane])
            require(state.metadata==parent.metadata(receipts[64][lane],64),"FIRST64_METADATA")
            require(y.shape==(N,5),"OWNER_SOURCE_SHAPE")
            previous=(m._I(state.population_lower,state.population_upper),
                      m._I(state.log_temperature_lower,state.log_temperature_upper))
            folder=priv/lane;folder.mkdir()
            lane_records=[]; lane_hashes={}
            for left,right in ((64,128),(128,160)):
                captured=[]
                native=m.run_step
                def tracked(*args,**kwargs):
                    obj=native(*args,**kwargs)
                    captured.append(obj)
                    return obj
                m.run_step=tracked
                try:
                    previous,receipt=parent.native_map(worker,m,model,base,h,he,previous,
                                                left,right,receipts[right][lane],folder)
                finally:
                    m.run_step=native
                require(len(captured)==3,"THREE_ORIGINAL_NATIVE_STEPS")
                second=captured[-1];require(second.certified and second.stage_event is not None
                                            and second.final_event is not None,"SOURCE_EVENT_MISSING")
                require(all(receipt["three_source_maps_certified"]) and receipt["all_14_ledgers_include_zero"],
                        "RECEIPT_ACCEPTANCE")
                require(max(receipt["local_error_bounds"].values())<2e-4 and
                        max(receipt["source_interval_widths"].values())<2e-3,
                        "ORIGINAL_NO_TOLERANCE_RELAXATION")
                pop,logt=previous
                for value in (pop.lo,pop.hi,logt.lo,logt.hi):
                    require(value.shape[0]==N,"ENDPOINT_SHAPE")
                sh=hsh=hashlib.sha256(b"".join(v.astype("<f8",copy=False).tobytes()
                         for v in (pop.lo,pop.hi,logt.lo,logt.hi))).hexdigest()
                lane_hashes[str(right)]=sh
                if lane==RECOMB:reference_state_arrays[right]=sh
                else:require(sh==reference_state_arrays[right],"CROSS_LANE_ENDSTATE_PHYSICS")
                duration=float(base.forcing.duration_seconds(0))
                mid=duration*((left+right)/(2*parent.TICKS))
                t1=duration*(right/parent.TICKS)
                stage_t=mid+m.sdirk.GAMMA*(t1-mid)
                for label,time_s,event in (("stage",stage_t,second.stage_event),
                                           ("final",t1,second.final_event)):
                    fields=event_fields(event)
                    refkey=f"{left}_{right}_{label}"
                    etag=digest_numeric(fields)
                    # Strict cross-lane equality of 16 native numeric flux-derived fields.
                    if lane==RECOMB: refhashes[refkey]=etag
                    else:require(refhashes[refkey]==etag,"CROSS_LANE_PHYSICAL_EVENT_"+refkey)
                    # Thermal source at this actual original final event:
                    # re-evaluate the same original owner operator on the
                    # accepted endpoint box, not a made-up interpolation.
                    therm=None
                    if label=="final":
                        exact=m.event_box(model,pop,m.iv.exp(logt),t1)
                        therm=final_thermal(m,model,pop,logt,exact,t1)
                    summary=row_sums(fields,FIELDS)
                    if therm is not None:summary.update(row_sums(therm,FINAL_FIELDS))
                    summary["interval_ticks"]=[left,right]
                    summary["source_event_sample"]=label
                    summary["proper_source_time_s"]=time_s
                    summary["numeric_event_payload_sha256"]=etag
                    lane_records.append(summary)
                    if lane==RECOMB:
                        for j in range(N):
                            writer.writerow((j,left,right,label,format(time_s,".17e"),
                              *(format(float(f[j]),".17e") for f in fields),
                              *(format(float(f[j]),".17e") if therm is not None else ""
                                for f in (therm if therm is not None else [None]*len(FINAL_FIELDS)))))
                del captured,second
            lane_results[lane]={"source_state_numeric_shas":lane_hashes,
                                "original_source_acceptance":True,
                                "original_events":lane_records}
    require(len(refhashes)==4,"ACTUAL_ORIGINAL_SOURCE_SAMPLES")
    res={"schema":"REC_ORIGINAL_F05_ALLLANE_STAGE_OTS_EVENT_V1",
         "source_original_tar_sha256":TAR_SHA,
         "source_original_kernel_sha256":KERNEL_SHA,
         "source_REI_owner_head":REI_OWNER,
         "source_REC_parent_head":REC_PARENT,
         "original_source_physical_realizations":1,
         "original_shape_audit_lanes":3,
         "newly_replayed_audit_lanes":2,
         "original_physical_cells":N,
         "physical_source_stage_samples_per_cell":4,
         "physical_source_event_rows":4*N,
         "official_original_tick":"160/131072",
         "original_hist_source_intervals":[[64,128],[128,160]],
         "source_lane_results":lane_results,
         "source_event_bytes_sha256":sha(file),
         "cross_lane_event_fields":"EXACT_NUMERIC_PAYLOAD_EQUAL",
         "source_energy_scope":"ORIGINAL_26_EVENT_NET_CHEMICAL_OTS_AND_KINETIC_SOURCE_POINTWISE",
         "new_authoritative_owner_accepted_tick":False,
         "rei_canonical_DAG":"28/88",
         "rei_working_DAG":"33/88",
         "rei_physical_fast_DAG":"4/7",
         "rec_h5_physical_DAG":"0/313",
         "production":"HOLD","original_tick161":"NOT_ACCEPTED"}
    (pub/"SCIENCE_RESULT.json").write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"ORIGINAL_F05_ALLLANE_EVENT_PHYSICS_READY",
       "rows":4*N,"sha_csv":res["source_event_bytes_sha256"],
       "tick128":list(v["source_state_numeric_shas"]["128"] for v in lane_results.values()),
       "Bdot_final":[x["dot_B_lo_erg_s"] for x in lane_results[RECOMB]["original_events"]
                      if x["source_event_sample"]=="final"],
       "thermalRHS_final":[x.get("original_total_U_rhs_lo_erg_s") for x in
               lane_results[RECOMB]["original_events"] if x["source_event_sample"]=="final"]},
               sort_keys=True),flush=True)
    return res

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--rec",type=Path,required=True)
    p.add_argument("--rei",type=Path,required=True)
    p.add_argument("--first64-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();run(a.rec,a.rei,a.first64_dir,a.output)
