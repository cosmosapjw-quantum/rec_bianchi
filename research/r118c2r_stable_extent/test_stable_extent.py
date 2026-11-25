import numpy as np
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import State,L
from stable_extent import StableReaction
class Net:
    ncore=0;gt=np.ones(1,dtype=L);gc=np.ones(1,dtype=L)
    def point_values(self,s):return (s.nt+s.dt)/self.gt
    def rates(self,s,event,delta=L(0)):
        i,j,sg,r,_=event;f=s.nt[i]+s.dt[i]+delta;c=s.nc[j]+s.dc[j]+sg*delta;b=s.n2+s.d2-delta
        return r*b*(1+f)*(c+(sg==1)),r*(s.neutral-b)*f*(c+(sg==-1))
def test_balanced_sub_ulp_atom():
    s=State(np.ones(1,dtype=L),np.ones(1,dtype=L),L(1),L(5),np.zeros(1,dtype=L),np.zeros(1,dtype=L))
    event=(0,0,1,L(1),0)
    n=StableReaction(Net(),s)
    assert n.net_rates(s,event)[0]==0
    s.d2=L('1e-25')
    assert Net().rates(s,event)[0]==Net().rates(s,event)[1]
    f,g,a,b=n.net_rates(s,event)
    assert abs(f/(5*L('1e-25'))-1)<1e-17 and g>0
def test_event_local_rate_resolves_sub_ulp_trial():
    s=State(np.ones(1,dtype=L),np.ones(1,dtype=L),L(1),L(5),np.zeros(1,dtype=L),np.zeros(1,dtype=L))
    event=(0,0,1,L(1),0);s.d2=L('1e-25')
    n=StableReaction(Net(),s);r=n.local_rates(s,event)
    f0,g,a,b=r(L(0));f1,_,_,_=r(L('1e-26'))
    assert f0>f1>0
    assert abs((f0-f1)/L('1e-26')-9)<1e-15
