"""Two figures from saved primary JSONL only; never imports adapter/oracle/NPZ."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
rows=[json.loads(line) for line in (R/'results/primary002/raw_rows.jsonl').read_text().splitlines()]
summary=json.loads((R/'results/primary002/SUMMARY.json').read_text())
if summary['result']!='PASS_SCOPED':raise ValueError('FIGURE_REQUIRES_COMPLETED_PRIMARY')
out=R/'results/figures';out.mkdir(parents=True,exist_ok=False)
plt.rcParams.update({'font.size':10})
root=[r for r in rows if r['group']=='root'];comp=[r for r in rows if r['group']=='composite']
fig,axes=plt.subplots(2,1,figsize=(11.5,8.5));fig.subplots_adjust(top=.86,bottom=.14,hspace=.55,left=.12,right=.96)
fig.suptitle('Constant-shear retarded characteristic and Wien reference',y=.96,fontsize=16)
axes[0].plot(range(len(root)),[r['details']['delta']-r['details']['flrw_delta'] for r in root],'o',ms=4)
axes[0].set_yscale('symlog',linthresh=1e-9);axes[0].set_title('48 declared crossings: delay shift relative to FLRW',loc='left');axes[0].set_xlabel('Saved root-case index');axes[0].set_ylabel('Δ − Λ')
axes[1].plot(range(len(comp)),[r['details']['Wien_offset'] for r in comp],'o-',color='#187b79')
axes[1].set_title('12 represented-field composites: signed native-Wien correction',loc='left');axes[1].set_xlabel('Saved composite-case index');axes[1].set_ylabel('W(x_s) − W(x_t)')
for ax in axes:ax.grid(color='#e3e6ea')
fig.text(.08,.035,'Finite constant-shear Bianchi I subclass; prescribed reference temperature.\nSaved primary controls only. Parent REC-HISTORY remains PARTIAL; actual-history calibration remains open.',fontsize=10)
fig.savefig(out/'characteristic_reference.png',dpi=180);fig.savefig(out/'characteristic_reference.pdf');plt.close(fig)
a=[r for r in rows if r['group']=='actual'];e=[r for r in rows if r['group']=='envelope']
fig,axes=plt.subplots(2,1,figsize=(11.5,8.5));fig.subplots_adjust(top=.86,bottom=.16,hspace=.58,left=.13,right=.96)
fig.suptitle('Actual early retained prefix and conditional error controls',y=.96,fontsize=16)
axes[0].plot([r['details']['z'] for r in a],[r['details']['value'] for r in a],'o',color='#314b6d')
axes[0].invert_xaxis();axes[0].set_title('8 actual scalar h/4 interior queries at their own early domain',loc='left');axes[0].set_xlabel('Source redshift z');axes[0].set_ylabel('Saved scalar departure')
ratios=[float(r['details']['independent_error'])/r['details']['bounds']['e_in'] for r in e]
axes[1].plot(range(len(e)),ratios,'D-',color='#187b79',label='Independent error / supplied conditional bound');axes[1].axhline(1,color='#b34141',ls='--',label='Containment limit')
axes[1].set_title('12 analytic-field tubes with supplied bounds and root perturbations',loc='left');axes[1].set_xlabel('Saved envelope-case index');axes[1].set_ylabel('Error / bound');axes[1].legend(loc='upper left',bbox_to_anchor=(0,-.26),frameon=False,fontsize=9)
for ax in axes:ax.grid(color='#e3e6ea')
fig.text(.07,.025,'Actual h/4 data retain 0/313 coverage at the ADM01 target face. No actual M2 or independent uncertainty inferred.\nEnvelope controls use declared analytic fields; physical HOLD and prior campaign HOLDs remain.',fontsize=10)
fig.savefig(out/'actual_prefix_envelopes.png',dpi=180);fig.savefig(out/'actual_prefix_envelopes.pdf');plt.close(fig)
(out/'RENDER_RECEIPT.json').write_text(json.dumps({'source':'results/primary002/raw_rows.jsonl and SUMMARY.json','scientific_recomputation':False,'NPZ_loads':0,'files':['characteristic_reference.png','characteristic_reference.pdf','actual_prefix_envelopes.png','actual_prefix_envelopes.pdf']},indent=2)+'\n')
print('Two figures rendered from saved rows only.')
