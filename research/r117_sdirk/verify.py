"""Re-run source-owned R116 reference slices with actual REC SDIRK."""
import concurrent.futures,csv,gzip,hashlib,json,math,pathlib,subprocess,sys
d=pathlib.Path(__file__).resolve().parent; refs=d.parent/'r116_species_thermal'
exe,out=map(lambda p:pathlib.Path(p).resolve(),sys.argv[1:3]); out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=json.loads((refs/'SLICE_RECEIPT.json').read_text())
for name in ['helium','hydrogen','thermal']:
 p=out/(name+'.tsv');p.write_bytes(gzip.decompress((refs/(name+'.tsv.gz')).read_bytes()))
 assert sha(p)==next(r['sha256'] for r in sources['slices'] if r['name']==name)
def run(case):
 name,n,eps=case;path=out/f'{name}_{n}_{eps}.tsv'
 argv=[str(exe),str(out/(name+'.tsv')),str(n),str(eps)]
 with path.open('wb') as f:subprocess.run(argv,stdout=f,check=True)
 rows=list(csv.DictReader(path.open(),delimiter='\t'));assert len(rows)==n+1
 r=[{k:float(v) for k,v in q.items()} for q in rows]
 assert all(all(map(math.isfinite,q.values())) and 0<=q['xp']<=1 and min(q['x_heii'],q['x_heiii'])>=0 and q['tm_k']>0 for q in r)
 def peak(k):return max(abs(q[k]) for q in r)
 result=dict(case=name,n=n,eps=eps,command=argv,sha256=sha(path),max_thermal_defect=peak('heat_defect_j_per_h'),peak_delta_xe=peak('delta_xe'),peak_delta_tm_k=peak('delta_tm_k'),max_scaled_residual=peak('scaled_residual'),final_delta_xe=r[-1]['delta_xe'],final_delta_tm_k=r[-1]['delta_tm_k'])
 if eps==0:assert result['peak_delta_xe']==result['peak_delta_tm_k']==0.
 assert result['max_thermal_defect']<1e-27
 return result
cases=[(name,n,eps) for name in ['helium','hydrogen','thermal'] for n,eps in [(1024,0.),(1024,0.01)]+[(n,0.001) for n in (256,512,1024,2048,4096)]]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p: results=list(p.map(run,cases))
ratios={}
for name in ['helium','hydrogen','thermal']:
 r=[q for q in results if q['case']==name and q['eps']==0.001 and q['n']>=1024]
 ratios[name]={k:abs(r[1][k]-r[0][k])/abs(r[2][k]-r[1][k]) if r[2][k]!=r[1][k] else None for k in ['final_delta_xe','final_delta_tm_k']}
assert all(3.4<r<4.7 for r in ratios['hydrogen'].values())
(out/'RESULTS.json').write_text(json.dumps(dict(schema='rec.r117.sdirk/1',scope='prescribed smooth directional sky; conditional HeI/Planck closure; not Bianchi feedback',binary_sha256=sha(exe),cases=results,ratios=ratios),indent=2)+'\n')
print(ratios)
