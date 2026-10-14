"""Read-only clock comparison on original adjacent accepted rows.

No evolution solver. Unknown trajectory/interpolation errors are not replaced
with zero. Frozen full-grid indices are retained even for a partial interval.
"""
from __future__ import annotations
import argparse, bisect, csv, hashlib, json, math, sys, time
from dataclasses import dataclass
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Mapping, Sequence

@dataclass(frozen=True)
class Evaluation:
    value: float
    left_id: int
    right_id: int
    weight: float

class NativeSeries:
    def __init__(self, ids: Sequence[int], L: Sequence[float], time_s: Sequence[float], fields: Mapping[str, Sequence[float]]):
        self.ids=list(ids)
        self.data={'L':list(L),'time_s':list(time_s),**{k:list(v) for k,v in fields.items()}}
        n=len(self.ids)
        if not n or any(len(v)!=n for v in self.data.values()):raise ValueError('shape')
        if any(not math.isfinite(x) for v in self.data.values() for x in v):raise ValueError('nonfinite')
        if any(b<=a for a,b in zip(self.ids,self.ids[1:])):raise ValueError('native index order')
        for k in ('L','time_s'):
            if any(b<=a for a,b in zip(self.data[k],self.data[k][1:])):raise ValueError('nonmonotone clock')
    def bracket(self, coordinate: str, x: float):
        if coordinate not in ('L','time_s') or not math.isfinite(x):raise ValueError('query coordinate')
        xs=self.data[coordinate];j=bisect.bisect_left(xs,x)
        if j<len(xs) and xs[j]==x:return j,j,0.
        if j==0 or j==len(xs):raise ValueError('extrapolation')
        if self.ids[j]!=self.ids[j-1]+1:raise ValueError('missing original accepted rows')
        return j-1,j,(x-xs[j-1])/(xs[j]-xs[j-1])
    def at(self, coordinate: str, field: str, x: float):
        i,j,w=self.bracket(coordinate,x);v=self.data[field]
        return Evaluation(v[i]+w*(v[j]-v[i]),self.ids[i],self.ids[j],w)

def exact_clock_split(reference: NativeSeries, candidate: NativeSeries, L: float, field: str):
    r=reference.at('L',field,L);c=candidate.at('L',field,L)
    tr=reference.at('L','time_s',L);tc=candidate.at('L','time_s',L)
    rt=reference.at('time_s',field,tc.value)
    same_L=c.value-r.value;clock=r.value-rt.value;same_time=c.value-rt.value
    return {'same_L':same_L,'clock_transport':clock,'same_time':same_time,
            'identity_residual':same_time-(same_L+clock),
            'reference_at_L':r.value,'candidate_at_L':c.value,'reference_at_candidate_time':rt.value,
            'reference_time_s':tr.value,'candidate_time_s':tc.value,'delta_time_s':tc.value-tr.value,
            'reference_time_bracket':[rt.left_id,rt.right_id],
            'reference_L_bracket':[r.left_id,r.right_id],'candidate_L_bracket':[c.left_id,c.right_id]}

def common_grid(max_L: float):
    lo=math.log(1/21);hi=math.log(1/5)
    all_L=[lo+(j/1000)*math.log(21/5) for j in range(1001)];all_L[0]=lo;all_L[-1]=hi
    return [(j,L) for j,L in enumerate(all_L) if L<=max_L],[j for j,L in enumerate(all_L) if L>max_L]

def uncertainty_bound(e_c,e_r,e_tc,e_tr,m,M):
    """Conditional inverse-clock bound. Supplied constants must be justified externally."""
    if any(x is None for x in (e_c,e_r,e_tc,e_tr,m,M)):return None
    if any(not math.isfinite(x) for x in (e_c,e_r,e_tc,e_tr,m,M)) or min(e_c,e_r,e_tc,e_tr,M)<0 or m<=0:raise ValueError('invalid bound domain')
    return e_c+e_r+(M/m)*(e_tc+e_tr)

def linear_interpolation_bound(x0,x1,x,M2,e0,e1):
    if not x0<x1 or not x0<=x<=x1:raise ValueError('interpolation interval')
    if any(v is None for v in (M2,e0,e1)):return None
    if any(not math.isfinite(v) or v<0 for v in (M2,e0,e1)):raise ValueError('invalid error bound')
    w=(x-x0)/(x1-x0)
    return (1-w)*e0+w*e1+M2*(x-x0)*(x1-x)/2

def paired_ready(cases):
    return {'ZERO','SHEAR_PLUS','SHEAR_MINUS','SHEAR_HALF_PLUS','SHEAR_HALF_MINUS'}<=set(cases)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load_selected(root: Path,case: str,manifest):
    p=root/'inputs'/case
    info=manifest['cases'][case]
    if sha(p/'native_rows.csv')!=info['selection']['selected_csv_sha256']:raise ValueError('input bytes')
    ids=json.loads((p/'native_row_indices.json').read_text())
    with (p/'native_rows.csv').open() as f:rows=list(csv.DictReader(f))
    if len(ids)!=len(rows) or any(row['case_id']!=case for row in rows):raise ValueError('row identity')
    names=('x_HII','x_HeII','x_HeIII','temperature_K','ne_proper_cm3','nH_proper_cm3','J0_photon_u_eV_per_H','J2_photon_u_eV_per_H')
    fields={name:[float(row[name]) for row in rows] for name in names}
    fields['xe']=[float(row['ne_proper_cm3'])/float(row['nH_proper_cm3']) for row in rows]
    return NativeSeries(ids,[math.log(float(r['a'])) for r in rows],[float(r['time_s']) for r in rows],fields)

def decimal_at(series,coordinate,field,x):
    """Independent 80-digit barycentric arithmetic on the identical binary64 target."""
    if not hasattr(series,'_decimal_axes'):series._decimal_axes={}
    if coordinate not in series._decimal_axes:
        series._decimal_axes[coordinate]=[Decimal.from_float(v) for v in series.data[coordinate]]
    xs=series._decimal_axes[coordinate]
    j=bisect.bisect_left(xs,x)
    ys=series.data[field]
    if j<len(xs) and xs[j]==x:return Decimal.from_float(ys[j])
    if j==0 or j==len(xs) or series.ids[j]!=series.ids[j-1]+1:raise ValueError('oracle coverage')
    return (Decimal.from_float(ys[j-1])*(xs[j]-x)+Decimal.from_float(ys[j])*(x-xs[j-1]))/(xs[j]-xs[j-1])

def analyze(root: Path):
    out=root/'results'
    out.mkdir(exist_ok=True)
    target=out/'clock_comparison.csv'
    if target.exists():raise FileExistsError('preserve existing results')
    start=time.monotonic();manifest=json.loads((root/'SOURCE_INTAKE.json').read_text())
    r=load_selected(root,'ZERO',manifest);c=load_selected(root,'SHEAR_PLUS',manifest)
    grid,omitted=common_grid(min(r.data['L'][-1],c.data['L'][-1]))
    queries=[('FROZEN_GRID',j,L) for j,L in grid]+[('TERMINAL_DIAGNOSTIC_NOT_GRID',None,min(r.data['L'][-1],c.data['L'][-1]))]
    fields=['x_HII','x_HeII','x_HeIII','temperature_K','xe','ne_proper_cm3','J0_photon_u_eV_per_H','J2_photon_u_eV_per_H']
    rows=[];max_scaled=0.;max_identity=0.;endpoint={}
    # Predeclared arithmetic criterion on gross operands, never a relative error of a tiny difference.
    criterion=4096*sys.float_info.epsilon
    with localcontext() as ctx:
        ctx.prec=80
        for kind,index,L in queries:
            for field in fields:
                q=exact_clock_split(r,c,L,field)
                dL=Decimal.from_float(L)
                tc=decimal_at(c,'L','time_s',dL);rr=decimal_at(r,'L',field,dL);cc=decimal_at(c,'L',field,dL);rt=decimal_at(r,'time_s',field,tc)
                oracle={'same_L':cc-rr,'clock_transport':rr-rt,'same_time':cc-rt}
                scale=max(abs(float(cc))+abs(float(rr))+abs(float(rt)),1e-100)
                err=max(abs(q[k]-float(oracle[k])) for k in oracle)/scale
                max_scaled=max(max_scaled,err);max_identity=max(max_identity,abs(q['identity_residual'])/scale)
                if err>criterion:raise ArithmeticError(f'oracle mismatch {field}: {err}')
                row={'kind':kind,'frozen_grid_index':index,'ln_a':L,'zbar_at_same_a':math.exp(-L)-1,'field':field,**q,
                     'same_time_oracle80':str(oracle['same_time']),'arithmetic_scaled_error':err,
                     'evolution_error':None,'interpolation_error':None,'result_class':'PARTIAL_DIAGNOSTIC_UNRESOLVED'}
                rows.append(row)
                if index is None:endpoint[field]=row
    with target.open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    sampled={field:{k:max(abs(row[k]) for row in rows if row['field']==field and row['kind']=='FROZEN_GRID') for k in ('same_L','clock_transport','same_time')} for field in fields}
    summary={'scope':'Immutable original ZERO/PLUS terminal partial histories; same-source finite-q diagnostic only',
             'selected_stage':'R6','source_head':manifest['repo_head'],'covered_frozen_indices':[j for j,L in grid],
             'omitted_frozen_indices':omitted,'terminal_diagnostic_is_not_grid':True,'queries':len(queries),'fields':fields,
             'rows':len(rows),'endpoint':endpoint,'sampled_max_abs':sampled,'arithmetic_criterion':criterion,
             'max_scaled_decimal_difference':max_scaled,'max_scaled_clock_identity_residual':max_identity,
             'comparison_target':'Joint affine reconstruction in operational binary64 ln(a), not original solver dense output',
             'evolution_error':None,'interpolation_error':None,'five_case_coefficients':None,
             'scientific_admission':'NOT_ISSUED','production_solver_runs':0,'wall_s':time.monotonic()-start,
             'output_sha256':sha(target),'source_intake_sha256':sha(root/'SOURCE_INTAKE.json'),'analysis_source_sha256':sha(__file__)}
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps({'scope':summary['scope'],'rows':len(rows),'covered_grid':len(grid),'omitted':len(omitted),'max_scaled_decimal_difference':max_scaled,'arithmetic_criterion':criterion,'endpoint':endpoint},indent=2))
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);args=ap.parse_args();analyze(args.root)
