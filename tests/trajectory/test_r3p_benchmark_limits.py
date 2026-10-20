"""Regression for the observed inherited-hard-limit initialization failure."""
import json
import os
from pathlib import Path
import resource
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.skipif(not hasattr(os, "sched_setaffinity"), reason="Linux resource protocol")
@pytest.mark.parametrize("cpus,expected", [(1, "FileNotFoundError"), (4, "ValueError")])
def test_initialization_obeys_inherited_cap_and_retains_failure(tmp_path, cpus, expected):
    output = tmp_path / "audit"
    env = os.environ.copy()
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        env[key] = "1"

    def constrained_child():
        resource.setrlimit(resource.RLIMIT_CPU, (20, 21))
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})

    result = subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts/benchmark_r3p_audit.py"),
         "--raw", str(tmp_path / "absent-raw"), "--checkpoint", str(tmp_path / "absent-checkpoint"),
         "--output", str(output), "--backend", "legacy", "--cpus", str(cpus)],
        cwd=ROOT, env=env, preexec_fn=constrained_child, capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 2, result.stderr
    report = json.loads((output / "result.json").read_text())
    assert report["status"] == "FAILED"
    assert report["first_failure"]["type"] == expected
    assert "not allowed to raise maximum limit" not in report["first_failure"]["message"]
    if cpus == 1:
        assert report["effective_cpu_limits"] == [20, 21]
        assert report["first_failure"]["type"] == "FileNotFoundError"
    else:
        assert report["first_failure"]["message"] == "R3P_AFFINITY_TOO_SMALL"
    assert report["new_physical_steps"] == 0
    assert "audit_cpu_s" not in report
