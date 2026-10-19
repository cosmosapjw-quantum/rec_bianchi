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
    def finalizer_control(self, module_name):
        """Exercise the real finally branch with synthetic hashing costs.

        Running that branch, rather than only its budget helper, detects moving
        the resource sample ahead of the expensive source/artifact identity work.
        These receipts are explicitly synthetic and evolve no physical state.
        """
        import ast
        import importlib
        from types import SimpleNamespace
        from unittest.mock import patch
        root=Path(__file__).resolve().parents[2]
        sys.path.insert(0,str(root/"scripts"))
        module=importlib.import_module(module_name)
        import build_r3o_rust
        main=next(n for n in ast.parse(Path(module.__file__).read_text()).body
                  if isinstance(n,ast.FunctionDef) and n.name=="main")
        branch=next(n for n in main.body if isinstance(n,ast.Try)).finalbody
        code=compile(ast.Module(body=branch,type_ignores=[]),module.__file__,"exec")
        is_build=module_name=="build_r3o_rust"
        cpu_cap,wall_cap=(240.,480.) if is_build else (20.,60.)
        for over in (False,True):
            with self.subTest(over_budget=over):
                directory=Path(os.environ["REC_R3O_TEST_OUTPUT"])/self._testMethodName/str(over)
                directory.mkdir(parents=True,exist_ok=False)
                (directory/"synthetic_artifact.txt").write_text("no numerical data\n")
                clock={"cpu":1.,"wall":1.,"hash_called":False}
                after=(cpu_cap+1.,wall_cap+1.) if over else (2.,2.)
                def hashing_cost():
                    clock.update(cpu=after[0],wall=after[1],hash_called=True)
                def own_hashes():
                    if is_build:hashing_cost()
                    return {"synthetic_source":"unchanged"}
                def artifact_hash(path):
                    hashing_cost()
                    return "synthetic_hash_only"
                report={"schema":"rec.r3o.synthetic-finalizer-control.v1",
                        "synthetic_clock_only":True,"physical_steps":0,
                        "status":"BUILD_PASS" if is_build else "BOUNDED_PASS",
                        "code_before":{"synthetic_source":"unchanged"}}
                budget=SimpleNamespace(start_cpu=0.,start_wall=0.,cpu_s=cpu_cap,wall_s=wall_cap,commands=[])
                fake_time=SimpleNamespace(monotonic=lambda:clock["wall"])
                namespace=dict(vars(module),report=report,budget=budget,exit_code=0,
                    ev=directory,code_before={"synthetic_source":"unchanged"},
                    own_code_hashes=own_hashes,sha256=artifact_hash,time=fake_time,
                    signal=SimpleNamespace(ITIMER_REAL=0,setitimer=lambda *args:None))
                with patch.object(build_r3o_rust,"cpu",lambda:clock["cpu"]),patch.object(build_r3o_rust,"time",fake_time):
                    exec(code,namespace)
                filename="build.json" if is_build else "verification.json"
                result=json.loads((directory/filename).read_text())
                self.assertTrue(clock["hash_called"])
                self.assertEqual(result["process_tree_cpu_s"],after[0])
                self.assertEqual(result["wall_s"],after[1])
                self.assertEqual(namespace["exit_code"],2 if over else 0)
                self.assertEqual(result["exit_code"],namespace["exit_code"])
                self.assertEqual(result["final_receipt_write_reserve"],{"cpu_s":2.,"wall_s":3.})
                self.assertEqual(result["status"]=="FAILED",over)

    def test_build_finalizer_accounts_for_source_hash_work(self):
        self.finalizer_control("build_r3o_rust")

    def test_verifier_finalizer_accounts_for_artifact_hash_work(self):
        self.finalizer_control("verify_r3o_rust")

    def test_missing_committed_lock_fails_before_cargo(self):
        root=Path(__file__).resolve().parents[2]
        sys.path.insert(0,str(root/"scripts"))
        import build_r3o_rust
        from unittest.mock import patch
        directory=Path(os.environ["REC_R3O_TEST_OUTPUT"])/self._testMethodName
        directory.mkdir(exist_ok=False)
        package=directory/"missing-lock-package";package.mkdir()
        output=directory/"expected_failure"
        with patch.object(build_r3o_rust,"PACKAGE",package),patch.object(sys,"argv",["build_r3o_rust.py","--output",str(output)]):
            code=build_r3o_rust.main()
        result=json.loads((output/"build.json").read_text())
        self.assertEqual(code,2)
        self.assertIn("COMMITTED_CARGO_LOCK_REQUIRED",result["failure"]["message"])
        self.assertEqual(result["commands"],[])
        self.assertFalse((package/"Cargo.lock").exists())

    def test_locked_cargo_build_rejects_and_preserves_invalid_lock(self):
        import shutil
        cargo=shutil.which("cargo")
        if cargo is None:self.skipTest("actual Cargo not on PATH for this launcher-only control")
        root=Path(__file__).resolve().parents[2]
        sys.path.insert(0,str(root/"scripts"))
        from build_r3o_rust import Budget
        directory=Path(os.environ["REC_R3O_TEST_OUTPUT"])/self._testMethodName
        directory.mkdir(exist_ok=False)
        (directory/"src").mkdir()
        (directory/"src/main.rs").write_text("fn main() {}\n")
        (directory/"Cargo.toml").write_text('[package]\nname="r3o-invalid-lock-control"\nversion="0.0.0"\nedition="2024"\n[workspace]\n')
        lock=directory/"Cargo.lock";lock.write_bytes(b"version = INVALID_LOCK\n")
        before=lock.read_bytes()
        budget=Budget(directory,cpu_s=10.,wall_s=20.)
        env=dict(os.environ,CARGO_HOME=str(directory/"cargo_home"),CARGO_TARGET_DIR=str(directory/"target"))
        # metadata --no-deps intentionally does not resolve dependencies or parse
        # the lock. Exercise the actual --locked build gate; malformed TOML must
        # stop Cargo before it compiles this dependency-free control package.
        result=budget.run([cargo,"build","--locked","--offline","--release","-j1","--manifest-path",directory/"Cargo.toml"],
            cwd=directory,env=env,label="invalid_lock",expected=(101,))
        self.assertEqual(result["returncode"],101)
        self.assertEqual(lock.read_bytes(),before)
        self.assertIn("lock",Path(result["stderr"]).read_text().lower())
        self.assertFalse((directory/"target/release/r3o-invalid-lock-control").exists())

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
        self.assertEqual(result["resource_measurement_coverage"]["live_scope"],"MAPPED_CHILD_AND_DESCENDANTS_POLLED")

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


class R3ORustCli(unittest.TestCase):
    def test_one_step_is_rejected_before_build_or_output_creation(self):
        import tempfile
        root=Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/"must_not_be_created"
            result=subprocess.run([sys.executable,"-B",str(root/"scripts/verify_r3o_rust.py"),
                "--steps","1","--output",str(output)],cwd=root,
                capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,2)
            self.assertIn("argument --steps: invalid choice:",result.stderr)
            self.assertFalse(output.exists())


if __name__=="__main__":unittest.main()
