"""One presentation correction from saved data; preserve original figures."""
from pathlib import Path
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator

UNIT=Path(__file__).resolve().parents[1]


def signed_scale(ax,y):
    maximum=max(float(np.max(np.abs(y))),1e-280)
    exponent=int(math.floor(math.log10(maximum)))
    scale=10.**exponent
    ax.set_yscale('symlog',linthresh=1e-4)
    ax.set_yticks([-1.,0.,1.],['−1','0','1'])
    ax.yaxis.set_minor_locator(NullLocator())
    limit=max(1.2,maximum/scale*1.15)
    ax.set_ylim(-limit,limit)
    ax.axhline(0,color='0.6',lw=.5)
    ax.tick_params(labelsize=9)
    return np.asarray(y)/scale,exponent


def main():
    result=UNIT/'results/primary001'
    dest=UNIT/'results/figures002';dest.mkdir(parents=True,exist_ok=False)
    with np.load(result/'ANALYTIC_RESPONSE.npz',allow_pickle=False) as f:
        data={k:f[k] for k in f.files}
    comparison=json.loads((result/'COMPLEX_COMPARISON.json').read_text())
    axes=['xe','xHII','ln TR','ln TM','ln nH','ln H']
    plt.rcParams.update({'font.size':10,'axes.titlesize':11,'axes.labelsize':10,
                         'pdf.compression':6,'savefig.facecolor':'white'})
    fig=plt.figure(figsize=(12,8.4))
    grid=fig.add_gridspec(3,3,height_ratios=[1,1,.72])
    fig.subplots_adjust(left=.075,right=.98,bottom=.17,top=.90,wspace=.40,hspace=.65)
    for j in range(6):
        ax=fig.add_subplot(grid[j//3,j%3])
        y,exponent=signed_scale(ax,data['d_outgoing'][:,j])
        ax.plot(np.arange(314),y,lw=1)
        ax.set_title('Derivative: '+axes[j])
        ax.set_xlabel('Outgoing row')
        ax.set_ylabel('Response ['+format(10.**exponent,'.0e')+']')
        ax.set_xticks([0,100,200,313])
    residual=fig.add_subplot(grid[2,:])
    outgoing=[comparison['outputs']['outgoing'][j]['normalized_error'] for j in range(6)]
    coefficient=[max(group[j]['normalized_error'] for group in comparison['coefficients'].values()) for j in range(6)]
    residual.plot(np.arange(6),outgoing,'o-',ms=4,label='Outgoing derivative')
    residual.plot(np.arange(6),coefficient,'s-',ms=4,label='Maximum coefficient')
    residual.axhline(2e-8,color='#B43A36',ls='--',label='Criterion: 2e−8')
    residual.set_yscale('symlog',linthresh=1e-15)
    residual.set_yticks([0.,1e-12,2e-8],['0','1e−12','2e−8'])
    residual.yaxis.set_minor_locator(NullLocator())
    residual.set_ylim(-1e-15,2e-7)
    residual.set_xticks(np.arange(6),axes)
    residual.set_ylabel('Error / scale')
    residual.set_title('Analytic tangent versus complex step (h = 1e−20)',fontsize=11)
    residual.tick_params(labelsize=9)
    residual.legend(loc='upper left',ncol=3,fontsize=8,frameon=False)
    fig.suptitle('Local HyRec primitive response — stable arithmetic',y=.97,fontsize=14)
    fig.text(.075,.08,'Response = derivative of dimensionless signed Wien occupation per dimensionless primitive increment.',fontsize=10)
    fig.text(.075,.045,'Bracketed axis factors give the ordinate unit. Rows 0–310: virtual bins; 311–313: Lyα, Lyβ, Lyγ. Zero ticks are retained.',fontsize=9)
    fig.savefig(dest/'six_axis_outgoing.png',dpi=144)
    fig.savefig(dest/'six_axis_outgoing.pdf')
    plt.close(fig)
    fig,panels=plt.subplots(2,2,figsize=(11,6.8))
    fig.subplots_adjust(left=.09,right=.98,bottom=.19,top=.87,wspace=.30,hspace=.50)
    quantities=[('d_F','Ionization source F','Ionization'),
                ('d_R_gamma','Single Lyα number event','Number'),
                ('d_radiation_energy','Radiation energy event','Energy'),
                ('d_atomic_energy','Paired atomic energy event','Energy')]
    colors=['#355C7D','#C06C84','#457B9D','#E09F3E','#548235','#8064A2']
    for ax,(key,title,label) in zip(panels.flat,quantities):
        y,exponent=signed_scale(ax,data[key])
        ax.bar(np.arange(6),y,color=colors,width=.65)
        ax.set_xticks(np.arange(6),axes)
        ax.set_ylabel(label+' ['+format(10.**exponent,'.0e')+']')
        ax.set_title(title)
    fig.suptitle('Primitive ionization, number and paired energy responses',y=.97,fontsize=14)
    fig.text(.09,.10,'Units per dimensionless primitive increment: ionization d(dxHII/d ln a); number m⁻³ s⁻¹; energy J m⁻³ s⁻¹.',fontsize=10)
    fig.text(.09,.055,'Axes xe and xHII are independent source arguments. The physical pure-H derivative combines both columns. Zero ticks are retained.',fontsize=9)
    fig.savefig(dest/'ionization_number_energy.png',dpi=144)
    fig.savefig(dest/'ionization_number_energy.pdf')
    plt.close(fig)
    (dest/'FIGURE_SCOPE.json').write_text(json.dumps({'source':'immutable saved primary001 arrays only',
          'purpose':'one root-authorized presentation correction, first figures preserved',
          'changes':['short ordinate labels','shared units captions','explicit sparse signed-log ticks including zero','144dpi export'],
          'source_evaluations':0,'linear_solves':0,'criterion_changes':0,'physical_epsilon':None},indent=2)+'\n')


if __name__=='__main__':
    main()
