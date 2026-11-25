"""Run all standalone cases from the final Rust executable and summarize."""
import concurrent.futures,csv,gzip,hashlib,json,pathlib,subprocess,sys
D=pathlib.Path(__file__).resolve().parent
exe,out=map(lambda p:pathlib.Path(p).resolve(),sys.argv[1:3])
out.mkdir(parents=True,exist_ok=False)
meta=json.loads((D/'SLICE_RECEIPT.json').read_text())
for r in meta['slices']:
    data=gzip.decompress((D/(r['name']+'.tsv.gz')).read_bytes())
    assert hashlib.sha256(data).hexdigest()==r['sha256']
    (out/(r['name']+'.tsv')).write_bytes(data)
def run(case):
    name,n,eps=case; dst=out/f'{name}_{n}_{eps}.tsv'
    cmd=[str(exe),str(out/(name+'.tsv')),str(n),str(eps)]
    with dst.open('wb') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.PIPE,check=True)
    rows=list(csv.DictReader(dst.open(),delimiter='\t'));assert len(rows)==n+1
    def peak(k):return max(abs(float(r[k])) for r in rows)
    assert all(0<=float(r['xp'])<=1 and 0<=float(r['x_heii']) and 0<=float(r['x_heiii']) and float(r['tm_k'])>0 for r in rows)
    q=dict(case=name,n=n,eps=eps,peak_delta_xe=peak('delta_xe'),peak_delta_tm_k=peak('delta_tm_k'),final_delta_xe=float(rows[-1]['delta_xe']),final_delta_tm_k=float(rows[-1]['delta_tm_k']),max_heat_defect=peak('heat_defect_j_per_h'),max_scaled_residual=peak('scaled_residual'),max_iterations=peak('iterations'),sha256=hashlib.sha256(dst.read_bytes()).hexdigest())
    if eps==0:assert q['peak_delta_xe']==q['peak_delta_tm_k']==0.
    return q
cases=[(name,n,eps) for name in ['helium','hydrogen','thermal'] for n,eps in [(1024,0.),(1024,0.01)]+[(n,0.001) for n in [256,512,1024,2048,4096]]]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(run,cases))
ratios={}
for name in ['helium','hydrogen','thermal']:
    r=[q for q in results if q['case']==name and q['eps']==0.001 and q['n']>=1024]
    ratios[name]={k:abs(r[1][k]-r[0][k])/abs(r[2][k]-r[1][k]) for k in ('final_delta_xe','final_delta_tm_k')}
    assert all(1.7<x<2.4 for x in ratios[name].values())
result=dict(schema='rec.r116.standalone/1',scope='prescribed directional Planck/Sobolev tracer; no geometry feedback',binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),n_cases=len(results),results=results,time_ratios=ratios)
(out/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(ratios,indent=2))
