"""Independent double-precision state-equation assembly and linear solve.
Reads source CSV-like JSON literals directly, without importing the producer.
This is independent-method software validation, not a different-author R6/C9.
"""
from pathlib import Path
import numpy as np, math,json
H=6.62607015e-34; C=299792458; KB=1.380649e-23;T0=2.72548
ROOT=Path(__file__).resolve().parents[1]
src=json.loads((ROOT/'input/LAMDA_HD_PR161_SOURCE_TRANSCRIPTION.json').read_text())
ref=json.loads((ROOT/'evidence/RESULTS.json').read_text())
assert ref['original_35Hz']=='FAIL7/8'
E=np.array([float(x['E_cm1']) for x in src['levels']]);g=np.arange(9)*2+1

def calc(Tgas,n,ortho,z):
 Tbg=T0*(1+z);Q=np.zeros((9,9));rad=[]
 def add(u,l,v):
  Q[l,u]+=v;Q[u,u]-=v
 for v in src['radiative_lines']:
  u,l=v['upper_J'],v['lower_J']; A=float(v['A_s1'])
  x=H*(E[u]-E[l])*C*100/(KB*Tbg)
  nbg=1/math.expm1(x) if x<705 else 0.0
  down=A*(1+nbg); up=A*(g[u]/g[l])*nbg
  add(u,l,down);add(l,u,up)
  rad.append((u,l,down,up))
 i=src['temperature_nodes_K'].index(Tgas)
 p=src['collision_partner_para_H2']['rates_cm3_s1']
 o=src['collision_partner_ortho_H2']['rates_cm3_s1']
 coll=[]
 for a,b in zip(p,o):
  u,l=a['upper_J'],a['lower_J']
  rate=n*((1-ortho)*float(a['values'][i])+ortho*float(b['values'][i]))
  up=rate*(g[u]/g[l])*math.exp(-H*(E[u]-E[l])*C*100/(KB*Tgas))
  add(u,l,rate);add(l,u,up)
  coll.append((u,l,rate,up))
 mat=Q.copy();mat[-1,:]=1
 rhs=np.zeros(9);rhs[-1]=1
 populations=np.linalg.solve(mat,rhs)
 net=sum(H*C*100*(E[u]-E[l])*(populations[u]*d-populations[l]*up) for u,l,d,up in rad)
 return populations,net,np.max(np.abs(Q@populations))

cases=[]
for T in (50,100,200):
 for z in (0,30):
  for f in (0.,1.):
   n=1e4
   p,net,res=calc(T,n,f,z)
   key=f'{T}:{z}:10000:{int(f)}'
   import csv
   with open(ROOT/'evidence/HD9_CMB_144_DIAGNOSTIC_CASES.csv') as fh:
    hit=next(v for v in csv.DictReader(fh) if v['case']==key)
   v=float(hit['full9_net_W_per_HD_DIAGNOSTIC'])
   rel=abs(v-net)/max(abs(v),1e-45)
   assert rel<2e-9,(T,z,f,rel)
   assert res<2e-17,('Q balance',res)
   assert abs(sum(p)-1)<5e-14
   assert min(p)>=-1e-15  # float64 tiny high-J cancellation, not population acceptance
   cases.append({'T_K':T,'z':z,'f_ortho':f,'nH2_cm3':n,'relative_net_error':rel,
                 'generator_residual_s_minus1':res,'minimum_population':float(min(p))})
(ROOT/'evidence/INDEPENDENT_NUMPY_12_CASES.json').write_text(json.dumps({'method':'NumPy float64 independently assembled Q; mpmath80 source reference',
 'tested_cases':len(cases),'max_relative_net_error':max(x['relative_net_error'] for x in cases),
 'max_generator_residual_s_minus1':max(x['generator_residual_s_minus1'] for x in cases),
 'status':'PASS_NONAUTHORITATIVE_FULL9_DIAGNOSTIC','cases':cases},indent=2)+'\n')
print('independent_cases',len(cases),'max_relative',max(x['relative_net_error'] for x in cases))
