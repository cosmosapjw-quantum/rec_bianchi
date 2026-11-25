"""Conservative selected-wing defect correction to the original FULL equations.

The original optical-depth closure is held fixed. This is not a replacement
for the entire FULL diffusion/2p operator, nor a second 2s reaction owner.
"""
import numpy as np
from dataclasses import replace
from scipy.optimize import root
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import complete_original_full_atomic,_original_escape_factors,FullOutgoingAtomicResult
from full_bianchi_hyrec.recoil.original_hyrec_native import populate_original_hyrec_diffusion
L=np.longdouble
class LinearProject:
    def __init__(self,coarse,fine):
        self.coarse=np.asarray(coarse,dtype=L);self.fine=np.asarray(fine,dtype=L)
        if np.any(np.diff(self.coarse)<=0) or np.min(self.fine)<self.coarse[0] or np.max(self.fine)>self.coarse[-1]:raise ValueError('projection domain')
        i=np.searchsorted(self.coarse,self.fine,side='right')-1
        self.i=np.minimum(i,len(self.coarse)-2);self.w=(self.fine-self.coarse[self.i])/(self.coarse[self.i+1]-self.coarse[self.i])
    def lift(self,x):
        x=np.asarray(x,dtype=L);return x[self.i]*(1-self.w)+x[self.i+1]*self.w
    def deposit(self,x):
        x=np.asarray(x,dtype=L);y=np.zeros(len(self.coarse),dtype=L)
        np.add.at(y,self.i,x*(1-self.w));np.add.at(y,self.i+1,x*self.w);return y
class WingCorrection:
    def __init__(self,table,graph,neutral0):
        self.table=table;self.e=np.asarray(table.energy_eV,dtype=L);self.neutral0=L(neutral0)
        self.windows=[];allidx=[]
        for lo,hi in ((133,139),(140,147)):
            co=self.e[lo:hi+1];E=graph['et'];i=graph['i'];j=graph['j'];mask=(E[i]>=co[0])&(E[i]<=co[-1])&(E[j]>=co[0])&(E[j]<=co[-1])
            ids=np.unique(np.r_[i[mask],j[mask]])
            if len(ids)==0:raise ValueError('no wing edges')
            g=LinearProject(co,E[ids]);self.windows.append((lo,hi,g,np.searchsorted(ids,i[mask]),np.searchsorted(ids,j[mask]),np.asarray(graph['K'][mask],dtype=L)))
            allidx.extend(range(lo,hi+1))
        self.idx=np.array(allidx)
    def action(self,snap,v,diff):
        x=L(1-snap.xHII);nh=L(snap.nH_cgs)*L(1e6);Tm=L(snap.Tm_eV);Tr=L(snap.Tr_eV)
        q=np.zeros(311,dtype=L);new=q.copy();old=q.copy();gross=L(0);energy=L(0)
        for lo,hi,p,i,j,K in self.windows:
            v0=np.asarray(v[lo:hi+1],dtype=L)
            f=1/np.expm1(p.coarse/Tr)+v0/x
            if np.min(f)<=0:raise ValueError('negative native occupation')
            z=np.exp(-(p.coarse-L('10.198714553953742'))/Tm)
            ac=f/(z*(1+f))
            af=p.lift(ac);zf=np.exp(-(p.fine-L('10.198714553953742'))/Tm)
            ff=af*zf/(1-af*zf)
            if np.min(ff)<=0 or np.any(af*zf>=1):raise ValueError('fine occupation domain')
            fac=K*(1+ff[i])*(1+ff[j])*x/self.neutral0 # density scale divided by nH
            F=fac*(af[j]-af[i]);d=np.zeros(len(p.fine),dtype=L)
            np.add.at(d,i,F);np.add.at(d,j,-F)
            new[lo:hi+1]=p.deposit(d)
            G=np.asarray(diff.Aup_s_inv[lo:hi],dtype=L)*v0[:-1]-np.asarray(diff.Adn_s_inv[lo+1:hi+1],dtype=L)*v0[1:]
            old[lo:hi]-=G;old[lo+1:hi+1]+=G
            gross+=np.sum(fac*(af[j]+af[i]))+np.sum(abs(G))
            energy+=F@(p.fine[i]-p.fine[j])
        q=new-old
        if abs(q.sum())>1e-15*max(gross,L('1e-4900')) or abs(new@self.e-energy)>1e-14*max(gross*10,L('1e-4900')):raise ValueError('projection ledger')
        return q,new,old,gross
    def solve(self,snap,lam):
        orig=complete_original_full_atomic(snap)
        if lam==0:return orig,dict(correction=np.zeros(311),new=np.zeros(311),old=np.zeros(311),gross=0.,root_residual=0.,nfev=0,heat=0.)
        # Form exact affine FULL Schur response to source columns on selected nodes.
        # Unit column amplitude is chosen near actual source to avoid cancellation.
        idx=self.idx;v0=orig.virtual_departures;scale=max(np.max(abs(v0[idx])),1e-30)
        # Assemble full real/virtual matrix directly, solve simultaneous RHS.
        A=np.zeros((313,313));A[:2,:2]=snap.Trr;A[:2,2:]=snap.Trv;A[2:,:2]=snap.Tvr.T
        np.fill_diagonal(A[2:,2:],snap.Tvv[0])
        A[2+np.arange(1,311),2+np.arange(310)]=snap.Tvv[1,1:]
        A[2+np.arange(310),2+np.arange(1,311)]=snap.Tvv[2,:-1]
        B=np.zeros((313,len(idx)));B[2+idx,np.arange(len(idx))]=1.
        resp=np.linalg.solve(A,B)
        # The source uses KB_NATIVE_EV_K; obtain actual T in the same convention.
        from full_bianchi_hyrec.trajectory.hmla_flrw import KB_NATIVE_EV_K
        diff=populate_original_hyrec_diffusion(np.column_stack((self.table.energy_eV,self.table.integrated_rates_s_inv.T)),float(snap.Tm_eV/KB_NATIVE_EV_K))
        def fun(y):
            v=v0.copy();v[idx]=v0[idx]+scale*y
            q,*_=self.action(snap,v,diff)
            return y-np.asarray(resp[2+idx]@np.asarray(q[idx]*lam,float)/scale,float)
        y=np.zeros(len(idx));nfev=0
        for weight in (.25,.5,1.):
            target=lam;lam=target*weight
            r=root(fun,y,method='hybr',options={'xtol':1e-10,'maxfev':200});nfev+=r.nfev
            if not np.isfinite(r.x).all() or np.max(abs(fun(r.x)))>1e-8:raise ValueError(f'FULL correction root {r.message} {np.max(abs(fun(r.x)))}')
            y=r.x;lam=target
        v=v0.copy();v[idx]+=scale*y
        q,new,old,gross=self.action(snap,v,diff);q*=lam
        corrected=replace(snap,sv=snap.sv+np.asarray(q,float))
        r=complete_original_full_atomic(corrected)
        pi,trans=_original_escape_factors(snap.Dtau)
        outgoing=r.outgoing_virtual.copy();active=idx
        if np.any(snap.Dtau[active]<=1e-30):raise ValueError('transparent selected face')
        outgoing[active]+=trans[active]*np.asarray(q[active],float)/((1-snap.xHII)*pi[active]*snap.Tvv[0,active])
        # Source correction enters both local average and escaping radiation.
        if np.min(1/np.expm1(self.e/L(snap.Tr_eV))+outgoing)<=0 or np.min(1/np.expm1(self.e/L(snap.Tr_eV))+r.average_virtual)<=0:raise ValueError('FULL occupation positivity')
        r=FullOutgoingAtomicResult(real_departures=r.real_departures,virtual_departures=r.virtual_departures,outgoing_virtual=outgoing,outgoing_lyman=r.outgoing_lyman,average_virtual=r.average_virtual,dxHII_dln_a=r.dxHII_dln_a,normalized_matrix_residual=r.normalized_matrix_residual)
        residual=float(np.max(abs(r.virtual_departures[idx]-v[idx]))/scale)
        if residual>1e-8 or r.normalized_matrix_residual>2e-10:raise ValueError('FULL corrected residual')
        return r,dict(correction=q,new=new,old=old,gross=float(gross),root_residual=residual,nfev=nfev,heat=float(-q@self.e))
