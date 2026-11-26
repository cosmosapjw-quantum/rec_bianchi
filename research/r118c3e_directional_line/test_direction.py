import numpy as np
from directional import retarded
def test_exact_lrs():
 e=np.linspace(-2.,0.,1001);q=.1;F=np.zeros((len(e),3,3))
 F[:,0,0]=np.exp(-q*e);F[:,1,1]=np.exp(-q*e);F[:,2,2]=np.exp(2*q*e)
 d,R=retarded(e,F,0.,np.array([.03,.07]),np.array([[0.,0.,1.],[1.,0.,0.]]))
 assert np.max(abs(d-np.array([[.03,.07]])/np.array([[1.2],[.9]])))<1e-7
 assert np.max(abs(d+R-np.array([.03,.07])))<1e-12
