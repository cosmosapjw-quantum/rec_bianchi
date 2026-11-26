import numpy as np
from refined import positive_pairs,action,L
def test_pair_cut_and_fine_limit():
 e=np.array([0.,1.,2.],dtype=L);f=np.array([.2,.8,1.2,1.9],dtype=L);i=np.array([0,0,1,2]);j=np.array([1,3,2,3]);K=np.array([2.,3.,4.,5.],dtype=L)
 p,g=positive_pairs(e,f,i,j,K)
 target=p.deposit(action(p.lift(e),i,j,K))
 assert np.max(abs(action(e,*g)-target))<1e-14
 assert min(g[2])>=0
 p,g=positive_pairs(f,f,i,j,K)
 a=np.array([.2,.4,.1,.5],dtype=L)
 assert np.max(abs(action(a,*g)-action(a,i,j,K)))<1e-14
