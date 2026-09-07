"""Render saved target-grid diagnostics only. No model/test imports or replay."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[3]


def read_csv(path):
    with path.open(newline='',encoding='utf-8') as handle:return list(csv.DictReader(handle))


def points(rows,field,**selection):
    chosen=[x for x in rows if all(x[k]==str(v) for k,v in selection.items())]
    chosen.sort(key=lambda x:int(x['level']))
    if [int(x['level']) for x in chosen]!=list(range(6)):
        raise ValueError('six distinct refinement levels required for every plotted series')
    x=[int(v['nodes']) for v in chosen];y=[float(v[field]) for v in chosen]
    if not all(math.isfinite(v) for v in y):raise ValueError('nonfinite plotted series')
    return x,y


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();run=args.run.resolve();out=args.out.resolve()
    if out==ROOT or ROOT in out.parents:ap.error('render outside the worktree')
    payload=run/'payload'
    process=json.loads((run/'PROCESS.json').read_text(encoding='utf-8'))
    report=json.loads((payload/'RESULT.json').read_text(encoding='utf-8'))
    if (process.get('returncode')!=0 or process.get('result_contract_ok') is not True
        or report.get('classification')!='PASS_BOUNDED_TARGET_GRID_DIAGNOSTIC'
        or report.get('source_commit')!=process.get('source_commit')
        or report.get('source_tree')!=process.get('source_tree')):
        raise RuntimeError('successful saved diagnostic plus actual process receipt required')
    weak=read_csv(payload/'WEAK_MOMENTS.csv');gap=read_csv(payload/'ATOMIC_TABLE_CONTRAST.csv')
    if len(weak)!=576 or len(gap)!=288:raise ValueError('unexpected row census')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out.mkdir(parents=True,exist_ok=False)
    titles=['weak_error','weak_jvp_error','weak_error_budget','atomic_table_gap']
    fixed={'case':'curved','direction':'photon','power':2}
    for width in (90,180):
        font=7 if width==90 else 9
        with plt.rc_context({'font.size':font,'axes.labelsize':font,'legend.fontsize':font}):
            for title in titles:
                fig,ax=plt.subplots(figsize=(width/25.4,width*.82/25.4),layout='constrained')
                if title in ('weak_error','weak_jvp_error'):
                    field='error' if title=='weak_error' else 'jvp_error'
                    for table,kind,marker,ls in [('base','chi','o','-'),('hires','chi','x','-'),
                                                ('base','log_control','s','--'),('hires','log_control','+','--')]:
                        x,y=points(weak,field,table=table,read_kind=kind,**fixed)
                        ax.plot(x,y,marker=marker,linestyle=ls,linewidth=.9,markersize=4,
                                label=table+' '+('chi' if kind=='chi' else 'log control'))
                    ylabel='Weak moment error [1/s]' if field=='error' else 'Weak moment JVP error [1/s]'
                elif title=='weak_error_budget':
                    for field,label,marker,ls in [('read_error','read','o','-'),('scatter_error','scatter','s','--'),
                                                   ('cross_error','cross','x',':'),('error','total','+','-.')]:
                        x,y=points(weak,field,table='base',read_kind='chi',**fixed)
                        ax.plot(x,y,marker=marker,linestyle=ls,linewidth=.9,markersize=4,label=label)
                    ylabel='Signed error components [1/s]'
                else:
                    for kind,marker,ls in [('chi','o','-'),('log_control','s','--')]:
                        x,y=points(gap,'target_table_difference',read_kind=kind,**fixed)
                        ax.plot(x,y,marker=marker,linestyle=ls,linewidth=.9,markersize=4,
                                label='target '+('chi' if kind=='chi' else 'log control'))
                    x,y=points(gap,'direct_table_difference',read_kind='chi',**fixed)
                    ax.plot(x,y,linestyle=':',linewidth=1.,label='direct-bin reference')
                    ylabel='Hires minus base moment [1/s]'
                ax.set_xscale('log',base=2)
                ax.set_xticks([5,9,17,33,65,129],[str(n) for n in (5,9,17,33,65,129)])
                # Symlog transforms the axis, never the data: signed zeros remain zero.
                ax.set_yscale('symlog',linthresh=1e-14)
                ax.axhline(0,linewidth=.6,linestyle=':')
                ax.set_xlabel('Target photon nodes N');ax.set_ylabel(ylabel)
                ax.legend(loc='upper center',bbox_to_anchor=(.5,1.24),ncol=2,frameon=False)
                fig.savefig(out/f'{title}_{width}mm.png',dpi=240)
                plt.close(fig)
    caption=('All panels use the same curved manufactured continuum chi, fixed atomic populations, '
             'photon perturbation direction and psi(u)=u^2. Weak errors compare each atomic table with '
             'that same table evaluated at exact continuum source-bin energies. The four series are '
             'not four different physical models. Error-budget panel: base table, chi read; signed '
             'read+scatter+cross equals total. Table-gap panel separates atomic discretization from '
             'target-grid error; neither table is certified as the continuum atomic truth. '
             'Y axes use a symmetric-log transform with a linear region +/-1e-14 s^-1; no value is '
             'floored or replaced, including zero. Zero is not proof of mathematical equality. '
             'Lines guide finite-grid comparisons, not time evolution. No fitted convergence order, '
             'strong convergence of C_i, physical phase-space measure or provider admission is implied.\n')
    (out/'CAPTIONS.txt').write_text(caption,encoding='utf-8')
    inputs=[run/'PROCESS.json',payload/'RESULT.json',payload/'WEAK_MOMENTS.csv',payload/'ATOMIC_TABLE_CONTRAST.csv']
    def git(*a):return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()
    receipt={'classification':'RENDERED_SAVED_TARGET_GRID_DATA','renderer_commit':git('rev-parse','HEAD'),
             'renderer_tree':git('rev-parse','HEAD^{tree}'),'consumed_source_commit':process['source_commit'],
             'consumed_source_tree':process['source_tree'],'matplotlib':matplotlib.__version__,
             'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
             'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.png'))},
             'tests_replayed':False,'visual_audit':'NOT_PERFORMED','claim':'NO_PASS_REC_PHYSICAL_SPLIT'}
    (out/'RENDER_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))
    return 0


if __name__=='__main__':raise SystemExit(main())
