"""Render the single scientific figure only from saved exact primary outputs."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent


def main():
    source=HERE/'results'/'primary001'
    rows=json.loads((source/'retimings.json').read_text())
    chords=json.loads((source/'chords.json').read_text())
    summary=json.loads((source/'summary.json').read_text())
    figure_dir=HERE/'figures';figure_dir.mkdir(exist_ok=True)
    fig,axes=plt.subplots(2,1,figsize=(10.5,8.3),constrained_layout=True)
    colors={'cross_left':'#0072B2','cross_right':'#D55E00'}
    for case,color in colors.items():
        selected=[r for r in rows if r['case']==case]
        x=[r['incoming_index'] for r in selected]
        axes[0].scatter(x,[abs(r['direct']['display']) for r in selected],s=13,color=color,
                        label=case.replace('_',' ')+' |exact remainder|',zorder=3)
        axes[0].plot(x,[r['bound']['display'] for r in selected],lw=.8,color=color,alpha=.6,
                     label=case.replace('_',' ')+' absolute jump bound')
    within=[r for r in rows if r['case'].startswith('within')]
    axes[0].scatter([r['incoming_index'] for r in within],
                    [r['direct']['display'] for r in within],s=6,color='#009E73',
                    label='within cell: exactly zero',zorder=4)
    positive=[abs(r['direct']['display']) for r in rows if r['direct']['display']!=0]
    floor=min(positive)/10 if positive else 1e-30
    axes[0].set_yscale('symlog',linthresh=floor,linscale=.5)
    axes[0].set_ylabel('|Retiming remainder| / bound\n(occupation departure)')
    axes[0].set_title(f"{summary['executed_retimings']} exact retimings; {summary['skipped_retimings']} causal-prefix skips")
    axes[0].legend(fontsize=8,ncol=2,loc='upper right')
    axes[1].scatter([r['incoming_index'] for r in chords],
                    [abs(r['direct']['display']) for r in chords],s=14,color='#6A3D9A',label='|exact chord remainder|')
    axes[1].plot([r['incoming_index'] for r in chords],
                 [r['bound']['display'] for r in chords],lw=1,color='#333333',label='absolute Peano jump bound')
    positive_chord=[abs(r['direct']['display']) for r in chords if r['direct']['display']!=0]
    axes[1].set_yscale('symlog',linthresh=min(positive_chord)/10 if positive_chord else 1e-30,linscale=.5)
    axes[1].set_ylabel('|Chord remainder| / bound\n(occupation departure)')
    axes[1].set_title(f"{summary['executed_chords']} exact Peano chords; final-cell endpoints use causal fallback")
    axes[1].legend(fontsize=9)
    for ax in axes:
        ax.set_xlabel('Original incoming query index')
        ax.grid(True,which='both',alpha=.16)
    fig.suptitle('Native-real piecewise-linear history: exact jump remainders\n'
                 'Physical epsilon unavailable; physical bound coverage 0/313',fontsize=13)
    fig.savefig(figure_dir/'history_remainders.png',dpi=170)
    fig.savefig(figure_dir/'history_remainders.pdf')
    plt.close(fig)
    print('SAVED history_remainders.png history_remainders.pdf; source: results/primary001/*.json')


if __name__=='__main__':
    main()
