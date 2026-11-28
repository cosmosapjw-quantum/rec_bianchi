from pathlib import Path
import numpy as np,sys,json
from scipy.linalg import solve_banded
from scipy.interpolate import CubicSpline
from event import Events,MovingSpline
D=Path(__file__).resolve().parent;P=D.parent
sys.path.insert(0,str(P/'r118c4k_lambda_tangent'))
from rec import Map,context
c=context(128);z=np.load(P/'r118c4h_goal_adjoint/goal_q3_128_-0.5.npz');he=z['he'];c.v=np.stack([np.interp(he,c.he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=he
m=Map(c,-.5);ev=Events(m)
rows=[]
for j,(g,ms) in enumerate(zip(m.g,ev.moving)):
 x=g.x;y=m.D.x;h=np.diff(x);N=len(x);M=g(x,2);A=np.zeros((5,N));b=np.zeros(N)
 def put(row,col,v):A[2+row-col,col]=v
 put(0,0,-h[1]);put(0,1,h[0]+h[1]);put(0,2,-h[0]);put(N-1,N-3,-h[-1]);put(N-1,N-2,h[-2]+h[-1]);put(N-1,N-1,-h[-2])
 i=np.arange(1,N-1);A[3,i-1]=h[:-1];A[2,i]=2*(h[:-1]+h[1:]);A[1,i+1]=h[1:]
 def dot(A,v):
  o=np.zeros(N)
  for k in range(-2,3):
   jj=np.arange(max(0,-k),min(N,N-k));o[jj+k]+=A[2+k,jj]*v[jj]
  return o
 b[i]=6*np.diff(np.diff(y)/h);b0=b.copy();b0[i]=6*np.diff(np.diff(g(x))/h)
 r=b-dot(A,M);r0=b0-dot(A,M);M0=solve_banded((2,2),A,b)
 # Recompute represented nominal spline exactly from stored nodes; compare
 # derivatives with original evaluation. Node error is amplified by divided differences.
 g0=CubicSpline(x,y,extrapolate=False);ms0=MovingSpline(g0,ms.dx)
 q=(x[:-1]+x[1:])/2;d=ms(q);d0=ms0(q)
 rows.append(dict(ray=j,ordinate_gap=float(np.max(abs(g(x)-y))),rhs_norm=float(np.max(abs(b))),nominal_absolute=float(np.max(abs(r))),nominal_relative=float(np.max(abs(r))/max(np.max(abs(b)),1e-300)),reevaluated_absolute=float(np.max(abs(r0))),reevaluated_relative=float(np.max(abs(r0))/max(np.max(abs(b0)),1e-300)),curvature_gap=float(np.max(abs(M-M0))),recomputed_spline_coeff_gap=float(np.max(abs(g.c-g0.c))),derivative_change_max=float(np.max(abs(d-d0)))))
out=dict(rows=rows,scope='Audit original represented spline residual using known ordinates vs evaluated ordinates; no change to executed full history.')
(D/'SPLINE_RESIDUAL_AUDIT.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print('maxima', {k:max(r[k] for r in rows) for k in rows[0] if k!='ray'})
print('worst',max(rows,key=lambda r:r['reevaluated_relative']))
