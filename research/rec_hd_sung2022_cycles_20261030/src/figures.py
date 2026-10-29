"""Plots of sourced HD lab constraints (not observed astrophysical cooling)."""
from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'evidence/RESULTS.json').read_text())
out=ROOT/'evidence'
# Source-normalized graph cycles with no inferred statistical sigma.
fig,ax=plt.subplots(figsize=(9,4.6))
labels=['2022 J2-J0 minus Sung R0+R1','2022 J3-J1 minus Sung R1+R2','1984 R3 minus Sung R3']
vals=[float(r['difference_MHz']) for r in d['cycles']]
ax.barh(np.arange(3),vals)
ax.set_yticks(np.arange(3), labels)
ax.invert_yaxis();ax.axvline(0,linewidth=.8,color='black')
ax.set_xlabel('Difference between reported laboratory nominal centers (MHz)')
ax.set_title('Three measured HD rotational-frequency cycle closures')
ax.grid(True,axis='x',alpha=.2)
fig.tight_layout();fig.savefig(out/'FIG1_LAB_CYCLE_RESIDUALS.png',dpi=180);plt.close(fig)
# H2 conditional collisional shift and Lorentz halfwidth at 296 K.
fig,ax=plt.subplots(figsize=(8,4.4))
pressures=[0,.1,.5,1.]
for row in d['line_atlas']:
    j=int(row['upper_J']);delta=float(row['h2_delta_cm_minus1_atm_minus1'])
    ax.plot(pressures,np.array(pressures)*delta*29979.2458,marker='o',label=f'R({j-1})')
ax.set_xlabel('H2 partial pressure (atm), conditional T=296 K')
ax.set_ylabel('Fitted pressure-shift model (MHz)')
ax.set_title('HD experimentally fitted H2 frequency-shift coefficients')
ax.grid(True,alpha=.2);ax.legend()
fig.tight_layout();fig.savefig(out/'FIG2_H2_PRESSURE_SHIFT_296K.png',dpi=180);plt.close(fig)
