#!/usr/bin/env python3
"""REC consumer of immutable REI352 native H/He tick161 candidate material.

Physical output: helium-resolved TOTAL Thomson scattering cross-sectional AREA,
signed native tick electron-number change, spatial sign classifications.
No spatial density, null path, CMB tau, F05 acceptance or new IVP is generated.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, localcontext
import gzip
import hashlib
import json
from pathlib import Path

SOURCE_NAME = "ORIGINAL_REI_F05_TICK161_PHYSICAL_CANDIDATE_46080.csv.gz"
RECEIPT_NAME = "ORIGINAL_NATIVE_TICK160_161_FAILURE_RECEIPT.json"
SOURCE_SHA256 = "713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d"
RECEIPT_SHA256 = "63d7d32a52073f370f70ce22e97b60bbb4c6fc4499c6737e9d7f8ee79b3fc780"
SIGMA_T_CM2 = Decimal("6.6524587051e-25")
C_CM_S = Decimal("29979245800")
N = 46080
ORIGINAL_SOURCE_PR = 352
ORIGINAL_SOURCE_HEAD = "ea8d6bf94197392c69f939f03c1673ed3afe349c"
ORIGINAL_PARENT_STATE_SHA = "cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
ORIGINAL_KERNEL_SHA = "579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
ORIGINAL_SOURCE_TAR_SHA = "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
T0_HEX = "0x1.6afb23f875d98p+39"
T1_HEX = "0x1.6d3fe8fed02fap+39"
EXPECTED_FIELDS = (
    "node","source_H_nuclei_N_lower","source_H_nuclei_N_upper",
    "source_He_nuclei_N_lower","source_He_nuclei_N_upper",
    "tick160_xHII_lower","tick160_xHII_upper",
    "tick161_preview_xHII_lower","tick161_preview_xHII_upper",
    "tick161_preview_xHeII_lower","tick161_preview_xHeII_upper",
    "tick161_preview_xHeIII_lower","tick161_preview_xHeIII_upper",
    "tick160_Tgas_K_lower","tick160_Tgas_K_upper",
    "tick161_preview_Tgas_K_lower","tick161_preview_Tgas_K_upper",
    "tick160_electron_count_N_lower","tick160_electron_count_N_upper",
    "tick161_preview_electron_count_N_lower","tick161_preview_electron_count_N_upper",
    "tick161_preview_U_erg_lower","tick161_preview_U_erg_upper",
    "tick160_to_161_delta_logT_lower","tick160_to_161_delta_logT_upper",
    "tick160_to_161_delta_electron_N_lower","tick160_to_161_delta_electron_N_upper"
)

def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_clock(receipt:dict)->Decimal:
    if receipt.get("interval") != {"depth":6,"left_tick":160,"right_tick":161}:
        raise ValueError("SOURCE_TICK_OR_ORIGINAL_INTERVAL_DRIFT")
    if receipt.get("accepted_parent_tick") != 160:
        raise ValueError("ORIGINAL_ACCEPTED_PARENT_TICK_CHANGED")
    procs=receipt.get("processes",[])
    if len(procs)!=3:
        raise ValueError("ORIGINAL_THREE_SHAPE_LANE_SOURCE_MISSING")
    for p in procs:
        e=p["envelope"]
        if (e["interval"] != {"depth":6,"left_tick":160,"right_tick":161}
            or e["time"] != {"t0_hex":T0_HEX,"t1_hex":T1_HEX}
            or e["classification"] != "VALIDATED_LOCAL_ERROR_GATE_FAILURE"
            or e["scientific_accept"] is not False):
            raise ValueError("HISTORICAL_SOURCE_REJECTION_OR_CLOCK_DRIFT")
    h=Decimal.from_float(float.fromhex(T1_HEX))-Decimal.from_float(float.fromhex(T0_HEX))
    if h <= 0:
        raise ValueError("NONPOSITIVE_ORIGINAL_PROPER_TICK")
    return h


def locked_inputs(root:Path)->tuple[Path,dict,Decimal]:
    d=root/"source_inputs"
    file=d/SOURCE_NAME
    receipt=d/RECEIPT_NAME
    if sha256(file)!=SOURCE_SHA256 or sha256(receipt)!=RECEIPT_SHA256:
        raise ValueError("ORIGINAL_F05_SOURCE_OR_CLOCK_BYTES_CHANGED")
    packet=json.loads(receipt.read_bytes())
    return file,packet,source_clock(packet)


def result_format(d:Decimal)->str:
    # Deterministic 18 significant figures, not a formal outward interval cast.
    return format(d,".17E")


def compute(root:Path,out:Path)->dict:
    root=Path(root);out=Path(out)
    source,receipt,h=locked_inputs(root)
    with localcontext() as ctx:
        ctx.prec=90
        fields=("nh_lo","nh_hi","nhe_lo","nhe_hi","e160_lo","e160_hi",
                "e161_lo","e161_hi","de_lo","de_hi",
                "he161_lo","he161_hi","h161_lo","h161_hi",
                "positive_e160_lo","positive_e160_hi",
                "positive_de_lo","positive_de_hi",
                "negative_de_lo","negative_de_hi")
        s={k:Decimal(0) for k in fields}
        count={"definite_local_increase":0,"definite_local_decrease":0,
               "ambiguous_local_sign":0}
        nrows=0
        sample_nodes=[]
        with gzip.open(source,"rt",encoding="ascii",newline="") as fd:
            reader=csv.DictReader(fd)
            if tuple(reader.fieldnames or ()) != EXPECTED_FIELDS:
                raise ValueError("SOURCE_H_HE_ELECTRON_FIELD_CONTRACT_CHANGED")
            for row in reader:
                if int(row["node"])!=nrows:
                    raise ValueError("ORIGINAL_SOURCE_NODE_IDENTITY_NOT_CONTIGUOUS")
                nrows+=1
                q=lambda name: Decimal(row[name])
                values={name:q(name) for name in EXPECTED_FIELDS[1:]}
                if not all(v.is_finite() for v in values.values()):
                    raise ValueError("NONFINITE_ORIGINAL_NATIVE_SOURCE")
                for label in ("source_H_nuclei_N","source_He_nuclei_N",
                              "tick160_xHII","tick161_preview_xHII",
                              "tick161_preview_xHeII","tick161_preview_xHeIII",
                              "tick160_Tgas_K","tick161_preview_Tgas_K",
                              "tick160_electron_count_N","tick161_preview_electron_count_N",
                              "tick161_preview_U_erg",
                              "tick160_to_161_delta_logT",
                              "tick160_to_161_delta_electron_N"):
                    if values[label+"_lower"]>values[label+"_upper"]:
                        raise ValueError("INVERTED_ORIGINAL_NATIVE_INTERVAL_"+label)
                for label in ("source_H_nuclei_N","source_He_nuclei_N",
                              "tick160_electron_count_N","tick161_preview_electron_count_N",
                              "tick160_Tgas_K","tick161_preview_Tgas_K"):
                    if values[label+"_lower"]<=0:
                        raise ValueError("NONPOSITIVE_ORIGINAL_SOURCE_"+label)
                for label in ("tick161_preview_xHII","tick161_preview_xHeII",
                              "tick161_preview_xHeIII"):
                    if values[label+"_lower"]<0 or values[label+"_upper"]>1:
                        raise ValueError("ORIGINAL_NATIVE_SPECIES_FRACTION_UNPHYSICAL")
                if (values["tick161_preview_xHeII_upper"]+
                    values["tick161_preview_xHeIII_upper"])>1:
                    raise ValueError("ORIGINAL_HE_SPECIES_COUNT_OVERFILLED")
                Hlo=values["source_H_nuclei_N_lower"]*values["tick161_preview_xHII_lower"]
                Hhi=values["source_H_nuclei_N_upper"]*values["tick161_preview_xHII_upper"]
                Helo=values["source_He_nuclei_N_lower"]*(values["tick161_preview_xHeII_lower"]+
                                                         2*values["tick161_preview_xHeIII_lower"])
                Hehi=values["source_He_nuclei_N_upper"]*(values["tick161_preview_xHeII_upper"]+
                                                         2*values["tick161_preview_xHeIII_upper"])
                Elo=values["tick161_preview_electron_count_N_lower"]
                Ehi=values["tick161_preview_electron_count_N_upper"]
                if Hlo+Helo>Ehi or Hhi+Hehi<Elo:
                    raise ValueError("ORIGINAL_ELECTRON_CHARGE_ENCLOSURE_DISJOINT")
                E160lo=values["tick160_electron_count_N_lower"]
                E160hi=values["tick160_electron_count_N_upper"]
                Dlo=values["tick160_to_161_delta_electron_N_lower"]
                Dhi=values["tick160_to_161_delta_electron_N_upper"]
                if Dlo > Ehi-E160lo or Dhi < Elo-E160hi:
                    raise ValueError("ORIGINAL_CORRELATED_ELECTRON_INCREMENT_DISJOINT")
                for name,v in (
                    ("nh_lo",values["source_H_nuclei_N_lower"]),
                    ("nh_hi",values["source_H_nuclei_N_upper"]),
                    ("nhe_lo",values["source_He_nuclei_N_lower"]),
                    ("nhe_hi",values["source_He_nuclei_N_upper"]),
                    ("e160_lo",E160lo),("e160_hi",E160hi),("e161_lo",Elo),
                    ("e161_hi",Ehi),("de_lo",Dlo),("de_hi",Dhi),
                    ("he161_lo",Helo),("he161_hi",Hehi),
                    ("h161_lo",Hlo),("h161_hi",Hhi)
                ):
                    s[name]+=v
                if Dlo>0:
                    count["definite_local_increase"]+=1
                    s["positive_e160_lo"]+=E160lo
                    s["positive_e160_hi"]+=E160hi
                    s["positive_de_lo"]+=Dlo
                    s["positive_de_hi"]+=Dhi
                    if len(sample_nodes)<3:sample_nodes.append({"node":nrows-1,"kind":"INCREASE"})
                elif Dhi<0:
                    count["definite_local_decrease"]+=1
                    s["negative_de_lo"]+=Dlo
                    s["negative_de_hi"]+=Dhi
                else:
                    count["ambiguous_local_sign"]+=1
                    if len(sample_nodes)<6:sample_nodes.append({"node":nrows-1,"kind":"AMBIGUOUS"})
        if nrows!=N or sum(count.values())!=N:
            raise ValueError("INCOMPLETE_46080_ORIGINAL_PHYSICAL_CELLS")
        if not (s["de_hi"]<0 and s["e161_lo"]>0 and s["nh_lo"]>0):
            raise ValueError("NONNEGATIVE_F05_GLOBAL_RECOMBINATION_CHANGE")
        if not (s["e161_lo"]-s["e160_hi"]<=s["de_hi"] and
                s["e161_hi"]-s["e160_lo"]>=s["de_lo"]):
            raise ValueError("GLOBAL_SOURCE_INCREMENT_OUTSIDE_ENDPOINT_BOX")
        area161=(SIGMA_T_CM2*s["e161_lo"],SIGMA_T_CM2*s["e161_hi"])
        delta_area=(SIGMA_T_CM2*s["de_lo"],SIGMA_T_CM2*s["de_hi"])
        he_frac=(s["he161_lo"]/s["e161_hi"],s["he161_hi"]/s["e161_lo"])
        h_frac=(s["h161_lo"]/s["e161_hi"],s["h161_hi"]/s["e161_lo"])
        xe_H=(s["e161_lo"]/s["nh_hi"],s["e161_hi"]/s["nh_lo"])
        delta_xe=(s["de_lo"]/s["nh_lo"],s["de_hi"]/s["nh_hi"])
        delta_frac=(s["de_lo"]/s["e160_lo"],s["de_hi"]/s["e160_hi"])
        positive_cell_weight=(s["positive_e160_lo"]/s["e160_hi"],
                              s["positive_e160_hi"]/s["e160_lo"])
        area_rate=(delta_area[0]/h,delta_area[1]/h)
        e_rate=(s["de_lo"]/h,s["de_hi"]/h)
        if not (he_frac[0]>0 and he_frac[1]<1 and he_frac[0]<=he_frac[1]):
            raise ValueError("INVALID_PHYSICAL_HELIUM_ELECTRON_FRACTION")
        if not (positive_cell_weight[1]<Decimal("0.001")):
            raise ValueError("MISWEIGHTED_LOCAL_ELECTRON_GAINS")
        # Source candidate computed physical nuclei counts: not electron density.
        machine={
          "schema":"REC_REI_ORIGINAL_F05_TICK161_THOMSON_SCATTERING_CAPACITY_V1",
          "scope":"SOURCE_CONDITIONAL_NONAUTHORITATIVE_ORIGINAL_26EVENT_CHEMISTRY",
          "input_rei_source_pr":ORIGINAL_SOURCE_PR,
          "input_rei_source_head":ORIGINAL_SOURCE_HEAD,
          "source_gzip_sha256":SOURCE_SHA256,
          "original_rejected_attempt_receipt_sha256":RECEIPT_SHA256,
          "original_source_tar_sha256":ORIGINAL_SOURCE_TAR_SHA,
          "original_accepted_state_array_sha256":ORIGINAL_PARENT_STATE_SHA,
          "original_kernel_sha256":ORIGINAL_KERNEL_SHA,
          "original_tick":160,"candidate_tick":161,
          "original_worker_acceptance":"FAILED_UNCHANGED",
          "original_historical_logT_upper":"2.1245050576368385e-4",
          "original_unchanged_strict_gate":"2e-4",
          "source_physical_cells":nrows,
          "source_shape_lanes":3,"independent_source_populations":1,
          "sigma_T_original_REI_F08_cm2":str(SIGMA_T_CM2),
          "c_cm_per_s":str(C_CM_S),
          "native_proper_tick_seconds":result_format(h),
          "source_t0_hex":T0_HEX,"source_t1_hex":T1_HEX,
          "new_original_ivps":0,"new_evolved_source_states":0,
          "global_electron_160_N":[result_format(s["e160_lo"]),result_format(s["e160_hi"])],
          "global_electron_161_candidate_N":[result_format(s["e161_lo"]),result_format(s["e161_hi"])],
          "global_electron_delta_N":[result_format(s["de_lo"]),result_format(s["de_hi"])],
          "native_H_nuclei_N":[result_format(s["nh_lo"]),result_format(s["nh_hi"])],
          "native_He_nuclei_N":[result_format(s["nhe_lo"]),result_format(s["nhe_hi"])],
          "source_H_electron_161_N":[result_format(s["h161_lo"]),result_format(s["h161_hi"])],
          "source_He_electron_161_N":[result_format(s["he161_lo"]),result_format(s["he161_hi"])],
          "electron_fraction_per_H_global_161_candidate":[result_format(x) for x in xe_H],
          "electron_fraction_per_H_delta_per_tick":[result_format(x) for x in delta_xe],
          "He_fraction_of_total_electrons_161_candidate":[result_format(x) for x in he_frac],
          "H_fraction_of_total_electrons_161_candidate":[result_format(x) for x in h_frac],
          "Thomson_scattering_area_161_cm2":[result_format(x) for x in area161],
          "Thomson_scattering_area_delta_cm2":[result_format(x) for x in delta_area],
          "Thomson_scattering_area_rate_cm2_s":[result_format(x) for x in area_rate],
          "electron_number_rate_per_s":[result_format(x) for x in e_rate],
          "relative_electron_change_per_tick":[result_format(x) for x in delta_frac],
          "local_electron_change_classes":count,
          "mass_weighted_fraction_in_definitely_increasing_cells":[result_format(x) for x in positive_cell_weight],
          "definite_increase_electron_delta_N":[result_format(s["positive_de_lo"]),result_format(s["positive_de_hi"])],
          "definite_decrease_electron_delta_N":[result_format(s["negative_de_lo"]),result_format(s["negative_de_hi"])],
          "sample_original_node_sign_witnesses":sample_nodes,
          "no_cell_volume_or_null_paths_in_this_source":True,
          "cosmological_LoS_tau":"NOT_COMPUTABLE_FROM_TOTAL_N_ONLY",
          "observed_CMB_visibility":"NOT_COMPUTED",
          "rei_original_accepted_tick":"160/131072",
          "rei_canonical":"28/88","rei_working":"33/88",
          "rei_physical_fast":"4/7","rec_H5_physical":"0/313",
          "canonical_delta":0,"production":"HOLD",
          "source_owner_swap":False,"merge":False,"force_push":False,
          "tolerance_change":False,"auto_next_node":False
        }
        out.mkdir(parents=True,exist_ok=True)
        path=out/"SCIENCE_RESULT.json"
        path.write_text(json.dumps(machine,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({k:machine[k] for k in [
           "source_physical_cells","native_proper_tick_seconds",
           "global_electron_delta_N","Thomson_scattering_area_delta_cm2",
           "He_fraction_of_total_electrons_161_candidate",
           "local_electron_change_classes","rei_canonical"]},sort_keys=True))
        return machine


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--unit-root",type=Path,default=Path(__file__).resolve().parent)
    ap.add_argument("--out",type=Path,required=True)
    ns=ap.parse_args()
    compute(ns.unit_root,ns.out)
