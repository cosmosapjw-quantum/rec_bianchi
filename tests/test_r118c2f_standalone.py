import numpy as np
from pathlib import Path
from full_bianchi_hyrec.trajectory.standalone import independent_history, ground_state
from full_bianchi_hyrec.recoil.calibrated_source import Bath, density, owner_cells
ROOT=Path(__file__).resolve().parents[1]
TABLE=ROOT/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'
def test_independent_history_and_qss_population():
    history=independent_history(TABLE,z_end=1100.,points=101,rtol=1e-8,atol=1e-10)
    q=history['states'][-1]
    assert 0<q['x_HII']<1 and 0<q['x_1s']<1
    assert abs(q['x_1s']+q['x_2s']+q['x_2p']+q['x_HII']-1)<1e-14
    assert q['n_1s_m3']==q['x_1s']*q['n_H_m3']
    assert q['qss_relative_residual']<1e-12
def test_calibrated_density_is_positive_and_linear_in_ground_population():
    from full_bianchi_hyrec.recoil import pair_cell_conductance as p
    ns=p.nu_abs+p.dnu*np.array([-.2,.2,1.]);nt=p.nu_abs+p.dnu*np.array([.2,-.1,0.])
    a=density(nt,ns,.2,Bath(3000.,250e6))
    b=density(nt,ns,.2,Bath(3000.,125e6))
    ref=p.const_exact*np.exp(-p.beta*p.h*ns+p.logSmj(ns,nt,.2))*ns*nt*p.exact_amp2(ns,nt,.2)
    assert np.all(a>=0) and np.allclose(b,a/2,rtol=1e-14)
    assert np.allclose(a,ref,rtol=2e-12)
    assert len(owner_cells())==35
