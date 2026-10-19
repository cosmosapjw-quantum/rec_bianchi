"""Adversarial contracts against the actual newly built standalone Rust CLI.

The bounded verifier supplies the executable and reviewed request. No compilation
or upstream test campaign occurs in these tests; all raw failures are retained.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from dataclasses import asdict
import math
sys.dont_write_bytecode=True


@unittest.skipUnless(os.environ.get("REC_R3O_BINARY"),"run scripts/verify_r3o_rust.py for actual-client tests")
class R3ORustContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binary=Path(os.environ["REC_R3O_BINARY"])
        cls.source=Path(os.environ["REC_R3O_SOURCE"])
        cls.directory=Path(os.environ["REC_R3O_TEST_OUTPUT"])
        cls.request=json.loads(Path(os.environ["REC_R3O_REQUEST"]).read_text())

    def invoke(self,request,extra=None,raw=None,existing=None):
        root=self.directory/self._testMethodName
        root.mkdir(exist_ok=False)
        inp=root/"request.json"
        inp.write_text(raw if raw is not None else json.dumps(request,allow_nan=False))
        out=root/"result.json"
        if existing is not None:out.write_text(existing)
        command=[str(self.binary),"--input",str(inp),"--output",str(out),"--mode","fixed"]+(extra or [])
        with (root/"stdout.log").open("xb") as stdout,(root/"stderr.log").open("xb") as stderr:
            result=subprocess.run(command,cwd=self.source,stdout=stdout,stderr=stderr,timeout=10)
        (root/"command.json").write_text(json.dumps({"command":command,"returncode":result.returncode}))
        return result.returncode,out

    def test_missing_fourth_predictor_memory_is_rejected(self):
        req=copy.deepcopy(self.request);del req["native"]["thermal_prev2"]
        code,path=self.invoke(req)
        self.assertEqual(code,2)
        self.assertIn("thermal_prev2",json.loads(path.read_text())["error"])

    def test_short_python_state_history_is_rejected(self):
        req=copy.deepcopy(self.request);req["python_states"].pop()
        code,path=self.invoke(req)
        self.assertEqual(code,2)
        self.assertIn("SHAPE_GRID_OR_CAP",json.loads(path.read_text())["error"])

    def test_short_rhs_history_is_rejected(self):
        req=copy.deepcopy(self.request);req["python_rhs"].pop()
        code,path=self.invoke(req)
        self.assertEqual(code,2)
        self.assertIn("SHAPE_GRID_OR_CAP",json.loads(path.read_text())["error"])

    def test_wrong_grid_order_is_rejected(self):
        req=copy.deepcopy(self.request);req["python_states"][1]["iz"]+=1
        code,path=self.invoke(req)
        self.assertEqual(code,2)
        self.assertIn("TIME_COUNT_ORDER",json.loads(path.read_text())["error"])

    def test_unknown_field_is_rejected(self):
        req=copy.deepcopy(self.request);req["full_source_override"]=True
        code,path=self.invoke(req)
        self.assertEqual(code,2)
        self.assertIn("unknown field",json.loads(path.read_text())["error"])

    def test_nonfinite_input_is_rejected(self):
        raw=json.dumps(self.request).replace('"h2": 4.245e-05','"h2": 1e999')
        self.assertIn("1e999",raw)
        code,path=self.invoke(None,raw=raw)
        self.assertEqual(code,2)
        self.assertIn("error",json.loads(path.read_text()))

    def test_cpu_work_caps_are_not_silently_expanded(self):
        code,path=self.invoke(self.request,extra=["--max-attempts","33"])
        self.assertEqual(code,2)
        self.assertIn("CAP",json.loads(path.read_text())["error"])

    def test_create_only_output_preserves_old_bytes(self):
        marker='{"preserve":"old evidence"}\n'
        code,path=self.invoke(self.request,existing=marker)
        self.assertEqual(code,2)
        self.assertEqual(hashlib.sha256(path.read_bytes()).digest(),hashlib.sha256(marker.encode()).digest())

    def test_portable_packet_retains_separate_exact_native_and_python_states(self):
        root=Path(__file__).resolve().parents[2]
        sys.path.insert(0,str(root/"scripts"))
        from verify_r3o_rust import load_boundary_packet,DEFAULT_PACKET,ORIGINAL_ZIP,bits
        boundary=load_boundary_packet(DEFAULT_PACKET,ORIGINAL_ZIP)
        self.assertEqual(bits(asdict(boundary["native"])),bits(self.request["native"]))
        self.assertEqual(bits(asdict(boundary["python"])),bits(self.request["python_states"][0]))
        self.assertNotEqual(bits(asdict(boundary["native"])),bits(asdict(boundary["python"])))

    def test_altered_portable_packet_is_rejected(self):
        root=Path(__file__).resolve().parents[2]
        sys.path.insert(0,str(root/"scripts"))
        from verify_r3o_rust import load_boundary_packet,DEFAULT_PACKET,ORIGINAL_ZIP
        packet=json.loads(DEFAULT_PACKET.read_text())
        packet["states"]["native"]["xe"]=math.nextafter(packet["states"]["native"]["xe"],math.inf)
        directory=self.directory/self._testMethodName;directory.mkdir(exist_ok=False)
        path=directory/"altered_packet.json";path.write_text(json.dumps(packet))
        with self.assertRaisesRegex(ValueError,"DERIVED_PACKET_HASH"):
            load_boundary_packet(path,ORIGINAL_ZIP)


@unittest.skipUnless(os.environ.get("REC_R3O_TEST_OUTPUT"),"requires a create-only test evidence directory")
class R3OBuildGuardContracts(unittest.TestCase):
    def test_process_tree_cpu_cap_retains_actual_failure(self):
        root=Path(__file__).resolve().parents[2]
        sys.path.insert(0,str(root/"scripts"))
        from build_r3o_rust import Budget
        directory=Path(os.environ["REC_R3O_TEST_OUTPUT"])/self._testMethodName
        directory.mkdir(exist_ok=False)
        budget=Budget(directory,cpu_s=2.4,wall_s=10.)
        command=[sys.executable,"-B","-c","import time; until=time.process_time()+1.5\nwhile time.process_time()<until: pass\n"]
        with self.assertRaisesRegex(RuntimeError,"COMMAND_FAILED"):
            budget.run(command,cwd=directory,env=dict(os.environ),label="expected_cpu_limit")
        result=budget.commands[-1]
        self.assertIn("AGGREGATE_CPU_CAP",result["failure"])
        self.assertGreater(result["max_polled_process_tree_rss_bytes"],0)
        self.assertIsNotNone(result["pid_namespace_mapping"]["procfs_pid"])
        self.assertNotEqual(result["returncode"],0)

    def test_published_vigilode_archive_materializes_without_private_checkout(self):
        root=Path(__file__).resolve().parents[2]
        sys.path.insert(0,str(root/"scripts"))
        import build_r3o_rust
        from unittest.mock import patch
        directory=Path(os.environ["REC_R3O_TEST_OUTPUT"])/self._testMethodName
        directory.mkdir(exist_ok=False)
        extracted=directory/"vendor-vigilode-a21d573"
        with patch.object(build_r3o_rust,"VENDOR",extracted):
            record=build_r3o_rust.ensure_vigilode()
        self.assertTrue((extracted/"crates/rodas5p-core/src/matrix.rs").is_file())
        self.assertTrue((extracted/"crates/rodas5p-integrators/src/rodas5p_fast.rs").is_file())
        self.assertGreater(len(record["members"]),120)
        self.assertEqual(record["upstream_commit"],"a21d573980f66fe02891bd216153443b5352f921")


if __name__=="__main__":unittest.main()
