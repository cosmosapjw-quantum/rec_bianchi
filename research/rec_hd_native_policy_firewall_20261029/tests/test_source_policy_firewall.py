import sys, unittest
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import source_policy_firewall as s

# Public, immutable PR156 result rows, not the raw private LAMDA file.
# (nu_E numerator, denominator, nu_P numerator, denominator): J=1->0 ... J=8->7.
FROZEN_PUBLIC_ROWS = [
 (13374930469958794919,5000000,2674986094000,1),
 (1332890250930289919,250000,5331561951400,1),
 (19879323162796857291,2500000,7951728180800,1),
 (52591535167862954543,5000000,10518307081200,1),
 (13015354732561910729,1000000,13015353487100,1),
 (38571409466318598107,2500000,15428565614100,1),
 (22182121643381812819,1250000,17745695903500,1),
 (49892404686912474057,2500000,19956961867900,1),
]

class FakeAdapter:
    def __init__(self):
        self.calls=[]
    def transition_qualification(self,data,line_id):
        self.calls.append(('qualification',line_id))
        eu,ed,pu,pd=FROZEN_PUBLIC_ROWS[line_id-1]
        gap=abs(Fraction(eu,ed)-Fraction(pu,pd))
        return dict(absolute_gap_Hz=str(Decimal(gap.numerator)/Decimal(gap.denominator)),
                    consistent_internal_energy_photon_binding=gap<=35)
    def require_energy_frequency_bridge(self,data,line_id):
        self.calls.append(('owner_gate',line_id))
        if line_id != 1:
            raise ValueError('original owner rejects')
        return SimpleNamespace(id=line_id)
    def line_coefficients(self,data,line_id,*args):
        self.calls.append(('actual_coefficients',line_id))
        return {'j_nu':123,'alpha_nu':456}

class TestPolicyFirewall(unittest.TestCase):
    def setUp(self):
        self.data=SimpleNamespace(source_sha256=s.LAMDA_SHA256, source_bytes=s.LAMDA_BYTES)
        self.a=FakeAdapter()
    def test_actual_pinned_gap_gate_one_pass_seven_fail(self):
        passes=[]
        for j,(eu,ed,pu,pd) in enumerate(FROZEN_PUBLIC_ROWS,1):
            passes.append(abs(Fraction(eu,ed)-Fraction(pu,pd)) <= 35)
        self.assertEqual(passes,[True,False,False,False,False,False,False,False])
    def test_one_scoped_success(self):
        r=s._strict_bridge_core(self.a,self.data,1)
        self.assertEqual(r["line_id"],1)
        self.assertEqual([x[0] for x in self.a.calls],['qualification','owner_gate'])
    def test_seven_fail_closed_before_coefficients(self):
        for line_id in range(2,9):
            with self.subTest(line_id=line_id):
                self.a.calls=[]
                with self.assertRaises(s.EnergyBridgeHeld):
                    s._strict_bridge_core(self.a,self.data,line_id)
                self.assertEqual(self.a.calls,[('qualification',line_id)])
    def test_bad_source_hash(self):
        self.data.source_sha256='wrong'
        with self.assertRaises(s.SourcePinError):s._strict_bridge_core(self.a,self.data,1)
        self.assertFalse(self.a.calls)
    def test_bad_source_bytes(self):
        self.data.source_bytes=2288
        with self.assertRaises(s.SourcePinError):s._strict_bridge_core(self.a,self.data,1)
    def test_nonint_identifiers_fail(self):
        for line in (True,1.0,'1'):
            with self.subTest(line=line),self.assertRaises(s.EnergyBridgeHeld):s._strict_bridge_core(self.a,self.data,line)
    def test_malformed_gap_fails_closed(self):
        class Bad(FakeAdapter):
            def transition_qualification(self,data,line_id):return {'absolute_gap_Hz':'NaN','consistent_internal_energy_photon_binding':True}
        with self.assertRaises(s.EnergyBridgeHeld):s._strict_bridge_core(Bad(),self.data,1)
    def test_owner_disagreement_fails(self):
        class Bad(FakeAdapter):
            def require_energy_frequency_bridge(self,data,line_id):raise RuntimeError('held')
        with self.assertRaises(s.EnergyBridgeHeld):s._strict_bridge_core(Bad(),self.data,1)
    def test_no_pseudo_source_identity_from_label_only(self):
        # A mock can forge `source_sha256`; the public byte validator must reject it.
        for raw in (b"", b"fake", "not bytes", bytearray(b"a"*2289)):
            with self.subTest(kind=type(raw).__name__),self.assertRaises(s.SourcePinError):
                s.validate_pinned_raw_bytes(raw)
    def test_public_bridge_rejects_diagnostic_mock_even_with_source_labels(self):
        with self.assertRaises(s.SourcePinError):s.strict_bridge(self.a,self.data,1)
        self.assertEqual(self.a.calls,[])
    def test_git_blob_hash(self):
        self.assertEqual(s.git_blob_sha1(b'abc'),'f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f')
    def test_public_gate_rejects_unpinned_mock_despite_fake_true_gate(self):
        with self.assertRaises(s.SourcePinError):
            s.guarded_line_coefficients(self.a,self.data,1,1,2,3)
        self.assertFalse(self.a.calls)
    def test_adapter_pin_rejects_nonmatching_file(self):
        with self.assertRaises(s.SourcePinError):s.load_pinned_adapter(__file__)
    def test_fixed_phi_exact_sensitivity(self):
        nu=Fraction(5331561951400,1);eps=Fraction(1000000,1)
        r=s.exact_fixed_phi_policy_ratios(nu,eps)
        x=(nu+eps)/nu
        self.assertEqual(r['B_ul'],x**(-3))
        self.assertEqual(r['j_nu'],x)
        self.assertEqual(r['alpha_nu'],x**(-2))
        self.assertEqual(r['source_function'],x**3)
    def test_gap_uncertainty_bounds(self):
        lo,hi=s.covariance_free_gap_sd_bounds('0.000001','0.000002')
        self.assertEqual(lo,Decimal('29979.2458'))
        self.assertEqual(hi,Decimal('89937.7374'))
    def test_correlated_limit_zeros(self):
        lo,hi=s.covariance_free_gap_sd_bounds('0.5','0.5')
        self.assertEqual(lo,0)
        self.assertEqual(hi,Decimal('29979245800'))
    def test_bad_marginals(self):
        for bad in ('NaN','Infinity','-0.1','oops'):
            with self.subTest(bad=bad),self.assertRaises(ValueError):s.covariance_free_gap_sd_bounds(bad,0.2)
    def test_bad_ratios(self):
        for bad,delta in [(0,1),(-2,3),('NaN',1),(2,-3),(True,1)]:
            with self.subTest(bad=bad),self.assertRaises(ValueError):s.exact_fixed_phi_policy_ratios(bad,delta)
    def test_policy_ratios_at_zero_shift(self):
        self.assertEqual(set(s.exact_fixed_phi_policy_ratios(10,0).values()),{Fraction(1,1)})

if __name__=='__main__':unittest.main()
