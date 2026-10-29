import ast
from dataclasses import dataclass, replace
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import sys, unittest
sys.path.insert(0,str(Path(__file__).parents[1]/'src'))
from guard_graph import (git_blob_id,read_pinned_py,body_for,stage_guard_evidence,
                        ordered_straightline_calls,reachable_without_cuts,
                        all_observed_paths_guarded,validate_source_state,
                        SourceMismatch,UnsupportedControlFlow)

FIREWALL = Path(__file__).parents[2]/'rec_pr157_review'/'extracted'/'source_policy_firewall.py'
FIREWALL_SHA='e170417a8a205e17d45ae50e5c0f14641d020387'

@dataclass(frozen=True)
class FakeDataset:
    source_sha256: str
    source_bytes: int
    levels: tuple[int,...]
    _original_bytes: bytes
    def source_roundtrip(self):return self._original_bytes

class TestActualPinnedFirewall(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not FIREWALL.is_file():
            raise unittest.SkipTest('Pinned PR157 source ZIP not restored: actual source check requires it')
        cls.m=read_pinned_py(FIREWALL,FIREWALL_SHA)
    def test_source_pin_real_blob(self):
        self.assertEqual(git_blob_id(FIREWALL.read_bytes()),FIREWALL_SHA)
    def test_actual_wrapper_order(self):
        facts=stage_guard_evidence(self.m)
        self.assertTrue(facts['guarded_research_entry_static_sequence'])
        self.assertEqual(facts['wrapper_order']['order'],'GUARD_PRECEDES_CONSUMER')
        self.assertFalse(facts['other_callers_covered'])
    def test_malformed_mutation_does_not_pass_source_identity(self):
        with TemporaryDirectory() as t:
            f=Path(t)/'fw.py'; f.write_bytes(FIREWALL.read_bytes()+b'\n# altered')
            with self.assertRaises(SourceMismatch):read_pinned_py(f,FIREWALL_SHA)
    def test_direct_wrapper_call_is_not_global_dominator(self):
        g={'external_direct':('owner.line_coefficients',),
           'firewall.guard':('owner.line_coefficients',),
           'owner.line_coefficients':('owner.einstein_B',)}
        self.assertEqual(reachable_without_cuts(g,{'external_direct','firewall.guard'},
                                             {'owner.line_coefficients'}, {'firewall.guard'}),
                         [['external_direct','owner.line_coefficients']])

class TestGraphTheorem(unittest.TestCase):
    def test_cut_if_and_only_if_all_paths_intersect(self):
        # Exhaustive directed simple graphs on three vertices (2**6=64),
        # all possible 3-bit guard selections; direct definition oracle.
        vs=['r','g','c']; edges=[(a,b) for a in vs for b in vs if a!=b]
        for mask in range(1<<6):
            graph={v:tuple(b for k,(a,b) in enumerate(edges) if a==v and mask>>k&1) for v in vs}
            for mask2 in range(1<<3):
                cuts={v for k,v in enumerate(vs) if mask2>>k&1}
                def dfs(u,path):
                    if u in cuts:return False
                    if u=='c':return True
                    return any(dfs(v,path|{v}) for v in graph[u] if v not in path)
                oracle=not dfs('r',{'r'})
                self.assertEqual(all_observed_paths_guarded(graph,{'r'},{'c'},cuts),oracle)
    def test_missing_graph_edge_does_not_prove_global_coverage(self):
        g={'guarded':('safe',),'safe':('consumer',)}
        self.assertTrue(all_observed_paths_guarded(g,{'guarded'},{'consumer'},{'safe'}))
        g['unmodelled_direct'] = ('consumer',)
        self.assertFalse(all_observed_paths_guarded(g,{'guarded','unmodelled_direct'},{'consumer'},{'safe'}))
    def test_cycle_terminates_and_gives_shortest_witness(self):
        g={'a':('b',),'b':('a','c'),'c':()}
        self.assertEqual(reachable_without_cuts(g,{'a'},{'c'},set()),[['a','b','c']])
    def test_no_shortcut_across_control_flow(self):
        mod=ast.parse('''\ndef f(flag):\n if flag:\n  guard()\n consumer()\n''')
        with self.assertRaises(UnsupportedControlFlow):ordered_straightline_calls(body_for(mod,'f'),'guard','consumer')
    def test_nested_guard_consumer_same_statement_rejected(self):
        mod=ast.parse('''\ndef f():\n return consumer(guard())\n''')
        with self.assertRaises(UnsupportedControlFlow):ordered_straightline_calls(body_for(mod,'f'),'guard','consumer')

class TestSourceStateClosure(unittest.TestCase):
    def setUp(self):
        self.dir=TemporaryDirectory(); p=Path(self.dir.name)/'owner_fixture.py';p.write_text('# synthetic owner, not real LAMDA\n')
        self.mod=type('M',(),{})();self.mod.__file__=str(p);self.mod.HDDataset=FakeDataset
        self.raw=b'synthetic deterministic source bytes';self.sha=sha256(self.raw).hexdigest()
        self.blob=git_blob_id(p.read_bytes())
        def parser(raw):
            return FakeDataset(sha256(raw).hexdigest(),len(raw),(3,5,7),raw)
        self.mod.parse_hd=parser;self.data=parser(self.raw)
    def tearDown(self):self.dir.cleanup()
    def go(self,d):
        return validate_source_state(self.mod,d,expected_module_blob=self.blob,
                expected_source_sha256=self.sha,expected_source_bytes=len(self.raw))
    def test_legitimate_canonical_source_passes(self):
        self.assertEqual(self.go(self.data)['status'],'PASS_SOURCE_STATE_CLOSURE')
    def test_same_source_raw_bytes_do_not_prove_parsed_field_integrity(self):
        tampered=replace(self.data,levels=(3,5,99))
        self.assertEqual(tampered.source_roundtrip(),self.raw)
        self.assertEqual(tampered.source_sha256,self.sha)
        with self.assertRaisesRegex(SourceMismatch,'parsed dataset differs'):
            self.go(tampered)
    def test_forged_digest_label_and_wrong_bytes(self):
        with self.assertRaises(SourceMismatch):self.go(replace(self.data,_original_bytes=b'bad'))
    def test_forged_owner_path(self):
        Path(self.mod.__file__).write_text('# changed')
        with self.assertRaises(SourceMismatch):self.go(self.data)
    def test_wrong_dataset_class(self):
        x=type('NotDataset',(),{})();x.source_sha256=self.sha;x.source_bytes=len(self.raw)
        x.source_roundtrip=lambda:self.raw
        with self.assertRaises(SourceMismatch):self.go(x)

if __name__=='__main__':unittest.main()
