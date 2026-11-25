from pathlib import Path
import numpy as np
from scipy.constants import h,k,e
from full_bianchi_hyrec.trajectory.atomic_dynamic_companion import DynamicTwoS,L
from full_bianchi_hyrec.trajectory.atomic_physical_exterior import physical_blocks,ExteriorPairs
from full_bianchi_hyrec.standalone_line import prepare
from full_bianchi_hyrec.recoil.calibrated_source import owner_cells,PCC
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'
def setup():
 q=prepare(dict(bounds=owner_cells(),nu0=PCC.nu_abs,dnu=PCC.dnu,T_m_K=3000.,n_1s_m3=2.5e8,z0=np.exp(-h*PCC.nu_abs/(k*3000.)),pairs=np.zeros((0,2),int),Q1=np.zeros((0,2,2))),1)
 return DynamicTwoS(A,q)
def test_unique_disjoint_physical_blocks_and_thermal_null():
 n=setup();b=physical_blocks(n)
 assert len(b)==6
 assert sum(x[0]=='cross' for x in b)==2
 assert all(any(i>=n.ncore for i in x[1]+x[2]) for x in b)
 assert len(set((tuple(x[1]),tuple(x[2])) for x in b))==6
 s=n.initial(3000.,2.5e8,equilibrium=True)
 pairs=ExteriorPairs(n,[(b[0][1][0],b[0][2][0],1e20)])
 q=pairs.action(s)
 assert abs(q[0])<1e-12*q[1]
def test_positive_exchange_and_centered_energy():
 n=setup();b=physical_blocks(n);i=b[0][1][0];j=b[0][2][0]
 s=n.initial(3000.,2.5e8,equilibrium=True)
 s.dt[j]+=s.nt[j]*L('.2')
 p=ExteriorPairs(n,[(i,j,1e20)])
 old=s.dt.copy();r=p.step(s,.1)
 assert r['number_relative']<1e-12 and r['energy_relative']<1e-12
 assert np.min(s.nt+s.dt)>=0 and np.any(s.dt!=old)
