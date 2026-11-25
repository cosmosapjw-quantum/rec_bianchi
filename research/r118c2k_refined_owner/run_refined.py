"""Actual mixed-grid graph, direct source and coupled evolution campaign."""
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from scipy.constants import h,e
from scipy.integrate import solve_ivp
from full_bianchi_hyrec.standalone_line import prepare
from full_bianchi_hyrec.trajectory.atomic_refined_owner import RefinedTwoS,compile_integrals,assemble,Scatter
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import L
from full_bianchi_hyrec.recoil.calibrated_source import Bath
p=argparse.ArgumentParser();p.add_argument('--compiled',type=Path,required=True);p.add_argument('--rates',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--bath',choices=['z900','z1100','z1300'],required=True);a=p.parse_args()
r=a.out.resolve();r.mkdir(exist_ok=False)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
st=json.loads((a.compiled/'STATES.json').read_text())['states'][a.bath]
with np.load(a.compiled/(a.bath+'.npz')) as z:data={k:z[k] for k in z.files}
q=prepare(data,4);net=RefinedTwoS(a.rates,q,16)
neutral=st['n_H_m3']*(st['x_1s']+st['x_2s']);n2=st['n_H_m3']*st['x_2s']
t=time.monotonic();integ=compile_integrals(net,Bath(q['T'],q['n1s']))
np.savez_compressed(r/'QUAD.npz',**{f'{i}_{j}_{k}':v for i,j,x,y,w in integ for k,v in [('x',x),('y',y),('w',w)]})
print('compiled',a.bath,'seconds',time.monotonic()-t,flush=True)
rows=[];cases=[];refs=[]
def init(net,kind):
 if kind=='thermal':return net.initial(q['T'],neutral,equilibrium=True)
 s=net.initial(st['T_r_K'],neutral,n2)
 if kind=='pulse':
  for typ,i,j,_,_ in net.cross_blocks:
   if typ=='cross':
    ix=net.ids(j);s.dt[ix]+=s.nt[ix]*L('.25')
 return s
for n in (16,32,64,128):
 net=RefinedTwoS(a.rates,q,n);edges,report=assemble(net,data,integ);sc=Scatter(net,edges)
 # For action parity use the actual same material ground state as the quadrature anchor.
 s=net.initial(q['T'],q['n1s'],n2=0.)
 thermal=sc.action(s);err=abs(thermal[0])/thermal[1]
 tests=[]
 for i,sg in enumerate((1,-1)):
  s=net.initial(q['T']*(1+sg*.001),q['n1s'],n2=0.)
  E,g=sc.action(s);want=report['direct'][i]*h*q['dnu']/e
  tests.append(dict(sign=sg,action=E,direct=want,relative=float(abs(E/want-1))))
 assert err<1e-12
 report.update(n=n,tracked=len(net.et),hat_modes=net.ncore,com_modes=net.ncom,companion=len(net.ec),events=len(net.events),edges=len(edges),source_rate=net.source_rate_relative,source_energy=net.source_energy_relative,phase_error=net.phase_relative,thermal_error=err,action=tests)
 rows.append(report);print('GRAPH',a.bath,n,report,flush=True)
 np.savez_compressed(r/f'GRAPH{n}.npz',i=sc.i,j=sc.j,K=sc.K,new=sc.new,cross=sc.cross,et=net.et,gt=net.gt,ec=net.ec,gc=net.gc,events=np.array(net.events,dtype=L),parent_offsets=net.offset,bounds=net.bounds)
 for kind,steps in [('thermal',2),('actual',4),('pulse',4)]+([('pulse',j) for j in (1,2,8,16)] if n==128 and a.bath=='z1100' else []):
  s=init(net,kind);old=s.clone();gross=L(0);bath_energy=L(0);cross=L(0);new_energy=L(0);hist=[]
  for j in range(steps):
   ds=.1/steps
   # existing source BE plus positive explicit SSPRK2 for the common graph
   b=net.step(s,ds);v=sc.step(s,ds);gross+=L(b['gross'])+L(v['gross'])
   bath_energy+=L(v['bath_energy_eV_m3']);cross+=L(v['cross_into_com']);new_energy+=L(v['new_energy'])
   dn=s.dt-old.dt;dc=s.dc-old.dc;da=s.d2-old.d2
   N=np.sum(dn)+da;E=dn@net.et+dc@net.ec+net.transition*da+bath_energy
   hist.append(dict(step=j+1,n2=float(s.n2+s.d2),delta_n2=float(da),cross=float(cross),new_energy=float(new_energy),bath_energy=float(bath_energy),number_relative=float(abs(N)/gross),energy_relative=float(abs(E)/(gross*net.transition)),gross=float(gross),scatter=v))
   assert np.min(s.nt+s.dt)>=0 and np.min(s.nc+s.dc)>=0 and 0<=s.n2+s.d2<=s.neutral
   assert hist[-1]['number_relative']<1e-11 and hist[-1]['energy_relative']<1e-11
  name=f'n{n}_{kind}_{steps}';f=r/(name+'.npz')
  np.savez_compressed(f,et=net.et,ec=net.ec,nt=s.nt,nc=s.nc,dt=s.dt,dc=s.dc,initial_dt=old.dt,initial_dc=old.dc,n2=s.n2,d2=s.d2,initial_d2=old.d2,neutral=s.neutral)
  row=dict(case=name,n=n,kind=kind,steps=steps,terminal=hist[-1],max_N=max(v['number_relative'] for v in hist),max_E=max(v['energy_relative'] for v in hist),state_sha256=sha(f))
  (r/(name+'.json')).write_text(json.dumps(hist,indent=2)+'\n');cases.append(row);print('RUN',a.bath,name,row['terminal'],flush=True)
 if n==128 and a.bath=='z1100':
  s=init(net,'pulse');base=s.clone();nt=len(s.nt);nc=len(s.nc);scale=L(s.n2)
  # Independent unsplit ODE, no implicit event step. Vectorized stoichiometry.
  ii=np.array([z[0] for z in net.events]);jj=np.array([z[1] for z in net.events]);sg=np.array([z[2] for z in net.events],dtype=L);rate=np.array([z[3] for z in net.events],dtype=L)
  def fun(t,y):
   v=np.asarray(y,dtype=L)*scale;s.dt=base.dt+v[:nt];s.dc=base.dc+v[nt:nt+nc];s.d2=base.d2+v[-3]
   f=net.point_values(s);fc=(s.nc+s.dc)/net.gc;b=s.n2+s.d2
   F=rate*(b*(1+f[ii])*(fc[jj]+(sg==1))-(s.neutral-b)*f[ii]*(fc[jj]+(sg==-1)))
   d,flux,gross=sc.rhs(s);np.add.at(d,ii,F);c=np.zeros(nc,dtype=L);np.add.at(c,jj,sg*F)
   return np.asarray(np.r_[d,c,-np.sum(F),np.sum(flux[sc.cross]),flux[sc.new]@sc.de[sc.new]]/scale,float)
  ode=solve_ivp(fun,(0,.1),np.zeros(nt+nc+3),method='DOP853',rtol=3e-12,atol=2e-14)
  assert ode.success
  v=ode.y[:,-1]*float(scale)
  for row in cases:
   if row['n']==128 and row['kind']=='pulse':
    z=row['terminal'];refs.append(dict(steps=row['steps'],delta_n2_ref=float(v[-3]),cross_ref=float(v[-2]),new_energy_ref=float(v[-1]),delta_n2_relative=abs(z['delta_n2']/v[-3]-1),cross_relative=abs(z['cross']/v[-2]-1),new_energy_relative=abs(z['new_energy']/v[-1]-1)))
  print('ODE',refs,flush=True)
 (r/'RESULTS.json').write_text(json.dumps(dict(bath=a.bath,source_sha256=sha(a.compiled/(a.bath+'.npz')),rate_sha256=sha(a.rates),quad_sha256=sha(r/'QUAD.npz'),graphs=rows,cases=cases,reference=refs),indent=2,allow_nan=False)+'\n')
