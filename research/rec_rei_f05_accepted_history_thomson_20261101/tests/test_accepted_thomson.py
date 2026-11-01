"""Original F05 accepted 0→160 interval, authentic physical Thomson changes."""
import csv
from decimal import Decimal
import gzip
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("rec192_original_f05_accepted",ROOT/"compute_accepted160.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class OriginalAcceptedF05ThomsonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir=tempfile.TemporaryDirectory()
        cls.output=Path(cls.dir.name)
        cls.data=m.compute(ROOT,cls.output)

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()

    def test_source_byte_authority(self):
        assert m.sha(ROOT/"source_inputs"/m.TAR_NAME)==m.TAR_SHA
        base=ROOT.parents[1]/"research/rec_rei_f05_native_thomson_medium_20261101/source_inputs"
        assert m.sha(base/m.INIT_NAME)==m.INIT_SHA
        assert m.sha(base/m.FORCE_NAME)==m.FORCE_SHA
        self.assertEqual(self.data["original_accepted_raw_arrays_sha256"],m.ORIGINAL_ARRAY_SHA)

    def test_accepted_history_three_intervals_and_distinct_lanes(self):
        rows=self.data["accepted_intervals"]
        self.assertEqual([(r["left_tick"],r["right_tick"]) for r in rows],
                         [(0,64),(64,128),(128,160)])
        self.assertEqual(self.data["source_shape_lanes"],3)
        self.assertEqual(self.data["source_independent_physical_realizations"],1)
        self.assertEqual(self.data["official_accepted_tick"],160)
        self.assertEqual(self.data["source_archive_terminal_status"],"BLOCKED_MINIMUM_STEP")
        self.assertIn("NOT_IN_ORIGINAL_SOURCE_ARCHIVE",self.data["intermediate_accepted_64_128_states"])

    def test_tamper_original_archive_sha_rejected(self):
        with mock.patch.object(m,"TAR_SHA","0"*64):
            with self.assertRaisesRegex(ValueError,"ACCEPTED_ARCHIVE_SHA_DRIFT"):
                m.verify_accepted_archive(ROOT/"source_inputs"/m.TAR_NAME)

    def test_tamper_accepted_state_array_sha_rejected(self):
        with mock.patch.object(m,"ORIGINAL_ARRAY_SHA","0"*64):
            with self.assertRaisesRegex(ValueError,"NUMERIC_STATE_ARRAY_SHA_DRIFT"):
                m.verify_accepted_archive(ROOT/"source_inputs"/m.TAR_NAME)

    def test_wrong_original_clock_fails(self):
        base=ROOT.parents[1]/"research/rec_rei_f05_native_thomson_medium_20261101/source_inputs"
        with (base/m.FORCE_NAME).open(newline="") as f:
            reader=csv.DictReader(f)
            rows=list(reader)
            fields=reader.fieldnames
        assert fields
        rows[0]["z_mid"]="5.96"
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"altered.csv"
            with p.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=fields)
                w.writeheader()
                w.writerows(rows)
            with self.assertRaisesRegex(ValueError,"NONCONSTANT_ORIGINAL_SOURCE_VOLUME"):
                m.z_and_time(p)

    def test_original_accepted_time_and_units(self):
        self.assertEqual(self.data["source_accepted_0_to_160_seconds"],
                         "7.79495799866924805E+11")
        self.assertEqual(self.data["source_z_first_interval"],"5.95")
        self.assertGreater(Decimal(self.data["source_total_proper_volume_cm3"]),0)
        self.assertEqual(self.data["c_cm_s"],str(m.C))
        self.assertEqual(self.data["sigma_T_cm2"],str(m.SIGMA))

    def test_global_charge_and_electron_recombination(self):
        initial=Decimal(self.data["initial_global_electron_number"])
        final=[Decimal(x) for x in self.data["accepted160_global_electron_number"]]
        change=[Decimal(x) for x in self.data["accepted_global_electron_change_N"]]
        dh=[Decimal(x) for x in self.data["accepted_0_to_160_H_electron_delta_N"]]
        dhe=[Decimal(x) for x in self.data["accepted_0_to_160_He_electron_delta_N"]]
        self.assertLess(change[1],0)
        self.assertGreater(initial,final[1])
        for d,h,he in zip(change,dh,dhe):
            self.assertLess(abs((h+he-d)/d),Decimal("5e-17"))
        self.assertEqual(sum(self.data["source_native_electron_change_classes"].values()),m.N)

    def test_original_accepted_160_matches_parent_rec191(self):
        repo=ROOT.parents[1]
        prior=json.loads((repo/"research/rec_rei_f05_native_thomson_medium_20261101/results/SCIENCE_RESULT.json").read_text())
        now=[Decimal(x) for x in self.data["accepted160_volume_mean_Thomson_rate_s_inv"]]
        before=[Decimal(x) for x in prior["accepted_160_volume_weighted_mean_Thomson_rate_s_inv"]]
        for a,b in zip(now,before):
            self.assertLess(abs(a/b-1),Decimal("5e-15"))
        now_c=[Decimal(x) for x in self.data["accepted160_electron_clumping"]]
        before_c=[Decimal(x) for x in prior["accepted_160_source_electron_clumping_factor"]]
        for a,b in zip(now_c,before_c):
            self.assertLess(abs(a/b-1),Decimal("5e-15"))

    def test_clumping_and_not_optical_depth(self):
        self.assertGreater(Decimal(self.data["initial_electron_clumping"]),Decimal(1))
        self.assertLess(Decimal(self.data["accepted_0_to_160_Delta_electron_clumping"][1]),0)
        self.assertEqual(self.data["continuous_thomson_optical_depth"],
                         "NOT_COMPUTED_FROM_TWO_ENDPOINTS")
        self.assertEqual(self.data["observed_CMB_tau"],"NOT_COMPUTED")
        self.assertEqual(self.data["F05_tick161"],"NOT_ACCEPTED_V2_SHADOW_ONLY")
        self.assertEqual(self.data["REI_canonical_DAG"],"28/88")
        self.assertEqual(self.data["REC_H5_physical_DAG"],"0/313")
        self.assertFalse(self.data["auto_next"])

    def test_native_physics_each_row_and_mean_sign(self):
        file=self.output/"ORIGINAL_ACCEPTED_F05_THOMSON_CHANGE_46080.csv.gz"
        self.assertEqual(m.sha(file),self.data["source_physical_csv_gzip_sha256"])
        signed={"definite_gain":0,"definite_loss":0,"sign_ambiguous":0}
        with gzip.open(file,"rt",newline="") as f:
            rows=csv.DictReader(f)
            self.assertEqual(tuple(rows.fieldnames or ()),m.FIELDS)
            for i,row in enumerate(rows):
                self.assertEqual(int(row["node"]),i)
                label=row["accepted_electron_change_sign_class"]
                signed[label]+=1
                if i in (0,1200,20200,46079):
                    vol=Decimal(row["source_proper_volume_cm3"])
                    n=Decimal(row["initial_tick0_n_e_cm3"])
                    g=Decimal(row["accepted_tick0_Thomson_rate_s_inv"])
                    lo=Decimal(row["accepted_0_to_160_DeltaThomson_rate_lower_s_inv"])
                    hi=Decimal(row["accepted_0_to_160_DeltaThomson_rate_upper_s_inv"])
                    self.assertGreater(vol,0)
                    self.assertLess(abs(g/(m.C*m.SIGMA*n)-1),Decimal("5e-17"))
                    self.assertLessEqual(lo,hi)
            self.assertEqual(i+1,m.N)
        self.assertEqual(signed,self.data["source_native_electron_change_classes"])

    def test_independent_byte_exact_replay(self):
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/"fresh"
            b=m.compute(ROOT,a)
            self.assertEqual(b,self.data)
            for name in ("SCIENCE_RESULT.json",
                         "ORIGINAL_ACCEPTED_F05_THOMSON_CHANGE_46080.csv.gz"):
                self.assertEqual((a/name).read_bytes(),(self.output/name).read_bytes())

if __name__=="__main__":
    unittest.main()
