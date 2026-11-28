"""Actual limiter-cell contribution to receiving weak moments, moving-event derivative."""
from pathlib import Path
import sys,json,hashlib,numpy as np
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss,legval,legder
D=Path(__file__).resolve().parent;P=D.parent;I=P/'r118c4i_weak_adjoint';H=P/'r118c4h_goal_adjoint'
sys.path[:0]=[str(P/'r118c3w_common_history'),str(P/'r118c3x_three_moments'),str(D.parents[1]/'src')]
from common_base import context
g={'__file__':str(I/'active_limiter.py'),'__name__':'prior'};exec(compile((I/'active_limiter.py').read_text(),str(I/'active_limiter.py'),'exec'),g);Map=g['Map']
src=I/'ACTIVE_LIMITER_INPUT.npz';z=np.load(src);c=context(128);he=np.load(H/'goal_q3_128_-0.5.npz')['he'];c.he=he;lam=float(z['lam']);s0=int(z['step'])-1;A=z['co'];meta=json.loads((I/'ACTIVE_LIMITER.json').read_text());x,w=leggauss(24)
def roots(mp,ray,ch):
 f=mp.f[ray];g=mp.g[ray];return np.array([g(f(s)+c.lr[ch]) for s in he[s0:s0+2]])
def inv(mp,ray,ch,u):return mp.g[ray](mp.f[ray](u)-c.lr[ch])
def integrate(mp,ray,ch,poly,l,r):
 a,b=roots(mp,ray,ch);a=max(a,l);b=min(b,r)
 if not b>a:return np.zeros(5)
 q=(a+b)/2+(b-a)/2*x;t=inv(mp,ray,ch,q);t=2*(t-he[s0])/(he[s0+1]-he[s0])-1.;v=legval(t,poly);W=((q-l)/(r-l))[:,None]**np.arange(5);return np.sum(w[:,None]*v[:,None]*W,axis=0)*(b-a)/(2*(r-l))
m0=Map(c,lam);rows=[]
for h in [1e-3,3e-4,1e-4]:
 mm,mp=Map(c,lam-h),Map(c,lam+h)
 for row in meta['rows']:
  ray,ch=int(row['ray']),int(row['channel']);srcch=int(c.src[ch]);poly=A[ray,srcch]
  ta,tb=roots(m0,ray,ch)
  if not np.isfinite(ta+tb) or ta<he[0] or tb>he[-1]:continue
  # Integrate in one interval spanning full nominal cell arrival with margin.
  l=ta-.1*(tb-ta);r=tb+.1*(tb-ta)
  fd=(integrate(mp,ray,ch,poly,l,r)-integrate(mm,ray,ch,poly,l,r))/(2*h)
  f=m0.f[ray];fl=lambda u:(mp.f[ray](u)-mm.f[ray](u))/(2*h)
  roots_fd=(roots(mp,ray,ch)-roots(mm,ray,ch))/(2*h)
  roots_ana=np.array([(fl(s)-fl(t))/f(t,1) for s,t in zip(he[s0:s0+2],[ta,tb])])
  q=(ta+tb)/2+(tb-ta)/2*x;t=inv(m0,ray,ch,q);dt=(fl(q)-fl(t))/f(t,1);xx=2*(t-he[s0])/(he[s0+1]-he[s0])-1
  df=legval(xx,legder(poly))*2/(he[s0+1]-he[s0])*dt
  W=((q-l)/(r-l))[:,None]**np.arange(5)
  bulk=np.sum(w[:,None]*df[:,None]*W,axis=0)*(tb-ta)/(2*(r-l))
  boundary=(legval(1.,poly)*roots_ana[1]*((tb-l)/(r-l))**np.arange(5)-legval(-1.,poly)*roots_ana[0]*((ta-l)/(r-l))**np.arange(5))/(r-l)
  exact=bulk+boundary
  row0=dict(ray=ray,ch=ch,srcch=srcch,h=h,root_gap=float(np.max(abs(roots_ana-roots_fd))),relative_gap=float(np.linalg.norm(exact-fd)/max(np.linalg.norm(fd),1e-300)),bulk_only_gap=float(np.linalg.norm(bulk-fd)/max(np.linalg.norm(fd),1e-300)),boundary_fraction=float(np.linalg.norm(boundary)/max(np.linalg.norm(fd),1e-300)),fd=fd.tolist(),bulk=bulk.tolist(),boundary=boundary.tolist())
  rows.append(row0);print(row0,flush=True)
assert len(rows)>0
(D/'EVENT_MOTION.json').write_text(json.dumps(dict(rows=rows,source_sha=hashlib.sha256(src.read_bytes()).hexdigest(),scope='isolated actual outgoing active-limiter source cell contribution (zero outside), exact moving-boundary formula with numerical lambda derivative of source spline; not derivative of full signed history or full accepted solver'),indent=2)+'\n')
