"""REC physical source-locked tests: F05 tick161 Thomson capacity only."""
from decimal import Decimal
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("rec_f05_thomson_capacity",ROOT/"capacity.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def number(pair):
    return Decimal(pair[0]),Decimal(pair[1])


class OriginalF05ThomsonCapacityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.result=mod.compute(ROOT,Path(cls.tmp.name))
        cls.status=json.loads((Path(cls.tmp.name)/"SCIENCE_RESULT.json").read_text())
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_exact_original_rei_owner_source_and_rejected_receipt(self):
        self.assertEqual(mod.sha256(ROOT/"source_inputs"/mod.SOURCE_NAME),mod.SOURCE_SHA256)
        self.assertEqual(mod.sha256(ROOT/"source_inputs"/mod.RECEIPT_NAME),mod.RECEIPT_SHA256)
        self.assertEqual(self.status["original_worker_acceptance"],"FAILED_UNCHANGED")
        self.assertEqual(self.status["original_tick"],160)
        self.assertEqual(self.status["candidate_tick"],161)

    def test_original_native_proper_time_clock_from_locked_receipt(self):
        self.assertAlmostEqual(float(self.status["native_proper_tick_seconds"]),
                               4871848749.168213,places=5)
        self.assertGreater(number(self.status["global_electron_161_candidate_N"])[0],Decimal(0))

    def test_original_46080_spatial_cells_no_lane_triple_count(self):
        self.assertEqual(self.status["source_physical_cells"],46080)
        self.assertEqual(self.status["source_shape_lanes"],3)
        self.assertEqual(self.status["independent_source_populations"],1)
        self.assertEqual(sum(self.status["local_electron_change_classes"].values()),46080)

    def test_thomson_area_is_exact_sigma_times_electron_number(self):
        area=number(self.status["Thomson_scattering_area_161_cm2"])
        electrons=number(self.status["global_electron_161_candidate_N"])
        for a,n in zip(area,electrons):
            self.assertLess(abs((a/(n*mod.SIGMA_T_CM2))-1),Decimal("1e-16"))

    def test_correlated_area_delta_negative_and_frozen_local_error_gate(self):
        da=number(self.status["Thomson_scattering_area_delta_cm2"])
        ne=number(self.status["global_electron_delta_N"])
        self.assertLess(da[1],0)
        self.assertLess(ne[1],0)
        for a,n in zip(da,ne):
            self.assertLess(abs((a/(n*mod.SIGMA_T_CM2))-1),Decimal("1e-16"))
        self.assertGreater(Decimal(self.status["original_historical_logT_upper"]),
                           Decimal(self.status["original_unchanged_strict_gate"]))

    def test_H_He_charge_decomposition_covers_original_electron_field(self):
        h=number(self.status["source_H_electron_161_N"])
        he=number(self.status["source_He_electron_161_N"])
        total=number(self.status["global_electron_161_candidate_N"])
        self.assertLessEqual(h[0]+he[0],total[1])
        self.assertGreaterEqual(h[1]+he[1],total[0])
        self.assertGreater(he[0],0)
        self.assertGreater(h[0],he[1])

    def test_He_fraction_requires_helium_electrons(self):
        f=number(self.status["He_fraction_of_total_electrons_161_candidate"])
        self.assertGreater(f[0],Decimal("0.0734"))
        self.assertLess(f[1],Decimal("0.0735"))
        self.assertLessEqual(f[0],f[1])

    def test_source_global_xe_may_exceed_one_because_he(self):
        f=number(self.status["electron_fraction_per_H_global_161_candidate"])
        self.assertGreater(f[0],1)
        self.assertLess(f[1],Decimal("1.2"))

    def test_spatial_gain_signs_and_mass_weight_show_global_loss(self):
        self.assertEqual(self.status["local_electron_change_classes"],{
            "definite_local_increase":1458,
            "definite_local_decrease":42894,
            "ambiguous_local_sign":1728
        })
        weight=number(self.status["mass_weighted_fraction_in_definitely_increasing_cells"])
        self.assertGreater(weight[0],0)
        self.assertLess(weight[1],Decimal("0.000001"))
        self.assertLess(number(self.status["definite_decrease_electron_delta_N"])[1],0)

    def test_no_fake_LOS_tau_and_no_owner_admission(self):
        self.assertEqual(self.status["cosmological_LoS_tau"],
                         "NOT_COMPUTABLE_FROM_TOTAL_N_ONLY")
        self.assertEqual(self.status["observed_CMB_visibility"],"NOT_COMPUTED")
        self.assertEqual(self.status["rei_original_accepted_tick"],"160/131072")
        self.assertEqual(self.status["rei_canonical"],"28/88")
        self.assertEqual(self.status["rec_H5_physical"],"0/313")
        self.assertFalse(self.status["source_owner_swap"])
        self.assertFalse(self.status["merge"])

    def test_source_byte_forgery_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            fake=Path(d)
            (fake/"source_inputs").mkdir()
            (fake/"source_inputs"/mod.SOURCE_NAME).write_bytes(b"forged")
            (fake/"source_inputs"/mod.RECEIPT_NAME).write_bytes(
                (ROOT/"source_inputs"/mod.RECEIPT_NAME).read_bytes())
            with self.assertRaisesRegex(ValueError,"SOURCE_OR_CLOCK_BYTES"):
                mod.locked_inputs(fake)

    def test_clock_receipt_forgery_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            fake=Path(d)
            (fake/"source_inputs").mkdir()
            os.link(ROOT/"source_inputs"/mod.SOURCE_NAME,
                    fake/"source_inputs"/mod.SOURCE_NAME)
            (fake/"source_inputs"/mod.RECEIPT_NAME).write_bytes(b"{}")
            with self.assertRaisesRegex(ValueError,"SOURCE_OR_CLOCK_BYTES"):
                mod.locked_inputs(fake)

    def test_fresh_independent_regeneration_is_byte_exact(self):
        with tempfile.TemporaryDirectory() as x, tempfile.TemporaryDirectory() as y:
            a=mod.compute(ROOT,Path(x))
            b=mod.compute(ROOT,Path(y))
            self.assertEqual((Path(x)/"SCIENCE_RESULT.json").read_bytes(),
                             (Path(y)/"SCIENCE_RESULT.json").read_bytes())
            self.assertEqual(a,b)
            self.assertFalse(a["auto_next_node"])


if __name__=="__main__":
    unittest.main()
