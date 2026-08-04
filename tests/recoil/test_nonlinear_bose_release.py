import numpy as np
from full_bianchi_hyrec.recoil.nonlinear_bose_release import HarmonicGrid, apply_nonlinear_bose_operator

def synthetic_grid():
    d=np.asarray([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]],dtype=float)
    return HarmonicGrid.from_directions(d,np.full(6,1/6),ell_max=1)

def test_discrete_be_family_is_exact_null():
    g=synthetic_grid(); mode=np.asarray([2.,3.]); pi=np.asarray([.4,.9]); z=pi/mode; q=.8
    f=q*z/(1-q*z); occ=np.repeat(f[:,None],g.n_angle,axis=1)
    m=np.zeros((2,2,2)); m[0,0,1]=m[0,1,0]=.7
    r=apply_nonlinear_bose_operator(occ,mode_measure=mode,equilibrium_weight=pi,pair_moments=m,same_cell_rates=np.zeros((2,2)),grid=g)
    assert np.max(np.abs(r.occupation_action))<1e-14 and abs(r.number_residual)<1e-14

def test_nonlinear_pair_conserves_number_and_dissipates_free_energy():
    g=synthetic_grid(); mode=np.asarray([2.,3.]); pi=np.asarray([.4,.9])
    occ=np.asarray([[.25,.10,.18,.12,.22,.11],[.02,.08,.03,.07,.04,.06]])
    m=np.zeros((2,2,2)); m[0,0,1]=m[0,1,0]=.7; m[1,0,1]=m[1,1,0]=.1
    r=apply_nonlinear_bose_operator(occ,mode_measure=mode,equilibrium_weight=pi,pair_moments=m,same_cell_rates=np.zeros((2,2)),grid=g)
    assert abs(r.number_residual)<1e-13 and r.entropy_production<=1e-13 and np.linalg.norm(r.Q_gamma+r.Q_atom)==0

def test_same_frequency_bose_factors_cancel_to_linear_angular_damping():
    g=synthetic_grid(); mode=np.asarray([2.]); pi=np.asarray([.4]); occ=np.asarray([[.3,.1,.2,.12,.25,.15]])
    same=np.asarray([[0.],[-.5]]); m=np.zeros((2,1,1))
    a=apply_nonlinear_bose_operator(occ,mode_measure=mode,equilibrium_weight=pi,pair_moments=m,same_cell_rates=same,grid=g)
    b=apply_nonlinear_bose_operator(4*occ,mode_measure=mode,equilibrium_weight=pi,pair_moments=m,same_cell_rates=same,grid=g)
    assert np.linalg.norm(b.occupation_action-4*a.occupation_action)<1e-13 and abs(a.number_residual)<1e-14
