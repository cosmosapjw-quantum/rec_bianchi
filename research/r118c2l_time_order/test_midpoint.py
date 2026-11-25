import numpy as np
import pytest
from midpoint import extent, source_step, coupled_step, StepRejected
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import State,L

class Decay:
    events=[(0,0,1,L(1),0)]
    def rates(self,s,event,delta=L(0)):
        return s.n2+s.d2-delta,L(0)

def make():
    return State(np.array([1],dtype=L),np.array([1],dtype=L),L(1),L(2),np.zeros(1,dtype=L),np.zeros(1,dtype=L))

def test_scalar_midpoint():
    s=make();d,g,r=extent(Decay(),s,Decay.events[0],L('0.5'))
    assert abs(d-L('0.4'))<1e-14 and r<1e-14 and abs(d-g)<1e-14

def test_stiff_positivity_rejection_transaction():
    s=make()
    with pytest.raises(StepRejected):source_step(Decay(),s,6.)
    assert s.d2==0 and np.all(s.dt==0) and np.all(s.dc==0)

def test_invariants():
    s=make();source_step(Decay(),s,1.)
    assert abs(s.dt[0]+s.d2)<1e-15 and abs(s.dc[0]+s.d2)<1e-15
    assert 0<s.n2+s.d2<1

def test_scatter_failure_transaction():
    class Bad:
        def step(self,s,dt):
            s.dt[0]+=7
            raise StepRejected('test scatter rejection')
    s=make()
    with pytest.raises(StepRejected):coupled_step(Decay(),Bad(),s,1.)
    assert s.d2==0 and np.all(s.dt==0) and np.all(s.dc==0)
