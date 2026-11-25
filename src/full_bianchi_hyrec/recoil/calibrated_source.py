"""State-calibrated positive COM-KHW source compiler.
Fixed physical frequency grid anchored at the original 3000 K width.
Use explicit actual T and ground-state n1s. No module-global mutation,
no reference spectrum/trajectory or external HyRec runtime.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from scipy.special import kve
from . import pair_cell_conductance as PCC, exterior_interface as EX, same_cell_regular as SC, far_exterior as FAR
from .scalar_com_khw import conditional_full_scalar_mean_amplitude_squared
from scipy.constants import h,k,c

@dataclass(frozen=True)
class Bath:
    T_m_K: float
    n_1s_m3: float
    def __post_init__(self):
        if not (math.isfinite(self.T_m_K) and 2000<=self.T_m_K<=5000 and math.isfinite(self.n_1s_m3) and self.n_1s_m3>=0):
            raise ValueError("bounded calibrated H I source T=2000..5000 K, n1s>=0")
    @property
    def z0(self):return math.exp(-h*PCC.nu_abs/(k*self.T_m_K))

def owner_cells():
    return np.asarray(EX.interior_cells()+EX.EXTERIOR_CELLS+FAR.FAR_CELLS,float)

def density(nt,ns,mu,bath):
    """Positive physical integrand in fixed x=(nu-nu_abs)/dnu_ref.
    At 3000 K, n1s=250 cm^-3 equals the original production integrand.
    All bath-dependent thermal factors explicitly evaluated.
    """
    M=PCC.M;T=bath.T_m_K;beta=1/(k*T)
    den=np.sqrt(ns*ns+nt*nt-2*ns*nt*mu);Q=h/c*den
    a_s=(ns-nt*mu)/den;b_s=np.sqrt(np.maximum(0,1-a_s*a_s))
    P=M*h*(ns-nt)/Q-Q/2
    A=PCC.nu_int-ns+ns*P*a_s/(M*c)+h*ns*ns/(2*M*c*c)
    B=ns*math.sqrt(M*k*T)*b_s/(M*c)
    a_t=(ns*mu-nt)/den
    C=PCC.nu_int+nt-nt*P*a_t/(M*c)+h*nt*nt/(2*M*c*c)
    amp=conditional_full_scalar_mean_amplitude_squared(A,B,C,-B)
    ks=h*ns/(M*c*c);kt=h*nt/(M*c*c);delta=ks-kt;transfer2=2*ks*kt*(1-mu)
    q=np.sqrt(delta*delta+transfer2);root=np.sqrt(transfer2)/q
    sq=np.sqrt(1+transfer2/4);minus=transfer2/4/(sq+1)
    gminus=minus/root+(delta/q)**2/(root*(1+root))-delta/2
    zeta=M*c*c/(k*T);K=float(kve(2,zeta))
    if not math.isfinite(K) or K<=0:K=math.sqrt(math.pi/(2*zeta))*(1+15/(8*zeta)+105/(128*zeta**2)-945/(3072*zeta**3))
    logS=-zeta*gminus-np.log(2*q*K)
    scale=bath.n_1s_m3*c*PCC.sigT*PCC.area_int*h*PCC.dnu/(M*c*c)
    out=scale*np.exp(-beta*h*ns+logS)*ns*nt*amp
    if np.any(~np.isfinite(out)) or np.any(out<0):raise ValueError("invalid calibrated source density")
    return out

# R118-C2E positive source quadrature, BASS 8a92aaa, fixed physical grid.
def angular(par):
 z,w=PCC.leggauss(par['ob']);c=.5*np.sqrt(.005)*(z+1);cw=.5*np.sqrt(.005)*w
 z,w=PCC.leggauss(par['om']);mu=.5*(.999+.99)*z+.5*(.999-.99);mw=.25*(.999+.99)*w
 z,w=PCC.leggauss(par['of']);t=.5*np.sqrt(.001)*(z+1);tw=.5*np.sqrt(.001)*w
 a=np.r_[-1+2*c*c,mu,1-t*t];b=np.r_[2*c*cw,mw,t*tw];return a,b
def uv_nodes(a,b,par,half):
 at,bt=a;as_,bs=b;lo=(at+as_)/2;hi=(bt+bs)/2;delta=PCC.gamma/PCC.dnu
 breaks=[lo,hi,(at+bs)/2,(bt+as_)/2]
 if lo<0<hi:breaks += [max(lo,-half),0,min(hi,half)]
 breaks=sorted(set(round(float(v),15) for v in breaks if lo-1e-14<=v<=hi+1e-14))
 U=[];W=[]
 for l,r in zip(breaks,breaks[1:]):
  if r-l<1e-14:continue
  if lo<0<hi and abs(l)<=half+1e-14 and abs(r)<=half+1e-14:
   z,w=PCC.leggauss(par['nl']);l1=np.arctan(l/delta);r1=np.arctan(r/delta);t=(l1+r1)/2+(r1-l1)*z/2
   u=delta*np.tan(t);ww=(r1-l1)*w/2*delta/np.cos(t)**2
  else:z,w=PCC.leggauss(par['nb']);u=(l+r)/2+(r-l)*z/2;ww=(r-l)*w/2
  U.extend(u);W.extend(ww)
 u=np.array(U)[:,None];w=np.array(W)[:,None];vmin=np.maximum(at-u,u-bs);vmax=np.minimum(bt-u,u-as_)
 z,wv=PCC.leggauss(par['nv']);v=(vmin+vmax)/2+(vmax-vmin)*z/2
 ww=2*w*(vmax-vmin)/2*wv
 assert np.all(ww>=0)
 return (PCC.nu_abs+PCC.dnu*(u+v)).ravel(),(PCC.nu_abs+PCC.dnu*(u-v)).ravel(),ww.ravel()
def tensor_nodes(a,b,n):
 z,w=PCC.leggauss(n)
 def get(a):return PCC.nu_abs+PCC.dnu*((a[0]+a[1])/2+(a[1]-a[0])*z/2),(a[1]-a[0])*w/2
 nt,wt=get(a);ns,ws=get(b);return np.broadcast_to(nt[:,None],(n,n)).ravel(),np.broadcast_to(ns[None,:],(n,n)).ravel(),(wt[:,None]*ws[None,:]).ravel()

def _block(nt,ns,mu,w,i,j,bath,levels,bounds):
    # W/z0 evaluated directly as a finite rate conductance; f in physical
    # occupation and normalized activity a=f/(z_rel(1+f)) for point states.
    D=density(nt,ns,mu,bath)*w/bath.z0
    shape=D.shape;batch=shape[0]
    xt=np.broadcast_to((nt-PCC.nu_abs)/PCC.dnu,shape).reshape(batch,-1)
    xs=np.broadcast_to((ns-PCC.nu_abs)/PCC.dnu,shape).reshape(batch,-1);D=D.reshape(batch,-1)
    l,r=bounds[i];a,b=bounds[j];t=(xt-l)/(r-l);s=(xs-a)/(b-a)
    if min(t.min(),s.min())<0 or max(t.max(),s.max())>1:raise ValueError("source quadrature outside owner cell")
    out={}
    for n in levels:
        N=n+1;it=np.minimum((n*t).astype(int),n-1);js=np.minimum((n*s).astype(int),n-1);u=n*t-it;v=n*s-js
        hats=([1-np.maximum(u,v),np.maximum(v-u,0),np.maximum(u-v,0),np.minimum(u,v)] if i==j else [(1-u)*(1-v),(1-u)*v,u*(1-v),u*v])
        index=(np.arange(batch)[:,None]*N*N+it*N+js).ravel();Q=np.zeros(batch*N*N)
        for off,hat in zip([0,1,N,N+1],hats):Q+=np.bincount(index+off,weights=(D*hat).ravel(),minlength=len(Q))
        out[n]=Q.reshape(batch,N,N)
    raw=np.stack([D.sum(axis=1),np.sum(D*xt,axis=1),np.sum(D*xs,axis=1)],axis=1)
    # independent direct source energy action: hot, cold, and narrow Bose.
    # Thermal activity evaluated analytically to avoid near-null cancellation.
    T=bath.T_m_K;zr_t=np.exp(-h*PCC.dnu*xt/(k*T));zr_s=np.exp(-h*PCC.dnu*xs/(k*T))
    direct=[]
    for kind in (0,1,2):
        if kind<2:
            Tr=T*(1+.001*(1 if kind==0 else -1))
            yt=h*(PCC.nu_abs+PCC.dnu*xt)/(k*Tr);ys=h*(PCC.nu_abs+PCC.dnu*xs)/(k*Tr)
            ft=1/np.expm1(yt);fs=1/np.expm1(ys)
            at=ft/(zr_t*(1+ft));aa=fs/(zr_s*(1+fs))
        else:
            at=.3*(1+.25*np.exp(-.5*((xt-1.2)/.22)**2));aa=.3*(1+.25*np.exp(-.5*((xs-1.2)/.22)**2))
            ft=at*zr_t/(1-at*zr_t);fs=aa*zr_s/(1-aa*zr_s)
        direct.append(np.sum(D*(1+ft)*(1+fs)*(aa-at)*(xt-xs),axis=1))
    return out,raw,np.stack(direct,axis=1)

def _job(arg):
    i,j,bath,levels=arg;bounds=owner_cells()
    def batch(mu,nodes,I,J):
        nt,ns,w=nodes;parts=[_block(nt[None,:],ns[None,:],mu[q:q+8,None],w,I,J,bath,levels,bounds) for q in range(0,len(mu),8)]
        return {n:np.concatenate([v[0][n] for v in parts]) for n in levels},np.concatenate([v[1] for v in parts]),np.concatenate([v[2] for v in parts])
    if i==j:
        par=SC.PRODUCTION_LANE;mu,w=angular(par);u,wu=SC._u_rule(i,par['nu'],par['nu_pole']);y,wy=PCC.leggauss(par['ny']);a,b=bounds[i]
        half=np.minimum(u-a,b-u)[None,:,None];parts=[]
        for q in range(0,len(mu),8):
            m=mu[q:q+8,None,None];s=np.sqrt((1-m)/2);ym=np.minimum(par['ymax']*math.sqrt(bath.T_m_K/3000),half/s)
            v=s*ym*y[None,None,:];nt=PCC.nu_abs+PCC.dnu*(u[None,:,None]+v);ns=PCC.nu_abs+PCC.dnu*(u[None,:,None]-v)
            ww=2*s*wu[None,:,None]*ym*wy[None,None,:];parts.append(_block(nt,ns,m,ww,i,i,bath,levels,bounds))
        Q={n:np.concatenate([v[0][n] for v in parts]) for n in levels};raw=np.concatenate([v[1] for v in parts]);direct=.5*np.concatenate([v[2] for v in parts])
    else:
        core=j<17;par=PCC.PRODUCTION_LANE if core else EX.LANES['production'];mu,w=angular(par)
        I,J=(i,j) if core else (j,i);a,b=bounds[I],bounds[J];use=np.arange(len(mu))<par['ob']
        if not core:use|=EX._crosses_resonance_mean(tuple(a),tuple(b))|((mu>.995)&EX._touching_intervals(tuple(a),tuple(b)))
        Q={n:np.zeros((len(mu),n+1,n+1)) for n in levels};raw=np.zeros((len(mu),3));direct=raw.copy()
        for mask,nodes in [(use,uv_nodes(a,b,par,.05 if core else .08)),(~use,tensor_nodes(a,b,par['nf']))]:
            if not np.any(mask):continue
            q,r,v=batch(mu[mask],nodes,I,J)
            for n in levels:Q[n][mask]=q[n] if core else q[n].transpose(0,2,1)
            raw[mask]=r if core else r[:,[0,2,1]];direct[mask]=v
    scale=8*np.pi*PCC.dnu/c**3*.75*(1+mu**2);raw*=scale[:,None];direct*=scale[:,None];err=0.;sym=0.
    out={}
    for n in levels:
        q=Q[n]*scale[:,None,None]
        if i==j:
            sym=max(sym,float(np.sum(w[:,None,None]*abs(q-q.transpose(0,2,1)))/max(np.sum(w[:,None,None]*q),1e-300)))
            q=(q+q.transpose(0,2,1))/2
        x=np.linspace(*bounds[i],n+1);y=np.linspace(*bounds[j],n+1)
        marg=np.stack([q.sum(axis=(1,2)),np.einsum('aij,i->a',q,x),np.einsum('aij,j->a',q,y)],axis=1)
        err=max(err,float(np.max(abs(marg-raw)/np.maximum(raw[:,0,None],1e-300))))
        if np.min(q)<0 or not np.all(np.isfinite(q)):raise ValueError("nonpositive calibrated conductance")
        out[n]=np.einsum('a,aij->ij',w,q)
    return i,j,out,w@direct,err,sym

def compile_isotropic(bath,levels=(1,4),workers=4):
    """Source integration over actual scattering angle, scalar isotropic
    occupation. This is NOT an angular-resolved general Bianchi network."""
    from concurrent.futures import ProcessPoolExecutor
    levels=tuple(levels)
    if any(n not in (1,2,4,8) for n in levels) or not 1<=workers<=4:raise ValueError("unsupported source resolution")
    jobs=[(i,j,bath,levels) for i in range(17) for j in range(i,35)]
    with ProcessPoolExecutor(max_workers=workers) as pool:rows=list(pool.map(_job,jobs))
    assert len(rows)==459
    return dict(pairs=np.array([r[:2] for r in rows]),bounds=owner_cells(),nu0=PCC.nu_abs,dnu=PCC.dnu,z0=bath.z0,T_m_K=bath.T_m_K,n_1s_m3=bath.n_1s_m3,max_marginal=max(r[4] for r in rows),max_same_sym=max(r[5] for r in rows),direct=np.sum([r[3] for r in rows],axis=0),**{f'Q{n}':np.array([r[2][n] for r in rows]) for n in levels})
