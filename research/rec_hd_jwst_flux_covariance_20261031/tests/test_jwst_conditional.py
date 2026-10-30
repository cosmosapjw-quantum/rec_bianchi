import sys, unittest, math
from pathlib import Path
import numpy as np
from scipy.optimize import nnls
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from jwst_conditional_fit import (read_flux,row_summary,covariance,profile_nonnegative_basis,make_basis,
                                  EPS,PRESSURE_LOG_K_CM3,T_EXACT)

class TestPhysicsAndSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records=read_flux(ROOT)
    def test_exact_census_and_source_version(self):
        d=row_summary(self.records)
        self.assertEqual((len(self.records),d['detected_positive_printed_error'],d['detected_rounded_error_zero'],d['upper_limit_3sigma']),
                         (364,283,8,73))
        self.assertTrue(all('arxiv_2501.02085v1' in r['source_version'] for r in self.records))
    def test_source_specific_expected_values(self):
        f=lambda src,ap,spec,line:next(x for x in self.records if (x['source'],x['aperture'],x['species'],x['line'])==(src,ap,spec,line))
        self.assertEqual(f('HH 211',7,'HD','R(4)')['value_printed'],0.93)
        self.assertEqual(f('HH 211',7,'HD','R(9)')['sigma_printed'],0.02)
        self.assertEqual(f('G28-IRS2',1,'H2','S(6)')['status'],'upper_limit_3sigma')
        self.assertEqual(f('BHR71-IRS1',3,'HD','R(7)')['status'],'detected_rounded_error_zero')
    def test_no_fake_errors_for_censored(self):
        self.assertTrue(all(x['sigma_printed'] is None for x in self.records if x['status']=='upper_limit_3sigma'))
        self.assertTrue(all(x['sigma_printed']==0 for x in self.records if x['status']=='detected_rounded_error_zero'))
    def test_26_common_apertures(self):
        h={(x['source'],x['aperture']) for x in self.records if x['species']=='H2'}
        d={(x['source'],x['aperture']) for x in self.records if x['species']=='HD'}
        self.assertEqual(h,d)
        self.assertEqual(len(d),26)
    def test_exact_source_grid_and_stationarity(self):
        s,ks,p,kp,res=make_basis(ROOT)
        self.assertEqual((len(s),len(p)),(342,1368))
        self.assertTrue(0<=res<1e-12)
        self.assertAlmostEqual(PRESSURE_LOG_K_CM3[0],7.0,places=12)
        self.assertAlmostEqual(PRESSURE_LOG_K_CM3[1],7.0+1.0/6.0,places=12)
        self.assertAlmostEqual(PRESSURE_LOG_K_CM3[-1],10.0,places=12)
        self.assertEqual(len(T_EXACT),9)
        self.assertEqual(set(q['source'] for q in ks),{'std','alternate'})
        self.assertTrue(np.all(s>0) and np.all(p>0))
    def test_covariance_correlation_extremes(self):
        f=np.array([1.,2.,3.]);s=np.array([.1,.2,.3]);
        c0=covariance(f,s,0);c1=covariance(f,s,1)
        self.assertTrue(np.allclose(c0,np.diag(s*s+(EPS*f)**2)))
        self.assertTrue(np.allclose(c1,np.diag(s*s)+EPS**2*np.outer(f,f)))
        self.assertTrue(np.all(np.linalg.eigvalsh(c1)>0))
    def test_covariance_excludes_zero_printed(self):
        with self.assertRaises(ValueError):covariance([1.],[0.],0.)
    def test_covariance_rejects_nonphysical_rho(self):
        for r in (-0.1,1.1):
            with self.assertRaises(ValueError):covariance([1.],[.1],r)
    def test_amplitude_one_basis_analytic(self):
        f=np.array([1.,1.6,2.3]);s=np.array([.2,.3,.1]);b=np.array([[[.3,.6,.2]]]);
        chi,coeff=profile_nonnegative_basis(f,s,b,rho=0)
        L=np.linalg.cholesky(covariance(f,s,0.))
        a, _=nnls(np.linalg.solve(L,b[0].T),np.linalg.solve(L,f))
        expected=np.sum((np.linalg.solve(L,(a@b[0])-f))**2)
        self.assertAlmostEqual(chi[0],expected,places=9)
        self.assertAlmostEqual(coeff[0,0],a[0],places=9)
    def test_nnls_two_component_vs_scipy_independent(self):
        rng=np.random.default_rng(17)
        f=rng.uniform(.05,2.,6)
        s=rng.uniform(.01,.3,6)
        b=rng.uniform(0.01,2.,(30,2,6))
        for rho in (0.,.45,1.):
            chi,coeff=profile_nonnegative_basis(f,s,b,rho=rho)
            L=np.linalg.cholesky(covariance(f,s,rho))
            wy=np.linalg.solve(L,f)
            for i in range(30):
                A=np.linalg.solve(L,b[i].T)
                x, _=nnls(A,wy)
                chisq=np.sum((A@x-wy)**2)
                self.assertAlmostEqual(chi[i],chisq,places=8)
                self.assertTrue(np.allclose(A@coeff[i],A@x,atol=1e-7))
    def test_negative_input_and_zero_emissivity_rejected(self):
        with self.assertRaises(ValueError):profile_nonnegative_basis([1.,2.],[.1,.1],np.array([[[-1.,2.]]]))
        with self.assertRaises(ValueError):profile_nonnegative_basis([1.,2.],[.1,.1],np.array([[[0.,0.]]]))
    def test_amplitude_basis_reparametrization_invariance(self):
        f=np.array([.1,.3,.4]);s=np.array([.02,.03,.02]); b=np.array([[[.2,.3,.4],[.1,.2,.1]]])
        chi,a=profile_nonnegative_basis(f,s,b,rho=0.)
        chi2,a2=profile_nonnegative_basis(f,s,b*np.array([[[2.],[3.]]]),rho=0.)
        self.assertAlmostEqual(chi[0],chi2[0],places=9)
        self.assertTrue(np.allclose(a2[0]*np.array([2.,3.]),a[0]))

if __name__=='__main__':unittest.main()
