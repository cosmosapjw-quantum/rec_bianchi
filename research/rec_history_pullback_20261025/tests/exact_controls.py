"""Independent rational polynomial/dense references; no linear solve."""
from fractions import Fraction as F
import math
import numpy as np
import interval as iv
import history_boundary as native
from chart import frac,enclosure,conditional_box,require_shapes
from common import save

def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))
def mv(A,x):return [dot(r,x) for r in A]
def mm(A,B):return [[dot(r,c) for c in zip(*B)] for r in A]
def trans(A):return list(map(list,zip(*A)))
def run(out,counter):
 def action(A,x):
  counter.charge('FRACTION_ORACLE_MATRIX_VECTOR_ACTION')
  return mv(A,x)
 a=[F(1,4),F(3,4)];h=F(1,2);yl=[F(1),F(3)];yr=[F(-2),F(7)];K=[[F(2),F(-1)],[F(0),F(3)]]
 P=[[1-a[0],a[0],F(0),F(0)],[F(0),F(0),1-a[1],a[1]]];g=[(r-l)/h for l,r in zip(yl,yr)];G=[[g[0],F(0)],[F(0),g[1]]]
 A=mm(K,P);C=mm(K,G);dy=[F(1,8),F(-1,4),F(1,4),F(1,8)];xi=[F(1,10),F(-1,20)]
 counter.charge('FRACTION_TOY_CHART_FORWARD');delta=[(1-a[j]-xi[j]/h)*(yl[j]+dy[2*j])+(a[j]+xi[j]/h)*(yr[j]+dy[2*j+1])-((1-a[j])*yl[j]+a[j]*yr[j]) for j in range(2)]
 tangent=[dot(P[j],dy)+g[j]*xi[j] for j in range(2)];remainder=[xi[j]/h*(dy[2*j+1]-dy[2*j]) for j in range(2)];assert all(d==t+r for d,t,r in zip(delta,tangent,remainder))
 counter.charge('FRACTION_TOY_DENSE_COMPOSITION');assert action(K,tangent)==[x+y for x,y in zip(action(A,dy),action(C,xi))]
 for w in ([F(1),F(-2)],[F(-3),F(1)]):
  counter.charge('FRACTION_TOY_TRANSPOSE');v=action(trans(K),w);lhs=dot(w,action(K,tangent));rhs=dot(action(trans(P),v),dy)+dot([g[j]*v[j] for j in range(2)],xi);assert lhs==rhs
 norm=lambda M:max(sum(abs(x) for x in row) for row in M)
 assert norm(A)==norm(K)
 shared=[[F(1,2),F(1,2)],[F(1,2),F(1,2)]];cancel=[[F(1),F(-1)]];sharedA=mm(cancel,shared);assert norm(sharedA)==0<norm(cancel)
 # Elementary interval query-product contains the exact rational toy entries.
 Kf=np.array([[float(x) for x in r] for r in K]);gf=np.array([float(x) for x in g]);ci=iv.mul(iv.point(Kf),iv.point(gf[None,:]))
 for i in range(2):
  for j in range(2):assert frac(ci[0][i,j])<=C[i][j]<=frac(ci[1][i,j])
 # Direct independent finite-box polynomial check on supplied rational radii.
 eL=[abs(dy[0]),abs(dy[2])];eR=[abs(dy[1]),abs(dy[3])];tau=list(map(abs,xi));b=[(1-a[j])*eL[j]+a[j]*eR[j]+abs(g[j])*tau[j]+tau[j]/h*(eL[j]+eR[j]) for j in range(2)]
 exactout=action(K,delta);bounds=action([[abs(v) for v in row] for row in K],b);assert all(abs(x)<=bd for x,bd in zip(exactout,bounds))
 toy={'a':np.array(list(map(float,a))),'h':float(h),'glo':gf,'ghi':gf,'lower':[-h*x for x in a],'upper':[h*(1-x) for x in a]}
 counter.interval('TOY_FINITE_BOX');box=conditional_box(iv.point(Kf),toy,np.array(list(map(float,eL))),np.array(list(map(float,eR))),np.array(list(map(float,tau))))
 assert all(abs(v)<=frac(bd) for v,bd in zip(exactout,box['bound']))
 counter.charge('EXACT_ZERO_POINT_PAIRING');zero=np.dot(np.array([1.,-1.]),np.array([1.,1.]));assert zero==0.
 zeros=action(K,[F(0),F(0)]);assert zeros==[F(0),F(0)]
 report={'status':'PASS','exact_tangent':[str(x) for x in tangent],'exact_remainder':[str(x) for x in remainder],'exact_delta':[str(x) for x in delta],'exact_outgoing':[str(x) for x in exactout],'exact_box':[str(x) for x in bounds],'disjoint_endpoint_norm':str(norm(A)),'K_norm':str(norm(K)),'shared_support_counterexample':{'K_norm':str(norm(cancel)),'KP_norm':str(norm(sharedA))},'exact_zero_pairing':float(zero),'rational_slope_query_intervals':'CONTAINED','solves':0}
 save(out/'EXACT_TOY_CONTROLS.json',report)
 # Actual-shape API refusal and old scalar knot semantics are separate controls.
 refusals=[]
 def refuse(name,fn):
  try:fn()
  except ValueError:refusals.append(name)
  else:raise AssertionError('REFUSAL_MISSING:'+name)
 st=native.interpolation(0.,.5,np.array([1.,2.,3.]),3,.5)
 refuse('nonzero_query_tangent_at_exact_knot',lambda:native.interpolation_jvp(st,np.zeros(3),1.))
 endpoint=native.interpolation_jvp(st,np.array([0.,3.,0.]),0.);assert endpoint==3.
 refuse('strict_upper_endpoint',lambda:native.interpolation(0.,.5,np.ones(3),3,1.))
 interior=native.interpolation(0.,.5,np.ones(3),3,.75);assert interior['k']==1
 refuse('nonfinite_query',lambda:native.interpolation(0.,.5,np.ones(3),3,np.nan))
 refuse('bad_endpoint_shape',lambda:native.interpolation_jvp(st,np.zeros(1),0.))
 save(out/'SCALAR_DOMAIN_CONTROLS.json',{'status':'PASS','refused':refusals,'endpoint_only_at_knot':endpoint,'valid_last_cell_interior':True})
 return report
