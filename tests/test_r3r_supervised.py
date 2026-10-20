"""Regression gates for the bounded R3R launch and source/cache binding."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "scripts/run_r3r_h4_supervised.py"


def command(out, *extra):
    return [sys.executable, "-B", str(LAUNCHER), "--expected-commit", "0"*40,
            "--new-allocation-id", "R3R_TEST_NO_PHYSICS_EXECUTION",
            "--evidence-dir", str(out), *extra]


@pytest.mark.parametrize("steps", [0, -1, 33, 129, 8192])
def test_invalid_step_cap_rejected_before_allocation(tmp_path, steps):
    out = tmp_path / "invalid"
    result = subprocess.run(command(out, "--steps", str(steps)),
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 2
    assert "1..32" in result.stderr
    assert not out.exists()


def test_no_full_or_event_mode(tmp_path):
    result = subprocess.run(command(tmp_path / "invalid", "--mode", "event"),
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 2
    assert "unrecognized arguments" in result.stderr


def test_expected_commit_mismatch_records_failure_without_worker(tmp_path):
    out = tmp_path / "mismatch"
    result = subprocess.run(command(out), capture_output=True, text=True, timeout=10)
    assert result.returncode == 2
    report = json.loads((out / "supervision.json").read_text())
    assert report["status"] == "FAILED"
    assert report["first_failure"]["message"] == "R3R_EXPECTED_COMMIT_MISMATCH"
    assert report["commands"] == []
    assert not (out / "worker").exists()
    assert report["limits"]["max_steps"] == 32
    assert report["limits"]["user_step_ceiling"] == 128


@pytest.mark.skipif(sys.platform != "linux", reason="actual inherited POSIX rlimit test")
def test_actual_lower_inherited_limits_are_preserved():
    source = (
        "import json,resource,sys;"
        "sys.path.insert(0," + repr(str(ROOT / "scripts")) + ");"
        "from run_r3r_h4_supervised import InheritedLimits;"
        "resource.setrlimit(resource.RLIMIT_CPU,(2,3));"
        "records=[];adapter=InheritedLimits(resource,records);"
        "adapter.setrlimit(resource.RLIMIT_CPU,(60,61));"
        "print(json.dumps({'limits':resource.getrlimit(resource.RLIMIT_CPU),'records':records}))")
    result = subprocess.run([sys.executable, "-B", "-c", source],
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    parsed = json.loads(result.stdout)
    assert parsed["limits"] == [2, 3]
    assert parsed["records"][-1]["applied"] == [2, 3]


def test_fresh_prefix_reads_source_when_B_can_read_stale_cache(tmp_path):
    """Actual same-size/mtime counterexample; no old cache is deleted."""
    module = tmp_path / "sealed_probe.py"
    module.write_text("VALUE = 1\n")
    import py_compile
    py_compile.compile(str(module), doraise=True)
    stat = module.stat()
    module.write_text("VALUE = 2\n")
    os.utime(module, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    source = "import sys;sys.path.insert(0," + repr(str(tmp_path)) + ");import sealed_probe;print(sealed_probe.VALUE)"
    # py_compile follows the parent cache prefix. Make the stale-cache probe
    # read that same prefix even when pytest itself uses a fresh private one.
    old_command = [sys.executable, "-B"]
    if sys.pycache_prefix is not None:
        old_command += ["-X", "pycache_prefix=" + sys.pycache_prefix]
    old = subprocess.run([*old_command, "-c", source],
                         capture_output=True, text=True, timeout=10)
    fresh = tmp_path / "fresh"
    fresh.mkdir()
    new = subprocess.run([sys.executable, "-B", "-X", "pycache_prefix="+str(fresh), "-c", source],
                         capture_output=True, text=True, timeout=10)
    assert old.returncode == new.returncode == 0
    assert old.stdout.strip() == "1"
    assert new.stdout.strip() == "2"
    assert not list(fresh.iterdir())
