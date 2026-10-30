"""GLS projection tests are synthetic linear algebra only, not HD uncertainty."""
import importlib.util, pathlib, unittest
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cycles',ROOT/'src/correlated_cycles.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class TestSyntheticGLS(unittest.TestCase):
    def test_weighted_least_squares_equals_cycle_quadratic(self):
        # GENERATED TO PROVE A MATRIX IDENTITY ONLY, never measurement inference.
        rng=np.random.default_rng(20261030)
        d=np.asarray(mod.incidence(),dtype=float)
        c=np.asarray(mod.C,dtype=float)
        a=rng.normal(size=(9,9))
        v=a@a.T+np.eye(9)*0.4
        y=rng.normal(size=9)
        L=np.linalg.cholesky(v)
        q=np.linalg.lstsq(np.linalg.solve(L,d),np.linalg.solve(L,y),rcond=None)[0]
        e=y-d@q
        lhs=np.dot(np.linalg.solve(L,e),np.linalg.solve(L,e))
        r=c@y
        rhs=r@np.linalg.solve(c@v@c.T,r)
        self.assertAlmostEqual(lhs,rhs,places=11)
    def test_fitted_cycle_unchanged_by_level_gauge(self):
        rng=np.random.default_rng(3)
        d=np.asarray(mod.incidence(),float)
        c=np.asarray(mod.C,float)
        y=rng.normal(size=9)
        self.assertTrue(np.allclose(c@(y+d@np.full(9,123.)),c@y,atol=1.e-12))

if __name__=='__main__':unittest.main()
