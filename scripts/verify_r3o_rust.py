#!/usr/bin/env python3
"""One bounded numerical/contract pass of an already built R3O Rust caller.

Authenticates R3M raw producers using load_reviewed_u6_boundary; independently
advances Python, invokes the standalone Rust/C and VigilODE lanes, then exercises
expected short partial failure, failed callbacks and malformed request contracts.
No compilation occurs here. Full 153327 steps and convergence/speedup are NOT_RUN.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import signal
import struct
import sys
import time
import traceback
sys.dont_write_bytecode = True
for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "RAYON_NUM_THREADS"):
    os.environ[_key] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"src"))
from build_r3o_rust import Budget, cpu, dump_new, reserve, sha256, own_code_hashes, ensure_vigilode, ORIGINAL_ZIP, PACKAGE

DEFAULT_PACKET = PACKAGE/"fixtures/r3m_u6_boundary.json"


def read_json(path):
    def reject(s):
        raise ValueError(f"R3O_JSON_NONFINITE:{s}")
    value = json.loads(Path(path).read_text(), parse_constant=reject)
    finite_tree(value)
    return value


def finite_tree(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("R3O_NONFINITE_OUTPUT")
    if isinstance(value, dict):
        for item in value.values(): finite_tree(item)
    elif isinstance(value, list):
        for item in value: finite_tree(item)


FIELDS = ("xe","Tm_K","hydrogen_prev","hydrogen_prev2","thermal_prev","thermal_prev2")


def bits(cp):
    return [struct.pack(">d",cp[k]).hex() for k in FIELDS]


def make_boundary_packet(boundary):
    from full_bianchi_hyrec.trajectory.primordial_2012_refined_low_z import (
        HyRec2012Cosmology,U5_CHECKPOINT_SHA256,SOURCE_ZIP_SHA256)
    states={lane:asdict(boundary[lane]) for lane in ("native","python")}
    c=HyRec2012Cosmology()
    return {"schema":"rec.r3o.derived-u6-boundary.v1",
        "representation":"DERIVED_BOUNDARY_PACKET_NOT_FULL_PRODUCER_ARTIFACT",
        "scope":"Six scalars per native/Python boundary: xe, Tm_K and four original predictor memories. No photon or full trajectory arrays.",
        "global_iz":58389,"h2":4.245e-5,"end_iz":211716,"source_nz":211717,
        "states":states,"state_fields":list(FIELDS),
        "binary64_hex":{lane:bits(states[lane]) for lane in states},
        "h2_binary64_hex":struct.pack(">d",4.245e-5).hex(),
        "cosmology":asdict(c),"source_zip_sha256":SOURCE_ZIP_SHA256,
        "u5_checkpoint_sha256":U5_CHECKPOINT_SHA256,
        "original_producer_inputs_sha256":boundary["inputs_sha256"],
        "parent_review":boundary["parent_review"],"producer_status_preserved":boundary["producer_status_preserved"],
        "historical_status":boundary["historical_status"],
        "derivation":"load_reviewed_u6_boundary authenticates all three full R3M files and original ZIP before and after extraction; native and Python tails remain separate",
        "reader_source_sha256":sha256(ROOT/"src/full_bianchi_hyrec/trajectory/primordial_2012_refined_low_z.py")}


def load_boundary_packet(path, source_zip):
    from full_bianchi_hyrec.trajectory.primordial_2012_refined_low_z import (
        LowZCheckpoint,HyRec2012Cosmology,R3M_FILES,SOURCE_ZIP_SHA256,U5_CHECKPOINT_SHA256,
        HISTORICAL_STATUS,source_stage_guard)
    path=Path(path)
    # The checked-in digest is itself covered by the build's code/fixture seal.
    seal=DEFAULT_PACKET.with_suffix(".sha256")
    expected=seal.read_text().strip().split()[0]
    if sha256(path)!=expected:
        raise ValueError("R3O_DERIVED_PACKET_HASH")
    packet=read_json(path)
    c=HyRec2012Cosmology()
    if (packet["schema"]!="rec.r3o.derived-u6-boundary.v1"
            or packet["representation"]!="DERIVED_BOUNDARY_PACKET_NOT_FULL_PRODUCER_ARTIFACT"
            or packet["global_iz"]!=58389 or packet["end_iz"]!=211716 or packet["h2"]!=4.245e-5
            or packet["source_nz"]!=211717 or packet["state_fields"]!=list(FIELDS)
            or packet["cosmology"]!=asdict(c) or packet["historical_status"]!=HISTORICAL_STATUS
            or packet["source_zip_sha256"]!=SOURCE_ZIP_SHA256
            or packet["u5_checkpoint_sha256"]!=U5_CHECKPOINT_SHA256
            or packet["original_producer_inputs_sha256"]!={**R3M_FILES,"source_zip":SOURCE_ZIP_SHA256}
            or sha256(source_zip)!=SOURCE_ZIP_SHA256
            or packet["h2_binary64_hex"]!=struct.pack(">d",4.245e-5).hex()
            or packet["reader_source_sha256"]!=sha256(ROOT/"src/full_bianchi_hyrec/trajectory/primordial_2012_refined_low_z.py")):
        raise ValueError("R3O_DERIVED_PACKET_PIN_OR_COSMOLOGY")
    states={}
    for lane in ("native","python"):
        cp=packet["states"][lane]
        if bits(cp)!=packet["binary64_hex"][lane] or cp["iz"]!=58389 or cp["peebles_event_iz"] is not None:
            raise ValueError("R3O_DERIVED_PACKET_EXACT_STATE")
        states[lane]=LowZCheckpoint(**cp)
        states[lane].validate(c)
        if not source_stage_guard(c,c.redshift(58389),states[lane].Tm_K)[0]:
            raise ValueError("R3O_DERIVED_PACKET_INITIAL_STAGE")
    return {**states,"inputs_sha256":packet["original_producer_inputs_sha256"],
        "parent_review":packet["parent_review"],"producer_status_preserved":packet["producer_status_preserved"],
        "historical_status":packet["historical_status"],"packet":packet}


def packet_command(args):
    """Read-only full producer intake; exporting/readback advances zero steps."""
    from full_bianchi_hyrec.trajectory.primordial_2012_refined_low_z import load_reviewed_u6_boundary,input_hashes
    ev=reserve(args.output);budget=Budget(ev,cpu_s=20.,wall_s=60.)
    record={"schema":"rec.r3o.boundary-packet-intake.v1","command":sys.argv,"physical_steps":0,"status":"FAILED"}
    code_before=own_code_hashes();exit_code=2
    try:
        record["inputs_before"]=input_hashes(args.raw_dir,args.source_zip)
        boundary=load_reviewed_u6_boundary(args.raw_dir,args.source_zip)
        packet=make_boundary_packet(boundary)
        budget.check()
        if args.export_boundary_packet:
            path=args.export_boundary_packet.resolve()
            path.parent.mkdir(parents=True,exist_ok=True)
            dump_new(path,packet)
            digest=sha256(path)
            with path.with_suffix(".sha256").open("x") as stream:
                stream.write(digest+"  "+path.name+"\n")
            record["status"]="DERIVED_BOUNDARY_PACKET_EXPORTED_FROM_VERIFIED_FULL_RAW"
        else:
            path=args.check_boundary_packet.resolve()
            observed=load_boundary_packet(path,args.source_zip)["packet"]
            if observed!=packet:
                raise ValueError("R3O_DERIVED_PACKET_FULL_RAW_READBACK_MISMATCH")
            digest=sha256(path)
            record["status"]="DERIVED_BOUNDARY_PACKET_MATCHES_REVIEWED_FULL_RAW"
        record.update(packet_path=str(path),packet_sha256=digest)
        exit_code=0
    except BaseException as exc:
        record["failure"]={"type":type(exc).__name__,"message":str(exc)}
        with (ev/"exception.txt").open("x") as stream:traceback.print_exc(file=stream)
    finally:
        record["inputs_after"]=input_hashes(args.raw_dir,args.source_zip)
        record["code_before"]=code_before;record["code_after"]=own_code_hashes()
        if (record["inputs_after"]!=record.get("inputs_before")
                or any(record["code_after"].get(k)!=v for k,v in code_before.items())):
            record["status"]="FAILED";record["identity_failure"]="INPUT_OR_EXISTING_CODE_MUTATION";exit_code=2
        record["process_tree_cpu_s"]=cpu()-budget.start_cpu
        record["wall_s"]=time.monotonic()-budget.start_wall
        if record["process_tree_cpu_s"]>20. or record["wall_s"]>60.:
            record["status"]="FAILED";record["resource_failure"]="PACKET_INTAKE_BUDGET";exit_code=2
        record["exit_code"]=exit_code
        dump_new(ev/"packet_receipt.json",record)
        print(json.dumps({k:record.get(k) for k in ("status","packet_sha256","process_tree_cpu_s","wall_s","failure")}))
    return exit_code


def validate_primary(out, request):
    n = request["steps"]
    if out["status"] != "BOUNDED_PASS" or out["exit_code"] != 0:
        raise ValueError("R3O_PRIMARY_DID_NOT_PASS")
    fixed = out["fixed"]
    rows = fixed["rows"]
    if len(rows) != n+1 or not fixed["success"] or fixed["work"]["accepted_steps"] != n:
        raise ValueError("R3O_FIXED_ROW_COUNT")
    if bits(rows[0]["rust"]) != bits(request["native"]):
        raise ValueError("R3O_NATIVE_INITIAL_JSON_ROUNDTRIP")
    maxima = [0.]*6
    rhs_max = [0.,0.]
    for i in range(n+1):
        row = rows[i]
        r, c, p = row["rust"], row["original_c"], request["python_states"][i]
        if bits(r) != bits(c) or bits(r) != row["rust_bits"] or bits(c) != row["original_c_bits"]:
            raise ValueError(f"R3O_EXTERNAL_SIX_SCALAR_BYTE_IDENTITY:{i}")
        if r["iz"] != 58389+i or c["iz"] != r["iz"] or row["python"] != p:
            raise ValueError("R3O_FIXED_EXTERNAL_TIME_OR_PYTHON_IDENTITY")
        for event in ("peebles_event_iz","peebles_event_reason"):
            if r[event] != c[event] or r[event] != p[event]:
                raise ValueError("R3O_FIXED_EXTERNAL_STAGE_IDENTITY")
        for k, field in enumerate(FIELDS):
            scale = max(abs(c[field]),1e-8 if k == 0 else 1.)
            value = abs(c[field]-p[field])/scale
            maxima[k] = max(maxima[k],value)
            if value > (5e-9 if k == 0 else 5e-10 if k == 1 else 2e-8):
                raise ValueError(f"R3O_FROZEN_STATE_TOLERANCE:{field}")
        if i<n:
            common = row["common_input_rhs"]
            if common["python_rhs"] != request["python_rhs"][i] or len(common["c_rhs"])!=2 or common["model"]!=2:
                raise ValueError("R3O_COMMON_RHS_SHAPE_OR_MODEL")
            p0,p1 = request["python_rhs"][i]
            c0,c1 = common["c_rhs"]
            rs = [abs(p0-c0)/max(abs(p0),abs(c0),1e-13),abs(p1-c1)/max(abs(c1),1.)]
            for k in range(2): rhs_max[k] = max(rhs_max[k],rs[k])
            if rs[0]>3e-10 or rs[1]>2e-10:
                raise ValueError("R3O_FROZEN_RHS_TOLERANCE")
    if not fixed["absorbing_input_stage_contract"]["success"]:
        raise ValueError("R3O_ABSORBING_STAGE_CONTRACT")
    diag = out["diagnostic"]
    if (not diag["success"] or diag["classification"]!="EXPLORATORY_METHOD_COMPARISON"
            or diag["autonomous"] is not False or diag["dense_interpolation"] is not False
            or diag["same_algorithm_parity"] is not False or diag["production_admission"] is not False
            or len(diag["times"])!=n+1 or len(diag["normalized_states"])!=n+1
            or len(diag["physical_states"])!=n+1 or diag["attempts"]>32 or diag["internal_steps"]>32):
        raise ValueError("R3O_EXPLORATORY_DIAGNOSTIC_CONTRACT")
    expected = [4.245e-5*i for i in range(n+1)]
    for i in range(n+1):
        if struct.pack(">d",diag["times"][i]) != struct.pack(">d",expected[i]):
            raise ValueError("R3O_DIAGNOSTIC_TIME_BYTE_IDENTITY")
        if len(diag["physical_states"][i])!=2 or len(diag["normalized_states"][i])!=2:
            raise ValueError("R3O_DIAGNOSTIC_STATE_SHAPE")
    if diag["work"]["ft_calls"]<=0 or diag["work"]["jacobian_builds"]<=0 or not diag["probes"]["success"]:
        raise ValueError("R3O_ACTUAL_JACOBIAN_AND_NONAUTONOMOUS_PARTIAL_T_REQUIRED")
    return {"steps":n,"six_scalar_byte_comparisons":6*(n+1),"same_c_initial_state":True,
            "max_state_scaled_residual":maxima,"max_common_rhs_scaled_residual":rhs_max,
            "diagnostic_attempts":diag["attempts"],"diagnostic_internal_steps":diag["internal_steps"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--build",type=Path,help="create-only build.json from build_r3o_rust.py")
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--raw-dir",type=Path,default=ROOT.parent/"rec_raw_verified/full5210_stored")
    ap.add_argument("--source-zip",type=Path,default=ORIGINAL_ZIP)
    ap.add_argument("--steps",type=int,default=16,choices=range(1,33))
    ap.add_argument("--boundary-packet",type=Path,help="use the sealed derived checkpoint packet; no full NPZ/CSV retrieval")
    group=ap.add_mutually_exclusive_group()
    group.add_argument("--export-boundary-packet",type=Path,help="create derived packet from authenticated full raw; zero numerical steps")
    group.add_argument("--check-boundary-packet",type=Path,help="read back packet against authenticated full raw; zero numerical steps")
    args=ap.parse_args()
    if args.export_boundary_packet or args.check_boundary_packet:
        return packet_command(args)
    if args.build is None:ap.error("--build required for numerical verification")
    if args.boundary_packet is None and not args.raw_dir.is_dir():
        args.boundary_packet=DEFAULT_PACKET
    ev=reserve(args.output)
    budget=Budget(ev,cpu_s=20.,wall_s=60.)
    report={"schema":"rec.r3o.rust-verification.v1","status":"FAILED","command":sys.argv,
        "limits":{"cpu_s":20.,"wall_s":60.,"memory_bytes":3*1024**3,"max_steps":32},
        "full_153327_steps":"NOT_RUN","global_convergence":"NOT_RUN","speedup":"NOT_RUN",
        "production_admission":False,"last_python_checkpoint":None}
    code_before=own_code_hashes()
    exit_code=2
    def alarm(signum,frame):
        raise RuntimeError("R3O_NUMERICAL_WALL_LIMIT")
    signal.signal(signal.SIGALRM,alarm)
    signal.setitimer(signal.ITIMER_REAL,57.)
    try:
        from full_bianchi_hyrec.trajectory.primordial_2012_refined_low_z import (
            load_reviewed_u6_boundary,input_hashes,HyRec2012Cosmology,continue_refined_low_z,HISTORICAL_STATUS)
        from full_bianchi_hyrec.trajectory.primordial_2012_full_start import make_hmla_source
        from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
        from verify_r3o_lowz import source_tree_hashes
        build=read_json(args.build)
        report["build_receipt_sha256"]=sha256(args.build)
        if build["status"]!="BUILD_PASS" or build["code_after"]!=code_before:
            raise ValueError("R3O_BUILD_SAME_CODE_BINDING")
        binary,source=Path(build["binary"]),Path(build["source_path"])
        report["binary_before_sha256"]=sha256(binary)
        if report["binary_before_sha256"]!=build["binary_sha256"]:
            raise ValueError("R3O_BINARY_BINDING")
        if ensure_vigilode()!=build["vigilode"] or source_tree_hashes(source)!=build["source_after"]:
            raise ValueError("R3O_SOURCE_BINDING")
        def current_inputs():
            if args.boundary_packet:
                return {"derived_boundary_packet":sha256(args.boundary_packet),
                    "checked_in_packet_seal":sha256(DEFAULT_PACKET.with_suffix(".sha256")),"source_zip":sha256(args.source_zip)}
            return input_hashes(args.raw_dir,args.source_zip)
        report["inputs_before"]=current_inputs()
        if args.boundary_packet:
            boundary=load_boundary_packet(args.boundary_packet,args.source_zip)
            report["input_representation"]="DERIVED_BOUNDARY_PACKET_NOT_FULL_PRODUCER_ARTIFACT"
            report["full_raw_read_during_this_numerical_pass"]=False
        else:
            boundary=load_reviewed_u6_boundary(args.raw_dir,args.source_zip)
            report["input_representation"]="VERIFIED_FULL_RAW_PRODUCERS"
            report["full_raw_read_during_this_numerical_pass"]=True
        report["original_producer_inputs_sha256"]=boundary["inputs_sha256"]
        budget.check()
        report["historical_status"]=HISTORICAL_STATUS
        states=[asdict(boundary["python"])];rhs=[]
        c=HyRec2012Cosmology()
        emla=make_hmla_source(c,OriginalHyRecPrimitiveRateTable.from_archive(args.source_zip))
        def accepted(current,candidate,step):
            states.append(asdict(candidate))
            rhs.append([step["hydrogen_rhs"],step["thermal_rhs"]])
            report["last_python_checkpoint"]=asdict(candidate)
        report["last_python_checkpoint"]=states[0]
        result=continue_refined_low_z(boundary["python"],c,emla,max_steps=args.steps,
            before_attempt=lambda *_:budget.check(),on_accept=accepted)
        if result["accepted_steps"]!=args.steps or len(states)!=args.steps+1 or len(rhs)!=args.steps:
            raise ValueError("R3O_PYTHON_BOUNDARY_AND_COUNT")
        request={"schema":"rec.r3o.rust-input.v1","h2":4.245e-5,"start_iz":58389,"end_iz":211716,
            "steps":args.steps,"native":asdict(boundary["native"]),"python_states":states,
            "python_rhs":rhs,"input_hashes":boundary["inputs_sha256"]}
        dump_new(ev/"request.json",request)
        report["request_sha256"]=sha256(ev/"request.json")
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1")
        base=[binary,"--input",ev/"request.json"]
        budget.run(base+["--output",ev/"primary.json"],cwd=source,env=env,label="primary",expected=(0,3,2))
        primary=read_json(ev/"primary.json")
        report["primary_sha256"]=sha256(ev/"primary.json")
        report["primary_summary"]=validate_primary(primary,request)
        budget.run(base+["--output",ev/"partial.json","--mode","diagnostic","--max-attempts","1"],
            cwd=source,env=env,label="partial",expected=(3,))
        partial=read_json(ev/"partial.json")["diagnostic"]
        if (partial["status"]!="PARTIAL_BOUNDED_FAILURE" or partial["attempts"]!=1
                or partial["accepted_steps"]!=1 or len(partial["times"])!=2
                or partial["last_committed_output"]["tau"]!=4.245e-5):
            raise ValueError("R3O_EXPECTED_SHORT_PARTIAL_STATE")
        report["expected_partial_failure"]={"status":"PASS","exit":3,"attempts":1,
            "actual_last_output":partial["last_committed_output"],"work":partial["work"]}
        budget.run(base+["--output",ev/"callback_failure.json","--mode","diagnostic","--max-attempts","3","--callback-limit","1"],
            cwd=source,env=env,label="callback_failure",expected=(3,))
        failed=read_json(ev/"callback_failure.json")["diagnostic"]
        if (failed["success"] or not failed["callbacks"]["failed_callbacks"]
                or failed["callbacks"]["source_work"]["rhs_calls"]!=1
                or failed["work"]["rejected_steps"]<1 or failed["work"]["jacobian_builds"]<1
                or failed["last_committed_output"]["state"]!=[boundary["native"].xe,boundary["native"].Tm_K]):
            raise ValueError("R3O_FAILED_CALLBACK_COUNTS_OR_STATE_NOT_RETAINED")
        report["failed_callback_control"]={"status":"PASS","exit":3,"attempts":failed["attempts"],
            "attempted_callbacks":failed["callbacks"]["evaluations_attempted"],
            "failed_callbacks":len(failed["callbacks"]["failed_callbacks"]),"work":failed["work"]}
        contracts=reserve(ev/"contracts")
        testenv=dict(env,REC_R3O_BINARY=str(binary),REC_R3O_SOURCE=str(source),
            REC_R3O_REQUEST=str(ev/"request.json"),REC_R3O_TEST_OUTPUT=str(contracts))
        budget.run([sys.executable,"-B","-m","unittest","discover","-s",ROOT/"tests/trajectory","-p","test_r3o_rust.py","-v"],
            cwd=ROOT,env=testenv,label="contracts")
        report["status"]="BOUNDED_RUST_FIXED_PARITY_AND_EXPLORATORY_VIGILODE_PASS"
        exit_code=0
    except BaseException as exc:
        report["failure"]={"type":type(exc).__name__,"message":str(exc)}
        with (ev/"exception.txt").open("x") as stream:traceback.print_exc(file=stream)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0.)
        try:
            if "inputs_before" in report:
                report["inputs_after"]=current_inputs()
                if report["inputs_after"]!=report["inputs_before"]:raise ValueError("R3O_INPUT_MUTATION")
            report["code_before"]=code_before
            report["code_after"]=own_code_hashes()
            if report["code_after"]!=code_before:raise ValueError("R3O_CODE_MUTATION")
            if "binary_before_sha256" in report:
                report["binary_after_sha256"]=sha256(binary)
                if report["binary_after_sha256"]!=report["binary_before_sha256"]:raise ValueError("R3O_BINARY_MUTATION")
                report["source_after"]=source_tree_hashes(source)
                if report["source_after"]!=build["source_after"]:raise ValueError("R3O_SOURCE_MUTATION")
                if sha256(args.build)!=report["build_receipt_sha256"]:raise ValueError("R3O_BUILD_RECEIPT_MUTATION")
                if ensure_vigilode()!=build["vigilode"]:raise ValueError("R3O_VIGILODE_MUTATION")
        except BaseException as exc:
            report["identity_failure"]=str(exc);report["status"]="FAILED";exit_code=2
        report["process_tree_cpu_s"]=cpu()-budget.start_cpu
        report["wall_s"]=time.monotonic()-budget.start_wall
        if report["process_tree_cpu_s"]>20. or report["wall_s"]>60.:
            report["resource_failure"]="R3O_TOTAL_NUMERICAL_BUDGET";report["status"]="FAILED";exit_code=2
        report["commands"]=budget.commands;report["exit_code"]=exit_code
        report["artifacts_sha256"]={str(p.relative_to(ev)):sha256(p) for p in sorted(ev.rglob("*")) if p.is_file()}
        dump_new(ev/"verification.json",report)
        print(json.dumps({k:report.get(k) for k in ("status","primary_summary","process_tree_cpu_s","wall_s","failure","identity_failure")}))
    return exit_code


if __name__=="__main__":raise SystemExit(main())
