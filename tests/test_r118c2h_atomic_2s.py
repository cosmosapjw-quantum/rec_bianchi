import numpy as np
from pathlib import Path
from full_bianchi_hyrec.trajectory.atomic_two_s_live import TwoSNetwork
from full_bianchi_hyrec.standalone_line import prepare,initial
from full_bianchi_hyrec.trajectory.atomic_point_transfer import point_partition
from full_bianchi_hyrec.recoil.calibrated_source import owner_cells,PCC
from scipy.constants import h,k,e
ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'
def setup():
    bounds=owner_cells();q=prepare(dict(bounds=bounds,nu0=PCC.nu_abs,dnu=PCC.dnu,T_m_K=3000.,n_1s_m3=2.5e8,z0=np.exp(-h*PCC.nu_abs/(k*3000.)),pairs=np.zeros((0,2),int),Q1=np.zeros((0,2,2))),1)
    return q,TwoSNetwork(ARCHIVE,q,3000.)
def test_two_s_actual_spikes_thermal_null_and_live_conservation():
    q,n=setup()
    f=initial(q,'thermal');nh=3e8;neutral=.85*nh
    n2=neutral*np.exp(-n.transition_eV*e/(k*3000.))/(1+np.exp(-n.transition_eV*e/(k*3000.)))
    x=n.step(f,n2,neutral,1.)
    assert abs(x.n2-n2)/n2<1e-11
    assert np.max(abs(x.f/f-1))<1e-11
    f=initial(q,'hot');x=n.step(f,n2*1.01,neutral,1.)
    assert x.n2>=0 and x.n2<=neutral and np.min(x.f)>=0
    assert abs(x.number_defect)<1e-10 and abs(x.energy_defect_eV_m3)<1e-8
def test_vacuum_birth_and_no_negative_occupation():
    q,n=setup();f=np.zeros_like(q['g']);x=n.step(f,1e-5,1e8,0.01)
    assert x.f.sum()>0 and 0<x.n2<1e-5
    assert np.min(x.f)>=0
    import pytest
    with pytest.raises(ValueError):n.step(-f-1.,1e-5,1e8,0.01)
