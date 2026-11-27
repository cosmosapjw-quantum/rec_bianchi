"""C3Z: same-history stable pair, actual stored polynomial audit, quadratic owner integration."""
from pathlib import Path
import sys,json,numpy as np
from numpy.polynomial.legendre import legval,legder,legroots
D=Path(__file__).resolve().parent;Y=D.parent/'r118c3y_arrival_forcing';X=D.parent/'r118c3x_three_moments';W=D.parent/'r118c3w_common_history'
def source_pair(nt,lam=None):
 s=(Y/'arrival_pair.py').read_text()
 token='  rec=np.array([B[i-1,...,0]'
 assert s.count(token)==1
 audit='''  stored=(base+B[i-1])[...,:311,:].copy()
  stored[...,0]+=fr
  stored/=fr[None,:,None]
  pa,pb,pc=stored[...,0],stored[...,1],stored[...,2]
  y=np.clip(np.divide(-pb,3*pc,out=np.zeros_like(pb),where=pc!=0),-1,1)
  lower=np.minimum(np.minimum(pa-pb+pc,pa+pb+pc),pa+pb*y+pc*(3*y*y-1)/2)
  for ii,jj in np.argwhere(np.any(stored[...,3:]!=0,axis=-1)):
   coeff=stored[ii,jj];roots=legroots(legder(coeff))
   roots=roots.real[(abs(roots.imag)<1e-10)&(abs(roots.real)<1)]
   lower[ii,jj]=np.min(legval(np.r_[-1,1,roots],coeff))
  cert['min_stored_full_ratio']=min(cert['min_stored_full_ratio'],float(np.min(lower)))
  cert['cells_checked']+=int(lower.size)
  cert['steps_checked']+=1
  assert np.all(lower>0),(i,float(np.min(lower)))
'''
 s=s.replace(token,audit+token)
 cert=dict(min_stored_full_ratio=float('inf'),cells_checked=0,steps_checked=0)
 ns={'__file__':str(D/'arrival_pair.py'),'__name__':'c3z','cert':cert,'legval':legval,'legder':legder,'legroots':legroots}
 exec(compile(s,str(Y/'arrival_pair.py'),'exec'),ns)
 if lam is None:
  err=ns['scalar'](nt);print('scalar replay absolute',nt,err,flush=True)
  (D/f'SCALAR_REPLAY_{nt}.json').write_text(json.dumps(dict(nt=nt,rows_max_abs=err))+'\n')
 else:
  ns['pair'](nt,lam)
  cert.update(nt=nt,lam=lam,scope='actual stored virtual full polynomial against conservative endpoint Planck floor')
  (D/f'FINAL_POS_{nt}_{lam:g}.json').write_text(json.dumps(cert,indent=2)+'\n');print(cert,flush=True)
def quad(nt,lam):
 sys.path.insert(0,str(D.parents[1]/'src'))
 # Surgical port of C3X direct integrator; exact higher moments against native operator.
 s=(X/'three_moments.py').read_text()
 def replace(a,b):
  nonlocal s
  assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
 # P=parent/r118c3w_common_history unchanged. positive3 imported from X.
 replace("from positive3 import reconstruct","sys.path.insert(0,str(D.parent/'r118c3x_three_moments'))\nfrom positive3 import reconstruct")
 replace('out=np.zeros((4,nr,313))','out=np.zeros((5,nr,313))')
 replace('for m in range(4):out[m]','for m in range(5):out[m]')
 replace('for k in range(4):U[k]','for k in range(5):U[k]')
 replace('b=owner(r,x+dx,tt);_,g0=apply(a,U[0]-U[1]);_,g1=apply(b,U[1]);F=.5*(a[0]+b[0])+g0+g1\n   return dx-h*F,tt,F,b',
 'b=owner(r,x+dx,tt);m0=owner(mid,xm,(T+tt)/2)\n   _,g0=apply(a,U[0]-3*U[1]+2*U[2]);_,g1=apply(m0,4*(U[1]-U[2]));_,g2=apply(b,2*U[2]-U[1]);F=(a[0]+4*m0[0]+b[0])/6+g0+g1+g2\n   return dx-h*F,tt,F,(b,m0)')
 replace('res,tt,F,b=trial(dx);maxroot','res,tt,F,(b,m0)=trial(dx);maxroot')
 replace('o0,_=apply(a,U[k]-U[k+1]);o1,_=apply(b,U[k+1]);o=a[1]/((k+1)*(k+2))+b[1]/(k+2)+o0+o1',
 'o0,_=apply(a,U[k]-3*U[k+1]+2*U[k+2]);o1,_=apply(m0,4*(U[k+1]-U[k+2]));o2,_=apply(b,2*U[k+2]-U[k+1]);w0=1/(k+1)-3/(k+2)+2/(k+3);w1=4/(k+2)-4/(k+3);w2=2/(k+3)-1/(k+2);o=w0*a[1]+w1*m0[1]+w2*b[1]+o0+o1+o2')
 replace("tag=f'm3_{nt}_{lam:g}'","tag=f'q3_{nt}_{lam:g}'")
 replace("scope='three weak moments, certified nonnegative polynomial (P3..6 correction if needed), actual direct finite native H-only response, fixed H, not continuum'","scope='three weak moments; quadratic native operator interpolation (endpoint+midpoint gas); certified positive full virtual history; fixed H; not continuum'")
 (D/'quadratic_generated.py').write_text(s)
 ns={'__file__':str(D/'quadratic_generated.py'),'__name__':'c3z_quad'};exec(compile(s,str(X/'three_moments.py'),'exec'),ns);ns['run'](nt,lam)
def line_budget():
 # Native line occupations on actual C3W scalar history. Derive boundary-crossing rates, not heat.
 sys.path.insert(0,str(D.parents[1]/'src'));sys.path.insert(0,str(W))
 from common_base import context
 from common_pair import Map,p,JumpResponse
 from scipy.constants import h,c,electron_volt
 ctx=context(128);z=np.load(W/'base_128.npz');he=z['he'];L,M,R=[z[k] for k in ['L','M','R']];v=z['rows'];m=Map(ctx,.5);m0=Map(ctx,0.)
 # Source line energies confirmed by exact native source edge map: outgoing indices 311..313.
 # ctx.es is outgoing-source energy assigned to each of 313 incoming channels.
 source_energy={}
 for j in range(311,314):
  vals=np.unique(ctx.es[ctx.src==j]);source_energy[j]=vals.tolist()
 # Outgoing 311 alpha 10.2, 312 beta 12.09, 313 gamma 12.75 (energies from actual native edge routing if present).
 # Gamma may not appear in src mapping if external boundary. Use native E21,E32,E42 constants as independently verified.
 E=np.array([10.1988,12.0875,12.7484]);nu=E*electron_volt/h
 for j,vals in source_energy.items():
  if vals:
   assert min(abs(np.array(vals)-E[j-311]))<.05,(j,vals,E)
 def sample(tt,i):
  j=np.searchsorted(he[:i],tt,side='right')-1;before=j<0;assert np.max(tt)<he[i-1]
  if i==1:return np.zeros_like(tt)
  j=np.clip(j,0,i-2);w=(tt-he[j])/(he[j+1]-he[j]);src=ctx.src[None,:]
  f=(1-3*w+2*w*w)*L[j,0,src]+(4*w-4*w*w)*M[j,0,src]+(2*w*w-w)*R[j,0,src]
  return np.where(before,0.,f)
 rows=[]
 for i in np.unique(np.linspace(1,len(he)-1,65).astype(int)):
  u=he[i];I0=sample(m0.t(u),i);tt=m.t(u);I=sample(tt,i)+p._planck_difference(ctx.ef[None,:]/(p.KB_NATIVE_EV_K*ctx.model.tcmb0_K*np.exp(-u)),tt-(u-ctx.lr))
  s,H,Tr=ctx.snap(u,*v[i,1:3],ctx.zero);a,w=m.state(u);op=JumpResponse(s,a,w);d=I-I0
  direct,induced,gas=op.apply(d);r0,o0,_=p.step(s,a,I0,w);r1,o1,_=p.step(s,a,I,w)
  dn=8*np.pi*(nu/c)**3/(s.nH_cgs*1e6)
  # f is signed departure, line boundary flux per H per ln a; geometry weight includes local redshift factor.
  f=dn*((w*a)@induced[:,311:]);ref=dn*((w*a)@(o1-o0)[:,311:]);err=np.linalg.norm(ref-f)/max(np.linalg.norm(f),1e-300)
  # incoming two line entries are boundary occupations with different energies; avoid unmatched subtraction.
  rows.append(dict(z=float(np.expm1(-u)),out_number_per_H_dln_a=f.tolist(),out_energy_eV_per_H_dln_a=(E*f).tolist(),native_reference_relative=float(err),gas_response=float(gas)))
 out=dict(energies_eV=E.tolist(),source_mapping_eV=source_energy,rows=rows,max_native_relative=max(x['native_reference_relative'] for x in rows),scope='outgoing signed real-line boundary crossing of occupation departure at each line; approximate eV rounded energies; actual scalar reference snapshots, fixed gas; not emitted power, net reaction heat or added virtual stock')
 (D/'LINE_FLUX.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items() if k!='rows'},flush=True)
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='scalar':source_pair(int(sys.argv[2]))
 elif mode=='pair':source_pair(int(sys.argv[2]),float(sys.argv[3]))
 elif mode=='quad':quad(int(sys.argv[2]),float(sys.argv[3]))
 elif mode=='line':line_budget()
 else:raise ValueError(mode)

