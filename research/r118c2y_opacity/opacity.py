"""Positive moment-matched coarse closure with local escape consistent with its rates.
Not an exact coarse representation of the fine nonlocal collision operator.
"""
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import root
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r118c2x_writeback'))
from writeback import WingCorrection,L
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import complete_original_full_atomic,_original_escape_factors,FullOutgoingAtomicResult,HPC_EV_CM
from full_bianchi_hyrec.recoil.original_hyrec_native import populate_original_hyrec_diffusion
from full_bianchi_hyrec.trajectory.hmla_flrw import KB_NATIVE_EV_K

def positive_graph(A,e):
    A=np.asarray(A,dtype=L);e=np.asarray(e,dtype=L)
    if A.shape!=(len(e),len(e)) or np.max(abs(A-A.T))>1e-12*np.max(abs(A)):raise ValueError('graph symmetry')
    d=e[:,None]-e[None,:];off=A.copy();np.fill_diagonal(off,0)
    g=np.maximum(-off,0)
    fine=-np.sum(off*d*d)/2
    pos=np.sum(g*d*d)/2
    if fine<=0 or pos<=0:raise ValueError('energy form')
    fac=fine/pos;g*=fac
    return g,dict(positive_offdiag=int(np.count_nonzero(off>0)),positive_mass=float(off[off>0].sum()),negative_mass=float(-off[off<0].sum()),energy_form=float(fine),rescale=float(fac),form_defect=float(abs(np.sum(g*d*d)/2-fine)/fine))

def pair_terms(g,z,fp,v,x):
    f=fp+v/x
    if np.min(f)<0:raise ValueError('negative occupation')
    # Off-diagonal emission and extinction of total f; departure v=x(f-fp).
    # Frozen other-bin occupation yields exactly affine dependence on v_i.
    a=f/z
    gam=np.sum(g*((1+f)[None,:]/z[:,None]-a[None,:]),axis=1)
    em=x*np.sum(g*((1+fp)[:,None]*a[None,:]-fp[:,None]*(1+f)[None,:]/z[:,None]),axis=1)
    # Direct pair antisymmetry is the conservation oracle.
    F=x*g*((1+f)[:,None]*a[None,:]-a[:,None]*(1+f)[None,:])
    net=F.sum(axis=1)
    gross=x*np.sum(g*((1+f)[:,None]*a[None,:]+a[:,None]*(1+f)[None,:]))
    if np.min(gam)<0 or np.max(abs(em-gam*v-net))>1e-15*max(gross,L('1e-4900')):raise ValueError('pair source/extinction')
    return gam,em,net

class OpacityCorrection(WingCorrection):
    def __init__(self,table,graph,neutral0):
        super().__init__(table,graph,neutral0)
        self.coarse=[];self.info=[]
        for lo,hi,p,i,j,K in self.windows:
            eye=np.eye(hi-lo+1,dtype=L)
            B=eye[p.i]*(1-p.w[:,None])+eye[p.i+1]*p.w[:,None]
            d=B[i]-B[j];A=d.T@(K[:,None]*d)
            g,info=positive_graph(A,p.coarse)
            info.update(lo=lo,hi=hi,edges=len(i),max_positive=float(np.max(A-np.diag(np.diag(A)))),max_diagonal=float(np.max(np.diag(A))))
            self.coarse.append((lo,hi,g/self.neutral0));self.info.append(info)
    def solve(self,s,lam):
        if lam==0:return super().solve(s,lam)
        orig=complete_original_full_atomic(s);idx=self.idx;v0=orig.virtual_departures;scale=max(np.max(abs(v0[idx])),1e-30)
        diff=populate_original_hyrec_diffusion(np.column_stack((self.table.energy_eV,self.table.integrated_rates_s_inv.T)),float(s.Tm_eV/KB_NATIVE_EV_K))
        x=L(1-s.xHII);E=self.e;z=np.exp(-(E-L('10.198714553953742'))/L(s.Tm_eV));fp=1/np.expm1(E/L(s.Tr_eV))
        mode=L(s.H_s_inv)*L(8*np.pi)*(E/L(HPC_EV_CM))**3/L(s.nH_cgs)
        gamma0=np.asarray(s.Dtau,dtype=L)*mode/x
        def evaluate(v,weight):
            gamma=gamma0.copy();em=np.zeros(311,dtype=L);net=em.copy();old=em.copy();vv=s.Tvv.copy()
            for lo,hi,g in self.coarse:
                sl=slice(lo,hi+1)
                gam,src,new=pair_terms(g,z[sl],fp[sl],np.asarray(v[sl],dtype=L),x)
                up=np.asarray(diff.Aup_s_inv[lo:hi],dtype=L);dn=np.asarray(diff.Adn_s_inv[lo+1:hi+1],dtype=L)
                gamma[lo:hi]-=weight*up;gamma[lo+1:hi+1]-=weight*dn;gamma[sl]+=weight*gam
                vv[1,lo+1:hi+1]*=1-weight;vv[2,lo:hi]*=1-weight
                em[sl]=weight*src;net[sl]=new
                flux=up*v[lo:hi]-dn*v[lo+1:hi+1]
                old[lo:hi]-=flux;old[lo+1:hi+1]+=flux
            if np.min(gamma[idx])<=0:raise ValueError('nonpositive replaced opacity')
            tau=s.Dtau.copy();tau[idx]=np.asarray(gamma[idx]*x/mode[idx],float)
            pi,trans=_original_escape_factors(tau)
            vv[0,idx]=np.asarray(gamma[idx]/pi[idx],float)
            sv=s.sv.copy();sv[idx]=vv[0,idx]*float(x)*s.incoming_virtual[idx]*(1-pi[idx])+np.asarray(em[idx],float)
            A=np.zeros((313,313));A[:2,:2]=s.Trr;A[:2,2:]=s.Trv;A[2:,:2]=s.Tvr.T
            np.fill_diagonal(A[2:,2:],vv[0]);A[2+np.arange(1,311),2+np.arange(310)]=vv[1,1:];A[2+np.arange(310),2+np.arange(1,311)]=vv[2,:-1]
            rhs=np.r_[s.sr,sv];y=np.linalg.solve(A,rhs)
            return y,A,rhs,gamma,tau,vv,em,net,old,pi,trans
        y=np.zeros(len(idx));nfev=0
        for weight in (lam*.25,lam*.5,lam):
            def fun(y):
                v=v0.copy();v[idx]+=scale*y
                sol,*_=evaluate(v,weight)
                return y-(sol[2+idx]-v0[idx])/scale
            r=root(fun,y,method='hybr',options={'xtol':1e-10,'maxfev':200})
            nfev+=r.nfev
            if np.max(abs(fun(r.x)))>1e-8:raise ValueError(f'opacity root {r.message} {np.max(abs(fun(r.x)))}')
            y=r.x
        v=v0.copy();v[idx]+=scale*y
        sol,A,rhs,gamma,tau,vv,em,net,old,pi,trans=evaluate(v,lam)
        real,virt=sol[:2],sol[2:]
        # Recompute nonlinear rate terms at converged v (independent consistency).
        chk=evaluate(virt,lam);res=float(np.max(abs(chk[0]-sol))/max(np.max(abs(sol)),1e-300))
        neighbor=np.zeros(311);neighbor[1:]=virt[:-1]*vv[1,1:];neighbor[:-1]+=virt[1:]*vv[2,:-1]
        source=-(real@s.Tvr)-neighbor+np.asarray(em,float)
        active=tau>1e-30;out=s.incoming_virtual.copy()
        eq=source[active]/(float(x)*pi[active]*vv[0,active])
        out[active]+=(eq-s.incoming_virtual[active])*trans[active]
        # Direct transfer identity using independently constructed mode density.
        left=mode[idx]*(out[idx]-s.incoming_virtual[idx])
        right=source[idx]-gamma[idx]*virt[idx]
        face=float(np.sum(abs(left-right))/max(np.sum(abs(left)),np.sum(abs(right)),L('1e-4900')))
        if min(fp+out)<=0 or min(fp+virt/x)<=0 or res>1e-8 or face>1e-8:raise ValueError(f'opacity validation {res} {face}')
        ly=orig.outgoing_lyman.copy()
        # Identical real-state linear map, including both Lyman excitation ratios.
        ly[0]=real[1]/(3*float(x));ly[1:]*=real[0]/orig.real_departures[0]
        dx=orig.dxHII_dln_a+float((real-orig.real_departures)@s.Beta_s_inv/s.H_s_inv)
        q=lam*(net-old);heat=-q@E
        matrix=float(np.max(abs(A@sol-rhs))/max(np.max(abs(rhs)),1e-300))
        r=FullOutgoingAtomicResult(real_departures=real,virtual_departures=virt,outgoing_virtual=out,outgoing_lyman=ly,average_virtual=virt/float(x),dxHII_dln_a=dx,normalized_matrix_residual=matrix)
        return r,dict(correction=q,new=net,old=old,root_residual=res,nfev=nfev,heat=float(heat),face=face,tau_ratio_min=float(np.min(tau[idx]/s.Dtau[idx])),tau_ratio_max=float(np.max(tau[idx]/s.Dtau[idx])),gamma_min=float(np.min(gamma[idx])))

def energy_action_graph(A,e):
    """Positive nearest-neighbour graph with B E = A E for zero-row-sum A.

    For activity Galerkin projection with linear barycentric basis, each cut
    flow is nonnegative because the lifted prefix indicator decreases in E.
    Reject a non-admissible cut rather than clipping it.
    """
    A=np.asarray(A,dtype=L);e=np.asarray(e,dtype=L)
    n=len(e)
    if A.shape!=(n,n) or n<2 or np.any(np.diff(e)<=0) or np.max(abs(A-A.T))>1e-12*np.max(abs(A)):raise ValueError('energy graph shape')
    d=e[:,None]-e[None,:]
    off=A.copy();np.fill_diagonal(off,0)
    b=np.sum(-off*d,axis=1)
    flow=np.array([np.sum(-off[:k,k:]*(e[None,k:]-e[:k,None])) for k in range(1,n)],dtype=L)
    if np.min(flow)<0:raise ValueError('nonpositive coarse cut flow')
    w=flow/np.diff(e);g=np.zeros_like(A)
    g[np.arange(n-1),np.arange(1,n)]=w;g+=g.T.copy()
    bb=np.sum(g*d,axis=1)
    scale=max(np.sum(abs(b)),L('1e-4900'));defect=float(np.sum(abs(bb-b))/scale)
    fine=-np.sum(off*d*d)/2
    if fine<=0 or defect>1e-14:raise ValueError('energy action graph residual')
    return g,dict(min_cut=float(np.min(flow)),max_cut=float(np.max(flow)),energy_form=float(fine),form_defect=float(abs(np.sum(g*d*d)/2-fine)/fine),energy_vector_defect=defect,positive_offdiag=int(np.count_nonzero(off>0)),positive_mass=float(off[off>0].sum()),negative_mass=float(-off[off<0].sum()))

class EnergyActionCorrection(OpacityCorrection):
    def __init__(self,table,graph,neutral0):
        super().__init__(table,graph,neutral0)
        self.coarse=[];self.info=[]
        for lo,hi,p,i,j,K in self.windows:
            eye=np.eye(hi-lo+1,dtype=L)
            B=eye[p.i]*(1-p.w[:,None])+eye[p.i+1]*p.w[:,None]
            d=B[i]-B[j];A=d.T@(K[:,None]*d)
            g,info=energy_action_graph(A,p.coarse)
            info.update(lo=lo,hi=hi,edges=len(i),nearest_neighbor_edges=hi-lo)
            self.coarse.append((lo,hi,g/self.neutral0));self.info.append(info)
