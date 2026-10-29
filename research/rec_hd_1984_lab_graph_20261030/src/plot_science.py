"""Three source-identified scientific diagnostics (no fake model error bars)."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from decimal import Decimal as D
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'evidence'
R=json.loads((E/'MEASURED_ROTATIONAL_GRAPH.json').read_text())
measured=[r for r in R['experimental_rows'] if r['experiment']=='1984']
labels=[f"{r['uJ']}→{r['lJ']}" for r in measured]
# Primary 1984 differences, error bars represent reported *measurement* uncertainty only
fig,ax=plt.subplots(figsize=(7.4,4.5))
y=[float(D(r['measured_minus_2021_photon_Hz']))/1e6 for r in measured]
e=[float(D(r['reported_measurement_uncertainty_Hz']))/1e6 for r in measured]
ax.errorbar(range(3),y,yerr=e,fmt='o',capsize=5)
ax.axhline(0,linestyle='--',linewidth=0.8)
ax.set_xticks(range(3),labels)
ax.set_xlabel('HD rotational J upper → lower')
ax.set_ylabel('1984 laboratory − inherited 2021 photon line (MHz)')
ax.set_title('1984 measured HD lines versus frozen photon frequencies')
ax.text(0.01,0.01,'Error bars: reported 1984 measurement terms only; catalog covariance unknown.',transform=ax.transAxes,fontsize=8,va='bottom')
fig.tight_layout();fig.savefig(E/'FIG1_1984_RESIDUAL_MHz.png',dpi=185);plt.close(fig)
# 2022 precise sources separate scale
s22=[r for r in R['experimental_rows'] if r['experiment']=='2022']
fig,ax=plt.subplots(figsize=(7.4,4.2))
ax.errorbar([0,1],[float(D(r['measured_minus_2021_photon_Hz']))/1e6 for r in s22],yerr=[float(D(r['reported_measurement_uncertainty_Hz']))/1e6 for r in s22],fmt='o',capsize=5)
ax.axhline(0,linestyle='--',linewidth=0.8);ax.set_xticks([0,1],['J2−J0','J3−J1']);ax.set_ylabel('2022 lab − inherited photon sum (MHz)');ax.set_title('2022 measured HD ground-state combination differences')
ax.text(0.01,0.01,'Lab reported errors only; old CDMS covariance not included.',transform=ax.transAxes,fontsize=8,va='bottom')
fig.tight_layout();fig.savefig(E/'FIG2_2022_RESIDUAL_MHz.png',dpi=185);plt.close(fig)
# Physically useful LTE conditional ratios from three new direct measured lines
fig,ax=plt.subplots(figsize=(7.4,4.6))
for u,l in [(4,3),(6,5),(7,6)]:
 subset=[s for s in R['experimental_LTE_rows'] if s['uJ']==u]
 ax.plot([q['T_K'] for q in subset],[float(D(q['LTE_n_upper_over_lower'])) for q in subset],marker='o',label=f'J{u}/J{l} (1984)')
ax.set_yscale('log');ax.set_xlabel('Temperature (K)');ax.set_ylabel('Conditional LTE population ratio');ax.set_title('Measured-frequency anchored LTE ratios, HD v=0')
ax.legend();fig.tight_layout();fig.savefig(E/'FIG3_CONDITIONAL_LTE.png',dpi=185);plt.close(fig)
(E/'FIGURE_QA.json').write_text(json.dumps({'figures':[x.name for x in sorted(E.glob('FIG*.png'))],'source':'5 independent lab measurements (3 new primary 1984; 2 parent 2022) and frozen source Einstein A','no_model_error_or_cosmological_history':True},indent=2)+'\n')
