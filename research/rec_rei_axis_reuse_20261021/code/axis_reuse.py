"""Read-only anchored response reduction of a frozen signed matter/radiation sweep.

No integrator, fitted coefficients, or benchmark. The model consumes ONLY axis
support rows; mixed-case outputs are used ONLY by the validation/report stage.
Norms must be constructed after prediction of the signed tensor components.
"""
from __future__ import annotations
import argparse
import csv
from decimal import Decimal, localcontext
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import resource
import sys
import time

INPUT_SHA256 = 'c322453eed4c4c236ff19501ea6eca50353d6ebecc604a6cab9647b3a090255c'
KEYS = ('signed_Sigma_requested', 'signed_Pi_m_requested', 'signed_Pi_r_requested')
OUTPUTS = ('final_signed_Sigma', 'final_signed_Pi_m', 'final_signed_Pi_r',
           'final_signed_Pi_total', 'final_Tgas_K', 'final_x_HII',
           'final_x_HeII', 'final_b', 'final_H', 'final_elapsed_s')
DISPLAY_FLOOR = 3.e-13  # inherited orientation/display floor, NOT solver tolerance
Key = tuple[float, float, float]

def build_table(rows, keys=KEYS, outputs=OUTPUTS):
    """Require a complete finite Cartesian grid and zero stress anchors."""
    table = {}
    for row in rows:
        key = tuple(float(row[k]) for k in keys)
        vals = {c: float(row[c]) for c in outputs}
        if not all(math.isfinite(x) for x in (*key, *vals.values())):
            raise ValueError('NONFINITE_INPUT')
        if key in table:
            raise ValueError(f'DUPLICATE_COORDINATE: {key}')
        table[key] = {**row, **vals}
    if not table:
        raise ValueError('EMPTY_GRID')
    axes = [sorted({k[i] for k in table}) for i in range(3)]
    if 0. not in axes[1] or 0. not in axes[2]:
        raise ValueError('ZERO_STRESS_ANCHOR_MISSING')
    if len(table) != math.prod(map(len, axes)):
        raise ValueError('INCOMPLETE_CARTESIAN_GRID')
    return table

def axis_support(table):
    """Copy only axis support: no references to held-out response rows."""
    return {k: dict(v) for k, v in table.items() if k[1] == 0. or k[2] == 0.}

def predict(support, key: Key, column: str):
    s, m, r = key
    return math.fsum((support[(s,m,0.)][column],
                      support[(s,0.,r)][column],
                      -support[(s,0.,0.)][column]))

def exact_residual(actual, axis_m, axis_r, anchor):
    """80-digit residual of the exact stored binary64 values, not ODE error."""
    with localcontext() as ctx:
        ctx.prec = 80
        a, m, r, z = map(Decimal.from_float, map(float,(actual,axis_m,axis_r,anchor)))
        return float(a-m-r+z)

def tensor_diagnostics(s, dm, dr, H, kappa_time):
    if not all(map(math.isfinite,(s,dm,dr,H,kappa_time))) or H <= 0 or kappa_time <= 0:
        raise ValueError('INVALID_PHYSICAL_NORMALIZATION')
    fac = kappa_time/(math.sqrt(3.)*H*H)
    pm, pr = fac*dm, fac*dr
    pt = math.fsum((pm,pr))
    return {'Sigma_half':math.sqrt(3.)*abs(s)/H,
            'signed_Pi_m':pm, 'signed_Pi_r':pr,
            'Pi_m_half':abs(pm), 'Pi_r_half':abs(pr), 'Pi_total_half':abs(pt),
            'Pi_m_frobenius':math.sqrt(2.)*abs(pm),
            'component_norm_sum':abs(pm)+abs(pr),
            'work_m':2*s*dm, 'work_r':2*s*dr}

def plan_cases(table):
    """A proposed NEW-scope design; existing cases here must all be reused."""
    km = max(abs(k[1]) for k in table)
    kr = max(abs(k[2]) for k in table)
    support, sentinels, remaining = [], [], []
    for s,m,r in sorted(table):
        k = [s,m,r]
        if m == 0. or r == 0.:
            support.append(k)
        elif (abs(m)==km and abs(r)==kr) or m == -r:
            sentinels.append(k)
        else:
            remaining.append(k)
    return {'support':support, 'sentinels':sentinels, 'remaining':remaining}

def orientation(v):
    return 0 if abs(v)<DISPLAY_FLOOR else (1 if v>0 else -1)

def analyze(table):
    support = axis_support(table)
    records = []
    accum = {c:[] for c in OUTPUTS}
    exact_accum = {c:[] for c in OUTPUTS}
    orientation_changes = {c:0 for c in OUTPUTS[:4]}
    cancellation_errors = []
    for key in sorted(table):
        s,m,r = key
        row = table[key]
        pred = {c:predict(support,key,c) for c in OUTPUTS}
        # Preserve tensor closure rather than fitting/adding component magnitudes.
        pred['final_signed_Pi_total'] = math.fsum((pred['final_signed_Pi_m'],pred['final_signed_Pi_r']))
        held = m != 0. and r != 0.
        rec = dict(zip(KEYS,key))
        rec.update(case_id=row.get('case_id',''), role='WITHHELD' if held else 'SUPPORT')
        for c in OUTPUTS:
            error = row[c]-pred[c]
            rec[c+'_actual'] = row[c]
            rec[c+'_predicted'] = pred[c]
            rec[c+'_error'] = error
            if held:
                accum[c].append(error)
                exact_accum[c].append(exact_residual(row[c],support[(s,m,0.)][c],support[(s,0.,r)][c],support[(s,0.,0.)][c]))
                if c in orientation_changes:
                    orientation_changes[c] += orientation(row[c]) != orientation(pred[c])
        rec['Pi_total_half_predicted'] = abs(pred['final_signed_Pi_total'])
        rec['component_norm_sum_predicted'] = abs(pred['final_signed_Pi_m'])+abs(pred['final_signed_Pi_r'])
        if held and m == -r:
            cancellation_errors.append(abs(rec['final_signed_Pi_total_error']))
        records.append(rec)
    summary = {'schema':'rec.rei.axis_reuse.validation.v1',
      'status':'STORED_GRID_ENDPOINT_COMPARISON_ONLY',
      'cases':len(table), 'support_cases':len(support),
      'withheld_cases':len(table)-len(support),
      'formula':'Fhat(S,m,r)=F(S,m,0)+F(S,0,r)-F(S,0,0)',
      'fit_coefficients':0, 'new_ODE_runs':0, 'benchmark_runs':0,
      'display_floor':DISPLAY_FLOOR,
      'floor_meaning':'Inherited orientation/display floor, not a physical or solver accuracy bound',
      'orientation_mismatches_above_display_floor':orientation_changes,
      'nonzero_cancellation_withheld_count':len(cancellation_errors),
      'cancellation_Pi_total_max_abs_error':max(cancellation_errors,default=None),
      'observables':{},
      'cost_claim':{'support_fraction':len(support)/len(table),
                    'avoided_fraction_before_new_sentinels':1-len(support)/len(table),
                    'measured_speedup':None,
                    'not_measured':'solver speed, parallel scaling, pipeline RSS reduction'},
      'limits':['finite stored endpoints only','same warm C15 source and initial family only',
                'no interpolation between grid points','no change to original solver',
                'not a certificate of ODE accuracy or full EoR',
                'split response approximation does not imply uncoupled matter/radiation physics']}
    for c, vals in accum.items():
        summary['observables'][c] = {'max_abs_error':max(map(abs,vals),default=0.),
            'rms_error':math.sqrt(math.fsum(x*x for x in vals)/len(vals)) if vals else 0.,
            'max_abs_exact_stored_float_interaction':max(map(abs,exact_accum[c]),default=0.),
            'comparison_to_display_floor':max(map(abs,vals),default=0.)/DISPLAY_FLOOR if c in OUTPUTS[:4] else None}
    return records, summary

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--csv',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--expected-sha256',default=INPUT_SHA256)
    args=ap.parse_args()
    start=time.monotonic(); cpu=time.process_time()
    raw=args.csv.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
    if digest != args.expected_sha256:
        raise ValueError('SOURCE_INPUT_SHA256_MISMATCH')
    if args.out.exists():
        raise FileExistsError('CREATE_ONLY_OUTPUT_EXISTS')
    rows=list(csv.DictReader(raw.decode('utf-8').splitlines()))
    table=build_table(rows)
    records, summary=analyze(table)
    # Reject an input whose physical shape differs from the frozen study.
    if len(table)!=729 or len(axis_support(table))!=153:
        raise ValueError('FROZEN_729_DESIGN_MISMATCH')
    summary['input']={'sha256':digest,'bytes':len(raw),'rows':len(rows),'columns':len(rows[0])}
    summary['scope']={'a_initial':sorted({float(r['initial_a']) for r in rows}),
                      'a_final':sorted({float(r['final_a']) for r in rows}),
                      'model_scope':sorted({r['final_model_scope'] for r in rows}),
                      'rei_result_commit':'c8e9f67aa031ffb33a9b0347bdea61dbb01fb746'}
    plan=plan_cases(table)
    plan.update(status='DESIGN_ONLY_NOT_SUBMITTED',existing_all_729='complete_reused',
                requires='new explicit scientific scope and finite allocation; preserve hard limits',
                prospective_executed_count=len(plan['support'])+len(plan['sentinels']),
                prospective_predicted_only_count=len(plan['remaining']))
    args.out.mkdir(parents=True)
    with (args.out/'withheld_comparison.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    (args.out/'SUMMARY.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    (args.out/'PROPOSED_NEW_SCOPE_DESIGN.json').write_text(json.dumps(plan,indent=2,allow_nan=False)+'\n')
    receipt={'argv':sys.argv,'python':platform.python_version(),
      'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'input_sha256':digest,'script_main_CPU_s':time.process_time()-cpu,
      'script_main_wall_s':time.monotonic()-start,
      'process_ru_maxrss_KiB_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      'measurement_scope':'main entry through result writing; imports/interpreter/receipt final write excluded; not whole allocation',
      'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in args.out.iterdir()},
      'new_native_or_ODE_runs':0}
    (args.out/'RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
    print(json.dumps(summary,indent=2,allow_nan=False))

if __name__=='__main__':
    main()
