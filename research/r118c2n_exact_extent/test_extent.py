import math
import numpy as np
import pytest
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import L,State
from equilibrium_extent import extent,source_step
class Decay:
    events=[(0,0,1,L(1),0)]
    transition=L(2)
    et=np.array([1],dtype=L);ec=np.array([1],dtype=L)
    def rates(self,s,event,delta=L(0)):
        return s.n2+s.d2-delta,L(0)
def make():
    return State(np.array([1],dtype=L),np.array([1],dtype=L),L(1),L(2),np.zeros(1,dtype=L),np.zeros(1,dtype=L))
def test_linear_exact_and_stiff_saturation():
    net=Decay();s=make()
    for h in (.01,.5,2.,8.,100.):
        d,diag=extent(net,s,net.events[0],h)
        assert abs(d+np.expm1(-L(h)))<2e-14
        assert 0<=d<=1
    source_step(net,s,100.)
    assert 0<=s.n2+s.d2<1e-18 and abs(s.dt[0]+s.d2)<1e-15
def test_reversible_nonlinear_second_order():
    class Model(Decay):
        def rates(self,s,event,delta=L(0)):
            b=s.n2+s.d2-delta
            return b*b,L('.04')
    from scipy.integrate import solve_ivp
    net=Model();s=make();ref=solve_ivp(lambda t,y: .04-y*y,(0,1),[1.],rtol=1e-13,atol=1e-15,method='DOP853').y[0,-1]
    err=[]
    for n in (4,8,16,32):
        s=make()
        for i in range(n):source_step(net,s,1/n)
        err.append(abs(float(s.n2+s.d2)-ref))
        assert .2<=s.n2+s.d2<=1.
    assert all(3.5<a/b<4.5 for a,b in zip(err,err[1:]))
def test_no_overshoot_for_reverse():
    class Model(Decay):
        def rates(self,s,event,delta=L(0)):
            b=s.n2+s.d2-delta
            return b,L('1.5')
    s=make();d,_=extent(Model(),s,Model.events[0],100.)
    assert abs(d+L('.5'))<1e-14
