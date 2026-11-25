import numpy as np
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import State,L
from stable_activity import StableScatter
class N:
 ncore=0;gt=np.ones(2,dtype=L);et=np.array([1.,2.],dtype=L);q={'n1s':1}
 def point_values(self,s):return (s.nt+s.dt)/self.gt
class Sc:
 net=N();i=np.array([0]);j=np.array([1]);K=np.array([1.],dtype=L);z=np.ones(2,dtype=L);de=np.array([-1.],dtype=L);cross=np.array([True]);new=cross
def test_sub_ulp_increment_preserved():
 s=State(np.ones(2,dtype=L),np.ones(1,dtype=L),L(1),L(2),np.zeros(2,dtype=L),np.zeros(1,dtype=L))
 sc=StableScatter(Sc(),s)
 assert sc.rates(s)[0][0]==0
 s.dt[1]=L('1e-25')
 assert s.nt[1]+s.dt[1]==s.nt[1]
 f,g=sc.rates(s)
 assert abs(f[0]/L('1e-25')-1)<1e-17 and g[0]>0
