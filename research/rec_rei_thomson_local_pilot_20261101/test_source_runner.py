#!/usr/bin/env python3
"""Run from the REC Git checkout; exact source-only test skips outside it."""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from source_runner import load,direction,moments,generate

class TestThomsonLocalBridge(unittest.TestCase):
    def test_qzero_isotropic(self):
        self.assertEqual(moments(0.),(1.,0.))
    def test_wolfram_moments(self):
        refs={-.01:(1.0000304626831134,.02011573906799715),
              -.005:(1.0000075574867307,.010028751537350536),
               .005:(1.0000074431963408,-.009971605628097748),
               .01:(1.0000295482477536,-.01988711879789478)}
        for q,(m,a) in refs.items():
            with self.subTest(q=q):
                x,y=moments(q)
                self.assertLess(abs(x-m),3e-12)
                self.assertLess(abs(y-a),3e-12)
    def test_sign_and_monotonicity(self):
        self.assertGreater(moments(-.01)[1],0.)
        self.assertLess(moments(.01)[1],0.)
        for q in [-.01,-.005,0.,.005,.01]:
            for j in range(21): self.assertGreater(direction(q,j/20.),0.)
    def test_out_of_domain_fails(self):
        with self.assertRaises(ValueError): direction(-1.,1.)
    def test_source_byte_lock(self):
        with tempfile.TemporaryDirectory() as td:
            bad=Path(td)/'bad.json'
            bad.write_text(json.dumps({'zbar':20.}),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Git blob'): load(bad)
    @unittest.skipUnless((ROOT/'research/rec_r3c_rei_bridge_20261015/REI_CONDITIONAL_BOUNDARY.json').exists(),
                         'exact original REC checkout unavailable in local sandbox')
    def test_exact_source_end_to_end(self):
        with tempfile.TemporaryDirectory() as td:
            status=generate(ROOT,td)
            self.assertTrue(status['exact_source_git_blob_loaded'])
            self.assertFalse(status['accepted_native_REI_input'])
            self.assertEqual(status['directional_rows'],210)
            self.assertEqual(status['angular_moment_rows'],10)
            self.assertEqual(status['canonical_REI'],'28/88')
            self.assertEqual(status['physical_REC_H5'],'0/313')

if __name__=='__main__': unittest.main()
