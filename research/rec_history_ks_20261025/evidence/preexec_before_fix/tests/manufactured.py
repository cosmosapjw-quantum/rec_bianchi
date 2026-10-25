"""Independent exact rational controls; <=10 small right-hand sides total."""
from fractions import Fraction as F
import numpy as np
import interval as iv
from certificate import certify

def rational(a): return [[F(float(x)) for x in row] for row in a]
def matmul(a,b): return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def exact_solve(a,b):
    a=rational(a); b=rational(b); n=len(a); m=len(b[0]); aug=[x+y for x,y in zip(a,b)]
    for k in range(n):
        owner=next(i for i in range(k,n) if aug[i][k]); aug[k],aug[owner]=aug[owner],aug[k]
        pivot=aug[k][k]; aug[k]=[x/pivot for x in aug[k]]
        for i in range(n):
            if i!=k:
                factor=aug[i][k]; aug[i]=[x-factor*y for x,y in zip(aug[i],aug[k])]
    return [row[n:] for row in aug]

def run():
    # Arithmetic assumptions exercised in this same bounded scientific child.
    tiny=np.nextafter(0.,1.); half=np.finfo(float).tiny/2
    assert tiny>0 and half>0 and half*1.==half and np.finfo(float).tiny*.5==half
    one=np.float64(1.);half_ulp=np.float64(2.**-53)
    assert np.add(one,half_ulp)==one and np.add(one,np.multiply(np.float64(3.),half_ulp))==np.add(one,np.float64(2.**-51))
    arithmetic={'round_to_nearest_ties_to_even':True,'gradual_underflow':True,'smallest_subnormal':float(tiny),'half_minimum_normal':float(half)}
    cases=[(np.array([[3.,1.],[-2.,4.]]),np.array([[1.,-1.],[2.,3.]]),np.array([[3.,1.],[0.5,1.]]),np.array([[-1.,1.],[-1.,0.]])),
           (np.array([[4.,1.,-1.],[2.,5.,1.],[1.,0.,3.]]),np.eye(3),np.array([[1.,-1.,.5],[1.,1.,-2.]]),np.array([[1e-15,-1.,2.],[.1,.2,.3]]))]
    reports=[]; count=0
    for M,B,T,P in cases:
        V=np.linalg.solve(M,B);Z=np.linalg.solve(M,np.eye(len(M)));count+=B.shape[1]+len(M)
        cert,a=certify(M,B,T,P,V,Z)
        assert cert['status']=='CERTIFIED_REPRESENTED_BINARY64_OPERATOR'
        exact=matmul(rational(T),exact_solve(M,B));pp=rational(P)
        exact=[[x+y for x,y in zip(row,p)] for row,p in zip(exact,pp)]
        for i,row in enumerate(exact):
            for j,k in enumerate(row): assert F(float(a['Klo'][i,j]))<=k<=F(float(a['Khi'][i,j]))
        norm=max(sum(abs(x) for x in row) for row in exact)
        assert F(cert['norm_lower'])<=norm<=F(cert['norm_upper'])
        zero=iv.box_weights((a['Klo'],a['Khi']),np.zeros(B.shape[1]));given=iv.box_weights((a['Klo'],a['Khi']),np.arange(B.shape[1])+1.)
        eps=[F(j+1) for j in range(B.shape[1])]
        for i,row in enumerate(exact): assert sum(abs(x)*e for x,e in zip(row,eps))<=F(given['bound'][i])
        assert max(zero['bound'])<=1e-300
        reports.append({'dimension':len(M),'exact_K':[[str(x) for x in row] for row in exact],'exact_norm':str(norm),'certificate':cert,'zero_epsilon':zero,'manufactured_epsilon':given})
    M,B,T,P=cases[0]
    fail,_=certify(M,B,T,P,np.zeros_like(B),np.zeros_like(M));assert fail['status']=='CERTIFICATE_FAILURE_RHO'
    refused=[]
    for label,fn in [('nonfinite',lambda:certify(np.array([[np.inf]]),np.ones((1,1)),np.ones((1,1)),np.zeros((1,1)),np.ones((1,1)),np.ones((1,1)))),('negative_epsilon',lambda:iv.box_weights(iv.point(np.eye(2)),[-1.,0.]))]:
        try: fn()
        except ValueError: refused.append(label)
    assert len(refused)==2 and count<=12
    return {'status':'PASS','small_rhs':count,'cases':reports,'rho_failure':fail,'refused':refused,'physical_epsilon':None,'arithmetic':arithmetic}
