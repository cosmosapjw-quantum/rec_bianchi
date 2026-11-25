import numpy as np
from full_bianchi_hyrec.recoil.calibrated_source import Bath, _job
from full_bianchi_hyrec.recoil.calibrated_angular import angular_lift
def test_source_angle_resolved_and_integrated_same_measure():
    q=_job((8,9,Bath(2999.967,216.268e6),(1,),True))
    mu,w,raw=q[6]
    assert np.all(np.diff(mu)>0) and np.all(w>0) and np.min(raw[1])>=0
    assert np.allclose(w@raw[1].reshape(len(mu),-1),q[2][1].ravel(),rtol=2e-14)
def test_six_ray_barycentric_angle_lift_preserves_first_moment_and_row_mass():
    d=np.vstack([np.eye(3),-np.eye(3)]);w=np.full(6,1/6)
    mu=np.array([-.9,-.2,.3,.999]);mass=np.array([.2,.4,.5,.9])
    G,err=angular_lift(mu,mass,d,w)
    assert np.all(G>=0) and np.array_equal(G,G.T)
    assert np.max(abs(G.sum(axis=1)-w*mass.sum()))<1e-13
    assert abs(np.sum(G*(d@d.T))-mu@mass)<1e-13

def test_unequal_weight_lebedev_first_moment_after_balance():
    from scipy.integrate import lebedev_rule
    d,w=lebedev_rule(7);d=d.T;w=w/(4*np.pi)
    mu=np.array([-.91,-.32,.13,.47,.91])
    mass=np.array([.17,.6,.33,.52,.2])
    G,_=angular_lift(mu,mass,d,w)
    assert np.all(G>=0) and np.array_equal(G,G.T)
    assert np.max(abs(G.sum(axis=1)-w*mass.sum()))<1e-12
    assert abs(np.sum(G*(d@d.T))-mu@mass)<1e-12
