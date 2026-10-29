#!/usr/bin/env python3
"""Eight exact source-derived local per-event ledger coefficients, NOT energy production."""
import json
from fractions import Fraction
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
j=json.loads((HERE/'results/RESULT.json').read_text())
rows=j['rows'];x=[r['J_upper'] for r in rows]
y=[float(Fraction(r['matter_plus_radiation_J_per_down_event']))*1e27 for r in rows]
fig,ax=plt.subplots(figsize=(3.55,2.75))
ax.bar(x,y,width=.66)
ax.axhline(0,linewidth=.8,color='black')
ax.set_xticks(x)
ax.set_xlabel(r'Upper $J$ in $J\to J-1$',fontsize=9)
ax.set_ylabel(r'$h(\nu_P-\nu_E)$ ($10^{-27}$ J/event)',fontsize=8.7)
ax.tick_params(labelsize=8)
ax.set_title('HD local source-energy ledger',fontsize=9.5)
ax.grid(axis='y',alpha=.20)
fig.subplots_adjust(left=.22,right=.97,bottom=.29,top=.88)
fig.text(.50,.075,'Near zero: J1 +5.46e-6; J8 -4.55e-3',ha='center',fontsize=7.1)
out=HERE/'results'
fig.savefig(out/'LOCAL_LEDGER.png',dpi=220)
fig.savefig(out/'LOCAL_LEDGER.svg')
plt.close(fig)
