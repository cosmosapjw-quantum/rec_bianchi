#!/usr/bin/env python3
"""Plot only saved discrete, source-conditional line-centre ratios."""
import json
from decimal import Decimal
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent
src=json.loads((root/'results/FIELD_SEMANTICS.json').read_text())
lines=src['lines']
x=[v['upper_J'] for v in lines]
y=[float(Decimal(v['alpha_peak_P_over_E_minus_one'])*Decimal(10)**6) for v in lines]
fig,ax=plt.subplots(figsize=(7.5,4.8))
ax.axhline(0,linestyle='--',linewidth=1)
ax.scatter(x,y,s=62,zorder=3)
for i,v in enumerate(y):
    ax.annotate((f'{v:+.2e}' if abs(v)<.001 else f'{v:+.4f}'),(x[i],v),xytext=(0,9 if v>=0 else -15),textcoords='offset points',ha='center',fontsize=8)
ax.set_xlim(.55,8.45);ax.set_ylim(min(y)-.14,max(y)+.14)
ax.set_xticks(x);ax.set_xlabel('HD upper rotational level J (J -> J-1)')
ax.set_ylabel('alpha_peak(printed) / alpha_peak(level-gap) - 1 [ppm]')
ax.set_title('Conditional HD frequency-policy response at own line centre')
ax.grid(axis='y',alpha=.23)
fig.text(.5,.035,'Fixed A, LTE level populations and Gaussian velocity width; no physical source choice',ha='center',fontsize=8)
fig.subplots_adjust(bottom=.20,top=.90)
fig.savefig(root/'results/OPACITY_POLICY_DIAGNOSTIC.png',dpi=170)
fig.savefig(root/'results/OPACITY_POLICY_DIAGNOSTIC.pdf')
plt.close(fig)
