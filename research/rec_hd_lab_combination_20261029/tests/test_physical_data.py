from __future__ import annotations
from pathlib import Path
import json,sys,tempfile,unittest
from fractions import Fraction
from decimal import Decimal
from shutil import copytree
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from physical_data import (ROOT,EXPECTED_LAB,EXPECTED_SOURCE_BLOB,exact_reconciliation,photon_power_and_thermo,read_verified_inputs,H,C,K_B,write_outputs)

class RealHDDataTests(unittest.TestCase):
    def test_source_count(self):
        rows,lab,src,hashes=read_verified_inputs();self.assertEqual(len(rows),8);self.assertEqual(src['git_blob'],EXPECTED_SOURCE_BLOB)
    def test_two_laboratory_anchor_values(self):
        _,lab,_,_=read_verified_inputs();self.assertEqual(tuple((x['upper_J'],x['lower_J'],x['nominal_kHz'],x['reported_uncertainty_kHz'],x['source_DOI']) for x in lab['measurements']),EXPECTED_LAB)
    def test_frozen_35hz_fail7(self):
        rows,*_=read_verified_inputs();self.assertEqual(sum(abs(u-p)>35 for u,p,a in rows),7)
    def test_difference_J20(self):
        s=exact_reconciliation()['measured_combinations'][0];self.assertEqual(s['experiment_minus_source_photon_combo_Hz'],'-14877400')
    def test_difference_J31(self):
        s=exact_reconciliation()['measured_combinations'][1];self.assertEqual(s['experiment_minus_source_photon_combo_Hz'],'-45034200')
    def test_measurement_rank_and_kernel(self):
        out=exact_reconciliation();self.assertEqual(out['rank'],2);v=out['null_vector_of_two_by_three_line_incidence'];self.assertEqual([v[0]+v[1],v[1]+v[2]],[0,0])
    def test_exact_candidate_decomposition(self):
        rows=exact_reconciliation();q=rows['conditionally_anchored_individual_lines_Hz'];self.assertEqual(q['derived_J2_1'],'5331547074000');self.assertEqual(q['derived_J3_2'],'7951698024000')
    def test_exact_2022_telescope(self):
        out=exact_reconciliation();q=out['conditionally_anchored_individual_lines_Hz'];a,b,c=[int(q[k]) for k in ['anchor_J1_0_from_pinned_2011_source_nominal','derived_J2_1','derived_J3_2']];self.assertEqual(a+b,8006533168000);self.assertEqual(b+c,13283245098000)
    def test_source_E_vs_P_different(self):
        rows=exact_reconciliation()['measured_combinations'];self.assertNotEqual(rows[0]['source_internal_energy_minus_photon_combo_Hz'],'0');self.assertNotEqual(rows[1]['source_internal_energy_minus_photon_combo_Hz'],'0')
    def test_source_tamper_A_rejected(self):
        with tempfile.TemporaryDirectory() as x:
            dir=Path(x);(dir/'data').mkdir();
            for p in ['LAB_ANCHORS.json','PR156_SOURCE_TRANSCRIPTION.json']:(dir/'data'/p).write_bytes((ROOT/'data'/p).read_bytes())
            f=dir/'data/PR156_SOURCE_TRANSCRIPTION.json';v=json.loads(f.read_text());v['rows'][1]['A_s_inv']='1e-9';f.write_text(json.dumps(v))
            with self.assertRaisesRegex(ValueError,'source photon or A'):read_verified_inputs(dir)
    def test_source_tamper_level_gap_rejected(self):
        with tempfile.TemporaryDirectory() as x:
            dir=Path(x);(dir/'data').mkdir()
            for p in ['LAB_ANCHORS.json','PR156_SOURCE_TRANSCRIPTION.json']:(dir/'data'/p).write_bytes((ROOT/'data'/p).read_bytes())
            f=dir/'data/PR156_SOURCE_TRANSCRIPTION.json';v=json.loads(f.read_text());v['rows'][2]['nu_E_Hz']='1/1';f.write_text(json.dumps(v))
            with self.assertRaisesRegex(ValueError,'source photon or A'):read_verified_inputs(dir)
    def test_lab_tamper_value_rejected(self):
        with tempfile.TemporaryDirectory() as x:
            dir=Path(x);(dir/'data').mkdir();
            for p in ['LAB_ANCHORS.json','PR156_SOURCE_TRANSCRIPTION.json']:(dir/'data'/p).write_bytes((ROOT/'data'/p).read_bytes())
            f=dir/'data/LAB_ANCHORS.json';v=json.loads(f.read_text());v['measurements'][0]['nominal_kHz']='8006533169';f.write_text(json.dumps(v))
            with self.assertRaisesRegex(ValueError,'experimental value'):read_verified_inputs(dir)
    def test_energy_and_lifetime(self):
        table=photon_power_and_thermo()['radiative_lines'];r=table[0];self.assertAlmostEqual(float(Decimal(r['photon_energy_J'])),float(H*Decimal(2674986094000)),places=43);self.assertGreater(float(r['spontaneous_lifetime_s']),0)
    def test_photon_A_scaling(self):
        table=photon_power_and_thermo()['radiative_lines'];
        for r in table:self.assertEqual(Decimal(r['photon_power_per_one_excited_molecule_W']),Decimal(r['photon_energy_J'])*Decimal(r['A_s_inv']))
    def test_photon_wavelength_identity(self):
        table=photon_power_and_thermo()['radiative_lines'];
        for r in table:self.assertAlmostEqual(float(Decimal(r['wavelength_m'])*Decimal(r['printed_photon_frequency_Hz'])),float(C),places=4)
    def test_lte_temperature_monotonic(self):
        r=photon_power_and_thermo()['measured_based_LTE_ratios'];self.assertEqual([x['T_K'] for x in r],['50','100','200']);
        for key in ['LTE_nJ2_over_nJ0_from_measured_E2-E0','LTE_nJ3_over_nJ1_from_measured_E3-E1']:
            self.assertLess(Decimal(r[0][key]),Decimal(r[1][key]));self.assertLess(Decimal(r[1][key]),Decimal(r[2][key]))
    def test_blackbody_occupation_monotonic(self):
        rows=photon_power_and_thermo()['radiative_lines'];
        for r in rows:self.assertLess(Decimal(r['blackbody_occupation_at_50K']),Decimal(r['blackbody_occupation_at_100K']))
    def test_no_promotion(self):
        self.assertEqual(exact_reconciliation()['production'],'HOLD');self.assertEqual(exact_reconciliation()['REC_physical_DAG'],'0/313 (+0)');self.assertEqual( exact_reconciliation()['sources']['CDMS_2011_V2_RAW'], 'NOT_ACQUIRED')
    def test_export(self):
        out,phy=write_outputs();self.assertEqual(len(phy['radiative_lines']),8);self.assertTrue((ROOT/'evidence/PHOTON_PHYSICAL_TABLE.csv').is_file())

if __name__=='__main__':unittest.main()
