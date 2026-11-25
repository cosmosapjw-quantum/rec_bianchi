import numpy as np
from pathlib import Path
from scipy.constants import h,k,e
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import DynamicTwoS
from full_bianchi_hyrec.standalone_line import prepare
from full_bianchi_hyrec.recoil.calibrated_source import owner_cells,PCC
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'
def setup():
 q=prepare(dict(bounds=owner_cells(),nu0=PCC.nu_abs,dnu=PCC.dnu,T_m_K=3000.,n_1s_m3=2.5e8,z0=np.exp(-h*PCC.nu_abs/(k*3000.)),pairs=np.zeros((0,2),int),Q1=np.zeros((0,2,2))),1)
 return DynamicTwoS(A,q)
def test_full_source_partition_and_thermal_null():
 n=setup()
 assert len(n.owner_indices)==311
 assert len(n.exterior_indices)==303
 assert np.min(n.gc)>0 and np.min(n.gt)>0
 assert np.max(n.ec)<np.min(n.et)
 s=n.initial(3000.,2.5e8,equilibrium=True)
 a=n.action(s)
 assert a['gross']>0 and np.max(abs(a['flux']))<1e-12*a['gross']
def test_live_companion_and_atom_ledgers_and_vacuum():
 n=setup();s=n.initial(3000.,2.5e8,n2=2e-6,tracked_vacuum=True)
 r=n.step(s,0.001)
 assert r['gross']>0 and s.d2<0
 assert np.any(s.dc!=0) and np.any(s.dt!=0)
 assert np.min(s.nt+s.dt)>=0 and np.min(s.nc+s.dc)>=0
 assert r['energy_relative']<1e-12 and r['number_relative']<1e-12
