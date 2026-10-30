from pathlib import Path
import sys,unittest
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'src'))
from density_degeneracy import compute

class DensitySourceDegeneracyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.rows=compute(R)
    def test_four_source_temperatures(self):
        self.assertEqual([r['Tgas_K'] for r in self.rows],[1000.,2000.,3000.,4000.])
    def test_physical_density_brackets(self):
        self.assertTrue(all(1.8<=r['density_factor']<=2.5 for r in self.rows))
    def test_first_calibration(self):
        self.assertAlmostEqual(self.rows[0]['density_factor'],2.4578830546851775,delta=2e-10)
    def test_matched_R9_over_R7(self):
        self.assertTrue(all(abs(r['alternate_R9_over_R7']/r['standard_at_equivalent_R9_over_R7']-1)<1e-9 for r in self.rows))
    def test_heldout_ratio_breaks_degeneracy(self):
        self.assertAlmostEqual(self.rows[0]['heldout_R9_over_R4_fractional_source_difference'],-0.21755691558461276,delta=2e-10)
        self.assertTrue(all(r['heldout_R9_over_R4_fractional_source_difference']<-0.03 for r in self.rows))

if __name__=='__main__':unittest.main()
