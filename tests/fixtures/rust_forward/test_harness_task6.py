"""Small checker/oracle tests. No test here executes or validates Rust kernels."""
from __future__ import annotations
import contextlib
import copy
from fractions import Fraction
import importlib.util
import io
import json
import math
from pathlib import Path
import sys
import unittest

D=Path(__file__).resolve().parent
ROOT=D.parents[2]
spec=importlib.util.spec_from_file_location('_rec_he_checker',ROOT/'scripts/check_rust_forward_parity.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
if str(D) not in sys.path:sys.path.insert(0,str(D))
import reference_v2 as ref
import input_wire_v2 as wire


def document(reference):
    """Synthetic valid data for checker unit tests, NOT a Rust observation."""
    return {'schema':ref.SCHEMA,'records':[{k:copy.deepcopy(v) for k,v in r.items() if k!='scales'} for r in reference['records']]}


def rational_flat(m):
    return [float(Fraction(x)) for row in m for z in row for x in z]


class HarnessTests(unittest.TestCase):
    # Invoked by --self-test with explicit fixtures; never auto-collected by pytest.
    __test__ = False
    def record(self,doc,id):return next(x for x in doc['records'] if x['id']==id)
    def check_bad(self,mutator):
        doc=document(self.reference);mutator(doc)
        with self.assertRaises(h.VerificationError):h.compare_document(doc,self.reference)

    def test_reference_scale_boundary(self):
        t=h.TOLERANCE
        self.assertTrue(h.compare_component(t,0.,1.))
        self.assertFalse(h.compare_component(math.nextafter(t,math.inf),0.,1.))
        self.assertTrue(h.compare_component(0.,0.,0.))
        self.assertFalse(h.compare_component(1e-300,0.,0.))

    def test_reject_nonfinite_and_wrong_type_components(self):
        for x in [math.nan,math.inf,-math.inf,True,'0']:
            self.assertFalse(h.compare_component(x,1.,1.))
            self.assertFalse(h.compare_component(1.,x,1.))
            self.assertFalse(h.compare_component(1.,1.,x))
        self.assertFalse(h.compare_component(1.,1.,-1.))

    def test_tiny_source_deletion_and_unit_change(self):
        self.assertFalse(h.compare_component(0.,1e-220,3e-220))
        for factor in [1e-100,1.,1e100]:
            self.assertFalse(h.compare_component(0.,1e-100*factor,2e-100*factor))
            self.assertTrue(h.compare_component(1e-100*factor,1e-100*factor,2e-100*factor))

    def test_strict_json_tokens_and_duplicate_keys(self):
        for raw in ['{"x":NaN}','{"x":Infinity}','{"x":-Infinity}','{"x":1e999}','{"x":1,"x":2}','{"x":']:
            with self.subTest(raw=raw),self.assertRaises(h.VerificationError):h.load_json(raw)
        self.assertEqual(h.load_json('{"x":{"float":"nan"}}'),{'x':{'float':'nan'}})

    def test_schema_missing_extra_shape_order(self):
        mutations=[lambda d:d.pop('schema'),lambda d:d.update(extra=1),lambda d:d['records'].pop(),lambda d:d['records'].reverse(),lambda d:d['records'][0].pop('values'),lambda d:d['records'][0]['values'].update(invented=[0.]),lambda d:d['records'][0]['values']['atomic_b'].pop()]
        for mutation in mutations:self.check_bad(mutation)

    def test_synthetic_identity_not_rust_parity(self):
        report=h.compare_document(document(self.reference),self.reference)
        self.assertEqual(report['records'],len(self.inputs['cases']))
        self.assertGreater(report['numeric_components'],1000)
        self.assertEqual(report['max_reference_scaled_difference'],0.)

    def test_matrix_conjugation_mutant(self):
        def mutate(d):self.record(d,'bf_P_Length_q1.2')['values']['photon_c'][3]*=-1
        self.check_bad(mutate)

    def test_matrix_transpose_mutant(self):
        def mutate(d):
            x=self.record(d,'pair_complex_tilted_screens')['values']['m12']
            x[2:4],x[4:6]=x[4:6],x[2:4]
        self.check_bad(mutate)

    def test_pair_extra_atomic_half_mutant(self):
        def mutate(d):self.record(d,'pair_perpendicular_vacuum')['values']['event_rate_density'][0]*=.5
        self.check_bad(mutate)

    def test_pair_extra_marginal_half_mutant(self):
        def mutate(d):
            r=self.record(d,'pair_complex_tilted_screens');r['values']['c1']=[x*.5 for x in r['values']['c1']]
        self.check_bad(mutate)

    def test_bf_sign_mutant(self):
        def mutate(d):self.record(d,'bf_P_forward')['values']['event_rate_density'][0]*=-1
        self.check_bad(mutate)

    def test_small_source_zero_mutant(self):
        def mutate(d):
            r=self.record(d,'bf_P_small');r['values']={k:[0.]*len(v) for k,v in r['values'].items()}
        self.check_bad(mutate)

    def test_nonfinite_output_mutant(self):
        def mutate(d):self.record(d,'bb_full_vacuum')['values']['atomic_b'][0]=math.inf
        self.check_bad(mutate)

    def test_missing_authority_to_zero_mutant(self):
        def mutate(d):
            r=self.record(d,'source_error_P_drift');r['status']='ok'
        self.check_bad(mutate)

    def test_measure_tag_mutant(self):
        def mutate(d):self.record(d,'pair_perpendicular_vacuum')['tags']['density_measure']='ContinuousPerJoulePerSteradian'
        self.check_bad(mutate)

    def test_two_full_tags_added_mutant(self):
        def mutate(d):self.record(d,'selected_mixed')['values']['photon_number'][0]*=2
        self.check_bad(mutate)

    def test_pair_identity_overlap_mutant(self):
        def mutate(d):
            r=self.record(d,'pair_perpendicular_vacuum');r['values']['m12'][0]=1.
        self.check_bad(mutate)

    def test_missing_table_zero_mutant(self):
        id=next(c['id'] for c in self.inputs['cases'] if c['op']=='domain' and c['source_case']['id']=='energy_P_low_missing')
        def mutate(d):
            r=self.record(d,id);r.update(status='ok',values={},tags={'coverage':'PhysicalZeroBelowThreshold'})
        self.check_bad(mutate)

    def test_extra_output_scale_cannot_loosen_gate(self):
        def mutate(d):
            r=self.record(d,'bf_P_small');r['scales']={'photon_c':1.};r['values']['photon_c']=[0.]*8
        self.check_bad(mutate)

    def test_validator_failures_exit_nonzero_in_subprocess(self):
        # Executes the real Python validation functions in child processes.
        # It does not execute Cargo or imitate a Rust observation.
        code=("import importlib.util,sys;from pathlib import Path;"
              "s=importlib.util.spec_from_file_location('h',sys.argv[1]);"
              "h=importlib.util.module_from_spec(s);s.loader.exec_module(h);"
              "h.compare_document(h.load_json(sys.stdin.buffer.read()),"
              "h.load_json(Path(sys.argv[2]).read_bytes()))")
        bad=document(self.reference);bad['records'][0]['values'].pop('atomic_b')
        nonfinite=document(self.reference);nonfinite['records'][0]['values']['atomic_b'][0]=float('inf')
        payloads={'nonfinite':json.dumps(nonfinite).encode(),'schema':json.dumps(bad).encode(),'malformed':b'{','truncated':json.dumps(document(self.reference)).encode()[:-4]}
        for name,payload in payloads.items():
            label='validator_'+name
            with self.assertRaises(h.VerificationError):
                h.run_process([sys.executable,'-c',code,str(ROOT/'scripts/check_rust_forward_parity.py'),str(D/'reference_values_v2.json')],payload,self.evidence,label)
            rc=json.loads((self.evidence/(label+'.process.json')).read_text())
            self.assertNotEqual(rc['exit'],0)

    def test_output_size_limit_is_not_success(self):
        with self.assertRaises(h.VerificationError):
            h.run_process([sys.executable,'-c','print("x"*100)'],b'',self.evidence,'stub_oversize',max_output_bytes=8)

    def test_reference_exact_bb_fixture_crosscheck(self):
        old=json.loads((D/'bb_reference_task3.json').read_text())
        for case in old['cases']:
            r=self.record(self.reference,'bb_'+case['id']+'_He584');b=3*1.7989e9/(8*math.pi)
            expected=rational_flat(case['integrated_b_over_bshell'])
            scale=r['scales']['atomic_b']/b
            for got,want in zip(r['values']['atomic_b'],expected):self.assertTrue(h.compare_component(got/b,want,scale))

    def test_reference_exact_pair_fixture_crosscheck(self):
        old=json.loads((D/'pair_reference_task4.json').read_text())
        for case in old['cases']:
            r=self.record(self.reference,'pair_'+case['id'])
            for key in ['m12','m21']:
                expected=rational_flat(case[key]);scale=r['scales'][key]
                for x,y in zip(r['values'][key],expected):self.assertTrue(h.compare_component(x,y,scale))
        perpendicular=self.record(self.reference,'pair_perpendicular_vacuum')['values']['m12']
        self.assertEqual(perpendicular,[0.,0.,0.,0.,0.,0.,1.,0.])

    def test_reference_bf_previous_si_component_crosscheck(self):
        old=json.loads((D/'task5_bf_reference.json').read_text())['si_complex']
        r=self.record(self.reference,'bf_P_Length_q1.2')
        for k,target in [('photon_c','photon_c'),('atomic','atomic_b')]:
            expected=[x for row in old[target] for z in row for x in z]
            for x,y in zip(r['values'][k],expected):self.assertTrue(h.compare_component(x,y,r['scales'][k]))

    def test_reference_scalar_pbf_closed_form(self):
        inp=next(c for c in self.inputs['cases'] if c['id']=='bf_P_scalar');s=inp['state'];co=s['constants'];e=inp['energy_ev'];f=.17;np=4.2
        phi=(ref.ME*ref.KB*s['temperature_k']/(2*math.pi*(ref.H/(2*math.pi))**2))**1.5
        eta=s['n_he_plus']*s['ne']*math.exp(-(e-co['chi_p_ev'])*ref.EV/(ref.KB*s['temperature_k']))/(4*phi)
        sigma=sum(ref.table('P','Length',1.2));want=ref.C*sigma*(3*eta*(1+f)-np*f)
        r=self.record(self.reference,'bf_P_scalar')
        for i in [0,6]:self.assertTrue(h.compare_component(r['values']['photon_c'][i],want,r['scales']['photon_c']))

    def test_reference_material_identities_from_separate_terms(self):
        r=self.record(self.reference,'selected_mixed');v=r['values'];g=r['scales']
        scale=g['internal_power_j']+g['heat_power_j']+g['photon_power_j']
        self.assertTrue(h.compare_component(sum([v['internal_power_j'][0],v['heat_power_j'][0],v['photon_power_j'][0]]),0.,scale))
        self.assertTrue(h.compare_component(v['photon_power_j'][0],v['q_photon'][0]*ref.C,g['photon_power_j']))
        pg=self.record(self.reference,'pair_grid')
        for n in pg['values']['photon_number']:self.assertTrue(h.compare_component(n,2*pg['values']['event_rate'][0],pg['scales']['photon_number']))

    def test_wire_bound_ids_and_original_domain_cases(self):
        encoded=wire.encode(self.inputs).decode().splitlines()
        self.assertEqual(len(encoded),len(self.inputs['cases'])+1)
        self.assertEqual(encoded[0],'REC_HE_WIRE_V2 '+str(len(self.inputs['cases'])))
        self.assertEqual([x.split()[0] for x in encoded[1:]],[x['id'] for x in self.inputs['cases']])
        self.assertEqual(sum(x['op']=='domain' for x in self.inputs['cases']),125)
        self.assertIn('NaN',' '.join(encoded))
        self.assertEqual(float(wire.number(5e-324)),5e-324)
        self.assertFalse(any('expected_error' in line or 'expected_domain' in line for line in encoded))

    def test_subprocess_nonzero_real_capture(self):
        with self.assertRaises(h.VerificationError):h.run_process([sys.executable,'-c','import sys; print("partial");sys.exit(7)'],b'',self.evidence,'stub_nonzero')
        rc=json.loads((self.evidence/'stub_nonzero.process.json').read_text());self.assertEqual(rc['exit'],7)
        self.assertEqual((self.evidence/'stub_nonzero.stdout.bin').read_bytes(),b'partial\n')

    def test_subprocess_missing_executable_capture(self):
        with self.assertRaises(h.VerificationError):h.run_process([str(self.evidence/'nonexistent_executable')],b'',self.evidence,'stub_missing_executable')
        self.assertIsNone(json.loads((self.evidence/'stub_missing_executable.process.json').read_text())['exit'])

    def test_subprocess_malformed_json_capture(self):
        raw=h.run_process([sys.executable,'-c','print("{")'],b'',self.evidence,'stub_malformed')
        with self.assertRaises(h.VerificationError):h.load_json(raw)

    def test_subprocess_schema_missing_capture(self):
        raw=h.run_process([sys.executable,'-c','print("{}")'],b'',self.evidence,'stub_schema')
        with self.assertRaises(h.VerificationError):h.compare_document(h.load_json(raw),self.reference)

    def test_subprocess_timeout_capture(self):
        with self.assertRaises(h.VerificationError):h.run_process([sys.executable,'-c','import time;time.sleep(2)'],b'',self.evidence,'stub_timeout',timeout=.1)
        self.assertEqual(json.loads((self.evidence/'stub_timeout.process.json').read_text())['execution_failure'],'TIMEOUT')


def run_suite(evidence,inputs,reference):
    HarnessTests.inputs=inputs;HarnessTests.reference=reference;HarnessTests.evidence=evidence
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(HarnessTests);stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    (evidence/'python_tests.log').write_text(stream.getvalue())
    if not result.wasSuccessful():raise h.VerificationError('Python self-tests failed; see python_tests.log')
    return {'python_tests_run':result.testsRun,'python_failures':len(result.failures),'python_errors':len(result.errors),'rust_executions':0,'scope':'checker regression, synthetic output mutants, fixed reference crosschecks only'}


if __name__=='__main__':
    raise SystemExit('Run scripts/check_rust_forward_parity.py --self-test instead; this does not run Rust.')
