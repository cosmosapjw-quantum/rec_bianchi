import json, hashlib, os
R="/home/cosmosapjw/rec_theory_runs/REC_R3M_U6_PILOT_20261019/evidence_full_001"; EV=R+"/full5210_stored"
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()
v=json.load(open(EV+"/verification.json")); o={}
o["python_history"]=v["python_history_sha256"]==sha(EV+"/python_u6_rt.npz")
o["partial"]={k:val==sha(EV+"/"+k) for k,val in v["partial_accepted_sha256"].items()}
o["native_bin"]=v["native_binary_sha256"]==sha(EV+"/native_u6_rt")
o["common_bin"]=v["common_binary_sha256"]==sha(EV+"/liboriginal_full_source.so")
o["native_stdout"]=v["native_run"]["stdout_sha256"]==sha(EV+"/native_oracle_stdout.csv")
o["native_stderr"]=v["native_run"]["stderr_sha256"]==sha(EV+"/native_oracle_stderr.txt")
for b in ("native_build","common_build"):
    o[b]=(v[b]["stdout_sha256"]==sha(EV+f"/{b}_stdout.txt"), v[b]["stderr_sha256"]==sha(EV+f"/{b}_stderr.txt"))
o["modified_src"]={k:val==sha(EV+"/source_extract/HyRec/"+k) for k,val in v["modified_source_sha256"].items()}
p=json.load(open(R+"/full5210_stored.r3l_profile.json"))
o["profile_verif_sha"]=p["verification"]["sha256"]==sha(EV+"/verification.json")
o["profile_status"]=(p["verification"]["status"],p["execution_status"],p["run_error"],p["closeout_errors"],p["timings"]["accounting_status"],p["timings"]["profiling_errors"])
t=p["timings"]
o["accounting"]={k:(t["measured_interval"][k], t["exclusive_sum"][k]+t["unattributed"][k], t["measured_interval"][k]-(t["exclusive_sum"][k]+t["unattributed"][k])) for k in t["measured_interval"]}
o["recomputed_exclusive_sum"]={k:sum(r["exclusive"][k] for r in t["phases"].values())-t["exclusive_sum"][k] for k in t["measured_interval"]}
o["unattributed"]=t["unattributed"]; o["profile_tree_cpu"]=t["process_tree_cpu_s"]
o["phases_top"]=sorted(((r["exclusive"]["parent_cpu_s"]+r["exclusive"]["children_cpu_s"],k,r["calls"],r["failed_calls"]) for k,r in t["phases"].items()),reverse=True)[:8]
o["failed_calls_total"]=sum(r["failed_calls"] for r in t["phases"].values())
o["source"]=p["source"]
lines=[json.loads(l) for l in open(R+"/full5210_stored.r3l_phases.jsonl")]
o["journal_events"]=[(l.get("event"),l.get("phase"),l.get("status")) for l in lines]
o["journal_closeout_profile_sha"]=lines[-1].get("profile_sha256")==sha(R+"/full5210_stored.r3l_profile.json")
o["res"]=v["resources"]
L=[json.loads(x) for x in open(R+"/full5210_stored.launcher_stdout.json") if x.strip()]
o["launcher_lines"]=len(L)
o["launcher_line0_eq_verification"]=L[0]==v
o["launcher_last_eq_profile"]=L[-1]==p
print(json.dumps(o,indent=1,default=str))
