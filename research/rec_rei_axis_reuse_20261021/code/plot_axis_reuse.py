"""Plot stored endpoints only. No solver runs; Matplotlib default colors."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import numpy as np
import matplotlib.pyplot as plt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--results', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise FileExistsError('CREATE_ONLY_FIGURES')
    args.out.mkdir(parents=True)
    src = args.results / 'withheld_comparison.csv'
    rows = list(csv.DictReader(src.open()))
    for row in rows:
        for k in row:
            if k not in ('case_id', 'role'):
                row[k] = float(row[k])
    S, M, R = 'signed_Sigma_requested', 'signed_Pi_m_requested', 'signed_Pi_r_requested'
    table = {(r[S], r[M], r[R]): r for r in rows}
    axes = [sorted({r[k] for r in rows}) for k in (S, M, R)]
    assert len(table) == 729 and len([r for r in rows if r['role']=='WITHHELD']) == 576
    outputs = []
    def save(fig, name):
        fig.savefig(args.out / (name + '.png'), dpi=180)
        fig.savefig(args.out / (name + '.svg'))
        outputs.append(name)
        plt.close(fig)

    # Real-coordinate cell boundaries: the grid is deliberately nonuniform.
    def edges(v):
        v=np.array(v)
        return np.r_[v[0]-(v[1]-v[0])/2, (v[:-1]+v[1:])/2, v[-1]+(v[-1]-v[-2])/2]
    mx=np.array(axes[1])*1e4; ry=np.array(axes[2])*1e4
    field=np.array([[table[(0., m, r)]['final_signed_Sigma_actual'] for m in axes[1]] for r in axes[2]])
    fig,ax=plt.subplots(figsize=(8.0,6.4),layout='constrained')
    im=ax.pcolormesh(edges(mx),edges(ry),field*1e7,shading='flat')
    xx,yy=np.meshgrid(mx,ry)
    ax.scatter(xx.ravel(), yy.ravel(), marker='+', s=14, linewidths=.6)
    ax.plot(mx,-mx,linestyle='--',label=r'Initial total stress zero: $P_{r0}=-P_{m0}$')
    ax.set(xlabel=r'Initial signed matter stress $P_{m0}\ [10^{-4}]$',
           ylabel=r'Initial signed radiation stress $P_{r0}\ [10^{-4}]$',
           title='Completed matter/radiation pilot: actual shear response\n'
                 r'$S_0=0$; warm LRS, $a=0.1999\rightarrow0.2$')
    ax.set_xticks([-4,-2,0,2,4]);ax.set_yticks([-4,-2,0,2,4])
    ax.set_xlim(mx[0],mx[-1]);ax.set_ylim(ry[0],ry[-1])
    ax.legend(loc='upper left',fontsize=8)
    fig.colorbar(im,ax=ax,label=r'Actual final signed shear $S_f\ [10^{-7}]$')
    save(fig,'actual_matter_radiation_response')

    fig,ax=plt.subplots(figsize=(8,5.6),layout='constrained')
    pairs=[('final_signed_Sigma','Shear'),('final_signed_Pi_m','Matter stress'),
           ('final_signed_Pi_r','Radiation stress'),('final_signed_Pi_total','Total stress')]
    for col,label in pairs:
        values=[max(abs(r[col+'_error']) for r in rows if r[S]==s and r['role']=='WITHHELD')/3e-13 for s in axes[0]]
        ax.plot(np.array(axes[0])*1e3,values,marker='o',label=label)
    ax.axhline(1.,linestyle='--',label='Inherited display/orientation floor')
    ax.set_yscale('log')
    ax.set(xlabel=r'Initial signed shear $S_0\ [10^{-3}]$',
           ylabel=r'Maximum endpoint mismatch / $(3\times10^{-13})$',
           title='153 axis cases reconstruct 576 withheld mixed endpoints\n'
                 'Retrospective finite-grid comparison, not an ODE error bound')
    ax.legend(fontsize=8,ncol=2)
    ax.grid(True,which='major',alpha=.25)
    save(fig,'withheld_endpoint_mismatch')

    cancel=[table[(0.,m,-m)] for m in axes[1] if m!=0.]
    fig,ax=plt.subplots(figsize=(8,5.6),layout='constrained')
    x=[r[M]*1e4 for r in cancel]
    actual=[r['final_signed_Sigma_actual']*1e11 for r in cancel]
    pred=[r['final_signed_Sigma_predicted']*1e11 for r in cancel]
    ax.plot(x,actual,'o-',label='Saved coupled endpoint')
    ax.plot(x,pred,'x--',label='Axis-only reconstruction')
    ax.axhline(0.,linestyle=':')
    ax.set(xlabel=r'Initial signed matter stress $P_{m0}\ [10^{-4}]$',
           ylabel=r'Final signed shear $S_f\ [10^{-11}]$',
           title=r'Initially cancelling stresses: $S_0=0,\ P_{r0}=-P_{m0}$'+'\n'
                 'Warm LRS, a=0.1999 to 0.2; endpoints, not full histories')
    ax.legend();ax.grid(True,alpha=.25)
    save(fig,'cancellation_response')

    receipt={'schema':'rec.rei.axis_reuse.figures.v1',
        'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
        'plot_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'data_points':{'heatmap':81,'withheld_endpoints':576,'cancellation':8},
        'new_ODE_runs':0,'colors':'matplotlib defaults',
        'scope':'Actual stored warm C15 endpoints and retrospective endpoint reconstruction only',
        'nonuniform_coordinates':'Cell edges use adjacent physical-coordinate midpoints; + marks are actual grid points',
        'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in args.out.iterdir()}}
    (args.out/'PROVENANCE.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'figures':outputs,'output_directory':str(args.out)},indent=2))

if __name__=='__main__':
    main()
