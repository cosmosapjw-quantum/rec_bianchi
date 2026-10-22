"""Repair the observed legend/data overlap; reuse all measured arrays unchanged."""
import os
os.environ["MPLCONFIGDIR"] = "/tmp/rec_diagnostic_c2_mpl"
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
import hashlib
import json
from pathlib import Path
import shutil
import time
START = time.perf_counter()
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

unit = Path(__file__).resolve().parents[1]
parent = unit/"figures"
out = parent/"v2"
out.mkdir(exist_ok=False)
with np.load(parent/"PLOT_DATA.npz", allow_pickle=False) as f:
    data = {k:f[k].copy() for k in f.files}
plt.rcParams.update({"font.size":8.5,"axes.titlesize":9.5,"axes.labelsize":8.5,
    "xtick.labelsize":8,"ytick.labelsize":8.5,"legend.fontsize":8,
    "pdf.fonttype":42,"ps.fonttype":42,"savefig.dpi":300})
fig, ax = plt.subplots(figsize=(90/25.4, 135/25.4), layout="constrained")
labels = []
for i, label in enumerate(data["case_labels"]):
    labels.append(label[1:3]+" "+("hot" if "actual_hot" in label else "ref")+" "+("R" if label.endswith("refined") else "N"))
    for key,color,shift,title in (("baseline_gather_ms","#226B8A",-.14,"Diagnostics"),
                                  ("baseline_collision_ms","#C16B22",.14,"CI/CE")):
        values = data[key][i]
        y = i+shift
        ax.plot([min(values),max(values)],[y,y],color=color,lw=1)
        ax.scatter(values,[y]*3,color=color,s=13,alpha=.7,label=title if i==0 else None)
        ax.plot(np.median(values),y,"|",color=color,markersize=10,markeredgewidth=1.8)
ax.set_yticks(range(8),labels)
ax.invert_yaxis()
ax.set_xscale("log")
ax.set_xlim(.4,40)
ax.set_xticks([.5,1,3,10,30],["0.5","1","3","10","30"])
ax.set_xlabel("Wall time per saved state (ms; log)")
ax.set_title("Baseline latency\n64 states / case; three repetitions",pad=32)
ax.legend(loc="lower left",bbox_to_anchor=(0,1.005),ncol=2,frameon=False,borderaxespad=0)
ax.grid(axis="x",alpha=.2)
ax.spines[["top","right"]].set_visible(False)
for ext in ("png","pdf"):
    fig.savefig(out/("baseline_latency."+ext))
plt.close(fig)
for name in ("baseline_cost_attribution.png","baseline_cost_attribution.pdf","PLOT_DATA.npz"):
    shutil.copyfile(parent/name,out/name)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
manifest = dict(status="RENDERED_REQUIRES_ACTUAL_VISUAL_REVIEW", repair="Move latency legend outside axes; no data or cost figure change.",
    predecessor_manifest_sha256=sha(parent/"FIGURE_MANIFEST.json"),
    original_plot_script_sha256=sha(unit/"code/summarize_profile.py"),
    repair_script_sha256=sha(Path(__file__)),plot_data_sha256=sha(out/"PLOT_DATA.npz"),
    files=[dict(filename=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.iterdir())],
    active_wall_seconds=time.perf_counter()-START,nominal_width_mm=90)
with (out/"FIGURE_MANIFEST.json").open("x") as stream:
    json.dump(manifest,stream,indent=2);stream.write("\n")
print(json.dumps(dict(status="RENDERED_V2",plot_data_unchanged=sha(parent/"PLOT_DATA.npz")==sha(out/"PLOT_DATA.npz"),active_wall_seconds=manifest["active_wall_seconds"])))
