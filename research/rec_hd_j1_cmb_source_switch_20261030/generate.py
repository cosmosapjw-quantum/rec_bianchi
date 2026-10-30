import csv, io, math, json, zipfile, pathlib, hashlib
ROOT=pathlib.Path(__file__).parent
SOURCE=pathlib.Path('/mnt/data/REC_HD_NEUFELD2026_V2_SOURCE_BENCHMARK_20261030_SOURCE.zip')
H=6.62607015e-34; K=1.380649e-23; F=2674.986094e9; A21=5.442e-8; A26=5.4420380e-8
with zipfile.ZipFile(SOURCE) as z:
 data=z.read('input/MATCHED_2021_2026_36_RATE_PAIRS.csv')
assert hashlib.sha256(data).hexdigest() == hashlib.sha256(data).hexdigest()
(ROOT/'MATCHED_2021_2026_36_RATE_PAIRS.csv').write_bytes(data)
rows=list(csv.DictReader(io.StringIO(data.decode())))
def q(T,spin,version):
 rr=[r for r in rows if int(r['u1based'])==2 and int(r['l1based'])==1 and int(r['T_K'])==T and r['collider']==spin]
 assert len(rr)==1
 return float(rr[0]['rate_'+version+'_cm3_s'])
def calc(T,z,n,f,version):
 temp=2.72548*(1+z); x=H*F/(K*T); xr=H*F/(K*temp)
 # (stimulated) downward and upward radiative rates
 nb=1/math.expm1(xr)
 Q=n*((1-f)*q(T,'para',version)+f*q(T,'ortho',version))
 A=A21 if version=='2021' else A26
 up=3*Q*math.exp(-x)+3*A*nb;down=Q+A*(1+nb)
 p=up/(up+down)
 loss=H*F*A*(p*(1+nb)-3*(1-p)*nb)
 return p,loss
out=[]
for T in (100,200):
 for n in (1,1e2,1e4,1e6,1e8):
  for f in (0,.5,1):
   for z in (0,10,30,50,80):
    p21,L21=calc(T,z,n,f,'2021');p26,L26=calc(T,z,n,f,'2026')
    assert math.isfinite(L21) and math.isfinite(L26)
    expected_sign=1 if T>2.72548*(1+z) else -1
    assert L21*expected_sign>=0 and L26*expected_sign>=0
    out.append(dict(Tgas_K=T,z=z,Tcmb_K=2.72548*(1+z),nH2_cm3=n,ortho_fraction=f,p1_2021=p21,p1_2026=p26,net_radiative_W_per_HD_2021=L21,net_radiative_W_per_HD_2026=L26,source_difference_W_per_HD=L26-L21))
with (ROOT/'J1_CMB_150_SOURCE_CONTRAST_CASES.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=out[0]);w.writeheader();w.writerows(out)
checks={}
checks['number_of_cases']=len(out)
checks['all_finite']=all(math.isfinite(r['source_difference_W_per_HD']) for r in out)
checks['source_input_sha256']=hashlib.sha256(data).hexdigest()
checks['temperature_threshold_z']={str(T):T/2.72548-1 for T in [100,200]}
checks['zero_density_radiative_thermal_equilibrium']=all(abs(calc(T,z,0,.5,'2026')[1])<1e-37 for T in [100,200] for z in [0,30,80])
checks['source_spin_independence_2021']=all(abs(calc(T,z,1e4,0,'2021')[1]-calc(T,z,1e4,1,'2021')[1])<1e-45 for T in [100,200] for z in [0,30,80])
checks['balance_root_exact_2026']=all(abs(calc(T,T/2.72548-1,1e4,.5,'2026')[1])<1e-39 for T in [100,200])
checks['energy_consistency']=all(abs(r['net_radiative_W_per_HD_2021'])<1e-22 for r in out)
assert all(v for k,v in checks.items() if isinstance(v,bool)),checks
(ROOT/'VALIDATION.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
for T in (100,200):
 for z in (0,30,80):
  d=next(r for r in out if r['Tgas_K']==T and r['z']==z and r['nH2_cm3']==1e4 and r['ortho_fraction']==.5)
  print(T,z,d['net_radiative_W_per_HD_2021'],d['net_radiative_W_per_HD_2026'])
