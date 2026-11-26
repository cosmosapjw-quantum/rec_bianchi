"""Native shared real/virtual Schur complement after eliminating 2s."""
import numpy as np
from scipy.linalg import solve_banded
from full_bianchi_hyrec.trajectory.hmla_flrw import LYA_FACT_CM3
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _original_escape_factors,accurate_escape_factors
def effective(s,rates,inc,w):
 w=w/w.sum();x1=1-s.xHII;pi0,_=_original_escape_factors(s.Dtau);pi,_=accurate_escape_factors(s.Dtau[None,:]/rates[:,None]);gamma=pi0*s.Tvv[0]
 inv=np.divide(pi,gamma[None,:],out=np.broadcast_to(1/(rates[:,None]*s.Tvv[0]),pi.shape).copy(),where=gamma[None,:]>0)
 vv=s.Tvv.copy();vv[0]=1/(w@inv)
 sv=vv[0]*x1*(w@((1-pi)*inc[:,:311]))
 ly=w@(rates[:,None]*inc[:,311:])
 L=LYA_FACT_CM3*s.H_s_inv/(s.nH_cgs*x1)
 sr=s.sr.copy();sr+=3*L*x1*np.array([1.664786871919931*(ly[1]-s.incoming_lyman[1]),ly[0]-s.incoming_lyman[0]])
 ab=np.zeros_like(vv);ab[1]=vv[0];ab[0,1:]=vv[2,:-1];ab[2,:-1]=vv[1,1:]
 z=solve_banded((1,1),ab,np.c_[sv,s.Tvr.T]);E=s.Trr-s.Trv@z[:,1:];b=sr-s.Trv@z[:,0]
 lam=E[1,1]-E[1,0]*E[0,1]/E[0,0];rhs=b[1]-E[1,0]*b[0]/E[0,0]
 real=np.linalg.solve(E,b)
 nonline=lam-L;source=rhs-3*L*x1*ly[0];net=source-nonline*real[1]
 direct=L*(real[1]-3*x1*ly[0])
 return dict(lam=float(lam),loss=float(nonline),source=float(source),net=float(net),line=float(direct),real=real,diag_non_line=float(s.Trr[1,1]-L))
