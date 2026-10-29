from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1]
s=json.loads((root/'evidence/NONLTE_GRID.json').read_text())
fig,ax=plt.subplots(figsize=(8.6,5.4))
for T in (50,100,200):
    a=[v for v in s['two_level_rows'] if v['T_K']==T and v['ortho_fraction']==0.5 and v['nH2_cm3']>0]
    ax.loglog([v['nH2_cm3'] for v in a],[v['cool_photon_W_per_HD'] for v in a],marker='o',label=f'{T} K')
ax.set(xlabel='Prescribed H$_2$ collider density (cm$^{-3}$)',ylabel='HD J=1→0 power per molecule (W)',title='HD J=1→0 two-level optically thin cooling (source-gated line)')
ax.legend();ax.grid(True,alpha=.25);fig.tight_layout();fig.savefig(root/'evidence/HD_J1_COOLING.png',dpi=180);plt.close(fig)

fig,ax=plt.subplots(figsize=(8.6,5.4))
for T in (50,100,200):
    a=[v for v in s['full9_rows'] if v['T_K']==T and v['ortho_fraction']==0.5 and v['nH2_cm3']>0]
    ax.loglog([v['nH2_cm3'] for v in a],[v['total_printed_power_W_per_HD'] for v in a],marker='o',label=f'{T} K')
ax.set(xlabel='Prescribed H$_2$ collider density (cm$^{-3}$)',ylabel='Summed HD emission per molecule (W)',title='Full 9-level diagnostic only; 7/8 frequency gates unresolved')
ax.legend();ax.grid(True,alpha=.25);fig.tight_layout();fig.savefig(root/'evidence/HD_9LEVEL_DIAGNOSTIC.png',dpi=180);plt.close(fig)

fig,ax=plt.subplots(figsize=(8.6,5.4))
for T in (50,100,200):
    a=[v for v in s['full9_rows'] if v['T_K']==T and v['ortho_fraction']==0.5 and v['nH2_cm3']>0]
    n=[v['nH2_cm3'] for v in a]
    for frac in (0,1):
        v=[x for x in s['full9_rows'] if x['T_K']==T and x['ortho_fraction']==frac and x['nH2_cm3']>0]
        # no extra source count claim, plot full-ladder ortho sensitivity as diagnostic
        if frac==0:
            ref=[x['total_printed_power_W_per_HD'] for x in v]
        else:
            ratio=[(x['total_printed_power_W_per_HD']/q-1)*100 for x,q in zip(v,ref)]
    ax.semilogx(n,ratio,marker='o',label=f'{T} K')
ax.axhline(0,linestyle=':',linewidth=1)
ax.set(xlabel='Prescribed H$_2$ collider density (cm$^{-3}$)',ylabel='Full-ladder ortho-vs-para emission change (%)',title='Spin-partner response absent in J=1 two-level, present in full ladder')
ax.legend();ax.grid(True,alpha=.25);fig.tight_layout();fig.savefig(root/'evidence/HD_SPIN_SENSITIVITY.png',dpi=180);plt.close(fig)
print('rendered 3 PNG figures')