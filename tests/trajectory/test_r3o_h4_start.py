"""Stdlib tests for the independent h4 start; no pytest installation needed.

Run: PYTHONPATH=src python -m unittest discover -s tests/trajectory -p test_r3o_h4_start.py -v
The native C/Python trajectory comparison has its own raw CLI evidence.
"""
from dataclasses import FrozenInstanceError, replace
import math
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
from full_bianchi_hyrec.trajectory import primordial_2012_refined_start as h2
from full_bianchi_hyrec.trajectory import primordial_2012_quarter_start as h4
from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
    _source_edges, causal_incoming_from_accepted_histories,
)
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table
from full_bianchi_hyrec.trajectory.primitive_rates import OriginalHyRecPrimitiveRateTable
from verify_r3o_h4_start import parse_native, prepare_source, save_npz_new, sha

ZIP = ROOT / 'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'


class QuarterStartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = h4.QuarterStartCosmology()
        cls.helium = h4.integrate_helium_stages(cls.c)
        cls.source = h4.make_hmla_source(cls.c, OriginalHyRecPrimitiveRateTable.from_archive(ZIP))
        cls.full = h4.integrate_full_start(cls.helium, cls.c, cls.source, accepted_steps=2)

    def test_quarter_clock_and_h2_defaults_are_separate(self):
        self.assertEqual(h4.DLNA, 8.49e-5/4)
        self.assertEqual(h4.DLNA.hex(), '0x1.6418ae4caf054p-16')
        self.assertEqual(self.c.izH0, 72892)
        self.assertEqual(len(self.helium.iz), 72893)
        self.assertEqual(h2.DLNA, 4.245e-5)
        self.assertEqual(h2.SOURCE_DLNA, 4.245e-5)
        self.assertEqual(h2.HyRec2012Cosmology().izH0, 36446)
        self.assertEqual(h2.integrate_helium_stages.__defaults__[0].izH0, 36446)
        self.assertEqual(self.c.redshift(72892), h2.HyRec2012Cosmology().redshift(36446))
        self.assertIsNot(h4.integrate_helium_stages.__globals__, h2.integrate_helium_stages.__globals__)
        with self.assertRaises(FrozenInstanceError):
            self.c.T0_K = 3.
        with self.assertRaisesRegex(ValueError, 'frozen original cosmology'):
            h4.QuarterStartCosmology(T0_K=3.)
        for index in (-1, .5, math.nan, True):
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, 'integer source index'):
                self.c.redshift(index)

    def test_helium_source_closure_ledgers_and_all_grid_rows(self):
        he = self.helium
        stages = np.array(he.stage)
        first = int(np.flatnonzero(stages == 'HeII_RECOMBINATION')[0])
        self.assertGreater(first, 4)
        self.assertTrue(np.all(stages[:first] == 'HeIII_SAHA'))
        self.assertIn('POST_SAHA', he.update_method)
        self.assertIn('SOURCE_PREDICTOR', he.update_method)
        # Closed-form initial Saha root; no C or checkpoint state enters it.
        z = 8000.; Tr = 2.7255*(1.+z); nH = self.c.nH0_m3*(1.+z)**3
        s = 2.414194e21*Tr*math.sqrt(Tr)*math.exp(-631462.7/Tr)/nH
        x3 = 2*s*self.c.fHe/(1+s+self.c.fHe)/(1+math.sqrt(1+4*s*self.c.fHe/(1+s+self.c.fHe)**2))
        self.assertLess(abs(he.xe[0]-(1+self.c.fHe+x3)), 3.e-16)
        self.assertLess(np.max(np.abs(np.array(he.xHII)+he.xHeII+2*np.array(he.xHeIII)-he.xe)), 5.e-13)
        self.assertLess(np.max(np.abs(np.array(he.xHeI)+he.xHeII+np.array(he.xHeIII)-self.c.fHe)), 5.e-13)
        np.testing.assert_array_equal(he.iz, np.arange(72893))
        self.assertTrue(all(z == self.c.redshift(i) for i, z in enumerate(he.z)))

    def test_predictor_seed_clock_and_wrong_h2_denominator_mutation(self):
        he = self.helium; i = 72892; seed = h4.source_native_derivative_seeds(he)
        np.testing.assert_array_equal(seed[0], [he.helium_rhs_dln_a[i-1], he.helium_rhs_dln_a[i]])
        expected = [(he.xe[i-1]-he.xe[i-3])/2./h4.DLNA-seed[0, 0],
                    (he.xe[i]-he.xe[i-2])/2./h4.DLNA-seed[0, 1]]
        np.testing.assert_array_equal(seed[1], expected)
        wrong = (he.xe[i]-he.xe[i-2])/2./h2.DLNA-seed[0, 1]
        self.assertNotEqual(seed[1, 1], wrong)
        with self.assertRaisesRegex(ValueError, 'grid/source identity'):
            replace(he, dlna=h2.DLNA)

    def test_h2_inputs_and_unbounded_steps_rejected_before_atomic_work(self):
        with self.assertRaisesRegex(ValueError, 'independent h4 cosmology'):
            h4.integrate_helium_stages(h2.HyRec2012Cosmology())
        with self.assertRaisesRegex(ValueError, 'independent h4 cosmology'):
            h4.integrate_full_start(self.helium, h2.HyRec2012Cosmology(), None)
        with self.assertRaisesRegex(ValueError, 'no h2 checkpoint'):
            h4.integrate_full_start(SimpleNamespace(iz=[36446]), self.c, None)
        for n in (0, -1, 9, True, 1.5):
            with self.subTest(n=n), self.assertRaisesRegex(ValueError, 'integer in'):
                h4.integrate_full_start(None, self.c, None, accepted_steps=n)

    def test_full_prefix_and_two_native_rhs_memories(self):
        r = self.full
        np.testing.assert_array_equal(r.iz, [72892, 72893, 72894])
        self.assertEqual(r.virtual_out.shape, (311, 2))
        self.assertEqual(r.average_virtual.shape, (311, 2))
        self.assertEqual(r.lyman_out.shape, (3, 2))
        self.assertEqual(r.full_evaluations, 8)
        np.testing.assert_array_equal(r.initial_predictor, h4.source_native_derivative_seeds(self.helium))
        np.testing.assert_array_equal(r.final_predictor[0], r.helium_rhs_dln_a)
        np.testing.assert_array_equal(r.final_predictor[1], r.hydrogen_rhs_dln_a)
        self.assertLess(np.max(r.matrix_residual), 2.e-10)
        for name in ('virtual_out', 'average_virtual', 'lyman_out', 'xe', 'final_predictor'):
            with self.subTest(name=name):
                self.assertFalse(getattr(r, name).flags.writeable)

    def test_one_step_keeps_previous_source_seed(self):
        r = h4.integrate_full_start(self.helium, self.c, self.source, accepted_steps=1)
        self.assertEqual(r.full_evaluations, 4)
        np.testing.assert_array_equal(r.final_predictor[:, 0], r.initial_predictor[:, 1])
        np.testing.assert_array_equal(r.final_predictor[:, 1], [r.helium_rhs_dln_a[0], r.hydrogen_rhs_dln_a[0]])

    def test_callback_has_only_detached_readonly_past_and_cannot_supply_state(self):
        class ReadOnlyObserved(RuntimeError):
            pass
        def callback(j, z, h, he, tm, vpast, lpast):
            self.assertFalse(vpast.flags.writeable)
            self.assertFalse(lpast.flags.writeable)
            self.assertEqual(vpast.shape, (311, j))
            self.assertEqual(lpast.shape, (3, j))
            raise ReadOnlyObserved()
        with self.assertRaises(ReadOnlyObserved):
            h4.integrate_full_start(self.helium, self.c, self.source, accepted_steps=1, common_input_oracle=callback)
        with self.assertRaisesRegex(ArithmeticError, 'NONFINITE'):
            h4.integrate_full_start(self.helium, self.c, self.source, accepted_steps=1,
                                   common_input_oracle=lambda *a: {'rhs': math.nan, 'xe': .1, 'Tm_K': .1})

    def test_mismatched_atomic_cosmology_rejected(self):
        wrong = replace(self.source, omega_b_h2=.024)
        with self.assertRaisesRegex(ValueError, 'atomic source cosmology'):
            h4.integrate_full_start(self.helium, self.c, wrong, accepted_steps=1)

    def test_quarter_first_active_photon_edge_and_future_rejection(self):
        energy = _canonical_twophoton_table(self.source.table.archive_path).energy_eV
        _, target, emit = _source_edges(energy)
        first = math.ceil(float(np.min(np.log(emit/target)))/h4.DLNA)
        z0 = self.c.redshift(self.c.izH0)
        def incoming(j, shift=0):
            return causal_incoming_from_accepted_histories(
                energies_eV=energy, virtual_history=np.ones((311, j)), lyman_history=np.ones((3, j)),
                z_start=z0, iz=j, z_face=self.c.redshift(self.c.izH0+j+shift), dlna=h4.DLNA, shear_q=0.)
        before = incoming(first-1); after = incoming(first)
        self.assertFalse(np.any(before.virtual_distortion))
        self.assertFalse(np.any(before.lya_lyb_incoming_distortion))
        self.assertTrue(np.any(after.virtual_distortion) or np.any(after.lya_lyb_incoming_distortion))
        eta0 = -math.log1p(z0); active = after.retarded_eta >= eta0
        k = np.floor((after.retarded_eta[active]-eta0)/h4.DLNA).astype(int)
        self.assertTrue(np.all(k >= 0) and np.all(k+1 <= first-1))
        with self.assertRaisesRegex(ValueError, 'current/unaccepted future'):
            incoming(first, 20)

    def test_exact_temporary_token_diff_and_frozen_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, manifest = prepare_source(ZIP, Path(tmp)/'source')
            changed = [p for p, h in manifest['original_member_sha256'].items()
                       if manifest['modified_member_sha256'][p] != h]
            self.assertEqual(changed, ['HyRec/hyrec_params.h'])
            self.assertIn(b'#define DLNA          (8.49e-5/4.)', (src/'hyrec_params.h').read_bytes())
            self.assertEqual(sha(ZIP), h4.PINNED_ZIP_SHA256)
            with self.assertRaises(FileExistsError):
                prepare_source(ZIP, Path(tmp)/'source')
            bad = Path(tmp)/'bad.zip'; bad.write_bytes(b'unreviewed')
            with self.assertRaisesRegex(ValueError, 'ZIP_SHA_MISMATCH'):
                prepare_source(bad, Path(tmp)/'bad_source')
            self.assertFalse((Path(tmp)/'bad_source').exists())

    def test_native_reader_contamination_incomplete_clock_and_footer(self):
        cases = [('', 'INCOMPLETE_START'), ('MEM,-1,nan,0,0,0\n', 'MEMORY_NONFINITE'),
                 ('V,0,311,0\n', 'SPECTRUM_NONFINITE'), ('V,0,0,0\nV,0,0,0\n', 'SPECTRUM_NONFINITE'),
                 ('DONE,72893,1,2.1225e-5\nV,0,0,0\n', 'OUTPUT_AFTER_DONE'),
                 ('mystery,0\n', 'UNKNOWN_OR_MALFORMED')]
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'raw.csv'
            for tail, match in cases:
                with self.subTest(tail=tail):
                    p.write_text('META,2.1225e-5,72892,46780,1\n'+tail)
                    with self.assertRaisesRegex(ValueError, match):
                        parse_native(p, 1)
            p.write_text('META,4.245e-5,36446,23390,8\n')
            with self.assertRaisesRegex(ValueError, 'H4_GRID_IDENTITY'):
                parse_native(p, 8)

    def test_checkpoint_memories_roundtrip_no_pickle_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'checkpoint.npz'
            data = {name: getattr(self.full, name) for name in self.full.__dataclass_fields__}
            digest = save_npz_new(p, data)
            with np.load(p, allow_pickle=False) as saved:
                self.assertEqual(float(saved['dlna']), h4.DLNA)
                np.testing.assert_array_equal(saved['final_predictor'], self.full.final_predictor)
                np.testing.assert_array_equal(saved['virtual_out'], self.full.virtual_out)
            with self.assertRaises(FileExistsError):
                save_npz_new(p, data)
            self.assertEqual(sha(p), digest)


if __name__ == '__main__':
    unittest.main()
