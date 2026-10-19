#!/usr/bin/env python3
"""Plot retained h4 start evidence without running either trajectory again."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

os.environ.update({"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"})
from verify_r3o_h4_start import parse_native, sha, json_new, h4, ZIP
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    src = args.evidence_dir.resolve(); out = args.output_dir.resolve()
    report = json.loads((src/"verification.json").read_text())
    if report["status"] != "PASS_SAME_H_START" or report["dlna"] != h4.DLNA:
        raise ValueError("complete same-h h4 start evidence required")
    identities = {}
    for name in ("python_h4_helium.npz", "python_h4_full_start.npz", "native_oracle.stdout"):
        identities[name] = sha(src/name)
        if identities[name] != report["artifacts"][name]["sha256"]:
            raise ValueError(f"evidence bytes changed: {name}")
    native = parse_native(src/"native_oracle.stdout", report["steps_requested"])
    out.mkdir(parents=True, exist_ok=False)
    os.environ.setdefault("MPLCONFIGDIR", str(out/"matplotlib_cache"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    table = _canonical_twophoton_table(ZIP)
    with np.load(src/"python_h4_helium.npz", allow_pickle=False) as he:
        ratios = []
        for col, key in enumerate(("z", "xe", "xHII", "xHeI", "xHeII", "xHeIII", "Tm_K")):
            ratios.append(np.abs(he[key]-native["helium"][:, col])/
                          (2.e-12*np.maximum(1., np.abs(native["helium"][:, col]))))
        he_ratio = np.max(ratios, axis=0)
        he_index = np.array(he["iz"])
    photon_ratios = {}
    with np.load(src/"python_h4_full_start.npz", allow_pickle=False) as p:
        for key, tag in (("virtual_out", "V"), ("average_virtual", "A"), ("lyman_out", "L")):
            energy = table.energy_eV if tag != "L" else np.array((10.198714553953742, 12.087365397278509, 12.748393192442178))
            tr = h4.KB_NATIVE_EV_K*2.7255*(1.+p["z"][:-1])
            fbb = 1./np.expm1(energy[:, None]/tr[None, :])
            cs = native["spectra"][tag]
            tolerance = 1.e-7*np.maximum(np.abs(p[key]), np.abs(cs))+1.e-10*fbb
            photon_ratios[key] = np.max(np.abs(p[key]-cs)/tolerance, axis=0)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2), constrained_layout=True)
    floor = 1.e-9
    axes[0].plot(he_index, np.maximum(he_ratio, floor), color="#305c94", linewidth=.65)
    axes[0].set_title("Independent HeIII / HeII history: 72,893 rows")
    axes[0].set_xlabel("Original h4 global state index")
    labels = {"virtual_out": "Outgoing virtual (311)", "average_virtual": "Average virtual (311)", "lyman_out": "Lyman (3)"}
    for key, values in photon_ratios.items():
        axes[1].plot(np.arange(len(values)), np.maximum(values, floor), marker="o", label=labels[key])
    axes[1].set_title(f"Initial FULL H+He: {report['steps_requested']} accepted photon columns")
    axes[1].set_xlabel("Accepted photon column j")
    axes[1].legend(fontsize=8, loc="lower right")
    for ax in axes:
        ax.axhline(1., color="#bb4139", linestyle="--", linewidth=1, label="Tolerance limit")
        ax.set_yscale("log"); ax.set_ylim(5.e-10, 2.)
        ax.set_ylabel("Absolute discrepancy / frozen same-h tolerance")
        ax.grid(alpha=.15)
    fig.suptitle("h4 = 2.1225e-5 · independent Python vs original C · local start comparison")
    fig.supxlabel("Dashed line: unchanged acceptance limit (1). Exact zeros are drawn at 1e-9.", fontsize=9)
    fig.savefig(out/"r3o_h4_start_residuals.png", dpi=160)
    fig.savefig(out/"r3o_h4_start_residuals.pdf")
    plt.close(fig)
    json_new(out/"r3o_h4_plot_inputs.json", {
        "source_evidence_dir": str(src), "source_sha256": identities,
        "plot_script_sha256": sha(Path(__file__)), "display_floor": floor,
        "display_floor_note": "zero/smaller values appear at 1e-9; this is not an uncertainty floor",
        "helium_max_tolerance_ratio": float(np.max(he_ratio)),
        "photon_tolerance_ratios_by_column": {k: v.tolist() for k, v in photon_ratios.items()},
        "new_trajectory_execution": False,
    })
    print(out/"r3o_h4_start_residuals.png")


if __name__ == "__main__":
    main()
