from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((p/'results/J1_CMB_RT_432_PHYSICAL_CASES.csv').open()))
fig,ax=plt.subplots(figsize=(7.8,5.1))
for T in [50,100,200]:
 s=[r for r in rows if int(r['Tgas_K'])==T and r['nH2_cm3']=='10000' and r['ortho_fraction']=='0.5' and r['N_HD_cm_minus2']=='1e18']
 ax.plot([int(q['z']) for q in s],[float(q['delta_T_RJ0_observed_K']) for q in s],marker='o',label=f'T_gas={T} K')
ax.axhline(0,linewidth=0.9)
ax.set(xlabel='Redshift z',ylabel='Observed CMB line-center contrast (Rayleigh-Jeans K)',title='HD J=1 to 0: source-pinned conditional CMB spectral contrast')
ax.legend();ax.grid(alpha=.2)
fig.tight_layout();fig.savefig(p/'results/FIG_CMB_J1_RT_CONTRAST.png',dpi=175);plt.close(fig)
print('figure',p/'results/FIG_CMB_J1_RT_CONTRAST.png')
