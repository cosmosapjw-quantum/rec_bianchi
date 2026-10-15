#!/usr/bin/env python3
"""Plot measured/independently verified Bianchi-I full-sky photon moment parity."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--input",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    c=a.parse_args()
    if c.output.exists():
        a.error("refuse to overwrite an existing scientific figure")
    d=json.loads(c.input.read_text())
    sorted_cases=sorted(d["cases"],key=lambda x:x["q_ref"])
    q=[x["q_ref"] for x in sorted_cases]
    energy=[x["energy_moment_full_sky_factor"]-1 for x in sorted_cases]
    approx=[x["small_B_energy_series_4th"]-1 for x in sorted_cases]
    fig,ax=plt.subplots(figsize=(8,5))
    ax.plot(q,energy,"o-",label="Gauss-Legendre 96, exact Bianchi-I null map")
    ax.plot(q,approx,"x--",label="Shear expansion to fourth order")
    ax.set_xlabel("Signed shear q_ref")
    ax.set_ylabel("Anisotropic photon energy factor minus 1")
    ax.set_title("Collisionless Bianchi I: photon energy vs shear")
    ax.grid(True,alpha=.25)
    ax.legend()
    fig.tight_layout()
    c.output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(c.output,dpi=180)
    plt.close(fig)
    print("PLOT",c.output,c.output.stat().st_size)


if __name__=="__main__":
    main()
