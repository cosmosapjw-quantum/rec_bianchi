"""Render only saved supplemental CSV data; never rerun the original study."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--payload',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args = ap.parse_args()
    payload, out = args.payload.resolve(), args.out.resolve()
    if out == ROOT or ROOT in out.parents:
        ap.error('render output must be outside the worktree')
    report_path = payload/'RESULT.json'
    csv_path = payload/'ADDITIONAL_JVP.csv'
    process_path = payload.parent/'PROCESS.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    process = json.loads(process_path.read_text(encoding='utf-8'))
    if (report.get('classification') != 'PASS_BOUNDED_NULLSPACE_SUPPLEMENT'
        or report.get('tests',{}).get('run') != 4
        or process.get('returncode') != 0
        or process.get('result_contract_ok') is not True):
        raise RuntimeError('plot requires the saved successful supplemental lane and actual process receipt')
    with csv_path.open(newline='',encoding='utf-8') as handle:
        rows = list(csv.DictReader(handle))
    expected = {(table,kind,axis) for table in ('base','hires')
                for kind in ('chi','log_control') for axis in (0,2,3,4)}
    keys = [(r['table'],r['read'],int(r['photon_axis'])) for r in rows]
    if len(keys) != 16 or set(keys) != expected:
        raise ValueError('CSV must contain exactly the sixteen distinct supplemental directions')
    errors = {key:float(row['scaled_jvp_error']) for key,row in zip(keys,rows)}
    if any(not math.isfinite(x) or x < 0 for x in errors.values()):
        raise ValueError('nonfinite or negative error diagnostic')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out.mkdir(parents=True,exist_ok=False)
    for width_mm in (90,180):
        fontsize = 7 if width_mm == 90 else 9
        with plt.rc_context({'font.size':fontsize,'axes.labelsize':fontsize,
                             'legend.fontsize':fontsize,'xtick.labelsize':fontsize,
                             'ytick.labelsize':fontsize}):
            fig,ax = plt.subplots(figsize=(width_mm/25.4,width_mm*.8/25.4),layout='constrained')
            for table,kind,marker,ls in [('base','chi','o','-'),('base','log_control','s','--'),
                                        ('hires','chi','x','-'),('hires','log_control','+','--')]:
                axes = [0,2,3,4]
                ax.plot(axes,[errors[(table,kind,i)] for i in axes],marker=marker,
                        linestyle=ls,markersize=4,linewidth=.9,
                        label=table+' '+('chi' if kind=='chi' else 'log control'))
            ax.set_xticks([0,2,3,4],['y0','y2','y3','y4'])
            ax.set_xlabel('Perturbed photon log-occupation')
            ax.set_ylabel('Recorded scaled JVP error')
            ax.set_ylim(bottom=0)
            ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
            ax.legend(loc='upper center',bbox_to_anchor=(.5,1.23),ncol=2,frameon=False)
            fig.savefig(out/f'additional_jvp_{width_mm}mm.png',dpi=240)
            plt.close(fig)
    caption = ('Two tables and two read operators at the same manufactured non-equilibrium state. '
               'Only y0,y2,y3,y4 are shown; the older 84-case study is not rerun. '
               'Each point is the saved maximum component error abs(error)/(1+abs(reference)) '
               'in the fixed numerical units of the test. References use 80/120-digit arithmetic, '
               'but plotted comparisons are binary64 diagnostics, not 80-digit implementation accuracy. '
               'Recorded zeros remain at zero; no display floor is used and zero is not a proof of '
               'mathematical equality. Connecting lines guide the eye and are not grid-convergence curves. '
               'These images do not replace or authenticate the historical PR79 artifact images.\n')
    (out/'CAPTION.txt').write_text(caption,encoding='utf-8')
    def git(*argv):
        return subprocess.check_output(['git','-C',str(ROOT),*argv],text=True).strip()
    receipt = {'classification':'RENDERED_FROM_SAVED_SUPPLEMENT_ONLY',
               'renderer_commit':git('rev-parse','HEAD'),'renderer_tree':git('rev-parse','HEAD^{tree}'),
               'consumed_source_commit':process.get('source_commit'),
               'consumed_source_tree':process.get('source_tree'),
               'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in (report_path,csv_path,process_path)},
               'matplotlib':matplotlib.__version__,'visual_audit':'NOT_PERFORMED',
               'original_tests_replayed':False,'supplement_tests_replayed':False,
               'claim':'NO_PASS_REC_PHYSICAL_SPLIT'}
    (out/'RENDER_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
