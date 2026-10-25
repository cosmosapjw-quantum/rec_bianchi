"""Root-authorized saved-data layout correction; no scientific source imports."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def main():
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    mixed=json.loads((a.results/'JOINT_LOCAL_CONTROLS.json').read_text());hist=json.loads((a.results/'HISTORY_ADMISSION.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),constrained_layout=True)
    for key in ('outgoing','F','R_gamma'):
        axes[0].semilogy(np.arange(len(mixed)),[row['metrics'][key]['normalized_error'] for row in mixed],'o-',label=key)
    axes[0].axhline(2e-5,color='red',ls='--',label='Joint criterion')
    axes[0].set_xticks(range(len(mixed)),[f"d{r['direction']} h={r['h']:g}" for r in mixed],rotation=25)
    axes[0].set_ylabel('Normalized central-difference residual')
    axes[0].set_title('Four fixed local checks\nNot convergence evidence')
    axes[0].legend()
    error=np.array([r['absolute_error'] for r in hist['records']],dtype=float)/hist['normalization']
    if np.any(error<0) or not np.all(np.isfinite(error)):raise ValueError('INVALID_SAVED_HISTORY_ERROR')
    query=np.arange(len(error));positive=error>0;zero=error==0
    axes[1].set_yscale('symlog',linthresh=1e-20)
    axes[1].plot(query[positive],error[positive],'.',label='Positive reconstruction error')
    axes[1].plot(query[zero],error[zero],'x',markersize=4,clip_on=False,label=f'Exact zero ({int(np.sum(zero))} queries)')
    axes[1].axhline(5e-9,color='red',ls='--',label='History criterion: 5e-9')
    axes[1].set_ylim(0,1e-8)
    axes[1].set_yticks([0,1e-20,1e-18,1e-16,1e-14,1e-12,1e-10,1e-8],labels=['0',r'$10^{-20}$',r'$10^{-18}$',r'$10^{-16}$',r'$10^{-14}$',r'$10^{-12}$',r'$10^{-10}$',r'$10^{-8}$'])
    axes[1].set_xlabel('Incoming query')
    axes[1].set_ylabel('Absolute error / global incoming scale')
    axes[1].set_title('Actual original payload / causal prefix admission\nSymlog: linear within 1e-20 of zero')
    axes[1].legend(loc='upper left',fontsize=8)
    fig.savefig(a.out/'joint_history_residuals.png',dpi=160);plt.close(fig)
    (a.out/'FIGURE_SCOPE.json').write_text(json.dumps({'saved_results_only':True,'source_results':str(a.results),'figure':'joint_history_residuals.png','zero_queries':int(np.sum(zero)),'symlog_linthresh':1e-20,'ylim':[0,1e-8],'physical_uncertainty':None,'fixed_checks_are_convergence_evidence':False,'first_PNGs_preserved':True,'requires_actual_PNG_review':True},indent=2)+'\n')
if __name__=='__main__':main()
