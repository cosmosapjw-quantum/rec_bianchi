"""Saved-output analysis and display repair; never import or execute the probe."""
from __future__ import annotations
import argparse
import csv
from collections import defaultdict
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import subprocess


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--payload', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    payload, out = args.payload.resolve(), args.out.resolve()
    source = Path(__file__).resolve().parents[3]
    if out == source or source in out.parents:
        parser.error('output must be outside the worktree')
    report = json.loads((payload/'RESULT.json').read_text())
    process = json.loads((payload.parent/'PROCESS.json').read_text())
    assert report['classification'] == 'COMPLETED_BOUNDED_WEAK_DIAGNOSTIC'
    assert report['script_exit_code'] == process['returncode'] == 0
    assert not process['timed_out']
    assert report['source_commit'] == process['source_commit']
    inputs = [payload/'MOMENTS.csv', payload/'DIRECT_REFERENCES.json',
              payload/'ORACLE_CHECKS.json', payload/'RESULT.json', payload.parent/'PROCESS.json']
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    with inputs[0].open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    references = json.loads(inputs[1].read_text())
    oracles = json.loads(inputs[2].read_text())
    keys = {(r['table'], r['case'], r['read'], int(r['nodes']), int(r['power'])) for r in rows}
    expected = {(t,c,k,n,p) for t in ('base','hires')
                for c in ('curved_emission','curved_absorption','affine_balance')
                for k in ('chi','log_control') for n in (5,9,17,33,65,129) for p in (0,1,2,4)}
    assert len(rows) == 288 and keys == expected and len(oracles) == 8 and len(references) == 6
    out.mkdir(parents=True, exist_ok=False)
    groups = defaultdict(list)
    for row in rows:
        groups[(row['table'],row['case'],row['read'],int(row['power']))].append(row)
    slopes = []
    for key, group in sorted(groups.items()):
        group.sort(key=lambda row:int(row['nodes']))
        for left, right in zip(group, group[1:]):
            item = dict(zip(('table','case','read','power'),key))
            item.update(nodes_from=int(left['nodes']), nodes_to=int(right['nodes']))
            for name in ('absolute_error','absolute_jvp_error'):
                a,b = float(left[name]),float(right[name])
                item[name+'_order'] = math.log(a/b)/math.log(float(left['h_grid'])/float(right['h_grid'])) if min(a,b)>0 else ''
            item['interpretation'] = 'raw diagnostic; affine primal roundoff slopes are not orders of convergence'
            slopes.append(item)
    write_csv(out/'LOCAL_SLOPES.csv',slopes)
    contrasts = []
    for case in ('curved_emission','curved_absorption','affine_balance'):
        base = next(r for r in references if r['table']=='base' and r['case']==case)
        hires = next(r for r in references if r['table']=='hires' and r['case']==case)
        for i,p in enumerate((0,1,2,4)):
            contrasts.append({'case':case,'power':p,'base_moment':base['moments'][i],
                              'hires_moment':hires['moments'][i],
                              'hires_minus_base_moment':hires['moments'][i]-base['moments'][i],
                              'base_jvp':base['jvp'][i],'hires_jvp':hires['jvp'][i],
                              'hires_minus_base_jvp':hires['jvp'][i]-base['jvp'][i],
                              'role':'fixed-table reference contrast, not atomic truth error'})
    write_csv(out/'TABLE_REFERENCE_CONTRAST.csv',contrasts)
    write_csv(out/'PEAK_C.csv',[{k:r[k] for k in ('table','case','read','nodes','h_grid','peak_C')} for r in rows if r['power']=='0'])
    decomposition = {}
    for value,reference,terms in [('moment','reference',('read_error','scatter_error','cross_error')),
                                   ('jvp','reference_jvp',('read_jvp_error','scatter_jvp_error','cross_jvp_error'))]:
        decomposition[value] = max(abs(float(r[value])-float(r[reference])-math.fsum(float(r[t]) for t in terms)) for r in rows)
    direct = Q(3,8)**2+Q(5,8)**2
    deposited = (Q(1,4)**2+2*Q(1,2)**2+Q(3,4)**2)/2
    assert deposited == Q(9,16) and direct == Q(17,32) and deposited-direct == Q(1,32)
    summary = {'rows':len(rows),'oracle_comparisons':len(oracles),'direct_references':len(references),
               'max_oracle_primal_scaled_error':max(r['primal_error'] for r in oracles),
               'max_oracle_jvp_scaled_error':max(r['jvp_error'] for r in oracles),
               'saved_decomposition_residuals':decomposition,
               'exact_supplied_witness':{'deposited_u2':str(deposited),'direct_u2':str(direct),'defect':str(deposited-direct)},
               'claim':'NO_PASS_REC_PHYSICAL_SPLIT','physical_source_authenticated':False,'provider_admitted':False,
               'numerical_tests_replayed':False}
    write_json(out/'SAVED_ANALYSIS.json',summary)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    styles = [('base','chi','o','-'),('base','log_control','x','--'),
              ('hires','chi','s','-'),('hires','log_control','+','--')]
    for column in ('absolute_error','absolute_jvp_error'):
        selected = { (t,k):[r for r in rows if r['table']==t and r['read']==k
                            and r['case']=='curved_emission' and r['power']=='2'] for t,k,_,_ in styles}
        values = [float(r[column]) for series in selected.values() for r in series]
        assert min(values)>0  # This particular display's upper panel is a positive-only detail.
        for width in (90,180):
            font = 7 if width==90 else 9
            with plt.rc_context({'font.size':font,'axes.labelsize':font,'xtick.labelsize':font,
                                  'ytick.labelsize':font,'legend.fontsize':font}):
                fig,(detail,full) = plt.subplots(2,1,figsize=(width/25.4,width*1.08/25.4),
                                               gridspec_kw={'height_ratios':[3,1]},layout='constrained')
                for t,k,marker,ls in styles:
                    series = sorted(selected[(t,k)],key=lambda r:int(r['nodes']))
                    x = [int(r['nodes'])-1 for r in series];y = [float(r[column]) for r in series]
                    for axis in (detail,full):
                        axis.plot(x,y,marker=marker,linestyle=ls,linewidth=.9,markersize=3,
                                  label=t+' '+('chi' if k=='chi' else 'log control'))
                detail.set_yscale('log');detail.set_ylim(min(values)/1.6,max(values)*1.6)
                detail.set_ylabel(('Moment error' if column=='absolute_error' else 'JVP error')+' [s$^{-1}$]')
                detail.legend(loc='lower left',ncol=2,frameon=False)
                detail.set_title('Curved emission, psi = u²; positive-error detail')
                full.set_yscale('symlog',linthresh=1e-16);full.set_ylim(0,max(values)*1.6)
                full.set_yticks([0,1e-16,1e-8]);full.set_yticklabels(['0','1e-16','1e-8'])
                full.set_ylabel('Full range')
                full.set_title('Symlog: linear for |error| <= 1e-16; zero retained')
                for axis in (detail,full):
                    axis.set_xscale('log',base=2);axis.set_xticks([4,8,16,32,64,128],[4,8,16,32,64,128])
                    axis.grid(alpha=.15)
                full.set_xlabel('Target intervals (N - 1)')
                fig.savefig(out/f'{column}_{width}mm.png',dpi=240);plt.close(fig)
    (out/'CAPTION.txt').write_text('Saved MOMENTS.csv only. Same uniform reference measure, continuous field, populations and perturbation; fixed atomic table. Top panels show positive recorded errors without flooring; bottom panels retain actual zero with a symlog linear interval |error| <= 1e-16 s^-1. Absolute errors are nonnegative. Four series can overlap; markers and line styles identify them. Connecting lines are finite-grid diagnostics, not a fitted or imposed universal order. No numerical probe was replayed.\n')
    for p in inputs:
        assert hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p)]
    def git(*args):return subprocess.check_output(['git','-C',str(source),*args],text=True).strip()
    write_json(out/'POSTPROCESS_RECEIPT.json',{'classification':'SAVED_DATA_ONLY_ANALYSIS_AND_DISPLAY',
               'source_commit':git('rev-parse','HEAD'),'source_tree':git('rev-parse','HEAD^{tree}'),
               'consumed_numerical_commit':process['source_commit'],'inputs':hashes,
               'input_bytes_unchanged':True,'numerical_tests_replayed':False,'visual_audit':'NOT_PERFORMED'})
    return 0


if __name__=='__main__':
    raise SystemExit(main())
