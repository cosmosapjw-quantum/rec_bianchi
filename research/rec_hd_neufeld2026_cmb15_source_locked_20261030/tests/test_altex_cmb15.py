"""Adversarial single-author review of Neufeld original-source extrapolation.

These tests are independent numerical checks, NOT an external blind referee.
"""
from __future__ import annotations
import math, sys, unittest
from pathlib import Path
import numpy as np
from scipy.linalg import solve as scipy_solve
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from compare_cmb_altex import compare
from hd_cmb15 import solve_cmb, TCMB0_K
from pr169_neufeld15_reference import parse_lamda, H, K_B, SI_CONVERSION

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'source/zenodo_v2'


def independent_ctmc(model,T,n,z):
    """Unrelated SciPy LU with normalization-row replacement; self-consistency crosscheck."""
    p=15
    M=np.zeros((p,p), dtype=float)
    def add(u,l,w):
        M[l,u]+=w
        M[u,u]-=w
    bath=TCMB0_K*(1+z)
    for u,l,A,nu in model.rad:
        nb=1/math.expm1(H*nu/(K_B*bath))
        add(u,l,A*(1+nb));add(l,u,A*model.levels[u][2]/model.levels[l][2]*nb)
    _,para=model.collision[2]
    temps,ortho=model.collision[3]
    index=temps.index(T)
    for (u,l),qs in para.items():
        q=n*(qs[index]+3*ortho[(u,l)][index])/4
        gup=model.levels[u][2]; glo=model.levels[l][2]
        dE=model.levels[u][1]-model.levels[l][1]
        add(u,l,q);add(l,u,q*gup/glo*math.exp(-SI_CONVERSION*dE/T))
    A=M.copy();A[-1,:]=1.
    rhs=np.zeros(p);rhs[-1]=1.
    return scipy_solve(A,rhs),M

class SourceExtraBlindReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.std=parse_lamda((DATA/'hd_lamda.dat').read_bytes(),verify=True)
        cls.alt=parse_lamda((DATA/'hd_lamda_altex.dat').read_bytes())

    def test_no_unintended_owner_swap(self):
        self.assertEqual(len(self.std.levels),15)
        self.assertEqual(self.std.rad,self.alt.rad)
        self.assertEqual(self.std.levels,self.alt.levels)

    def test_exact_changed_54_rows_highJ_only(self):
        changed=[]
        for collider in (2,3):
            q1=self.std.collision[collider][1];q2=self.alt.collision[collider][1]
            for edge in q1:
                if q1[edge]!=q2[edge]:changed.append((collider,edge))
        self.assertEqual(len(changed),54)
        self.assertTrue(all(edge[0]>8 for _,edge in changed))

    def test_source_state_finite_across_bath(self):
        for T,n,z in [(100,1e2,0),(100,1e4,50),(200,1e6,73),(400,1e8,100),
                      (1000,1e6,100),(2000,1e4,0),(3000,1e8,30),(4000,1e6,100)]:
            for m in (self.std,self.alt):
                y=solve_cmb(m,T,n,z)
                self.assertGreaterEqual(min(y['populations_J0_to_J14']),0)
                self.assertAlmostEqual(sum(y['populations_J0_to_J14']),1.,places=12)
                self.assertEqual(len(y['line_power_records']),14)

    def test_independent_scipy_same_author_not_blind(self):
        # Compare the original M-matrix elimination against full-rank LU on
        # conditions for which all fifteen populations are resolvable by LU.
        for T,n,z in [(1000,1e6,100),(4000,1e6,100),(3000,1e8,30),(2000,1e4,0)]:
            for m in (self.std,self.alt):
                a=solve_cmb(m,T,n,z)
                q,L=independent_ctmc(m,T,n,z)
                self.assertLess(np.max(np.abs(q-np.array(a['populations_J0_to_J14']))),1e-11)
                self.assertLess(np.max(np.abs(L@q)),1e-12)

    def test_thermo_equal_bath_raw_frequency_rounding(self):
        for T in (100.,200.,400.,1000.):
            z=T/TCMB0_K-1
            for m in (self.std,self.alt):
                x=solve_cmb(m,T,1e6,z)
                # Do not assume exactly zero when source ν vs term-E differs.
                maxd=max(abs(nu-100*299792458*(m.levels[u][1]-m.levels[l][1]))
                         for u,l,_,nu in m.rad)
                # A source-consistency estimate; no inflated 35 Hz owner gate.
                self.assertLess(maxd,50.)
                spont=x['spont_power_W_per_HD']
                # Stronger than a speculative absolute zero, small relative to
                # source spontaneous power, but not a publication error budget.
                self.assertLess(abs(x['net_cooling_W_per_HD'])/spont,1e-8)

    def test_sign_consistency_sample_only(self):
        for T,n,z in [(100,1e2,100),(100,1e4,0),(200,1e6,100),(1000,1e8,0)]:
            s=math.copysign(1,T-TCMB0_K*(1+z))
            for m in (self.std,self.alt):
                self.assertEqual(math.copysign(1,solve_cmb(m,T,n,z)['net_cooling_W_per_HD']),s)

    def test_no_fabricated_2026_fits_astro_obs(self):
        from fits_source_grid import load_fits
        for kind,path in [('standard','hd_population_grids.fits'),('alternate','hd_population_grids_altex.fits')]:
            y=load_fits(DATA/path,source_kind=kind)
            self.assertEqual(y['populations'].shape,(161,111,15))
            self.assertGreater(y['nan_count'],0)
            self.assertEqual(y['nan_count'],y['metadata_nan_count'])

if __name__=='__main__':unittest.main()
