import numpy as np
from scipy.linalg import expm
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import State,L
from patankar_scatter import PatankarScatter
class Net:
    et=np.array([1.,3.],dtype=L);transition=L(2.)
class Scatter:
    net=Net();i=np.array([0]);j=np.array([1]);cross=np.array([True]);new=np.array([True]);de=net.et[i]-net.et[j]
    def rates(self,s):
        y=s.nt+s.dt;f=3*y[1]-2*y[0];g=3*y[1]+2*y[0];return np.array([f],dtype=L),np.array([g],dtype=L)
def state(y=(1.,.01)):
    return State(np.array(y,dtype=L),np.array([1.],dtype=L),L(1),L(2),np.zeros(2,dtype=L),np.zeros(1,dtype=L))
def test_stiff_positive_conservation():
    s=state();r=PatankarScatter(Scatter()).step(s,1000.)
    assert min(s.nt+s.dt)>0
    assert abs(sum(s.dt))<1e-15
    assert abs(s.dt@Net.et+r['bath_energy_eV_m3'])<1e-14
    assert abs(s.dt[0]-r['cross_into_com'])<1e-14
def test_second_order_and_equilibrium():
    exact=expm(np.array([[-2.,3.],[2.,-3.]]))@np.array([1.,.01]);err=[]
    for n in (64,128,256,512,1024):
        s=state();sc=PatankarScatter(Scatter())
        for _ in range(n):sc.step(s,1/n)
        err.append(np.max(abs(np.asarray(s.nt+s.dt,float)-exact)))
    assert 3.8<err[-2]/err[-1]<4.2,err
    s=state((3.,2.));r=PatankarScatter(Scatter()).step(s,100.)
    assert np.max(abs(s.dt))==0 and r['energy_eV_m3']==0
