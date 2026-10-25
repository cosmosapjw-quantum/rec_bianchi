"""Saved-data layout-only correction; exact numeric values/scales unchanged."""
import argparse,json,os,resource
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def main():
 p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 cases=json.loads((a.results/'FINITE_CASES.json').read_text());deriv=json.loads((a.results/'DERIVATIVE_ADJOINT_CHECKS.json').read_text())
 fig,ax=plt.subplots(1,2,figsize=(12,5.4),constrained_layout=False)
 fig.subplots_adjust(left=.09,right=.98,bottom=.30,top=.84,wspace=.40)
 for direction in (1,2):
  rows=[r for r in cases if r['direction']==direction];t=np.array([r['t'] for r in rows]);r=np.array([r['outgoing_remainder_norm'] for r in rows]);floor=np.array([100*r['arithmetic_floor'] for r in rows])
  ax[0].set_xscale('log');ax[0].set_yscale('symlog',linthresh=1e-30);ax[0].plot(t,r,'o-',label=f'Direction {direction}');ax[0].plot(t,floor,':',label=f'Direction {direction}: 100 × floor')
  if np.any(r==0):ax[0].plot(t[r==0],r[r==0],'x',clip_on=False,label=f'Direction {direction}: exact zero')
 ax[0].set_xticks([.125,.25,.5,1.],labels=['.125','.25','.5','1']);ax[0].set_xticks([],minor=True)
 ax[0].set_xlabel('Fixed probe multiplier t (log axis)',labelpad=8);ax[0].set_ylabel('Outgoing Taylor remainder norm',labelpad=8);ax[0].set_ylim(bottom=0)
 ax[0].set_title('Four-step local remainder controls\nSymlog: linear within 1e-30 of zero',fontsize=11,pad=12)
 ax[0].legend(loc='upper center',bbox_to_anchor=(.5,-.27),ncol=2,fontsize=8,frameon=False)
 pairs=[(r['direction'],v) for r in deriv for v in r['pairings']];errors=np.array([v['normalized_error'] for _,v in pairs]);x=np.arange(len(errors));zero=errors==0
 ax[1].set_yscale('symlog',linthresh=1e-16);ax[1].plot(x[~zero],errors[~zero],'o',label='Nonzero residual');ax[1].plot(x[zero],errors[zero],'x',clip_on=False,label='Exact zero residual');ax[1].axhline(2e-12,color='red',ls='--',label='Frozen criterion: 2e-12');ax[1].set_ylim(0,4e-12);ax[1].set_xticks(x,[f"d{d},w{v['covector']}" for d,v in pairs])
 ax[1].set_xlabel('Direction and receiver covector',labelpad=8);ax[1].set_ylabel('Coordinate pairing residual / gross scale',labelpad=8);ax[1].set_title('Adjoint consistency\nSymlog: linear within 1e-16 of zero',fontsize=11,pad=12)
 ax[1].legend(loc='upper center',bbox_to_anchor=(.5,-.27),ncol=1,fontsize=8,frameon=False)
 fig.text(.5,.025,'Fixed local controls; no global convergence claim. Exact zeros are marked explicitly.',ha='center',fontsize=9)
 fig.savefig(a.out/'remainder_adjoint_consistency.png',dpi=160);plt.close(fig)
 (a.out/'FIGURE_SCOPE.json').write_text(json.dumps({'saved_data_only':True,'layout_only':True,'constrained_layout':False,'explicit_subplot_margins':{'left':.09,'right':.98,'bottom':.30,'top':.84,'wspace':.40},'left_x_ticks':[.125,.25,.5,1.],'left_symlog_linthresh':1e-30,'right_symlog_linthresh':1e-16,'adjoint_tolerance_unchanged':2e-12,'first_PNGs_preserved':True,'source_or_solver_execution':0,'operator_actions':0,'event_actions':0,'actual_PNG_review_required':True,'RLIMIT_CPU':resource.getrlimit(resource.RLIMIT_CPU),'RLIMIT_AS':resource.getrlimit(resource.RLIMIT_AS),'thread_environment':{k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS')}},indent=2)+'\n')
if __name__=='__main__':main()
