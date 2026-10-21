import math, unittest, tempfile, pathlib, json
import pilot

class Contracts(unittest.TestCase):
    def test_norm(self):
        r=pilot.norms(2.,3.,5.,7.)
        self.assertAlmostEqual(r['Sigma_frobenius'],math.sqrt(6)*2/5)
        self.assertAlmostEqual(r['Pi_frobenius'],7*math.sqrt(2/3)*3/25)
        self.assertAlmostEqual(r['Sigma_frobenius'],math.sqrt(2)*r['Sigma_half'])
    def test_relative_orientation(self):
        self.assertEqual(pilot.norms(-2.,3.,5.,7.)['alignment'],-1)
        self.assertEqual(pilot.norms(0.,3.,5.,7.)['alignment'],0)
    def test_nonfinite_refused(self):
        for value in [float('nan'),float('inf')]:
            with self.assertRaises(ValueError):pilot.norms(value,1,1,1)
    def test_nonpositive_h_refused(self):
        with self.assertRaises(ValueError):pilot.norms(1,1,0,1)
    def test_case_count_signs(self):
        cases=pilot.grid_cases()
        self.assertEqual(len(cases),25)
        self.assertEqual(len({(c['signed_sigma'],c['signed_pi']) for c in cases}),25)
    def test_signed_inverse(self):
        for target in [-.0004,0,.0004]:
            a=pilot.amplitude(target,2e-17,2e-26,3e-11,1e-28)
            observed=math.sqrt(2/3)*2e-26*(3e-11*a+1e-28)/(2e-17)**2
            self.assertAlmostEqual(observed,target,places=15)
    def test_inadmissible_stress_refused(self):
        with self.assertRaises(ValueError):pilot.amplitude(10.,1.,1.,1.,0.)
    def test_headroom_other_work_not_global_veto(self):
        self.assertEqual(pilot.admit(64,40,30,128*1024**3,64*1024**3,1024**3,4,0),30)
        self.assertEqual(pilot.admit(64,40,30,128*1024**3,64*1024**3,1024**3,4,10),20)
    def test_no_capacity(self):
        self.assertEqual(pilot.admit(64,64,0,128*1024**3,64*1024**3,1024**3,4,0),0)
    def test_atomic_create_only(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/'r.json';pilot.write_new(p,{'ok':1})
            with self.assertRaises(FileExistsError):pilot.write_new(p,{'ok':2})
            self.assertEqual(json.loads(p.read_text()),{'ok':1})

if __name__=='__main__':unittest.main()
