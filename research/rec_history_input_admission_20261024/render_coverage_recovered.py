"""New summary-only display after workspace reset; no query reconstruction."""
import json
import math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent
s=json.loads((R/'results/primary001/SUMMARY.json').read_text())
out=R/'results/figures';out.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.size':11})
fig=plt.figure(figsize=(12.8,6.8));ax=fig.add_axes([.22,.32,.74,.43])
fig.suptitle('History input coverage — recovered-summary display',y=.96,fontsize=18,fontweight='bold')
ax.set_title('313-query retained-cell availability; error calibration remains open',loc='left',pad=22,fontsize=13)
ax.text(0,1.025,'Open marker: full archive strict endpoint; tick: last eligible causal knot',transform=ax.transAxes,fontsize=9,color='#4b5563')
ax.axvspan(s['query_z_min'],s['query_z_max'],color='#b34141',alpha=.18,label='Required retarded source domain')
ax.axvline(s['face']['z'],color='#b34141',ls='--',lw=1.4,label=f"Target face z = {s['face']['z']:.6f}")
labels=['h/2 U4 · 2,006 columns','h/4 R3Q · 1,519 columns','h/4 smoke · 24 columns','h/2 U5 · 16,733 columns']
for i,c in enumerate(s['candidates']):
    ok=c['coverage_counts'].get('COVERED_RETAINED_CELL',0);color='#187b79' if ok else '#7b8794'
    end=math.exp(-(c['eta0']+c['h']*(c['face_causal_columns']-1)))-1
    ax.plot([c['z_first'],end],[i,i],lw=9,color=color,solid_capstyle='butt',label='Eligible causal prefix' if i==3 else None)
    if c['face_causal_columns']<c['columns']:
        ax.plot([end,c['z_last']],[i,i],lw=5,color=color,alpha=.30,ls='--',label='Future archive (ineligible at target face)')
        ax.plot(end,i,'|',color=color,ms=16,mew=2)
    ax.plot(c['z_first'],i,'o',color=color,ms=6)
    ax.plot(c['z_last'],i,'o',mec=color,mfc='white',mew=1.5,ms=6)
    ax.text(820,i,f'{ok}/313',ha='left',va='center',color=color,fontweight='bold')
ax.set_yticks(range(4),labels);ax.set_ylim(3.55,-.55);ax.set_xlim(1760,750)
ax.set_xlabel('Redshift z  (time increases to the right)');ax.grid(axis='x',color='#e3e6ea');ax.set_axisbelow(True)
ax.legend(loc='upper left',bbox_to_anchor=(0,-.22),ncol=2,frameon=False,fontsize=9)
fig.text(.055,.075,'New display from recovered exact SUMMARY only; original figures and detailed query rows were not recovered.\nCoverage means retained-cell availability. Physical-domain mismatch and all prior HOLDs remain; error calibration is open.\nTarget T₀ = 2.728 K; candidate T₀ = 2.7255 K. No scientific rerun; no query-delay panel reconstructed.',fontsize=10,color='#374151')
fig.savefig(out/'history_input_coverage_recovered.png',dpi=180)
fig.savefig(out/'history_input_coverage_recovered.pdf')
plt.close(fig)
print('Rendered recovered saved summary only; new scientific cases 0; no query reconstruction.')
