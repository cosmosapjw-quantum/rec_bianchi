"""Saved-data regressions; these tests never launch a science history."""
import copy
import json
import unittest
import run_epochs as subject


class EpochTests(unittest.TestCase):
    def setUp(self):
        self.c = subject.contract()
        self.b = json.loads((subject.HERE / 'evidence/baseline.json').read_text())
        self.r = json.loads((subject.HERE / 'evidence/refined.json').read_text())

    def test_frozen_input(self):
        subject.base.checked_members(subject.ROOT / self.c['archive'], self.c)

    def test_saved_mapping_and_cubic(self):
        subject.validate_epochs(self.b, self.c, 'baseline')
        subject.validate_epochs(self.r, self.c, 'refined')
        subject.compare(self.b, self.r, self.c)

    def test_wrong_epoch(self):
        self.b[0]['endpoint']['z'] = 19.0
        with self.assertRaisesRegex(ValueError, 'ENDPOINT_Z_MISMATCH'):
            subject.validate_epochs(self.b, self.c, 'baseline')

    def test_wrong_cosmology(self):
        self.b[0]['cosmology']['omh2'] = 0.14
        with self.assertRaisesRegex(ValueError, 'COSMOLOGY_MISMATCH'):
            subject.validate_epochs(self.b, self.c, 'baseline')

    def test_temperature_ratio_rejected(self):
        e = self.b[0]['endpoint']
        e['Tm_K'] /= e['Tgamma_K']
        with self.assertRaisesRegex(ValueError, 'CUBIC_EXPORT_MISMATCH:Tm_K'):
            subject.validate_epochs(self.b, self.c, 'baseline')

    def test_helium_mapping_rejected(self):
        self.b[0]['endpoint']['xHeII'] = 0.01
        with self.assertRaisesRegex(ValueError, 'MAPPING_MISMATCH:xHeII'):
            subject.validate_epochs(self.b, self.c, 'baseline')

    def test_excess_refinement_error(self):
        self.r[1]['endpoint']['xe_per_H'] *= 1.01
        with self.assertRaisesRegex(ValueError, 'ENDPOINT_REFINEMENT_FAILED'):
            subject.compare(self.b, self.r, self.c)

    def test_wrong_dlna(self):
        self.b[0]['grid']['DLNA'] *= 2
        with self.assertRaisesRegex(ValueError, 'DLNA_MISMATCH'):
            subject.validate_epochs(self.b, self.c, 'baseline')


if __name__ == '__main__':
    unittest.main()
