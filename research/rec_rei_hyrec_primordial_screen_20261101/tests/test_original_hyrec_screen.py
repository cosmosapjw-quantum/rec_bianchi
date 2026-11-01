#!/usr/bin/env python3
"""Source-authentic REC-owned HyRec -> REI non-IVP screen scientific tests."""
import importlib.util
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
SCRIPT=Path(__file__).resolve().parents[1]/"original_hyrec_screen.py"
spec=importlib.util.spec_from_file_location("original_rec_hyrec_physical_screen",SCRIPT)
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

class OriginalHyRecScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary,cls.source,cls.physics=m.prepare(ROOT)

    def test_actual_source_not_generated_surrogate(self):
        self.assertEqual(len(self.source),1581)
        self.assertEqual(self.source[0]["zbar"],20.)
        self.assertEqual(self.source[-1]["zbar"],1600.)
        self.assertEqual(self.boundary["source_sha256"],m.NATIVE_C_STDOUT_SHA256)
    def test_source_identity_negative(self):
        original=(ROOT/m.SOURCE_REL).read_bytes()
        boundary=(ROOT/m.BOUNDARY_REL).read_bytes()
        with self.assertRaisesRegex(ValueError,"BLOB_IDENTITY"):
            m.assert_original_source_bytes(original+b" ",boundary)
    def test_boundary_actual_scenario_not_adopted(self):
        self.assertEqual(self.boundary["decision"],"REI_REFERENCE_COUNTERFACTUAL_NOT_ADOPTED")
        self.assertAlmostEqual(self.source[0]["xe_per_H"],.000210349192936,delta=1e-15)
        self.assertAlmostEqual(self.source[0]["Tgas_K"],9.306042400380866,delta=1e-13)
        self.assertAlmostEqual(self.boundary["published_rei_approximate_initial"]["electron_fraction_per_H"],.0002,delta=1e-17)
    def test_thomson_rate_source_parity(self):
        self.assertLess(self.physics["opacity_parity_max_relative"],2e-12)
        self.assertAlmostEqual(self.physics["kappa"][0],self.source[0]["dtaudlna"]/21,delta=1e-18)
    def test_primordial_tau_and_probability(self):
        t=self.physics["tau"];v=self.physics["visibility"]
        self.assertEqual(t[0],0.)
        self.assertTrue(all(t[i+1]>t[i] for i in range(len(t)-1)))
        self.assertAlmostEqual(t[1100-20],1.1246680564687528,delta=4e-10)
        self.assertAlmostEqual(t[-1],32.55814961583067,delta=3e-7)
        self.assertEqual(20+max(range(len(v)),key=v.__getitem__),1078)
        self.assertAlmostEqual(m.cumulative_simpson_38(v)[-1],1-math.exp(-t[-1]),delta=1e-5)
    def test_source_variation_not_frozen_xe(self):
        native=self.physics["tau"][100-20]
        frozen=self.physics["tau_frozen"][100-20]
        self.assertAlmostEqual(native/frozen,1.1803041042519284,delta=2e-8)
        self.assertTrue(native>frozen)
    def test_quadrature_independent(self):
        native=self.physics["tau"][-1]
        trap=self.physics["trap"][-1]
        self.assertLess(abs(trap/native-1),1e-6)
        self.assertLess(abs(m.two_step_composite_simpson(self.physics["kappa"],1580,2)/native-1),1e-6)
    def test_earlier_redshift_forbidden(self):
        with self.assertRaises(ValueError):m.hubble(-1)
    def test_immutable_original_26_event_f05(self):
        self.assertEqual(m.ORIGINAL_LIMIT,2e-4)
        self.assertEqual(m.REI_AXBI_SCENARIO_SHA256,"07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696")
    def test_real_result_serialization(self):
        with tempfile.TemporaryDirectory() as t:
            result=m.run(ROOT,Path(t))
            self.assertEqual(result["new_model_rows"],1581)
            self.assertEqual(result["REI_canonical"],"28/88")
            self.assertEqual(result["REC_physical_H5"],"0/313")
            self.assertFalse(result["physical_completed_REI_first_F05"])
            out=Path(t)/result["output_file"]
            self.assertTrue(out.stat().st_size>2000)
            self.assertEqual(len(__import__("gzip").open(out,"rt").read().splitlines()),1582)
            self.assertEqual(json.loads((Path(t)/"SCIENCE_STATUS.json").read_text())["output_sha256"],result["output_sha256"])

if __name__=="__main__":
    unittest.main()
