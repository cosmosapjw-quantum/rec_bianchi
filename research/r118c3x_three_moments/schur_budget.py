"""Native direct/induced affine response on actual retarded signed incoming differences."""
import numpy as np,json,sys
from pathlib import Path
from scipy.constants import hbar,c,electron_volt
D=Path(__file__).resolve().parent;P=D.parent/'r118c3w_common_history';sys.path.insert(0,str(P))
from common_base import context
from common_pair import Map,p,JumpResponse
def run():
 ctx=context(128);z=np.load(P/'base_128.npz');he=z['he'];L,M,R=[z[k] for k in ['L','M','R']];v=z['rows'];m=Map(ctx,.5);m0=Map(ctx,0.)
 E=ctx.tab.energy_eV;edge=np.r_[E[0]-(E[1]-E[0])/2,(E[1:]+E[:-1])/2,E[-1]+(E[-1]-E[-2])/2]
 assert np.all(np.diff(edge)>0)
 N=np.diff(edge**3)/3;U=np.diff(edge**4)/4;pref=1/(np.pi**2*(hbar*c/electron_volt)**3)
 def sample(t,i):
  j=np.searchsorted(he[:i],t,side='right')-1;before=j<0;assert np.max(t)<he[i-1]
  if i==1:return np.zeros_like(t)
  j=np.clip(j,0,i-2);w=(t-he[j])/(he[j+1]-he[j]);src=ctx.src[None,:]
  f=(1-3*w+2*w*w)*L[j,0,src]+(4*w-4*w*w)*M[j,0,src]+(2*w*w-w)*R[j,0,src]
  return np.where(before,0.,f)
 rows=[]
 for i in np.unique(np.linspace(1,len(he)-1,65).astype(int)):
  u=he[i];I0=sample(m0.t(u),i);tt=m.t(u);I=sample(tt,i)+p._planck_difference(ctx.ef[None,:]/(p.KB_NATIVE_EV_K*ctx.model.tcmb0_K*np.exp(-u)),tt-(u-ctx.lr))
  s,H,Tr=ctx.snap(u,*v[i,1:3],ctx.zero);a,w=m.state(u);op=JumpResponse(s,a,w);d=I-I0
  direct,induced,gas=op.apply(d);r0,o0,_=p.step(s,a,I0,w);r1,o1,_=p.step(s,a,I,w)
  total=direct+induced;scale=max(np.linalg.norm(total),1e-300);err=np.linalg.norm((o1-o0)-total)/scale
  # Stable direct/induced moment budgets restricted to virtual continuum bins.
  # An occupation moment is a stored spectral diagnostic, not a transition rate.
  def budget(g):
   f=w@g[:,:311];nn=pref/(s.nH_cgs*1e6)
   return np.array([nn*N@f,nn*U@f,nn*N@abs(f),nn*U@abs(f)])
  b0,b1,bt=[budget(x) for x in [direct,induced,total]]
  assert np.linalg.norm(b0[:2]+b1[:2]-bt[:2])<1e-10*max(np.linalg.norm(bt[:2]),np.linalg.norm(b0[:2]),np.linalg.norm(b1[:2]),1e-300)
  rows.append(dict(u=float(u),z=float(np.expm1(-u)),direct=b0.tolist(),induced=b1.tolist(),total=bt.tolist(),gas=float(gas),native_out_relative=float(err),native_gas_abs=float(abs(r1.dxHII_dln_a-r0.dxHII_dln_a-gas)),induced_direct_L2=float(np.linalg.norm(induced)/max(np.linalg.norm(direct),1e-300))))
 out=dict(rows=rows,max_native_out_relative=max(r['native_out_relative'] for r in rows),max_native_gas_abs=max(r['native_gas_abs'] for r in rows),scope='actual C3W scalar history, fixed-gas angular .5 clock and native exact affine transfer. Virtual-bin signed occupation moments in photons/H and eV/H (box spectral quadrature). Not emission/absorption event rates or a new heat ledger; no stochastic packet interpretation.')
 (D/'SCHUR_BUDGET.json').write_text(json.dumps(out,indent=2)+'\n')
 print({k:v for k,v in out.items() if k!='rows'},flush=True)
 print('sample',rows[len(rows)//2],flush=True)
if __name__=='__main__':run()
