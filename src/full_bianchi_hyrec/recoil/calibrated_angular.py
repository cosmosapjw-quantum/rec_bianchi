"""Positive angular-frequency event measure at an explicit material bath.
Angular mass is integrated into the available dot-product levels, NOT
evaluated from a sign-indefinite truncated Legendre series. Each frequency
node pair is symmetrically balanced to preserve its isotropic rate.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy.special import eval_legendre
from .calibrated_source import _job,owner_cells,PCC

def compile_angular(bath,levels=(1,4),workers=4):
    levels=tuple(levels)
    if not levels or any(n not in (1,2,4,8) for n in levels) or not 1<=workers<=4:raise ValueError("invalid angular compilation")
    jobs=[(i,j,bath,levels,True) for i in range(17) for j in range(i,35)]
    with ProcessPoolExecutor(max_workers=workers) as pool:rows=list(pool.map(_job,jobs))
    assert len(rows)==459
    return dict(pairs=np.array([r[:2] for r in rows]),bounds=owner_cells(),nu0=PCC.nu_abs,dnu=PCC.dnu,z0=bath.z0,T_m_K=bath.T_m_K,n_1s_m3=bath.n_1s_m3,max_marginal=max(r[4] for r in rows),max_same_sym=max(r[5] for r in rows),direct=np.sum([r[3] for r in rows],axis=0),mu=np.concatenate([r[6][0] for r in rows]),weight=np.concatenate([r[6][1] for r in rows]),offset=np.r_[0,np.cumsum([len(r[6][0]) for r in rows])],**{f'Q{n}':np.array([r[2][n] for r in rows]) for n in levels},**{f'K{n}':np.concatenate([r[6][2][n] for r in rows]) for n in levels})

class AngularPlan:
    def __init__(self,d,w):
        d=np.asarray(d,float);w=np.asarray(w,float)
        if d.ndim!=2 or d.shape[1]!=3 or w.shape!=(len(d),) or np.any(w<=0) or np.any(~np.isfinite(d)) or np.max(abs(np.linalg.norm(d,axis=1)-1))>2e-12 or abs(w.sum()-1)>2e-12:raise ValueError("invalid angular quadrature")
        self.d=d;self.w=w;self.dot=np.clip(np.round(d@d.T,13),-1,1)
        self.mu,self.index=np.unique(self.dot,return_inverse=True)
        self.index=self.index.reshape(self.dot.shape);self.ww=w[:,None]*w[None,:]
        self.volume=np.bincount(self.index.ravel(),weights=self.ww.ravel())
        if self.mu[0]!=-1 or self.mu[-1]!=1:raise ValueError("antipodal angular grid required")
        opposite=np.argmin(self.dot,axis=1)
        if not np.all(self.dot[np.arange(len(w)),opposite]==-1) or not np.array_equal(opposite[opposite],np.arange(len(w))) or np.max(abs(w-w[opposite]))>2e-14:
            raise ValueError("equal-weight antipodal partners required")
        self.forward=np.diag(w)
        self.backward=np.zeros_like(self.ww);self.backward[np.arange(len(w)),opposite]=w
        self.backward=(self.backward+self.backward.T)*.5
        self.last_correction=0.
    def lift(self,mu,mass):
        mu=np.asarray(mu,float);mass=np.asarray(mass,float)
        if mu.shape!=mass.shape or np.any(mass<0) or np.any(~np.isfinite(mass)) or np.any(abs(mu)>1):raise ValueError("invalid positive angular mass")
        total=mass.sum()
        if total==0:self.last_correction=0.;return np.zeros_like(self.ww),0.
        m=mass/total;l=np.clip(np.searchsorted(self.mu,mu,side='right')-1,0,len(self.mu)-2);r=l+1
        t=np.clip((mu-self.mu[l])/(self.mu[r]-self.mu[l]),0,1)
        bins=np.bincount(l,weights=m*(1-t),minlength=len(self.mu))+np.bincount(r,weights=m*t,minlength=len(self.mu))
        G=self.ww*(bins/self.volume)[self.index]
        # G is symmetric to roundoff; make reciprocity bit-identical.
        G=(G+G.T)*.5
        d=np.ones(len(self.w));err=float('inf')
        for _ in range(600):
            row=d*(G@d);err=np.max(abs(row/self.w-1))
            if err<2e-13:break
            if np.any(row<=0):raise ValueError("angular lift empty row")
            d*=np.sqrt(self.w/row)
        else:
            y=np.log(d)
            for _ in range(80):
                d=np.exp(y);row=d*(G@d);r=np.log(row/self.w);err=np.max(abs(row/self.w-1))
                if err<2e-13:break
                J=np.eye(len(d))+G*d[None,:]/(G@d)[:,None]
                dy=np.linalg.lstsq(J,-r,rcond=1e-14)[0]
                for a in 2.**(-np.arange(20)):
                    yy=y+a*dy
                    if np.max(abs(yy))>300:continue
                    dd=np.exp(yy);rr=dd*(G@dd)
                    if np.all(rr>0) and np.max(abs(np.log(rr/self.w)))<np.max(abs(r)):y=yy;break
                else:raise ValueError("angular balance Newton stalled")
            else:raise ValueError("angular balance cap")
        G=G*(d[:,None]*d[None,:]);G=(G+G.T)*.5
        G/=G.sum()
        # Convex correction of the global P1 moment, not a claim of exact
        # angular-kernel recovery. Both endpoint couplings have the same
        # row marginal and are positive and reciprocal.
        target=float(m@mu);current=float(np.sum(G*self.dot))
        self.last_correction=0.
        if abs(target-current)>5e-15:
            extreme=1. if target>current else -1.
            lam=(target-current)/(extreme-current)
            if not 0.<=lam<=1.:raise ValueError("infeasible first angular moment")
            G=(1.-lam)*G+lam*(self.forward if extreme==1. else self.backward)
            self.last_correction=lam
        G=(G+G.T)*.5
        err=float(np.max(abs(G.sum(axis=1)/self.w-1)))
        if err>5e-13 or abs(np.sum(G*self.dot)-target)>5e-13:raise ValueError("angular moment correction residual")
        return G*total,err

def angular_lift(mu,mass,d,w):
    return AngularPlan(d,w).lift(mu,mass)

def assemble(data,sub,d,w):
    """Return unique undirected edges in frequency-major order. The
    same-node same-angle event is null and omitted; every other event
    retains positive conductance. Angular moments report closure error."""
    plan=AngularPlan(d,w);na=len(w);p=sub+1;nf=35*p
    src=data[f'K{sub}'];offset=data['offset'];rows=[];maximum=0.
    delta=np.zeros(5);gross=np.zeros(5);worst=np.zeros(5);correction=0.;max_correction=0.
    for index,(i,j) in enumerate(data['pairs']):
        sl=slice(offset[index],offset[index+1]);mu=data['mu'][sl];aw=data['weight'][sl]
        for v in range(p):
            for u in range(p):
                I=int(i)*p+v;J=int(j)*p+u
                if I>J:continue
                m=aw*src[sl,v,u]
                if m.sum()==0:continue
                G,err=plan.lift(mu,m);maximum=max(maximum,err)
                correction+=plan.last_correction*m.sum();max_correction=max(max_correction,plan.last_correction)
                for l in range(5):
                    exact=eval_legendre(l,mu)@m;approx=np.sum(G*eval_legendre(l,plan.dot))
                    gap=abs(approx-exact);delta[l]+=gap;gross[l]+=m.sum()
                    worst[l]=max(worst[l],gap/m.sum())
                ai,aj=np.nonzero(G>0)
                if I==J:sel=ai<aj;ai=ai[sel];aj=aj[sel]
                if len(ai):rows.append((I*na+ai,J*na+aj,G[ai,aj]))
    i=np.concatenate([r[0] for r in rows]).astype(np.uint32);j=np.concatenate([r[1] for r in rows]).astype(np.uint32);K=np.concatenate([r[2] for r in rows])
    order=np.lexsort((j,i));i=i[order];j=j[order];K=K[order]
    assert np.all(i<j) and np.all((i[1:]!=i[:-1])|(j[1:]!=j[:-1]))
    return dict(i=i,j=j,K=K,max_row_defect=maximum,moment_l1_relative=(delta/np.maximum(gross,1e-300)),moment_worst=worst,frequency_nodes=nf,angles=na,correction_mass_fraction=correction/gross[0],max_block_correction=max_correction)
