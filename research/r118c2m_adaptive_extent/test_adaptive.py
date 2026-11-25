import math
from pathlib import Path
import sys
import numpy as np
import pytest
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import State,L
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r118c2l_time_order'))
from adaptive import advance
class Decay:
    events=[(0,0,1,L(1),0)]; transition=L(2)
    et=np.array([1],dtype=L);ec=np.array([1],dtype=L)
    def rates(self,s,event,delta=L(0)):
        return s.n2+s.d2-delta,L(0)
class NoScatter:
    def step(self,s,dt):
        return dict(gross=0.,bath_energy_eV_m3=0.,cross_into_com=0.,new_energy=0.)
def make():
    return State(np.array([1],dtype=L),np.array([1],dtype=L),L(1),L(2),np.zeros(1,dtype=L),np.zeros(1,dtype=L))
def test_stiff_rejection_and_recovery():
    s=make()
    r=advance(Decay(),NoScatter(),s,16.,16.,1e-4)
    assert r['positivity_rejects']>0 and r['accepted']>0
    assert r['end_s']==16. and 0<s.n2+s.d2<1
    assert abs(float(s.n2+s.d2)/math.exp(-16)-1)<.02
    assert abs(s.dt[0]+s.d2)<1e-15 and abs(s.dc[0]+s.d2)<1e-15
def test_cap_is_transactional():
    s=make()
    with pytest.raises(RuntimeError):advance(Decay(),NoScatter(),s,16.,16.,1e-4,max_attempts=1)
    assert s.d2==0 and np.all(s.dt==0) and np.all(s.dc==0)
def test_invalid_tolerance():
    s=make()
    with pytest.raises(ValueError):advance(Decay(),NoScatter(),s,1.,1.,0.)
