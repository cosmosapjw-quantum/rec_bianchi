"""Recompute the published REC198 exposure/visibility on the original F08 gas (stdlib only)."""
import argparse
import bisect
import csv
import gzip
import hashlib
import io
import json
import math
from collections import defaultdict
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/rec_f08_s0_thomson_visibility_20261102"
HEADER = "normal_t_s n_reference_rest_m3 electrons_per_reference beta_x beta_y beta_z dir_x dir_y dir_z"
PIN = "75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843"
QPIN = "a6bcc931865db54402eb44727afe13d74b4ea40cf6f1c3b08acda239678c2d92"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_csv(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", newline="") as f:
        return list(csv.DictReader(f))

def group(rows, keys):
    out=defaultdict(list)
    for row in rows:
        out[tuple(row[k] for k in keys)].append(row)
    return out

def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("binary", type=Path)
    args.add_argument("--output", type=Path)
    args = args.parse_args()
    binary = args.binary.resolve()
    src = SOURCE / "source_inputs"
    profile = json.loads((src / "SOURCE_AUTHORITY.json").read_text())
    raw = src / "F08_ORIGINAL_NATIVE_GAS_640.csv.gz"
    qsrc = src / "F08_ORIGINAL_SOURCE_Q128.csv"
    precalc_times = SOURCE / "results/ORIGINAL_F08_S0_4MODE_644_TEMPORAL_THOMSON.csv.gz"
    precalc_rays = SOURCE / "results/ORIGINAL_F08_S0_128RAY_1536_REDSHIFT_VISIBILITY.csv.gz"
    if sha(raw) != PIN or sha(qsrc) != QPIN:
        raise ValueError("F08 original donor identity changed")
    time_oracle = group(read_csv(precalc_times), ["branch","model"])
    ray_oracle = group(read_csv(precalc_rays), ["branch","model","ray"])
    native = group(read_csv(raw), ["branch","model"])
    directions = {r["ray"]:tuple(float(r[k]) for k in ("qx","qy","qz")) for r in read_csv(qsrc)}
    n_h0 = profile["original_source_initial_nH_cm3"] * 1e6
    f_he = profile["original_source_He_H_number"]
    def charge(xh, he2, he3):
        return float(xh)+f_he*(float(he2)+2.*float(he3))
    x_initial = charge(*(profile["original_source_initial_"+s] for s in ["HII","HeII","HeIII"]))
    errors = {}
    counts = defaultdict(int)
    scenarios = {}
    def check(metric, value, reference):
        reference=float(reference)
        if reference == 0.:
            if value != 0.:
                raise ValueError((metric,value,reference))
            rel = 0.
        else:
            rel=abs(value-reference)/abs(reference)
        if not math.isfinite(rel) or rel>3e-13:
            raise ValueError((metric,value,reference,rel))
        errors[metric]=max(errors.get(metric,0.),rel)
        counts[metric]+=1
    with tempfile.TemporaryDirectory() as tmp:
        ray_path = Path(tmp) / "samples.tsv"
        for (branch,model), rows in sorted(native.items()):
            rows.sort(key=lambda r:int(r["step"]))
            H=profile["H_per_s"][branch]
            theta=math.fsum(H)
            times = [0.]+[float(r["proper_t_s"]) for r in rows]
            x = [x_initial]+[charge(r["xHII"],r["xHeII"],r["xHeIII"]) for r in rows]
            def run(q, extra=()):
                knots=sorted(set(times).union(extra))
                lines=[HEADER]
                for t in knots:
                    j=min(len(times)-2,bisect.bisect_right(times,t)-1)
                    f=(t-times[j])/(times[j+1]-times[j])
                    xe=x[j]*(1-f)+x[j+1]*f
                    k=[qi*math.exp(-hi*t) for qi,hi in zip(q,H)]
                    energy=math.hypot(*k)
                    lines.append(" ".join(map(repr,(t,n_h0*math.exp(-theta*t),xe,0.,0.,0.,*(v/energy for v in k)))))
                ray_path.write_text("\n".join(lines)+"\n")
                result=subprocess.run([str(binary),str(ray_path)],capture_output=True,text=True,check=True)
                return [{k:float(v) for k,v in r.items()} for r in csv.DictReader(io.StringIO(result.stdout),delimiter="\t")]
            cells=run(directions["0"])
            ref=sorted(time_oracle[branch,model],key=lambda r:int(r["step"]))
            for i, cell in enumerate(cells):
                check("temporal_delta_tau",cell["delta_tau"],ref[i+1]["delta_tau_from_previous_step"])
                check("temporal_visibility_mass",cell["visibility_mass"],ref[i+1]["source_step_scattering_probability"])
                check("temporal_tau",cell["tau_far"],ref[i]["tau_to_source_horizon"])
            check("temporal_tau",cells[-1]["tau_near"],ref[-1]["tau_to_source_horizon"])
            total=float(ref[0]["tau_to_source_horizon"])
            scenarios[f"{branch}/{model}"]={"tau":cells[0]["tau_far"],"visibility_sum":math.fsum(c["visibility_mass"] for c in cells)}
            check("sum_visibility",scenarios[f"{branch}/{model}"]["visibility_sum"],-math.expm1(-total))
            for ray,q in directions.items():
                rr=ray_oracle[branch,model,ray]
                if len(rr)!=3: raise ValueError("missing target redshift")
                emissions=[float(row["emission_t_s"]) for row in rr]
                result={r["far_t_s"]:r for r in run(q,emissions)}
                for t, row in zip(emissions,rr):
                    tau=result[t]["tau_far"]
                    check("redshift_selected_tau",tau,row["tau_to_receiver"])
                    check("redshift_selected_probability",-math.expm1(-tau),row["probability_scattering_to_receiver"])
    if (len(native),len(directions),counts["temporal_tau"],counts["redshift_selected_tau"])!=(4,128,644,1536):
        raise ValueError("incomplete original F08 comparison")
    receipt={"schema":"ORIGINAL_REC_R109_RAY_THOMSON_REPLAY_V1","rec_parent":"923621e5127c3b2c221e38ce518aa72d28b8f37e",
             "source_sha256":{p.name:sha(p) for p in (raw,qsrc,precalc_times,precalc_rays)},
             "counts":dict(counts),"max_relative_error":errors,"relative_error_limit":3e-13,"scenarios":scenarios,
             "scope":"Original comoving F08 Bianchi I and FLRW, two gas/transport representations per geometry. Embedded source redshift targets use the published emission times. Finite material tilt and parameter tangents have separate analytic and finite-difference tests."}
    blob=json.dumps(receipt,indent=2,sort_keys=True)+"\n"
    if args.output: args.output.write_text(blob)
    else: print(blob,end="")

if __name__=="__main__":
    main()
