"""One bounded figure process, saved results only; no source/solver imports."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

UNIT=Path(__file__).resolve().parents[1]


def main():
    result=UNIT/'results/primary001'
    destination=UNIT/'results/figures001';destination.mkdir(parents=True,exist_ok=False)
    with np.load(result/'ANALYTIC_RESPONSE.npz',allow_pickle=False) as f:
        data={k:f[k] for k in f.files}
    comparison=json.loads((result/'COMPLEX_COMPARISON.json').read_text())
    axes=['xe','xHII','ln TR','ln TM','ln nH','ln H']
    fig=plt.figure(figsize=(12,9),constrained_layout=True)
    grid=fig.add_gridspec(3,3,height_ratios=[1,1,.7])
    panels=[fig.add_subplot(grid[j//3,j%3]) for j in range(6)]
    for j,ax in enumerate(panels):
        y=data['d_outgoing'][:,j]
        ax.plot(np.arange(314),y,lw=1)
        maxval=max(float(np.max(np.abs(y))),1e-280)
        ax.set_yscale('symlog',linthresh=maxval*1e-5)
        ax.set_title('Derivative with respect to '+axes[j],fontsize=11)
        ax.set_xlabel('Outgoing row (311 virtual, then Lyα/β/γ)')
        ax.set_ylabel('Signed Wien occupation per primitive increment')
        error=comparison['outputs']['outgoing'][j]['normalized_error']
        ax.text(.04,.95,'Complex comparison: '+format(error,'.2e'),transform=ax.transAxes,va='top',fontsize=9)
        ax.axhline(0,color='0.5',lw=.5)
    residual=fig.add_subplot(grid[2,:])
    outgoing_error=[comparison['outputs']['outgoing'][j]['normalized_error'] for j in range(6)]
    coefficient_error=[max(group[j]['normalized_error'] for group in comparison['coefficients'].values()) for j in range(6)]
    residual.plot(np.arange(6),outgoing_error,'o-',label='Outgoing derivative')
    residual.plot(np.arange(6),coefficient_error,'s-',label='Maximum coefficient block')
    residual.axhline(2e-8,color='#B43A36',ls='--',label='Frozen comparison criterion')
    residual.set_yscale('symlog',linthresh=1e-15)
    residual.set_xticks(np.arange(6),axes)
    residual.set_ylabel('Normalized max derivative difference')
    residual.set_title('Analytic tangent versus complex step (h=10⁻²⁰)')
    residual.legend(loc='best',fontsize=9)
    fig.suptitle('Local primitive response at the retained HyRec face — stable arithmetic')
    fig.savefig(destination/'six_axis_outgoing.png',dpi=160)
    fig.savefig(destination/'six_axis_outgoing.pdf')
    plt.close(fig)
    fig,panels=plt.subplots(2,2,figsize=(11,7),constrained_layout=True)
    quantities=[('d_F','Ionization source F','d(dxHII/d ln a) per primitive increment'),
                ('d_R_gamma','Single Lyα number event','m⁻³ s⁻¹ per primitive increment'),
                ('d_radiation_energy','Radiation energy event','J m⁻³ s⁻¹ per primitive increment'),
                ('d_atomic_energy','Paired atomic energy event','J m⁻³ s⁻¹ per primitive increment')]
    for ax,(key,title,units) in zip(panels.flat,quantities):
        y=data[key]
        ax.bar(np.arange(6),y,color=['#355C7D','#C06C84','#457B9D','#E09F3E','#548235','#8064A2'])
        maximum=max(float(np.max(np.abs(y))),1e-280)
        ax.set_yscale('symlog',linthresh=maximum*1e-5)
        ax.set_xticks(np.arange(6),axes)
        ax.set_ylabel(units);ax.set_title(title);ax.axhline(0,color='0.5',lw=.5)
    fig.suptitle('Independent primitive coordinates; physical pure-H direction combines xe+xHII')
    fig.savefig(destination/'ionization_number_energy.png',dpi=160)
    fig.savefig(destination/'ionization_number_energy.pdf')
    plt.close(fig)
    (destination/'FIGURE_SCOPE.json').write_text(json.dumps({'source':'saved primary001 arrays only','source_evaluations':0,
          'linear_solves':0,'quantity_units':'native scalar source with SI event number/energy','physical_epsilon':None},indent=2)+'\n')


if __name__=='__main__':
    main()
