"""Source-pinned matrix checks and independent Decimal energy ledger oracle."""
import hashlib,json,os,sys,unittest
from decimal import Decimal,localcontext
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from audit_consumer import H,per_event,SOURCE_SHA

class MatrixContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads((ROOT/'CALLSITE_MATRIX.json').read_text())
    def test_unique_paths_and_shas(self):
        e=self.m['entries'];self.assertEqual(len(e),9)
        self.assertEqual(len(set((x['owner'],x['path']) for x in e)),9)
        self.assertTrue(all(len(x['git_blob_sha'])==40 for x in e))
    def test_no_cross_repo_import_or_physical_promotion(self):
        self.assertFalse(self.m['cross_repo_import'])
        self.assertFalse(self.m['physical_promotion'])
        self.assertEqual(self.m['canonical'],'28/88 (+0)')
    def test_scope_not_overclaimed(self):
        self.assertIn('not an exhaustive',self.m['scope'])
        self.assertIn('not a proof of absence',self.m['not_demonstrated'])
    def test_only_two_actual_hd_diagnostics(self):
        self.assertEqual(len(self.m['confirmed_direct_HD_consumers']),2)
        self.assertEqual(sum('DIRECT_IMPORTED' in e['verification'] for e in self.m['entries']),2)

SOURCE=Path(os.getenv('REC_HD_SOURCE_PATH',str(ROOT/'parent/source_private/hd.dat')))
@unittest.skipUnless(SOURCE.exists(),'private source unavailable')
class IndependentDecimal(unittest.TestCase):
    def test_raw_literal_oracle_8(self):
        src=SOURCE.read_bytes()
        self.assertEqual(hashlib.sha256(src).hexdigest(),SOURCE_SHA)
        s=src.decode('ascii').splitlines()
        a=s.index('!LEVEL + ENERGIES(cm^-1) + WEIGHT + J (or other quantum numbers)')+1
        b=s.index('!NUMBER OF RADIATIVE TRANSITIONS')
        w=[line.split()[1] for line in s[a:b]]
        a=s.index('!TRANS + U + L + A(s^-1) + FREQ(GHz) + E_u/k(K)')+1
        b=s.index('!NUMBER OF COLL PARTNERS')
        nu=[line.split()[4] for line in s[a:b]]
        with localcontext() as ctx:
            ctx.prec=90
            h=Decimal('6.62607015e-34');c=Decimal('299792458')
            for j in range(1,9):
                e=h*(Decimal('1e9')*Decimal(nu[j-1])-Decimal(100)*c*(Decimal(w[j])-Decimal(w[j-1])))
                exact=Fraction(per_event(w[j],w[j-1],nu[j-1])['matter_plus_radiation_J_per_down_event'])
                self.assertEqual(Fraction(e),exact)

if __name__=='__main__':unittest.main()
