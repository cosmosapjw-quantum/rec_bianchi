#!/usr/bin/env python3
"""Discrete source-literal diagnostic plot, not observational or physical fit."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from decimal import Decimal
p=Path(__file__).resolve().parent
r=json.loads((p/'results/print_precision_certificate.json').read_text())
rows=r['print_rows']
x=[row['j_up'] for row in rows]
y=[float(Decimal(row['absolute_delta_Hz'])) for row in rows]
lim=float(Decimal(rows[0]['nearest_rounding_bound_Hz']))
fig,ax=plt.subplots(figsize=(7.2,5.4))
ax.scatter(x,y,marker='o',s=55,zorder=3,label='|Printed energy-frequency gap|')
ax.axhline(lim,linestyle='--',linewidth=1.4,label=f'Nearest-rounding envelope: {lim:.4f} Hz')
ax.axhline(2*lim,linestyle=':',linewidth=1.4,label=f'Conservative truncation envelope: {2*lim:.4f} Hz')
ax.set_yscale('log'); ax.set_xticks(x)
ax.set_xlabel('Upper rotational level J (transition J to J-1)')
ax.set_ylabel('Absolute printed-column discrepancy (Hz)')
ax.set_title('HD LAMDA printed decimals: source-compatibility diagnostic')
ax.grid(axis='y',alpha=.24)
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.18),ncol=1,fontsize=8.3,frameon=False)
ax.text(.98,.055,'Public transcription only; not raw CDMS data',transform=ax.transAxes,ha='right',fontsize=8)
fig.subplots_adjust(bottom=.32,top=.91);fig.savefig(p/'results/printed_precision_discrepancy.png',dpi=180)
plt.close(fig)
