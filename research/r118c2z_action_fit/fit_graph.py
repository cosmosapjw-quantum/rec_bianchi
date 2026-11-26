"""Nonnegative cut-flow parameterization; fit dilute energy-action-exact graph."""
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r118c2y_opacity'))
from opacity import EnergyActionCorrection,energy_action_graph,L

def cut_fit(A,e,samples):
    A=np.asarray(A,dtype=L);e=np.asarray(e,dtype=L)
    n=len(e);baseline,info=energy_action_graph(A,e)
    cuts=baseline[np.arange(n-1),np.arange(1,n)]*np.diff(e)
    if np.min(cuts)<=0:raise ValueError('zero cut not represented')
    edges=[(i,j) for i in range(n) for j in range(i+2,n)]
    m=len(edges);C=np.zeros((n-1,m),dtype=L);mods=[]
    for k,(i,j) in enumerate(edges):
        cap=min(cuts[i:j]);C[i:j,k]=cap/cuts[i:j]
        g=np.zeros_like(A);g[i,j]=g[j,i]=cap/(e[j]-e[i])
        for k0 in range(i,j):g[k0,k0+1]=g[k0+1,k0]=-cap/(e[k0+1]-e[k0])
        mods.append(g)
    M=np.asarray(mods,dtype=L)
    if m==0:return baseline,info
    # Minimize worst per-sample relative L1 of binwise net action.
    # Additional nonnegative variables for absolute residual and epigraph.
    ns=len(samples);N=m+ns*n+1;mat=[];rhs=[]
    for row in C:
        a=np.zeros(N);a[:m]=row;mat.append(a);rhs.append(1.)
    for k,(F,q) in enumerate(samples):
        F=np.asarray(F,dtype=L);q=np.asarray(q,dtype=L)
        scale=np.sum(abs(q))
        if scale<=0:raise ValueError('zero action sample')
        v=((baseline*F).sum(axis=1)-q)/scale
        B=(M*F[None,:,:]).sum(axis=2).T/scale
        for i in range(n):
            for sign in (1.,-1.):
                a=np.zeros(N);a[:m]=sign*B[i];a[m+k*n+i]=-1
                mat.append(a);rhs.append(float(-sign*v[i]))
        a=np.zeros(N);a[m+k*n:m+(k+1)*n]=1;a[-1]=-1;mat.append(a);rhs.append(0.)
    obj=np.zeros(N);obj[-1]=1
    res=linprog(obj,A_ub=np.asarray(mat),b_ub=np.asarray(rhs),bounds=(0,None),method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
    if not res.success:raise ValueError(res.message)
    w=np.asarray(res.x[:m],dtype=L)
    if min(w)<0:raise ValueError('negative LP weight')
    occupancy=C@w;shrink=max(L(1),max(occupancy))
    # If the floating LP hits a cut at one plus roundoff, shrink all
    # nonlocal flows uniformly. Nearest-neighbour residual is then positive.
    w/=shrink
    if max(C@w)>1:w*=1-8*np.finfo(L).eps
    g=np.einsum('a,aij->ij',w,M)+baseline
    # Build residual cut exactly from nonlocal flows to avoid cancellation.
    residual=cuts*(1-C@w)
    g[np.arange(n-1),np.arange(1,n)]=residual/np.diff(e)
    g[np.arange(1,n),np.arange(n-1)]=residual/np.diff(e)
    if min(g.ravel())<0:raise ValueError('negative conductance')
    target=np.sum(baseline*(e[:,None]-e[None,:]),axis=1);actual=np.sum(g*(e[:,None]-e[None,:]),axis=1)
    defect=float(np.sum(abs(actual-target))/np.sum(abs(target)))
    if defect>1e-14:raise ValueError('cut residual')
    def errors(g):return [float(np.sum(abs((g*F).sum(axis=1)-q))/np.sum(abs(q))) for F,q in samples]
    # Dual certificate for the represented floating LP. Restrict the feasible
    # optimum to t<=baseline_worst; all residual epigraph variables <=t and
    # each nonlocal cut fraction <=1. Correct reduced-cost dual violations.
    y=np.minimum(np.asarray(res.ineqlin.marginals,dtype=L),L(0))
    Mlp=np.asarray(mat,dtype=L);blp=np.asarray(rhs,dtype=L)
    deficit=np.maximum(Mlp.T@y-np.asarray(obj,dtype=L),L(0))
    upper=np.r_[np.ones(m,dtype=L),np.full(ns*n+1,max(1.,max(errors(baseline))),dtype=L)]
    lower=blp@y-deficit@upper
    info.update(train_worst=max(errors(g)),baseline_worst=max(errors(baseline)),energy_vector_defect=defect,nonlocal_edges=int(np.count_nonzero(w)),lp_objective=float(res.fun),shrink=float(shrink),dual_lower=float(lower),dual_gap=float(max(errors(g))-lower),dual_deficit=float(np.max(deficit)))
    return g,info

class FitCorrection(EnergyActionCorrection):
    def __init__(self,table,graph,neutral0,fit):
        super().__init__(table,graph,neutral0)
        self.coarse=[(lo,hi,np.asarray(g,dtype=L)/self.neutral0) for (lo,hi,*_),g in zip(self.windows,fit)]
        if len(self.coarse)!=len(self.windows):raise ValueError('fit shape')
