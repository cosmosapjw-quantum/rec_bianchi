#!/usr/bin/env python3
"""Read-only ORIGINAL F05 26-event [64,128],[128,160] map; source-native material trajectory.

Original [0,64] already replayed in REI PR363, exact historical SHA.
The original owner tree and accepted history are ONLY READ. Output goes to
a separate REC worktree / outside the source tree. No official owner admission.
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
import subprocess
import tarfile
import time

import numpy as np

ORIGINAL_TAR_SHA = "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
ORIGINAL_KERNEL_SHA = "579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
ORIGINAL_POLICY_SHA = "c648c0ae1e10bced3b159e96f92bdc5f2bd3c1031b9a13e6b947dbf102557aa9"
SOURCE_REI_PR363_SHA = "abf83d4d883d5f311426b7f02cb001e70138ceb4"
SOURCE_REC_PR194_SHA = "b1f3dd6516539fc6b98a131528f42d8076b41fa3"
STATE64_SHA = "aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425"
STATE128_SHA = "bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6"
STATE160_SHA = "74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6"
LANE = "LOCAL_NEUTRAL_HAZARD_PRIMARY"
N = 46080
TICKS = 131072
SIGMA_T_CM2 = 6.6524587051e-25
C_CM_S = 29979245800.0
MPC_CM = 3.085677581491367e24
KB_ERG_K = 1.380649e-16
EV_ERG = 1.602176634e-12
CHI_H, CHI_HE1, CHI_HE2 = 13.598434599702, 24.587389011, 54.41776
SOURCE_Z = 5.95
SOURCE_INIT_SHA = "7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d"
SOURCE_FORCE_SHA = "9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268"
SOURCE_FINAL_ARRAY_SHA = "cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def ensure(condition: bool, label: str):
    if not condition:
        raise ValueError("REC195_ORIGINAL_F05_" + label)


def json_from_tar(tar, index: int, left: int, right: int):
    path = f"receipts/attempt_{index:08d}_{left:06d}_{right:06d}.json"
    receipt = json.load(tar.extractfile(path))
    ensure(receipt["action"] == "ACCEPT", "HISTORY_NOT_ACCEPTED")
    ensure(receipt["classification"] == "CANDIDATE_UNSEALED_LOCAL_EXECUTION",
           "HISTORY_PROVENANCE_DRIFT")
    env = next(x["envelope"] for x in receipt["processes"] if x["lane"] == LANE)
    ensure(env["scientific_accept"] and env["classification"] == "PASS", "LANE_NOT_PASS")
    return env


def metadata(env, endpoint):
    return {**{k: env[k] for k in (
        "accepted_index", "input_lock_sha256", "job_key", "lane",
        "parent_state_sha256", "predecessor_kernel_sha256",
        "runtime_contract_sha256", "stage_id")}, "endpoint_tick": endpoint}


def material_fields(poplo, pophi, loglo, loghi, h, he, v):
    ne_lo = poplo[:, 1] + poplo[:, 3] + 2 * poplo[:, 4]
    ne_hi = pophi[:, 1] + pophi[:, 3] + 2 * pophi[:, 4]
    b_lo = EV_ERG * (CHI_H * poplo[:, 1] + CHI_HE1 * poplo[:, 3]
                     + (CHI_HE1 + CHI_HE2) * poplo[:, 4])
    b_hi = EV_ERG * (CHI_H * pophi[:, 1] + CHI_HE1 * pophi[:, 3]
                     + (CHI_HE1 + CHI_HE2) * pophi[:, 4])
    t_lo, t_hi = np.exp(loglo), np.exp(loghi)
    u_lo = 1.5 * KB_ERG_K * (h + he + ne_lo) * t_lo
    u_hi = 1.5 * KB_ERG_K * (h + he + ne_hi) * t_hi
    gamma_lo = C_CM_S * SIGMA_T_CM2 * ne_lo / v
    gamma_hi = C_CM_S * SIGMA_T_CM2 * ne_hi / v
    fields = {"Ne": (ne_lo, ne_hi), "T": (t_lo, t_hi), "B": (b_lo, b_hi),
              "U": (u_lo, u_hi), "Gamma": (gamma_lo, gamma_hi)}
    for key, (a, b) in fields.items():
        ensure(np.isfinite(a).all() and np.isfinite(b).all() and
               np.all(a > 0) and np.all(b >= a), "BAD_" + key)
    return fields


def scalar_total(a) -> float:
    return float(math.fsum(float(x) for x in a))


def cell_clumping(field, v):
    el, eu = field["Ne"]
    volume = scalar_total(v)
    eltot, eutot = scalar_total(el), scalar_total(eu)
    low = volume * scalar_total(el * el / v) / (eutot * eutot)
    high = volume * scalar_total(eu * eu / v) / (eltot * eltot)
    return [low, high]


def summarize(fields, v):
    out = {k: [scalar_total(a), scalar_total(b)] for k, (a, b) in fields.items()}
    out["volume_mean_Gamma_s_inv"] = [C_CM_S * SIGMA_T_CM2 * x / scalar_total(v)
                                       for x in out["Ne"]]
    out["electron_clumping"] = cell_clumping(fields, v)
    return out


def change_from(source, dest):
    bounds = {}
    for k in ("Ne", "B", "U", "volume_mean_Gamma_s_inv"):
        lower = dest[k][0] - source[k][1]
        upper = dest[k][1] - source[k][0]
        ensure(lower <= upper, "INVERTED_DELTA_" + k)
        bounds["delta_" + k] = [lower, upper]
    return bounds


def check_nuclei(poplo, pophi, h, he):
    ensure(np.all(poplo > 0) and np.all(poplo <= pophi),
           "INVALID_SOURCE_SPECIES_BOX")
    # Original interval enclosures can overlap reference nucleus totals.
    Hlo, Hhi = poplo[:, 0] + poplo[:, 1], pophi[:, 0] + pophi[:, 1]
    Helo, Hehi = np.sum(poplo[:, 2:], axis=1), np.sum(pophi[:, 2:], axis=1)
    ensure(np.all(Hlo <= h * (1 + 1e-13)) and np.all(Hhi >= h * (1 - 1e-13)),
           "H_NUCLEAR_NOT_ENCLOSED")
    ensure(np.all(Helo <= he * (1 + 1e-13)) and np.all(Hehi >= he * (1 - 1e-13)),
           "HE_NUCLEAR_NOT_ENCLOSED")


def native_map(worker, module, model, base, h, he, previous, left, right, env,
               private_dir: Path):
    begin = time.perf_counter()
    pop_prev, logt_prev = previous
    duration = float(base.forcing.duration_seconds(0))
    t0, t1 = duration * (left / TICKS), duration * (right / TICKS)
    mid = t0 + 0.5 * (t1 - t0)
    kw = dict(model=model, base=base, parent_pop=pop_prev, parent_logt=logt_prev,
              t0=t0, t1=t1, total_h=h, total_he=he)
    full = module.run_step(**kw)
    ensure(full.certified, f"FULL_{left}_{right}")
    kw["t1"] = mid
    first = module.run_step(**kw)
    ensure(first.certified, f"HALF1_{left}_{right}")
    kw.update(parent_pop=first.population, parent_logt=first.log_temperature,
              t0=mid, t1=t1)
    second = module.run_step(**kw)
    ensure(second.certified, f"HALF2_{left}_{right}")
    pop, logt = second.population, second.log_temperature
    hfull = {"x_HII": module._I(full.population.lo[:, 1] / h, full.population.hi[:, 1] / h),
             "x_HeII": module._I(full.population.lo[:, 3] / he, full.population.hi[:, 3] / he),
             "x_HeIII": module._I(full.population.lo[:, 4] / he, full.population.hi[:, 4] / he),
             "log_T": full.log_temperature}
    hhalf = {"x_HII": module._I(pop.lo[:, 1] / h, pop.hi[:, 1] / h),
             "x_HeII": module._I(pop.lo[:, 3] / he, pop.hi[:, 3] / he),
             "x_HeIII": module._I(pop.lo[:, 4] / he, pop.hi[:, 4] / he),
             "log_T": logt}
    local = {k: float(np.max(np.maximum(np.abs(hhalf[k].lo-hfull[k].hi),
                              np.abs(hhalf[k].hi-hfull[k].lo)))) for k in hhalf}
    widths = {k: float(np.max(val.hi-val.lo)) for k, val in hhalf.items()}
    ledgers = {"H_nuclei": (float(np.min(pop.lo[:, 0]+pop.lo[:, 1]-h)),
                             float(np.max(pop.hi[:, 0]+pop.hi[:, 1]-h))),
               "He_nuclei": (float(np.min(np.sum(pop.lo[:, 2:5], axis=1)-he)),
                              float(np.max(np.sum(pop.hi[:, 2:5], axis=1)-he)))}
    for prefix, event, pbox, ts in (
        ("stage", second.stage_event, second.population, mid+module.sdirk.GAMMA*(t1-mid)),
        ("final", second.final_event, second.population, t1)):
        ledgers[prefix+"_photon_identity"] = (float(np.min(event.photon_identity.lo)),
                                               float(np.max(event.photon_identity.hi)))
        res = event.resolved_heat+event.unresolved_energy+event.escaped_energy+event.chemical_energy
        ledgers[prefix+"_total_energy"] = (float(np.min(res.lo)), float(np.max(res.hi)))
        for gi, rg in enumerate(module.group_photon_residuals(model, pbox, ts)):
            ledgers[f"{prefix}_group_{gi}_photon"] = (
                float(np.asarray(rg.lo)), float(np.asarray(rg.hi)))
    audit = module.primitive.audit_set_ledgers(ledgers)
    all_events = full.table_events+first.table_events+second.table_events
    ensure(not any(e.any_event for e in all_events), f"TABLE_EVENT_{left}_{right}")
    ensure(audit.all_include_zero and len(ledgers) == 14, f"LEDGER_{left}_{right}")
    ensure(max(local.values()) < 2e-4, f"LOCAL_GATE_{left}_{right}")
    ensure(max(widths.values()) < 2e-3, f"WIDTH_GATE_{left}_{right}")
    p = private_dir / f"ORIGINAL_REPLAY_TICK{right:06d}_NONAUTHORITATIVE.state"
    hsh = worker.state_io.write_state(p, metadata(env, right),
                                       pop.lo, pop.hi, logt.lo, logt.hi)
    ensure(hsh == env["candidate_state"]["sha256"],
           f"ORIGINAL_STATE_SHA_REPLAY_MISMATCH_{right}")
    # Stronger comparison with the original acceptance receipt gates, no relaxation.
    historical = env["diagnostics"]["validated_local_error_bounds"]
    for key, val in historical.items():
        ensure(abs(local[key]-val) <= 2e-12*max(1.0, abs(val)),
               f"ORIGINAL_LOCAL_DIAGNOSTIC_MISMATCH_{key}_{right}")
    elapsed = time.perf_counter()-begin
    print(json.dumps({"completed_interval":[left,right],"source_state_sha":hsh,
                      "seconds":elapsed,"all_14_ledgers_zero":True,
                      "max_local":max(local.values())}),flush=True)
    return (module._I(pop.lo, pop.hi), module._I(logt.lo, logt.hi)), {
        "interval_ticks": [left, right], "computed_sha256": hsh,
        "historical_sha256": env["candidate_state"]["sha256"],
        "history": "CANDIDATE_UNSEALED_LOCAL_EXECUTION",
        "three_source_maps_certified": [bool(x.certified) for x in (full,first,second)],
        "all_14_ledgers_include_zero": True, "table_event_count": 0,
        "local_error_bounds": local, "source_interval_widths": widths,
        "computation_elapsed_s": elapsed}


def run(repo: Path, rei: Path, first64_state: Path, out: Path):
    repo, rei, first64_state, out = (
        Path(x).resolve() for x in (repo, rei, first64_state, out))
    ensure(not out.exists(), "REFUSE_OVERWRITE_RESULT_DIR")
    ensure(subprocess.check_output(["git", "-C", str(rei), "rev-parse", "HEAD"],
                                   text=True).strip() == SOURCE_REI_PR363_SHA,
           "REI_OWNER_HEAD_DRIFT")
    ensure(subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor",
                           SOURCE_REC_PR194_SHA, "HEAD"], check=False).returncode == 0,
           "REC_PARENT_ANCESTRY_CHANGED")
    ensure(sha(first64_state) == STATE64_SHA, "PRIVATE_TICK64_SHA_MISMATCH")
    rei_unit = rei / "research/rei_f05_owner_original64_rust_20261101"
    source = rei_unit / "execute_original64.py"
    # Import authoritative REI source adapter; no write to source owner at any point.
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location("rec195_rei_original64", source)
    ensure(spec is not None and spec.loader is not None, "REI_SOURCE_LOADER")
    src = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = src
    spec.loader.exec_module(src)
    ensure(src.REPO == rei and src.STAGES == sorted(rei.glob(
        "stages/*UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY")),
        "REI_ORIGINAL_STAGE_MISMATCH")
    ensure(sha(src.ARCHIVE) == ORIGINAL_TAR_SHA and
           sha(src.A/"adaptive_policy.py") == ORIGINAL_POLICY_SHA, "ORIGINAL_LOCK_DRIFT")
    worker = src.module("rec195_original_attempt_worker", src.A/"attempt_worker.py")
    ensure(sha(worker.KERNEL_PATH) == ORIGINAL_KERNEL_SHA, "ORIGINAL_KERNEL_DRIFT")
    with tarfile.open(src.ARCHIVE, "r:gz") as tar:
        env64 = json_from_tar(tar, 1, 0, 64)
        env128 = json_from_tar(tar, 2, 64, 128)
        env160 = json_from_tar(tar, 4, 128, 160)
        ensure(env64["candidate_state"]["sha256"] == STATE64_SHA and
               env128["candidate_state"]["sha256"] == STATE128_SHA and
               env160["candidate_state"]["sha256"] == STATE160_SHA,
               "ORIGINAL_RECEIPT_HASH_DRIFT")
        ensure(env128["parent_state_sha256"] == STATE64_SHA and
               env160["parent_state_sha256"] == STATE128_SHA,
               "ORIGINAL_PARENT_CHAIN_DRIFT")
    worker.jax_guard.install_if_missing()
    m = worker._kernel()
    base, y, logt0, h, he = worker._context(m, LANE)
    ensure(y.shape == (N, 5), "SOURCE_CELL_COUNT")
    init = repo / "research/rec_rei_f05_native_thomson_medium_20261101/source_inputs/ORIGINAL_REI_F05_initial_material_state_z6.npz"
    forcing = repo / "research/rec_rei_f05_native_thomson_medium_20261101/source_inputs/ORIGINAL_REI_F05_canonical_time_resolved_forcing_nodes.csv"
    ensure(sha(init) == SOURCE_INIT_SHA and sha(forcing) == SOURCE_FORCE_SHA,
           "REC_ORIGINAL_MATERIAL_SHA_DRIFT")
    with np.load(init, allow_pickle=False) as f:
        w = np.asarray(f["W_node"], dtype=np.float64)
        check_init = np.stack([f[name] for name in
            ("N_HI","N_HII","N_HeI","N_HeII","N_HeIII")], axis=1)
    ensure(w.shape == (N,) and np.array_equal(y,check_init), "REI_REC_SOURCE_MATERIAL_MISMATCH")
    v = w * MPC_CM**3 / (1 + SOURCE_Z)**3
    ensure((v>0).all() and np.isfinite(v).all(), "SOURCE_CELL_VOLUME_INVALID")
    state64 = worker.state_io.read_state(first64_state, expected_sha256=STATE64_SHA)
    ensure(state64.metadata == metadata(env64, 64), "ORIGINAL_FIRST64_METADATA_MISMATCH")
    previous = (m._I(state64.population_lower, state64.population_upper),
                m._I(state64.log_temperature_lower,state64.log_temperature_upper))
    check_nuclei(state64.population_lower,state64.population_upper,h,he)
    out.mkdir(parents=True)
    private_dir = out / "private"
    public_dir = out / "public"
    private_dir.mkdir()
    public_dir.mkdir()
    model = m.rim.ReducedIntervalModel.from_repo(rei)
    trajectory = {0: (y, y, logt0, logt0),
                  64: (state64.population_lower,state64.population_upper,
                       state64.log_temperature_lower,state64.log_temperature_upper)}
    evidence = []
    for left, right, env in ((64,128,env128),(128,160,env160)):
        previous, ev = native_map(worker,m,model,base,h,he,previous,left,right,
                                   env,private_dir)
        evidence.append(ev)
        p, l = previous
        check_nuclei(p.lo,p.hi,h,he)
        trajectory[right] = (p.lo,p.hi,l.lo,l.hi)
    with tarfile.open(src.ARCHIVE, "r:gz") as tar:
        exact160 = tar.extractfile(
            f"checkpoints/generations/g-00000003-tick-000160/{LANE}.state").read()
    ensure(hashlib.sha256(exact160).hexdigest() == STATE160_SHA,
           "ORIGINAL_T160_SOURCE_SHA_DRIFT")
    ensure(exact160 == (private_dir / "ORIGINAL_REPLAY_TICK000160_NONAUTHORITATIVE.state").read_bytes(),
           "ORIGINAL_T160_BYTE_CONTENT_DIFF")
    # The REC accepted160 source archive contains exactly the same numeric payload
    # though the 3 native owner lanes have different metadata/state-file hashes.
    oldrec = repo / "research/rec_rei_f05_accepted_history_thomson_20261101/source_inputs/ORIGINAL_REI_F05_FIRST_INTERVAL_ACCEPTED160.tar.gz"
    ensure(sha(oldrec) == ORIGINAL_TAR_SHA, "REC_PARENT_TAR_SHA_DRIFT")
    from fractions import Fraction
    def rowfields(t):
        pl,pu,ll,lu = trajectory[t]
        f = material_fields(pl,pu,ll,lu,h,he,v)
        return f,summarize(f,v)
    tables = {t:rowfields(t) for t in (0,64,128,160)}
    # Only original source endpoints: no interpolation between them.
    path = public_dir / "ORIGINAL_F05_REPLAY_0_64_128_160_46080.csv.gz"
    with path.open("xb") as file:
        with gzip.GzipFile(fileobj=file, filename="", mode="wb",compresslevel=6,mtime=0) as sink:
            with io.TextIOWrapper(sink, encoding="ascii", newline="", write_through=True) as stream:
                writer = csv.writer(stream, lineterminator="\n")
                writer.writerow(["node","tick","source_volume_cm3","N_H","N_He",
                                 "Ne_lower","Ne_upper","T_lower_K","T_upper_K",
                                 "B_lower_erg","B_upper_erg","U_lower_erg",
                                 "U_upper_erg","Gamma_lower_s_inv","Gamma_upper_s_inv"])
                for t in (0,64,128,160):
                    fields,_ = tables[t]
                    nel,neu=fields["Ne"]; tl,tu=fields["T"]
                    bl,bu=fields["B"];ul,uu=fields["U"]
                    gl,gu=fields["Gamma"]
                    for i in range(N):
                        writer.writerow([i,t,*[format(float(x[i]),".17e") for x in
                           (v,h,he,nel,neu,tl,tu,bl,bu,ul,uu,gl,gu)]])
    points = {str(t):s for t,(f,s) in tables.items()}
    dt = float(base.forcing.duration_seconds(0)) / TICKS
    intervals=[]
    for a,b in ((0,64),(64,128),(128,160)):
        start,end=tables[a],tables[b]
        changes=change_from(start[1],end[1])
        changes["interval_ticks"]=[a,b]
        changes["source_dt_seconds"]=(b-a)*dt
        # Weakly conservative outer secants are NOT time-derivative bounds.
        changes["source_delta_U_secant_erg_s"]=[x/((b-a)*dt) for x in changes["delta_U"]]
        changes["source_delta_B_secant_erg_s"]=[x/((b-a)*dt) for x in changes["delta_B"]]
        el,eu=start[0]["Ne"],end[0]["Ne"]
        changes["electron_sign_class"] = {
            "definite_gain":int(np.sum(eu[0]>el[1])),
            "definite_loss":int(np.sum(eu[1]<el[0])),
            "ambiguous":int(np.sum((eu[0]<=el[1])&(eu[1]>=el[0])))}
        ensure(sum(changes["electron_sign_class"].values())==N,
               "ELECTRON_SIGN_PARTITION")
        intervals.append(changes)
    # Original source #363 0->64 independently computes these same source physics.
    ref = json.loads((rei_unit /
             "results/ORIGINAL64_PYTHON_PHYSICAL_RESULT.json").read_text())
    for name,pfield in (("electron_change_outer","delta_Ne"),
                        ("ionization_storage_change_outer_erg","delta_B"),
                        ("gas_thermal_change_outer_erg","delta_U")):
        got=intervals[0][pfield]
        expected=ref["physics"][name]
        for a,b in zip(got,expected):
            ensure(abs(a-b) <= 6e-12*max(1.0,abs(b)), "REI363_SCIENCE_PARITY_"+pfield)
    rec193=json.loads((repo /
       "research/rec_f05_rust_native_20261101/results/RUST_SCIENCE_RESULT.json").read_text())
    for g,n in zip(points["160"]["volume_mean_Gamma_s_inv"],
           (rec193["accepted_lower_mean_Thomson_rate_s_inv"],
            rec193["accepted_upper_mean_Thomson_rate_s_inv"])):
        ensure(abs(g-n)<2e-13*n, "REC193_T160_GAMMA_PARITY")
    metadata_out = {
        "schema":"REC_ORIGINAL_F05_0_64_128_160_PHYSICAL_TRAJECTORY_V1",
        "source_REI_PR363_sha":SOURCE_REI_PR363_SHA,
        "source_REC_parent_sha":SOURCE_REC_PR194_SHA,
        "original_tar_sha256":ORIGINAL_TAR_SHA,
        "original_kernel_sha256":ORIGINAL_KERNEL_SHA,
        "original_policy_sha256":ORIGINAL_POLICY_SHA,
        "input_first64_state_sha256":STATE64_SHA,
        "replayed_128_state_sha256":STATE128_SHA,
        "replayed_160_state_sha256":STATE160_SHA,
        "original_final160_array_sha256":SOURCE_FINAL_ARRAY_SHA,
        "cells_per_epoch":N,
        "physical_epochs":[0,64,128,160],
        "one_tick_duration_seconds":dt,
        "source_z":SOURCE_Z,
        "point_physics":points,
        "interval_physics":intervals,
        "original_maps":evidence,
        "csv_sha256":sha(path),
        "total_rows":N*len(points),
        "new_owner_accepted_ticks":0,
        "original_accepted_tick":"160/131072",
        "DAG_REI_canonical":"28/88",
        "DAG_REI_working":"33/88",
        "DAG_physical_fast":"4/7",
        "DAG_REC_H5":"0/313",
        "production":"HOLD",
        "science_status":"RECONSTRUCTED_HISTORICAL_ACCEPTED_ENDPOINT_MATERIAL_NOT_CONTINUUM_IVP_CERTIFICATE",
        "original_owner_modified":False,
        "f05_tick161":"NOT_ACCEPTED",
    }
    result=public_dir/"SCIENCE_RESULT.json"
    result.write_text(json.dumps(metadata_out,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":"SOURCE_IDENTICAL_REAL_PHYSICAL_TRAJECTORY",
         "head":SOURCE_REC_PR194_SHA,"epochs":list(points),
         "physical_rows":N*len(points),
         "source_state128":STATE128_SHA,
         "source_state160":STATE160_SHA,
         "science_result":str(result),"csv_sha256":metadata_out["csv_sha256"],
         "new_scientific_owner_nodes":0},sort_keys=True),flush=True)
    return metadata_out


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--rec-root",type=Path,required=True)
    p.add_argument("--rei-root",type=Path,required=True)
    p.add_argument("--first64-state",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    run(a.rec_root,a.rei_root,a.first64_state,a.output)
