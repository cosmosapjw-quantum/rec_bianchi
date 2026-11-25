import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r118c2n_exact_extent'))
import numpy as np,pytest
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import L,State
from adaptive_stiff import advance
class Net:
    et=np.array([1.],dtype=L);ec=np.array([1.],dtype=L);transition=L(2)
    events=[(0,0,1,L(1),0)]
    def rates(self,s,event,delta=L(0)):return s.n2+s.d2-delta,L(0)
class NoScatter:
    def step(self,s,h):return dict(gross=0.,bath_energy_eV_m3=0.,cross_into_com=0.,new_energy=0.)
def state():
    return State(np.array([1.],dtype=L),np.array([1.],dtype=L),L(1),L(2),np.zeros(1,dtype=L),np.zeros(1,dtype=L))
def test_decay_and_transaction():
    s=state();r=advance(Net(),NoScatter(),s,1.,.5,1e-3)
    assert abs(s.n2+s.d2-np.exp(-1))<1e-12 and r['accepted']>0
    s=state()
    with pytest.raises(RuntimeError):advance(Net(),NoScatter(),s,1.,.1,1e-3,max_attempts=1)
    assert s.d2==0
