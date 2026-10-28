"""Targeted independent-review regressions; no historical stationarity replay."""
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from precision_audit import parse_spcat_line, half_quantum, audit


def row(frequency='2674986.0000', uncertainty='0.0300', elo='0.0000', tag=3501):
    return (f'{frequency:>13}{uncertainty:>8}{"-9.1234":>8}{2:2d}'
            f'{elo:>10}{3:3d}{tag:7d}{101:4d}' + '  1  0'.ljust(24))


class ReviewRegressionTests(unittest.TestCase):
    def test_fresh_output_parent(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / 'results' / 'certificate.json'
            p = subprocess.run([sys.executable, str(ROOT/'precision_audit.py'), '--output', str(output)],capture_output=True,text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(output.read_text())['rounding_only_fail_count'], 7)

    def test_nonfinite_spcat_fields(self):
        for field in ('frequency', 'uncertainty', 'elo'):
            for value in ('Infinity', '-Inf', 'NaN', 'sNaN'):
                with self.subTest(field=field,value=value):
                    with self.assertRaisesRegex(ValueError, 'nonfinite'):
                        parse_spcat_line(row(**{field:value}))

    def test_valid_and_measured_tag_preserved(self):
        self.assertFalse(parse_spcat_line(row())['measured_tag'])
        self.assertTrue(parse_spcat_line(row(tag=-3501))['measured_tag'])
        self.assertEqual(parse_spcat_line(row())['frequency_literal'], '2674986.0000')

    def test_nonfinite_printed_decimals(self):
        for literal in ('Infinity', 'NaN', 'sNaN'):
            with self.assertRaises(ValueError): half_quantum(literal)
        source = json.loads((ROOT/'public_print_transcription.json').read_text())
        source['levels'][1]['w_cm_minus_1']='Infinity'
        with self.assertRaisesRegex(ValueError, 'nonfinite'):audit(source['levels'],source['radiative_lines'])

if __name__=='__main__': unittest.main()
