"""New controlled characteristic partial; all formulas are in THEORY.md."""
import itertools,math
from fractions import Fraction as F
import numpy as np
EPS=np.finfo(float).eps

def shear(v):
 v=np.asarray(v,dtype=float)
 if v.shape!=(3,):raise ValueError('SHEAR_SHAPE')
 if not np.all(np.isfinite(v)):raise ValueError('SHEAR_NONFINITE')
 if math.fsum(map(float,v))!=0:raise ValueError('SHEAR_TRACE')
 return v

def direction(n):
 n=np.asarray(n,dtype=float)
 if n.shape!=(3,) or not np.all(np.isfinite(n)) or abs(math.fsum(float(x*x) for x in n)-1)>128*EPS:raise ValueError('DIRECTION_NORMALIZATION')
 return n

def energies(es,et):
 es=np.asarray(es);et=np.asarray(et)
 if es.shape!=et.shape or not np.all(np.isfinite(es)) or not np.all(np.isfinite(et)) or np.any(et<=0) or np.any(es<=et):raise ValueError('ENERGY_RATIO')
 return np.array([math.log(float(a)/float(b)) for a,b in zip(es,et)])

def margins(r,d=None):
 r=np.asarray(r)
 if r.shape!=(313,) or not np.all(np.isfinite(r)) or np.any(r<=0):raise ValueError('FIXED_CELL_MARGIN')
 if d is not None and (np.shape(d)!=r.shape or not np.all(np.isfinite(d)) or np.any(np.abs(d)>=r)):raise ValueError('OUTSIDE_FIXED_CELL_MARGIN')

def rays():
 ns=[];weights=[];squares=[]
 for i in range(3):
  for s in (-1,1):
   n=np.zeros(3);n[i]=s;ns.append(n);weights.append(F(1,15));squares.append(tuple(F(int(j==i)) for j in range(3)))
 for signs in itertools.product((-1,1),repeat=3):
  ns.append(np.array(signs)/math.sqrt(3));weights.append(F(3,40));squares.append((F(1,3),)*3)
 return np.array(ns),np.array(list(map(float,weights))),weights,squares

def exact_rule():
 # Odd monomials cancel exactly by signed pairing, including odd total degree.
 rows=[]
 for ex in itertools.product(range(5),repeat=3):
  degree=sum(ex)
  if degree>4:continue
  if any(a%2 for a in ex):value=F(0);expected=F(0)
  else:
   value=sum((F(2,15) if all(ex[j]==0 for j in range(3) if j!=i) else F(0)) for i in range(3))
   value+=F(8)*F(3,40)/F(3)**(degree//2)
   def df(n):
    z=1
    for k in range(n,0,-2):z*=k
    return z
   expected=F(math.prod(df(a-1) for a in ex),df(degree+1))
  rows.append({'exponents':ex,'rule':str(value),'sphere':str(expected),'pass':value==expected})
 if not all(r['pass'] for r in rows):raise ValueError('EXACT_RULE_MOMENT')
 return rows

def derivatives(L,x,g,v,n):
 v=shear(v);n=direction(n);w=n*n;A=float(w@v);C=float(w@(v*v));AA=float(w@abs(v))
 W=np.exp(-x);hc=g-x*W;kc=(x*x-x)*W
 q1=L*A;q2=-2*L*A*A+2*L*L*(C-A*A)
 u1=hc*q1;u2=hc*q2+kc*L*L*A*A
 gross1=(abs(g)+x*W)*L*AA
 gross2=(abs(g)+x*W)*(2*L*AA*AA+2*L*L*(C+AA*AA))+(x*x+x)*W*L*L*AA*AA
 tangent=L[:,None]*n[None,:]*(v-A)[None,:]
 return dict(q1=q1,q2=q2,u1=u1,u2=u2,gross1=gross1,gross2=gross2,tangent=tangent,A=A,C=C,hc=hc,kc=kc)

def root(L,p,v,w):
 """Stable shifted Newton; returns delta, iterations, gross-scaled residual."""
 if p==0:return 0.,0,0.
 t=abs(p)*max(abs(float(a)) for a in v)
 if not math.isfinite(L) or L<=0 or t>=1:raise ValueError('CROSSING_DOMAIN')
 if min(1+p*float(a) for a in v)<=0:raise ValueError('NONPOSITIVE_DIRECTIONAL_RATE')
 d=L*p*math.fsum(float(a*b) for a,b in zip(w,v))
 for iteration in range(1,33):
  ev=[math.expm1(2*p*float(a)*(L-d)) for a in v]
  s=math.fsum(float(a)*b for a,b in zip(w,ev));logterm=.5*math.log1p(s)
  f=d-logterm;gross=abs(d)+abs(logterm)
  if (gross==0 and f==0) or (gross>0 and abs(f)<=256*EPS*gross):return d,iteration,(abs(f)/gross if gross else 0.)
  weighted=math.fsum(float(a)*float(b)*(1+c) for a,b,c in zip(w,v,ev))
  d-=f/(1+p*weighted/(1+s))
 raise ValueError('ROOT_ITERATION_CAP')

def increment(g,x,d):
 if d==0:return 0.
 return g*d+math.exp(-x)*math.expm1(-x*math.expm1(d))

def normalized(error,gross):
 error=np.asarray(error);gross=np.asarray(gross)
 if np.any((gross==0)&(error!=0)):return float('inf')
 return float(np.max(np.divide(abs(error),gross,out=np.zeros_like(error,dtype=float),where=gross!=0)))
