"""Scientific illustrations from actual source-bound opacity atlas, no experimental imitation."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'figures';F.mkdir(exist_ok=True)
with open(ROOT/'evidence'/'SPECTRAL_CASES_36.csv') as f:cases=list(csv.DictReader(f))
with open(ROOT/'evidence'/'VOIGT_PROFILE_ATLAS_7236.csv') as f:profiles=list(csv.DictReader(f))

fig,ax=plt.subplots(figsize=(8,4.5))
for j in (1,2,3,4):
 rows=[r for r in cases if int(r['j'])==j and float(r['p_atm'])==0.1]
 ax.plot([float(r['N_ref_cm_minus2']) for r in rows],[float(r['peak_tau']) for r in rows],marker='o',label=f'R({j-1})')
ax.set(xscale='log',xlabel='HITRAN-reference column N_ref (molecules cm$^{-2}$)',ylabel='Conditional peak optical depth',title='HD 296 K Voigt benchmark, p(H$_2$)=0.1 atm')
ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(F/'FIG1_PEAK_TAU_VS_COLUMN.png',dpi=150);plt.close(fig)

fig,ax=plt.subplots(figsize=(8,4.5))
for p in (0.01,0.1,0.5):
 rows=[r for r in profiles if int(r['J_upper'])==3 and float(r['p_H2_atm'])==p and float(r['N_ref_cm_minus2'])==1e24]
 x=[float(r['offset_cm_minus1']) for r in rows];y=[float(r['transmission']) for r in rows]
 ax.plot(x,y,label=f'p(H$_2$)={p} atm')
ax.set(xlabel='Offset from the pressure-shifted center (cm$^{-1}$)',ylabel='Transmission I/I$_0$',title='HD R(2), 296 K, conditional Voigt absorption, N_ref=10$^{24}$ cm$^{-2}$')
ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(F/'FIG2_R2_TRANSMISSION_3PRESSURES.png',dpi=150);plt.close(fig)

fig,ax=plt.subplots(figsize=(8,4.5))
for j in (1,2,3,4):
 rows=[r for r in cases if int(r['j'])==j and float(r['p_atm'])==0.1]
 ax.plot([float(r['N_ref_cm_minus2']) for r in rows],[float(r['equivalent_width_window_cm1']) for r in rows],marker='o',label=f'R({j-1})')
ax.set(xscale='log',yscale='log',xlabel='HITRAN-reference column N_ref (molecules cm$^{-2}$)',ylabel='Finite-window equivalent width (cm$^{-1}$)',title='HD source-bound conditional line equivalent widths, 296 K')
ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(F/'FIG3_EQUIV_WIDTH_4LINES.png',dpi=150);plt.close(fig)
print([p.name for p in F.glob('*.png')])
