"""Figures from saved result arrays only; no scientific source import/solve."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from common import save

def main():
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    c=json.loads((a.results/'CERTIFICATE.json').read_text())
    with np.load(a.results/'CERTIFICATE_ARRAYS.npz') as f:lo=f['row_gain_lower'];hi=f['row_gain_upper']
    fig,axes=plt.subplots(2,1,figsize=(10,7),constrained_layout=True)
    rows=np.arange(len(lo));axes[0].plot(rows,hi,label='Certified upper');axes[0].plot(rows,lo,'--',label='Certified lower');axes[0].set_ylabel('Incoming infinity row gain');axes[0].legend();axes[0].set_title('Stable represented operator: certified gain bounds')
    axes[0].text(.02,.03,f"norm ∈ [{c['norm_lower']:.12g}, {c['norm_upper']:.12g}]",transform=axes[0].transAxes)
    axes[1].semilogy(rows,np.maximum(hi-lo,1e-300));axes[1].set_xlabel('Outgoing row (311: Ly-alpha, 312: Ly-beta, 313: Ly-gamma)');axes[1].set_ylabel('Certificate interval width');axes[1].set_title('Width shown separately; no physical uncertainty assigned')
    fig.savefig(a.out/'row_gain_norm.png',dpi=160);plt.close(fig)
    mixed=json.loads((a.results/'JOINT_LOCAL_CONTROLS.json').read_text());hist=json.loads((a.results/'HISTORY_ADMISSION.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),constrained_layout=True)
    for key in ('outgoing','F','R_gamma'):
        axes[0].semilogy(np.arange(len(mixed)),[max(row['metrics'][key]['normalized_error'],1e-300) for row in mixed],'o-',label=key)
    axes[0].axhline(2e-5,color='red',ls='--',label='Joint criterion');axes[0].set_xticks(range(len(mixed)),[f"d{r['direction']} h={r['h']:g}" for r in mixed],rotation=25);axes[0].set_ylabel('Normalized central-difference residual');axes[0].set_title('Same-source joint local response');axes[0].legend()
    error=np.array([r['absolute_error'] for r in hist['records']])/hist['normalization'];axes[1].semilogy(np.arange(313),np.maximum(error,1e-300),'.');axes[1].axhline(5e-9,color='red',ls='--',label='History criterion');axes[1].set_xlabel('Incoming query');axes[1].set_ylabel('Absolute error / global incoming scale');axes[1].set_title('Actual original payload / causal prefix admission');axes[1].legend()
    fig.savefig(a.out/'joint_history_residuals.png',dpi=160);plt.close(fig)
    save(a.out/'FIGURE_SCOPE.json',{'source_results':str(a.results),'saved_results_only':True,'physical_uncertainty':None,'requires_actual_png_review':True})
if __name__=='__main__':main()
