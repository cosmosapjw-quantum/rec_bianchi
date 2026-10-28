"""Conditional component residual of an explicit affine thermal path.

All primitive arithmetic is rational. Every interval operation is rounded
outward to an absolute dyadic256 grid. Source background inclusions are inputs,
not regenerated or promoted to physical full-state error certificates here.
"""
from dataclasses import dataclass
from fractions import Fraction as Q

BITS=256
CN=Q(float(4.91466895548409e-22))
FHE=Q(float(.24)/(1-float(.24))/float(3.97153))
B=1+FHE
GUARD=Q(float(1e-10))

@dataclass(frozen=True)
class I:
    lo: Q
    hi: Q
    def __post_init__(self):
        a,b=Q(self.lo),Q(self.hi)
        if a>b: raise ValueError('REVERSED_INTERVAL')
        scale=1<<BITS
        la,ub=a*scale,b*scale
        object.__setattr__(self,'lo',Q(la.numerator//la.denominator,scale))
        object.__setattr__(self,'hi',Q(-((-ub.numerator)//ub.denominator),scale))
    @staticmethod
    def point(x):return I(Q(x),Q(x))
    @staticmethod
    def read(d):return I(Q(d['lo']),Q(d['hi']))
    def __add__(self,o):
        o=o if isinstance(o,I) else I.point(o)
        return I(self.lo+o.lo,self.hi+o.hi)
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,o):return self+-o if isinstance(o,I) else self+(-Q(o))
    def __rsub__(self,o):return -self+o
    def __mul__(self,o):
        o=o if isinstance(o,I) else I.point(o)
        v=[a*b for a in (self.lo,self.hi) for b in (o.lo,o.hi)]
        return I(min(v),max(v))
    __rmul__=__mul__
    def __truediv__(self,o):
        o=o if isinstance(o,I) else I.point(o)
        if o.lo<=0<=o.hi: raise ValueError('DENOMINATOR_CONTAINS_ZERO')
        return self*I(1/o.hi,1/o.lo)
    def __rtruediv__(self,o):return I.point(o)/self
    def square(self):
        return I(0 if self.lo<=0<=self.hi else min(self.lo*self.lo,self.hi*self.hi),max(self.lo*self.lo,self.hi*self.hi))
    def intersect(self,o):return I(max(self.lo,o.lo),min(self.hi,o.hi))
    def record(self):return {'lo':str(self.lo),'hi':str(self.hi)}
    def contains(self,x):return self.lo<=Q(x)<=self.hi
    def subset(self,o):return o.lo<=self.lo<=self.hi<=o.hi
    @property
    def width(self):return self.hi-self.lo
    @property
    def absmax(self):return max(abs(self.lo),abs(self.hi))

def chord_bounds(left,right,m2,h,alpha=None):
    """Exact chord theorem, returning rational endpoints without float conversion."""
    l=tuple(map(Q,left));r=tuple(map(Q,right));m2,h=Q(m2),Q(h)
    if l[0]>l[1] or r[0]>r[1] or m2<0 or h<=0:raise ValueError('INVALID_CHORD_DATA')
    if alpha is None:
        rad=m2*h*h/8
        return min(l[0],r[0])-rad,max(l[1],r[1])+rad
    alpha=Q(alpha)
    if not 0<=alpha<=1:raise ValueError('QUERY_OUTSIDE_CELL')
    rad=m2*h*h*alpha*(1-alpha)/2
    return (1-alpha)*l[0]+alpha*r[0]-rad,(1-alpha)*l[1]+alpha*r[1]+rad

def point_residual(T,x,slope,bg):
    tr=I.read(bg['Tr_K']);hh=I.read(bg['H'])
    if hh.lo<=0 or tr.lo<=0 or Q(T)<=0 or Q(x)<0:raise ValueError('NONPHYSICAL_PRIMITIVE_INPUT')
    gam=CN*tr.square().square()/hh*(I.point(x)/(B+I.point(x)))
    return I.point(slope)+2*I.point(T)-gam*(tr-I.point(T))

def evaluate_cell(native,bg):
    if native['binding']!=bg['source_query']:raise ValueError('FOREIGN_QUERY_BINDING')
    a,b,q,alpha=(Q(bg['binding'][k]) for k in ('a','b','q','alpha'))
    if not a<=q<=b or a==b or alpha!=(q-a)/(b-a):raise ValueError('INVALID_GEOMETRIC_ALPHA')
    bind=native['binding']
    for key,val in [('eta_left_hex',a),('eta_right_hex',b),('query_hex',q)]:
        if Q(float.fromhex(bind[key]))!=val:raise ValueError('GEOMETRIC_CLOCK_CHANGED')
    h=b-a; f=native['fields']['committed'];T=f['Tm_K'];x=f['xe']
    tl,rr=Q(T['left']),Q(T['right']);xl,xr=Q(x['left']),Q(x['right'])
    v,s=(rr-tl)/h,(xr-xl)/h
    for field,L,R,S in [(T,tl,rr,v),(x,xl,xr,s)]:
        if Q(field['slope'])!=S or Q(field['query'])!=L+alpha*(R-L):raise ValueError('AFFINE_IDENTITY_MISMATCH')
    if min(tl,rr)<=0 or min(xl,xr)<0:raise ValueError('NONPHYSICAL_AFFINE_INPUT')
    if any(n['phase']!='H_STEADY' for n in native['committed_nodes']):raise ValueError('UNAPPROVED_PHASE')
    for call in native['final_writer_calls']:
        if float.fromhex(call['fsR'])!=1 or float.fromhex(call['meR'])!=1:raise ValueError('CONSTANT_VARIATION_OUTSIDE_SCOPE')
    tt=I(min(tl,rr),max(tl,rr));xx=I(min(xl,xr),max(xl,xr))
    w=bg['whole_cell'];tr=I.read(w['Tr_K']);hh=I.read(w['H'])
    if hh.lo<=0 or tr.lo<=0:raise ValueError('INVALID_BACKGROUND')
    Apref=CN*tr.square().square()/hh
    den=B+xx; u=xx/den;ux=B/den.square();uxx=(-2*B)/(den.square()*den)
    alphaA=I.read(w['Gamma_bg_log_eta']);alphaAp=I.read(w['Gamma_bg_log_etaeta'])
    gam=Apref*u
    gp=Apref*(alphaA*u+ux*s)
    gpp=Apref*((alphaA.square()+alphaAp)*u+2*alphaA*ux*s+uxx*s*s)
    gap_naive=tr-tt
    dl=I.read(bg['points']['L']['Tr_K'])-tl
    dr=I.read(bg['points']['R']['Tr_K'])-rr
    gap_chord=I(min(dl.lo,dr.lo)-tr.hi*h*h/8,max(dl.hi,dr.hi))
    gap=gap_chord.intersect(gap_naive)
    naive=I.point(v)+2*tt-gam*gap_naive
    correlated=(I.point(v)+2*tt-gam*gap).intersect(naive)
    d2=-gpp*gap-2*gp*(I.read(w['Tr_eta_K'])-v)-gam*I.read(w['Tr_etaeta_K'])
    el=point_residual(tl,xl,v,bg['points']['L']);er=point_residual(rr,xr,v,bg['points']['R'])
    chord=I(*chord_bounds((el.lo,el.hi),(er.lo,er.hi),d2.absmax,h))
    tight=chord.intersect(correlated)
    query_chord=I(*chord_bounds((el.lo,el.hi),(er.lo,er.hi),d2.absmax,h,alpha)).intersect(tight)
    query_direct=point_residual(Q(T['query']),Q(x['query']),v,bg['points']['Q'])
    if not query_direct.subset(tight):
        # The independent direct evaluation can be slightly wider by rounding;
        # require nonempty intersection, never shrink the stored direct result.
        query_direct.intersect(tight)
    ratio=tr/tt;guard_margin=gap/tt-GUARD-Q(1,1<<52)*ratio
    out={'binding':bind,'alpha_exact':str(alpha),'h':str(h),'temperature_slope':str(v),'electron_slope':str(s),'phase':'H_STEADY_EXPLICIT_RECONSTRUCTION','units':'Kelvin per eta=ln(a)','physical_epsilon':None,'physical_defect':None,'physical_M2':None}
    for k,val in dict(gamma=gam,gamma_prime=gp,gamma_second=gpp,gap_naive=gap_naive,gap_correlated=gap,naive=naive,correlated=correlated,second_derivative=d2,endpoint_left=el,endpoint_right=er,chord=chord,tight=tight,query_chord=query_chord,query_direct=query_direct,guard_margin=guard_margin).items():out[k]=val.record()
    out['guard_on_reconstructed_path']='OFF_ROUNDING_MARGIN' if guard_margin.lo>0 else 'UNRESOLVED'
    out['bound_abs']=str(tight.absmax)
    return out
