import json, sys, unittest
from pathlib import Path
from decimal import Decimal
from fractions import Fraction

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from field_semantics import parse_lamda_hd,frequency_comparison,finite_decimal,ORIGINAL_HD_SHA256
SOURCE=(ROOT/'source_private'/'hd.dat').read_bytes()

def mutate(a,b):
    assert a.encode() in SOURCE
    return SOURCE.replace(a.encode(),b.encode(),1)

def q(x): return Fraction(x)

class SourceAndSemanticContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parsed=parse_lamda_hd(SOURCE)
        cls.result=frequency_comparison(cls.parsed)

    def test_raw_identity_and_core(self):
        self.assertTrue(self.parsed['raw_verified_this_execution'])
        self.assertEqual(self.parsed['source_sha256'],ORIGINAL_HD_SHA256)
        self.assertEqual(self.parsed['source_bytes'],2289)
        self.assertEqual(len(self.parsed['core']['levels']),9)
        self.assertEqual(len(self.parsed['core']['radiative']),8)
        self.assertEqual(len(self.parsed['core']['partners']),2)
        self.assertEqual(sum(len(p['collisions']) for p in self.parsed['core']['partners']),18)

    def test_frequency_metadata_mutation_invariant_core(self):
        x=parse_lamda_hd(mutate('5331.56195140','5331.56195141'),require_original=False)
        self.assertEqual(x['core_sha256'],self.parsed['core_sha256'])
        self.assertNotEqual(frequency_comparison(x)['lines'][1]['nu_P_over_nu_E_exact'],
                            self.result['lines'][1]['nu_P_over_nu_E_exact'])
        self.assertFalse(x['raw_verified_this_execution'])

    def test_upper_temperature_metadata_mutation_invariant_core(self):
        x=parse_lamda_hd(mutate('2674.98609400   128.4','2674.98609400   128.5'),require_original=False)
        self.assertEqual(x['core_sha256'],self.parsed['core_sha256'])
        self.assertNotEqual(x['optional_line_metadata'],self.parsed['optional_line_metadata'])

    def test_optional_frequency_absence_keeps_core(self):
        x=parse_lamda_hd(mutate('2674.98609400   128.4',''),require_original=False)
        self.assertEqual(x['core_sha256'],self.parsed['core_sha256'])
        self.assertFalse(frequency_comparison(x)['lines'][0]['printed_nu_available'])
        self.assertTrue(frequency_comparison(x)['lines'][1]['printed_nu_available'])

    def test_mutation_original_source_pin_fails(self):
        with self.assertRaisesRegex(ValueError,'immutable'):
            parse_lamda_hd(mutate('5331.56195140','5331.56195141'))

    def test_core_changes_when_A_changes(self):
        x=parse_lamda_hd(mutate('5.159E-07','5.160E-07'),require_original=False)
        self.assertNotEqual(x['core_sha256'],self.parsed['core_sha256'])

    def test_core_changes_when_collision_changes(self):
        x=parse_lamda_hd(mutate('1.6e-12','1.7e-12'),require_original=False)
        self.assertNotEqual(x['core_sha256'],self.parsed['core_sha256'])

    def test_reject_nonfinite_optional_frequency(self):
        with self.assertRaises(ValueError):
            parse_lamda_hd(mutate('5331.56195140','Infinity'),require_original=False)

    def test_reject_negative_A(self):
        with self.assertRaises(ValueError):
            parse_lamda_hd(mutate('5.159E-07','-5.159E-07'),require_original=False)

    def test_reject_collision_partner_relabel(self):
        with self.assertRaises(ValueError):
            parse_lamda_hd(mutate('2 HD-pH2','4 HD-pH2'),require_original=False)

    def test_exact_ratios(self):
        for x in self.result['lines']:
            r=q(x['nu_P_over_nu_E_exact'])
            self.assertEqual(q(x['alpha_peak_P_over_E_exact']),1/r**3)
            self.assertEqual(q(x['S_peak_P_over_E_exact']),r**3)
            self.assertEqual(q(x['integrated_j_P_over_E_exact']),r)
            self.assertEqual(x['j_peak_P_over_E_exact'],'1/1')

    def test_maximum_is_J2(self):
        rows=self.result['lines']
        idx=max(range(8),key=lambda i:abs(q(rows[i]['alpha_peak_P_over_E_exact'])-1))
        self.assertEqual(idx,1)
        self.assertEqual(len(rows),8)
        self.assertEqual(sum(abs(q(x['nu_P_over_nu_E_exact'])-1)>Fraction(1,10**9) for x in rows),6)

    def test_source_energy_sign(self):
        # nu_E - nu_P positive => alpha_P > alpha_E, because opacity ~ nu^-3
        for row in self.result['lines']:
            delta=q(row['delta_nu_E_minus_P_Hz_exact'])
            da=q(row['alpha_peak_P_over_E_exact'])-1
            self.assertEqual((delta>0)-(delta<0),(da>0)-(da<0))

    def test_literal_parser_rejects_inf_nan(self):
        for s in ('Infinity','NaN','1e9999999999999999999','1/2','abc',''):
            with self.subTest(s=s):
                with self.assertRaises((ValueError,OverflowError,MemoryError)):
                    finite_decimal(s)

    def test_exact_vs_independent_high_precision_direct_kernel(self):
        import mpmath as mp
        with mp.workdps(90):
            h=mp.mpf('6.62607015e-34'); c=mp.mpf('299792458'); k=mp.mpf('1.380649e-23')
            sigma_v=mp.mpf('1200'); T=mp.mpf('100')
            for j in (1,2,6,8):
                row=self.result['lines'][j-1]
                up=self.parsed['core']['levels'][j];lo=self.parsed['core']['levels'][j-1]
                A=mp.mpf(self.parsed['core']['radiative'][j-1]['A_s_inv'])
                dE=h*c*100*(mp.mpf(up['w_cm_inv'])-mp.mpf(lo['w_cm_inv']))
                nlo=mp.mpf(1);nup=mp.mpf(up['g'])/mp.mpf(lo['g'])*mp.exp(-dE/(k*T))
                def kernel(nu):
                    phi=c/(mp.sqrt(2*mp.pi)*nu*sigma_v)
                    Bul=A*c*c/(2*h*nu**3);Blu=Bul*mp.mpf(up['g'])/mp.mpf(lo['g'])
                    emiss=h*nu/(4*mp.pi)*nup*A*phi
                    absorb=h*nu/(4*mp.pi)*(nlo*Blu-nup*Bul)*phi
                    return emiss,absorb
                nu_E=dE/h;nu_P=mp.mpf(self.parsed['optional_line_metadata'][j-1]['nu_GHz'])*10**9
                jE,aE=kernel(nu_E);jP,aP=kernel(nu_P)
                target=q(row['alpha_peak_P_over_E_exact'])
                targ=mp.mpf(target.numerator)/mp.mpf(target.denominator)
                self.assertLess(abs(jP/jE-1),mp.mpf('1e-80'))
                self.assertLess(abs(aP/aE-targ),mp.mpf('1e-78'))

    def test_fixed_frequency_width_counterexample(self):
        # At fixed sigma_nu, phi0 is constant, so j_peak(P)/j_peak(E)=nuP/nuE, not 1.
        row=self.result['lines'][1]
        self.assertNotEqual(q(row['nu_P_over_nu_E_exact']),1)

if __name__=='__main__': unittest.main()
