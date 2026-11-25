from pathlib import Path
import numpy as np
from scipy.constants import h,k,e
from full_bianchi_hyrec.trajectory.atomic_refined_owner import RefinedTwoS, lift_pair, Scatter
from full_bianchi_hyrec.standalone_line import prepare
from full_bianchi_hyrec.recoil.calibrated_source import owner_cells,PCC
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'
def setup():
 q=prepare(dict(bounds=owner_cells(),nu0=PCC.nu_abs,dnu=PCC.dnu,T_m_K=3000.,n_1s_m3=2.5e8,z0=np.exp(-h*PCC.nu_abs/(k*3000.)),pairs=np.zeros((0,2),int),Q4=np.zeros((0,5,5))),4)
 return RefinedTwoS(A,q,16)
def test_registry_and_source_conservation():
 n=setup()
 assert len(n.bounds)==41 and len(n.owner_indices)==311
 assert n.ncom==33*5+2*17 and n.ncore==n.ncom+6*17
 assert len(n.exterior_indices)==297
 assert n.source_rate_relative<2e-15 and n.source_energy_relative<2e-15
 s=n.initial(3000.,2.5e8,equilibrium=True)
 v=n.action(s)
 assert np.max(abs(v['flux']))<1e-12*v['gross']
def test_lift_moments_and_positive_live_scatter():
 n=setup();i=n.ids(29);j=n.ids(35)
 x=np.array([-21.2,-20.5,-17.]);y=np.array([-24.,-23.,-22.]);w=np.array([1.,2.,3.])
 K=lift_pair(x,y,w,n.q['x'][i],n.q['x'][j])
 assert abs(K.sum()-w.sum())<1e-14
 assert abs(K.sum(axis=1)@n.q['x'][i]-w@x)<1e-12
 assert abs(K.sum(axis=0)@n.q['x'][j]-w@y)<1e-12
 s=n.initial(3000.,2.5e8,n2=2e-6)
 s.dt[j]+=0.1*s.nt[j]
 a=Scatter(n,[(i[0],j[0],1e12,True)])
 r=a.step(s,0.1)
 assert r['cross_into_com']>0 and r['number_relative']<1e-12 and r['energy_relative']<1e-12
 assert np.min(s.nt+s.dt)>=0
