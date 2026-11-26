"""Directional redshift-escape QSS balance on actual native angular state."""
import sys,numpy as np,json
from pathlib import Path
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3h_paired_history'))
sys.path.insert(0,str(D.parent/'r118c3j_integrated_history'))
from shared_gas_h import stf,B
from retarded import raymap,interpF
from line_cell import phase,A21,EL
from scipy.constants import k,m_p,c
LY=4.662899067555897e15
def run():
 v=np.load(D.parent/'r118c3j_integrated_history/mid1024_1.npz');g=np.genfromtxt(B/'plusfine.csv',names=True,delimiter=',');u=np.log(g['a'])
 F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
 mu,w=leggauss(8);M,ph=np.meshgrid(mu,2*np.pi*np.arange(16)/16,indexing='ij');n=np.stack([np.sqrt(1-M*M)*np.cos(ph),np.sqrt(1-M*M)*np.sin(ph),M],axis=-1).reshape(-1,3);w=np.repeat(w/32,16)
 Fref=interpF(u,F,v['rows'][0,0]);rows=[]
 for j in np.unique(np.linspace(0,len(v['line'])-1,33).astype(int)):
  t,x,p,fin,nh,Tr=v['line'][j];T=v['rows'][j+1,2];H=np.interp(t,u,g['h'])*2.1842852410855023e-18
  nf,ww=raymap(interpF(u,F,t),Fref,n,w);ww/=ww.sum()
  S=stf([np.interp(t,u,g[f'S{i}']) for i in range(5)]);rate=1+np.einsum('ni,ij,nj->n',nf,S,nf)
  width=np.sqrt(2*k*T/(m_p*c*c));C=phase(nh,width);kc=H*rate/width*C
  num=p-(3*x-p)*fin;df=A21*num/(A21*(3*x-p)+kc);J=kc*df;fstar=fin+df
  # stable atom loss calculated independently using stationary rate equation
  atom=A21*(num-(3*x-p)*df)
  # cancellation in atom loss can be severe at tau~1e9. Record relative rather than silently replace.
  native=LY*H/(nh*1e-6*x)*rate*num
  exact=kc*A21*num/(A21*(3*x-p)+kc)
  res=float(abs(ww@(atom-J))/max(abs(ww@J),1e-300))
  rows.append(dict(t=float(t),angle_sum=float(ww@rate),tau_min=float(min(A21*(3*x-p)/kc)),tau_max=float(max(A21*(3*x-p)/kc)),net_ratio=float((ww@J)/(ww@native)),atom_balance_rel=res,stable_balance_rel=float(abs(ww@(exact-J))/abs(ww@J)),min_f=float(min(fstar))))
  assert min(fstar)>=0 and res<1e-5
 o=dict(rows=rows,scope='directional H_n and normalized solid-angle weights, actual native angular-weighted incident line occupation used as common incident bath, fixed real level QSS; not actual direction-dependent incident history or full atom insertion')
 (D/'LINE.json').write_text(json.dumps(o,indent=2)+'\n');print('max cancellation residual',max(x['atom_balance_rel'] for x in rows),'max stable residual',max(x['stable_balance_rel'] for x in rows),'ratio range',min(x['net_ratio'] for x in rows),max(x['net_ratio'] for x in rows))
if __name__=='__main__':run()
