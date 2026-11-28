"""Controlled cold matter scan on actual source state and native ray geometry."""
from pathlib import Path
import sys,json,numpy as np,hashlib,importlib.util
D=Path(__file__).resolve().parent;P=D.parent
from thermal import context,p,JumpResponse,jvp
sys.path.insert(0,str(P/'r118c4k_lambda_tangent'))
spec=importlib.util.spec_from_file_location('prior_map',P/'r118c4k_lambda_tangent/rec.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def rel(a,b):return float(np.linalg.norm(a-b)/max(np.linalg.norm(b),1e-300))
def main():
 c=context(128);ref=P/'r118c4h_goal_adjoint/goal_q3_128_-0.5.npz';z=np.load(ref);he=z['he'];v=z['rows'][:,1:3];c.v=np.stack([np.interp(he,c.he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=he;M=m.Map(c,-.5)
 K=P/'r118c4n_exact_spline_atomic/EXACT_HISTORY.npz';q=np.load(K);I=q['last'][:,:,0][:,c.src];rows=[]
 for step in [63,918,1773]:
  u=he[step];x=v[step,0];a,w=M.state(u);_,H,Tr=c.snap(u,x,v[step,1],c.zero)
  for ratio in [.25,.5,.8,.95]:
   T=ratio*Tr
   for name,inc in [('zero',np.zeros_like(I)),('represented_terminal_stock',I)]:
    s,_,_=c.snap(u,x,T,c.zero)
    G,O,dG,dO,res,dpar=jvp(c,s,a,w,inc,T)
    def f(xx,tt):
     s,_,_=c.snap(u,xx,tt,c.zero);r,o,_=p.step(s,a,np.zeros_like(inc),w);j=JumpResponse(s,a,w);b,c0,g=j.apply(inc);return r.dxHII_dln_a+g,o+b+c0
    g,o=f(x,T);tests=[]
    for ep in [1e-3,1e-4,1e-5]:
     gp,op=f(x,T*np.exp(ep));gm,om=f(x,T*np.exp(-ep));tests.append(dict(eps=ep,gas_relative=float(abs((gp-gm)/(2*ep)-dG)/max(abs(dG),1e-300)),outgoing_relative=rel((op-om)/(2*ep),dO)))
    ex=min(1e-6,.05*x,.05*(1-x));gx=(f(x+ex,T)[0]-f(x-ex,T)[0])/(2*ex)
    scale=p.COMPTON_GAMMA_PER_T4_S_INV_K4*Tr**4/H;A=scale*x/(1+x+c.model.f_he);Ax=scale*(1+c.model.f_he)/(1+x+c.model.f_he)**2
    J=np.array([[gx,dG/T],[Ax*(Tr-T),-2-A]]);eig=np.linalg.eigvals(J);schur=gx-J[0,1]*J[1,0]/J[1,1]
    row=dict(step=step,ratio=ratio,incident=name,x=float(x),T=float(T),Tr=float(Tr),gas=float(g),base_gap=float(abs(G-g)/max(abs(g),1e-300)),outgoing_gap=rel(O,o),matrix_residual=res,tests=tests,J=J.tolist(),eigs=[[float(e.real),float(e.imag)] for e in eig],frozen=float(gx),schur=float(schur),relative_shift=float(abs(schur-gx)/max(abs(gx),1e-300)))
    rows.append(row);print(json.dumps(row),flush=True)
 (D/'COLD.json').write_text(json.dumps(dict(rows=rows,source_sha=hashlib.sha256(K.read_bytes()).hexdigest(),baseline_sha=hashlib.sha256(ref.read_bytes()).hexdigest(),scope='controlled cold snapshots at fixed x,H,geometry,represented stock; not self-consistent thermal trajectory'),indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
