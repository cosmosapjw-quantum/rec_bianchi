"""Open isolated Ly-alpha reaction plus external photon injection and escape."""
import numpy as np,json,sys
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3j_integrated_history'))
from line_cell import evolve,phase,A21,EL
def boundary(n,k,j,dt):
 if min(n,k,j,dt)<0:raise ValueError('domain')
 if k==0:return n+j*dt,0.,j*dt
 z=-np.expm1(-k*dt);n1=n*(1-z)+j/k*z
 inj=j*dt;esc=n+inj-n1
 return n1,esc,inj
def advance(p,n,X,C,k,j,dt):
 n,e0,i0=boundary(n,k,j,dt/2);p,n,_,_=evolve(p,n,X,C,dt);n,e1,i1=boundary(n,k,j,dt/2)
 return p,n,e0+e1,i0+i1
def run():
 data=np.load(D.parent/'r118c3j_integrated_history/mid1024_1.npz');L=data['line'];rows=[]
 for j in np.unique(np.linspace(0,len(L)-1,17).astype(int)):
  u,x1,p,f,nh,Tcmb=L[j];T=data['rows'][j+1,2];dlog=np.sqrt(2*1.380649e-23*T/(1.6735575e-27*299792458.**2));C=phase(nh,dlog);n=C*f;X=x1+p
  # Conditional open cell with specified escape rate A21/100 and boundary bath matching incoming f.
  k=A21/100;src=k*n
  out=[]
  for nt in [8,16,32]:
   pp,nn=p,n;esc=inj=0.;dt=20/A21/nt
   for _ in range(nt):
    pp,nn,e,i=advance(pp,nn,X,C,k,src,dt);esc+=e;inj+=i
   out.append(dict(steps=nt,p=pp,n=nn,escaped=esc,injected=inj,relative_residual=float(abs(pp+nn+esc-inj-p-n)/max(p+n,1e-300))))
  rows.append(out)
 o=dict(rows=rows,max_residual=max(x['relative_residual'] for row in rows for x in row),scope='isolated line cell with prescribed escape and injection, not Sobolev network; actual accepted source sample, hypothetical boundary rates')
 (D/'LINE.json').write_text(json.dumps(o,indent=2)+'\n');print(o['max_residual'])
if __name__=='__main__':run()
