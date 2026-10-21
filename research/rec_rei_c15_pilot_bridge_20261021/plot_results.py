from pathlib import Path
import json
import csv
import numpy as np
import matplotlib.pyplot as plt

import sys
root = Path(sys.argv[1])
package = Path(sys.argv[2])
package.mkdir(parents=True, exist_ok=True)
(package / "figures").mkdir(exist_ok=True)
cases = [json.loads(p.read_text()) for p in sorted((root / "run001").glob("case_*/result.json"))]

summary = []
history = []
for index, case in enumerate(cases):
    initial = case["initial_normalized"]
    final = case["history"][-1]
    summary.append({
        "case_id": f"case_{index:03d}",
        "signed_Sigma0_F": case["case"]["signed_sigma"],
        "signed_Pi0_F": case["case"]["signed_pi"],
        "Sigma0_F": initial["Sigma_frobenius"],
        "Pi0_F": initial["Pi_frobenius"],
        "A_gamma_equal_A_nu": case["initial_A"],
        "Sigma_end_F": final["Sigma_frobenius"],
        "signed_Sigma_end_F": final["signed_sigma_frobenius"],
        "Pi_end_F": final["Pi_frobenius"],
        "Tgas_end_K": final["Tgas_K"],
        "xHII_end": final["x_HII"],
        "xHeII_end": final["x_HeII"],
        "elapsed_proper_s": final["elapsed_s"],
    })
    for row in case["history"]:
        history.append({
            "case_id": f"case_{index:03d}",
            "signed_Sigma0_F": case["case"]["signed_sigma"],
            "signed_Pi0_F": case["case"]["signed_pi"],
            **{key: row[key] for key in (
                "elapsed_s", "Sigma_frobenius", "Pi_frobenius",
                "signed_sigma_frobenius", "signed_pi_frobenius",
                "Tgas_K", "x_HII", "x_HeII"
            )}
        })

for name, rows in (("PILOT_ENDPOINTS.csv", summary), ("PILOT_HISTORY.csv", history)):
    with (package / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

# Signed coordinates retain the relative orientation hidden by tensor norms.
fig, ax = plt.subplots(figsize=(8.2, 5.4))
for initial_shear in sorted({r["signed_Sigma0_F"] for r in summary}):
    group = sorted(
        [r for r in summary if r["signed_Sigma0_F"] == initial_shear],
        key=lambda r: r["signed_Pi0_F"]
    )
    ax.plot(
        [r["signed_Pi0_F"] * 1e4 for r in group],
        [(r["signed_Sigma_end_F"] - initial_shear) * 1e6 for r in group],
        marker="o",
        label=rf"$\widetilde{{\Sigma}}_0={initial_shear:g}$",
    )
ax.set_xlabel(r"Signed initial Frobenius stress $\widetilde{\Pi}_0$ [$10^{-4}$]")
ax.set_ylabel(r"Signed shear change $\widetilde{\Sigma}_{f}-\widetilde{\Sigma}_0$ [$10^{-6}$]")
ax.set_title("C15 warm LRS pilot: 25 coupled histories")
ax.set_ylim(-1.9, 2.5)
ax.legend(fontsize=9, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.01))
ax.grid(alpha=0.25)
fig.text(0.5, 0.015,
         "a = 0.1999 → 0.2; 16 steps/case; preliminary, not a full-EoR solution",
         ha="center", fontsize=9)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(package / "figures" / "SIGNED_SHEAR_RESPONSE.png", dpi=180)
plt.show()

# Norm-space slice: both tensor orientations are positive.
positive = [r for r in summary if r["signed_Sigma0_F"] >= 0 and r["signed_Pi0_F"] >= 0]
x = np.array(sorted({r["signed_Sigma0_F"] for r in positive}))
y = np.array(sorted({r["signed_Pi0_F"] for r in positive}))
z = np.array([
    [next(r["Sigma_end_F"] - r["signed_Sigma0_F"] for r in positive
          if r["signed_Sigma0_F"] == sx and r["signed_Pi0_F"] == py) * 1e6
     for sx in x] for py in y
])
fig, ax = plt.subplots(figsize=(7.6, 5.4))
image = ax.pcolormesh(x * 1e3, y * 1e4, z, shading="nearest")
fig.colorbar(image, ax=ax, label=r"$(\Sigma_f-\Sigma_0)\times 10^6$")
ax.set_xticks(x * 1e3)
ax.set_yticks(y * 1e4)
ax.set_xlim(0, 2)
ax.set_ylim(0, 4)
ax.set_xlabel(r"Initial Frobenius norm $\Sigma_0$ [$10^{-3}$]")
ax.set_ylabel(r"Initial Frobenius norm $\Pi_0$ [$10^{-4}$]")
ax.set_title("Positive-orientation slice of the coupled pilot")
fig.text(0.5, 0.015,
         "Nine computed points; no interpolated accuracy claim; warm LRS, not generic Bianchi I",
         ha="center", fontsize=9)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(package / "figures" / "SIGMA_PI_NORM_PLANE.png", dpi=180)
plt.show()

# Actual gas history, rather than magnifying an unresolved tiny Pi contrast.
zero = cases[12]
fig, ax = plt.subplots(figsize=(7.6, 5.0))
ax.plot(
    [row["elapsed_s"] / (365.25 * 86400) for row in zero["history"]],
    [row["Tgas_K"] for row in zero["history"]],
    marker="o",
    label=r"$\Sigma_0=\Pi_0=0$ reference",
)
ax.set_xlabel("Elapsed proper time [years]")
ax.set_ylabel("Gas temperature [K]")
ax.set_title("Active H/He warm-start evolution in the pilot")
ax.legend()
ax.grid(alpha=0.25)
fig.text(0.5, 0.015,
         "Prescribed initial gas T = 12000 K; no cold-start reionization inference",
         ha="center", fontsize=9)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(package / "figures" / "HHE_WARM_HISTORY.png", dpi=180)
plt.show()
