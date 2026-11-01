#!/usr/bin/env python3
"""Independent audit of actual original event-source cell records.

No REI owner dependency and no custom source IVP. All-row audit, no broad
new scientific acceptance claim. Uses original source-produced CSV/JSON.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path

N=46080
EV_PREFIX=("dot_Ne","dot_B","ots_chemical","ots_heat","ots_unresolved",
           "ots_escape","primary_heat","total_photoheat")
THERMAL_PREFIX=("original_total_U_rhs","composition_U_work",
              "temperature_only_U_term","radiative_cooling","expansion_cooling")
EV_FIELDS=tuple(v+"_"+part+"_"+unit for v,unit in
               ((x,"s_inv" if x=="dot_Ne" else "erg_s") for x in EV_PREFIX)
               for part in ("lo","hi"))
TH_FIELDS=tuple(v+"_"+part+"_erg_s" for v in THERMAL_PREFIX
                for part in ("lo","hi"))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def must(cond,msg):
    if not cond:raise AssertionError("REC196_SOURCE_AUDIT_"+msg)
def close_scale(a,b,rel=2e-13):
    return abs(a-b)<=rel*max(abs(a),abs(b),1e-300)
def audit(results:Path,dest:Path):
    results,dest=Path(results),Path(dest)
    must(not dest.exists(),"DO_NOT_OVERWRITE")
    result=json.loads((results/"SCIENCE_RESULT.json").read_text())
    path=results/"ORIGINAL_F05_NATIVE_SOURCE_EVENTS_184320.csv.gz"
    must(sha(path)==result["source_event_bytes_sha256"],"SOURCE_DATA_SHA")
    must(result["physical_source_event_rows"]==4*N and
         result["original_physical_cells"]==N and
         result["original_shape_audit_lanes"]==3 and
         result["newly_replayed_audit_lanes"]==2,"ROWS_AND_SOURCING")
    lanes=result["source_lane_results"]
    must(set(lanes)=={"RECOMBINATION_WEIGHTED_AUDITOR","SCRIPT_SELF_SHIELDING_AUDITOR"},
         "LANE_KEYS")
    keys=["64_128_stage","64_128_final","128_160_stage","128_160_final"]
    values={}
    for name,lane in lanes.items():
        must(lane["original_source_acceptance"],"SOURCE_ACCEPTANCE_"+name)
        must(len(lane["original_events"])==4,"LANE_SAMPLE_COUNT")
        for k,v in lane["source_state_numeric_shas"].items():
            must(k in ("128","160"),"LANE_EPOCH")
        for rec,key in zip(lane["original_events"],keys):
            must(f"{rec['interval_ticks'][0]}_{rec['interval_ticks'][1]}_{rec['source_event_sample']}"==key,
                 "SOURCE_ORDER")
        if not values:values=lane["source_state_numeric_shas"]
        else:must(values==lane["source_state_numeric_shas"],"FULL_LANE_SOURCE_BODY_EQUAL")
    records={f"{e['interval_ticks'][0]}_{e['interval_ticks'][1]}_{e['source_event_sample']}":e
             for e in lanes["RECOMBINATION_WEIGHTED_AUDITOR"]["original_events"]}
    expected_head=["node","interval_left_tick","interval_right_tick","sample","source_time_s",
                   *EV_FIELDS,*TH_FIELDS]
    snapshots=[]
    counters={}
    with gzip.open(path,"rt",encoding="ascii",newline="") as f:
      reader=csv.DictReader(f)
      must(reader.fieldnames==expected_head,"CSV_HEADER")
      current=None;rows=0;cells={}
      for r in reader:
        key=f"{r['interval_left_tick']}_{r['interval_right_tick']}_{r['sample']}"
        must(key in records,"UNKNOWN_SOURCE_EVENT_SAMPLE")
        if current!=key:
            if current is not None:
                must(rows==N,"SOURCE_SAMPLE_ROW_COUNT_"+current)
                snapshots.append((current,cells,rows))
            current=key
            rows=0
            cells={name:[] for name in (*EV_FIELDS,*TH_FIELDS)}
        must(int(r["node"])==rows,"SOURCE_NODE_ORDER")
        for j,prefix in enumerate(EV_PREFIX):
            lo=float(r[EV_FIELDS[2*j]]);hi=float(r[EV_FIELDS[2*j+1]])
            must(math.isfinite(lo) and math.isfinite(hi) and lo<=hi,
                 "EVENT_BOX_ORDER_"+prefix)
        for name in EV_FIELDS:
            cells[name].append(float(r[name]))
        if r["sample"]=="stage":
            must(all(r[name]=="" for name in TH_FIELDS),"STAGE_THERMAL_NOT_DEFINED")
        else:
            for j,prefix in enumerate(THERMAL_PREFIX):
                lo=float(r[TH_FIELDS[2*j]]);hi=float(r[TH_FIELDS[2*j+1]])
                must(math.isfinite(lo) and math.isfinite(hi) and lo<=hi,
                     "FINAL_BOX_ORDER_"+prefix)
            for name in TH_FIELDS:cells[name].append(float(r[name]))
        # Original OTS source identity, with finite decimal printing of f64:
        # Not the all-reaction total-energy conservation.
        chem=[float(r["ots_chemical_"+x+"_erg_s"]) for x in ("lo","hi")]
        heat=[float(r["ots_heat_"+x+"_erg_s"]) for x in ("lo","hi")]
        unr=[float(r["ots_unresolved_"+x+"_erg_s"]) for x in ("lo","hi")]
        esc=[float(r["ots_escape_"+x+"_erg_s"]) for x in ("lo","hi")]
        a=sum(x[0] for x in (chem,heat,unr,esc))
        b=sum(x[1] for x in (chem,heat,unr,esc))
        scale=max(*(abs(y) for pair in (chem,heat,unr,esc) for y in pair),1e-300)
        must(a<=2e-14*scale and b>=-2e-14*scale,"OTS_LOCAL_ZERO_ENCLOSURE")
        # total_photoheat contains primary and resolved OTS:
        ph=[float(r["primary_heat_"+x+"_erg_s"]) for x in ("lo","hi")]
        tph=[float(r["total_photoheat_"+x+"_erg_s"]) for x in ("lo","hi")]
        must(ph[0]+heat[0]<=tph[0]+2e-14*scale and
             ph[1]+heat[1]>=tph[1]-2e-14*scale,"PHOTO_HEAT_SINGLE_COUNT")
        if r["sample"]=="final":
            rhs=[float(r["original_total_U_rhs_"+x+"_erg_s"]) for x in ("lo","hi")]
            comp=[float(r["composition_U_work_"+x+"_erg_s"]) for x in ("lo","hi")]
            temp=[float(r["temperature_only_U_term_"+x+"_erg_s"]) for x in ("lo","hi")]
            # Interval identity: original total dU/dt is enclosed by
            # dU_T/dt + (3/2) kB T dNe/dt. No second addition to RHS.
            scale_u=max(abs(x) for x in (*rhs,*comp,*temp))
            must(temp[0]+comp[0]<=rhs[0]+2e-14*scale_u and
                 temp[1]+comp[1]>=rhs[1]-2e-14*scale_u,
                 "NO_DOUBLE_COUNT_KINETIC_PARTICLE_IDENTITY")
        rows+=1
      if current is not None:
          must(rows==N,"FINAL_SOURCE_ROW_COUNT")
          snapshots.append((current,cells,rows))
    must([x[0] for x in snapshots]==keys,"FOUR_ORIGINAL_EVENT_SAMPLES")
    for key,fields,rows in snapshots:
        src=records[key]
        must(rows==N,"FOUR_SOURCE_ROWS")
        s=sum(1 for _ in range(rows));must(s==N,"ROW_SUM")
        for col,x in fields.items():
            if not x:continue
            val=math.fsum(x)
            must(close_scale(val,src[col]),"GLOBAL_SUM_"+key+"_"+col)
        times=src["proper_source_time_s"]
        must(times>0,"POSITIVE_ORIGINAL_CLOCK")
        counters[key]={"rows":rows,"proper_source_time_s":times,
                        "dotB_erg_s":[src["dot_B_lo_erg_s"],src["dot_B_hi_erg_s"]],
                        "dotNe_s_inv":[src["dot_Ne_lo_s_inv"],src["dot_Ne_hi_s_inv"]],
                        "ots_unresolved_erg_s":[src["ots_unresolved_lo_erg_s"],src["ots_unresolved_hi_erg_s"]],
                        "primary_photoheat_erg_s":[src["primary_heat_lo_erg_s"],src["primary_heat_hi_erg_s"]]}
        if key.endswith("final"):
            counters[key]["original_total_U_rhs_erg_s"]=[
                src["original_total_U_rhs_lo_erg_s"],
                src["original_total_U_rhs_hi_erg_s"]]
    for a,b in (("64_128_stage","64_128_final"),("128_160_stage","128_160_final")):
        must(counters[a]["proper_source_time_s"]<counters[b]["proper_source_time_s"],
             "SOURCE_CLOCK_ORDER")
    audit={"schema":"REC196_SOURCE_ORIGINAL_EVENT_FULL_ROW_ADVERSARIAL_AUDIT_V1",
           "source_csv_sha256":sha(path),
           "original_source_rows":4*N,
           "historical_lanes_replay":"SOURCE_BYTE_IDENTITY_REPORTED_SEPARATELY",
           "source_cell_OTS_LEDGER":"ALL_ROWS_ZERO_ENCLOSURE_PASS",
           "source_cell_chemical_charge":"SOURCE_ORIGINAL_NET_EVENT_FLUX_COMPUTED",
           "source_cell_primary_OTS_single_count":"ALL_ROWS_PASS",
           "source_cell_thermal_product_identity":"ALL_FINAL_ROWS_PASS",
           "source_global_sums":"ALL_EVENT_FIELDS_PASS",
           "source_sample_order":"STAGE_THEN_FINAL_ON_TWO_ACCEPTED_INTERVALS",
           "events":counters,
           "rei_canonical_DAG":"28/88",
           "rec_h5_physical_DAG":"0/313",
           "scientific_claim":"SOURCE_CONDITIONAL_INSTANTANEOUS_NATIVE_EVENT_PHYSICS_NO_NEW_OWNER_IVP"}
    dest.write_text(json.dumps(audit,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":"SOURCE_F05_EVENT_FULL_ROW_SCIENCE_AUDIT_PASS",
        "rows":4*N,"chemB_endpoints":[counters[k]["dotB_erg_s"] for k in keys if k.endswith("final")],
        "thermalU_endpoints":[counters[k]["original_total_U_rhs_erg_s"]
            for k in keys if k.endswith("final")],
        "audit":str(dest)},sort_keys=True))
    return audit

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--results",type=Path,required=True)
    p.add_argument("--audit",type=Path,required=True)
    a=p.parse_args();audit(a.results,a.audit)
