"""Fixed-reference-measure target-grid research; never a physical provider.

Reuses original table loading, interpolation weights, paired APIs, and COM
apply/JVP. No old study tests, time integrator, workflow or source mutation.
New common measure/state choices are manufactured and are not PR79's inputs.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from pathlib import Path
import sys
import numpy as np
import mpmath as mp

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'docs/research/rec_multi_bin_affinity_20260907'))
import study as previous

LEVELS=tuple(range(6))
POWERS=(0,1,2,4)
MU0=8.0  # m^-3; manufactured normalization, not physical photon phase space.
NH=8.0   # hydrogen density, m^-3; fixed instantaneous source, no evolution.
CLAIM='NO_PASS_REC_PHYSICAL_SPLIT'
PINS=dict(previous.PINS, **{
    'docs/research/rec_multi_bin_affinity_20260907/study.py':'f1ad5926de6090e8317961c6cc58914cfd5c8ba3'
})


@dataclass(frozen=True)
class Case:
    name: str
    coeff: tuple[float,...]  # chi(u), ascending powers; same continuum input at every grid.
    eta: float


@dataclass(frozen=True)
class Direction:
    name: str
    coeff: tuple[float,...]  # delta chi(u), not independent directions at each grid.
    du: float=0.0
    dg: float=0.0
    ds: float=0.0
    dn: float=0.0


CASES=(Case('affine_balance',(.5,1.),0.),
       Case('curved',(.5,9/8,-1/8),-1/8),
       Case('odd_null',(.5,7/8,3/8,-1/4),0.))
DIRECTIONS=(Direction('photon',(1/16,5/32,-1/8)),
            Direction('mixed',(1/16,5/32,-1/8),1/64,-1/32,1/8,2.))
ZERO=Direction('zero',(0.,))


def polynomial(coeff,u):
    return np.polynomial.polynomial.polyval(u,coeff)


def nodes(level: int) -> np.ndarray:
    if isinstance(level,(bool,np.bool_)) or not isinstance(level,(int,np.integer)) or not 0<=level<=8:
        raise ValueError('integer refinement level 0..8 required')
    result=previous.U.copy()
    for _ in range(int(level)):
        fine=np.empty(2*len(result)-1)
        fine[::2]=result;fine[1::2]=(result[:-1]+result[1:])/2
        result=fine
    return result


def measure(u: np.ndarray) -> np.ndarray:
    """mu_i = integral hat_i(u) 8*(1+u^2) du, integrated exactly in algebra."""
    x=np.asarray(u)
    if x.dtype.kind not in 'fiu' or x.ndim!=1 or len(x)<2:
        raise ValueError('real one-dimensional grid required')
    x=x.astype(float)
    if not np.isfinite(x).all() or x[0]<=0 or x[-1]>=1 or np.any(np.diff(x)<=0):
        raise ValueError('finite increasing grid strictly inside (0,1) required')
    mu=np.zeros(len(x))
    for j,(a,b) in enumerate(zip(x[:-1],x[1:])):
        h=b-a
        mu[j]+=MU0*h*((1+a*a)/2+a*h/3+h*h/12)
        mu[j+1]+=MU0*h*((1+a*a)/2+2*a*h/3+h*h/4)
    return mu


def plan(t,u,mu,B):
    return previous.COMSourceDepositionPlan(mu,previous.E21_J*u,
        previous.E21_J*t['us'],B,np.array([1.]),np.array([[0.,0.,1.]]),
        'manufactured_common_8_times_1_plus_u_squared_du',
        'manufactured_nested_piecewise_linear_energy_hats')


def grid(t,level):
    u=nodes(level);mu=measure(u);B=previous.weights(u,t['us'])
    return {'u':u,'mu':mu,'B':B,'L':previous.weights(u,t['us'],True),
            'D':B[:,:t['n']]+B[:,t['n']:], 'h':float(np.diff(u).max()),
            'level':int(level),'plan':plan(t,u,mu,B)}


def populations(case):
    rho=math.exp(case.eta-2);xg=(9/16)/(1+rho)
    return rho*xg,xg


def fields(case,direction,u):
    chi=polynomial(case.coeff,u);dc=polynomial(direction.coeff,u)
    if np.any(chi<=0) or not np.isfinite(chi).all():
        raise ValueError('positive finite chi required')
    f=1/np.expm1(chi);y=np.log(f)
    return chi,f,y,dc,-f*(1+f)*dc,-(1+f)*dc


def psi(u):
    x=np.asarray(u,dtype=float)
    return np.array([x**p for p in POWERS])


def pair_rates(t,case,direction,legs,dlegs):
    xu,xg=populations(case);n=t['n']
    F=np.empty(n);R=np.empty(n);gamma=np.empty(n);dgamma=np.empty(n)
    for b in range(n):
        a=float(t['normalized'][b])
        pair=previous.PhysicalTwoPhotonRamanBin('two_photon',a,
            previous.E21_J/previous.H_PLANCK,
            previous.E21_J*t['us'][n+b]/previous.H_PLANCK,
            previous.E21_J*t['us'][b]/previous.H_PLANCK,xu,xg,1.)
        ft,fc=float(legs[b]),float(legs[n+b])
        F[b],R[b]=pair.paired_rates(companion_occupation=fc,tracked_occupation=ft)
        gamma[b]=pair.net_action(fc,ft)
        dgamma[b]=pair.jvp(companion_occupation=fc,tracked_occupation=ft,
            d_integrated_rate_s_inv=direction.ds*a,d_upper_population=direction.du,
            d_ground_population=direction.dg,d_companion_occupation=float(dlegs[n+b]),
            d_tracked_occupation=float(dlegs[b]))
    return F,R,gamma,dgamma


def direct(t,case,direction):
    """Same original API with continuum field sampled at atomic-bin energies.

    Removes target interpolation only. This is a per-table reference, not an
    independent validation of the original API or of atomic quadrature.
    """
    _,legs,_,_,dlegs,_=fields(case,direction,t['us'])
    F,R,gamma,dgamma=pair_rates(t,case,direction,legs,dlegs)
    n=t['n'];weights=psi(t['us'][:n])+psi(t['us'][n:])
    return {'F':F,'R':R,'gamma':gamma,'dgamma':dgamma,'legs':legs,
            'M':weights@gamma,'dM':weights@dgamma,'weights':weights}


def evaluate(t,g,case,direction,kind='chi'):
    if kind not in ('chi','log_control'):
        raise ValueError('unknown research read operator')
    chi,f,y,dc,_,dy=fields(case,direction,g['u'])
    if kind=='chi':
        q=g['B'].T@chi
        legs=1/np.expm1(q)
        dlegs=-legs*(1+legs)*(g['B'].T@dc)
    else:
        legs=np.exp(g['L'].T@y)
        dlegs=legs*(g['L'].T@dy)
    F,R,gamma,dgamma=pair_rates(t,case,direction,legs,dlegs)
    C=g['plan'].apply(np.r_[gamma,gamma],NH)[:,0]
    dC=g['plan'].jvp(np.r_[gamma,gamma],np.r_[dgamma,dgamma],NH,direction.dn)[:,0]
    beta=g['mu']/NH
    weights=psi(g['u'])*beta
    M=weights@C
    dM=weights@(dC-C*direction.dn/NH)
    xu,xg=populations(case);n=t['n']
    asc=math.log(xu/xg)+g['D'].T@chi
    dasc=direction.du/xu-direction.dg/xg+g['D'].T@dc
    aread=math.log(xu/xg)+np.log1p(1/legs[:n])+np.log1p(1/legs[n:])
    S=math.fsum(gamma);dS=math.fsum(dgamma)
    sigma=math.fsum(gamma*asc)
    dsigma=math.fsum(dgamma*asc+gamma*dasc)
    vector=np.r_[C,M,sigma];jvp=np.r_[dC,dM,dsigma]
    if not np.isfinite(np.r_[vector,jvp]).all():
        raise FloatingPointError('nonfinite research source/JVP')
    return dict(F=F,R=R,gamma=gamma,dgamma=dgamma,legs=legs,C=C,dC=dC,M=M,dM=dM,
        S=S,dS=dS,sigma=sigma,sigma_from_nodal=S*math.log(xu/xg)+(beta*chi)@C,
        affinity_defect=aread-asc,vector=vector,jvp=jvp)


def split_errors(t,g,out,reference):
    """Exact read/scatter/cross decomposition; neither leg is counted twice."""
    s0=reference['weights'];sn=psi(g['u'])@g['D'];ds=sn-s0
    dg=out['gamma']-reference['gamma'];ddg=out['dgamma']-reference['dgamma']
    return {'read':s0@dg,'scatter':ds@reference['gamma'],'cross':ds@dg,
            'dread':s0@ddg,'dscatter':ds@reference['dgamma'],'dcross':ds@ddg}


def coefficient_bound(coeff,order=0):
    # |u|<=1. Loose global polynomial derivative bound; not fitted to results.
    return sum(abs(c)*math.factorial(j)/math.factorial(j-order)
               for j,c in enumerate(coeff) if j>=order)


def bounds(t,case,direction,h):
    """Conditional O(h^2) envelope for chi reads, fixed bins and smooth fixtures."""
    fmax=1/math.expm1(.5)  # All declared continuum/nodal chi >=1/2.
    L1=fmax*(1+fmax);L2=L1*(1+2*fmax)
    Hchi=coefficient_bound(case.coeff,2)
    D0=coefficient_bound(direction.coeff);D2=coefficient_bound(direction.coeff,2)
    ef=L1*Hchi*h*h/8
    edf=(L1*D2+L2*Hchi*D0)*h*h/8
    xu,xg=populations(case);a=math.fsum(t['normalized'])
    K=xu*(1+fmax)+xg*fmax
    P=xu*(1+fmax)**2+xg*fmax**2
    KD=abs(direction.du)*(1+fmax)+abs(direction.dg)*fmax
    eg=a*2*K*ef
    edg=a*(2*abs(direction.ds)*K*ef+2*KD*ef+2*K*edf+2*abs(xu-xg)*L1*D0*ef)
    dactivity=a*(abs(direction.ds)*P+abs(direction.du)*(1+fmax)**2
                 +abs(direction.dg)*fmax**2+2*K*L1*D0)
    Hpsi=np.array([0.,0.,2.,12.])
    return {'M':2*eg+a*P*Hpsi*h*h/4,
            'dM':2*edg+dactivity*Hpsi*h*h/4,
            'assumptions':'chi>=1/2; fixed atomic bins; u in [epsilon,1-epsilon]; fixed B,mu'}


def state_bound(case,h):
    F=1/math.expm1(.5);L1=F*(1+F);L2=L1*(1+2*F)
    C1=coefficient_bound(case.coeff,1);C2=coefficient_bound(case.coeff,2)
    F2=L2*C1*C1+L1*C2
    a,b=previous.U[0],previous.U[-1]
    mass=MU0*((b-a)+(b**3-a**3)/3)
    return mass*h*h/8*np.array([F2,F2+2*L1*C1])


def _mp_poly(coeff,u):
    result=mp.mpf(0)
    for c in reversed(coeff):result=result*u+mp.mpf(float(c))
    return result


def state_reference(case,dps=80):
    with mp.workdps(dps):
        points=[mp.mpf(float(x)) for x in previous.U]
        return [mp.quad(lambda u:mp.mpf(MU0)*(1+u*u)*u**p/mp.expm1(_mp_poly(case.coeff,u)),points)
                for p in (0,1)]


def independent(t,g,case,direction,kind,dps=80,power=32):
    """Independent nonlinear primal finite differences, including actual COM C.

    The reference lifts fixed binary64 weights/rates, shares declared polynomial
    input data, and calls no original paired/COM API or analytic JVP.
    """
    if kind not in ('chi','log_control'):raise ValueError('read kind')
    n=t['n'];mat=g['B'] if kind=='chi' else g['L']
    reads=[[(int(i),float(mat[i,s])) for i in np.flatnonzero(mat[:,s])] for s in range(2*n)]
    scatter=[[(int(i),float(g['B'][i,s])) for i in np.flatnonzero(g['B'][:,s])] for s in range(2*n)]
    xu0,xg0=populations(case)
    with mp.workdps(dps):
        u=[mp.mpf(float(x)) for x in g['u']];mu=[mp.mpf(float(x)) for x in g['mu']]
        aa=[mp.mpf(float(x)) for x in t['normalized']]
        def primal(e):
            xu=mp.mpf(xu0)+e*mp.mpf(direction.du)
            xg=mp.mpf(xg0)+e*mp.mpf(direction.dg)
            scale=1+e*mp.mpf(direction.ds);nh=mp.mpf(NH)+e*mp.mpf(direction.dn)
            chi=[_mp_poly(case.coeff,x)+e*_mp_poly(direction.coeff,x) for x in u]
            y=[-mp.log(mp.expm1(x)) for x in chi]
            values=chi if kind=='chi' else y
            q=[mp.fsum(mp.mpf(w)*values[i] for i,w in support) for support in reads]
            legs=[1/mp.expm1(x) if kind=='chi' else mp.exp(x) for x in q]
            gamma=[aa[b]*scale*(xu*(1+legs[b])*(1+legs[n+b])-xg*legs[b]*legs[n+b]) for b in range(n)]
            C=[mp.mpf(0) for _ in u]
            for s,support in enumerate(scatter):
                for i,w in support:C[i]+=nh*mp.mpf(w)*gamma[s%n]/mu[i]
            M=[mp.fsum(mu[i]/nh*u[i]**p*C[i] for i in range(len(u))) for p in POWERS]
            sigma=mp.fsum(gamma)*mp.log(xu/xg)+mp.fsum(mu[i]/nh*chi[i]*C[i] for i in range(len(u)))
            return C+M+[sigma]
        h=mp.mpf(2)**(-power)
        p=primal(mp.mpf(0));plus=primal(h);minus=primal(-h)
        return p,[(a-b)/(2*h) for a,b in zip(plus,minus)]
