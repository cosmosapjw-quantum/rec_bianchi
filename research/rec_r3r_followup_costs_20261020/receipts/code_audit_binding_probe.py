#!/usr/bin/env python3
"""Independent R3R source-binding adversarial probe; no solver execution.

Runs the actual bind_source function against a tiny synthetic local Git repo.
This fixture tests identity admission and does not validate physical data.
"""
from pathlib import Path
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
LAUNCHER = ROOT / "scripts/run_r3r_h4_supervised.py"
EXPECTED_LAUNCHER_SHA256 = "fe8c946a8b0bdbab53d813c46ce22d188f6a0117b6872607d33032666a8fd85f"

def main():
    data = LAUNCHER.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != EXPECTED_LAUNCHER_SHA256:
        raise RuntimeError("AUDIT_LAUNCHER_SOURCE_CHANGED")
    # Compile the inspected source explicitly: this reviewer does not trust a
    # project timestamp cache while testing source binding.
    namespace = {"__name__": "r3r_independent_binding_probe",
                 "__file__": str(LAUNCHER)}
    exec(compile(data, str(LAUNCHER), "exec"), namespace)
    checks, commands = [], []
    with tempfile.TemporaryDirectory(prefix="rec_r3r_binding_fixture_") as temp:
        fixture = Path(temp)
        env = os.environ.copy()
        env.update({"GIT_AUTHOR_DATE": "2026-10-20T00:00:00Z",
                    "GIT_COMMITTER_DATE": "2026-10-20T00:00:00Z"})
        def git(*args):
            command = ["git", "-c", "user.name=R3R Independent Audit",
                       "-c", "user.email=r3r-audit@example.invalid",
                       "-c", "commit.gpgSign=false", "-c",
                       "core.hooksPath=/dev/null", *args]
            done = subprocess.run(command, cwd=fixture, env=env,
                                  capture_output=True, check=False)
            commands.append({"command": command, "exit_code": done.returncode,
                             "stdout": done.stdout.decode(),
                             "stderr": done.stderr.decode(),
                             "stdout_sha256": hashlib.sha256(done.stdout).hexdigest(),
                             "stderr_sha256": hashlib.sha256(done.stderr).hexdigest()})
            if done.returncode:
                raise RuntimeError("FIXTURE_GIT_FAILED")
            return done.stdout.decode().strip()
        physics, checkpoint, runtime = b"VALUE = 1\n", b"FROZEN-CHECKPOINT\n", b"RUNTIME\n"
        for name, content in (("physics.py", physics), ("checkpoint.bin", checkpoint),
                              ("runtime.py", runtime)):
            (fixture / name).write_bytes(content)
        manifest = {"files": {"physics.py": hashlib.sha256(physics).hexdigest(),
                              "checkpoint.bin": hashlib.sha256(checkpoint).hexdigest()}}
        (fixture / "manifest.json").write_text(json.dumps(manifest, sort_keys=True)+"\n")
        git("init", "-q")
        git("add", "physics.py", "checkpoint.bin", "runtime.py", "manifest.json")
        git("commit", "-q", "-m", "Synthetic source binding fixture")
        head = git("rev-parse", "HEAD")
        namespace.update({"ROOT": fixture, "MANIFEST": "manifest.json",
                          "CHECKPOINT": "checkpoint.bin",
                          "ADDED_RUNTIME": ("runtime.py", "manifest.json")})
        bind = namespace["bind_source"]
        value = bind(head)
        assert value["source_commit"] == head
        assert value["frozen_files_verified"] == 2
        assert len(value["source_sha256"]) == 4
        checks.append({"name": "matching_committed_fixture_is_accepted", "status": "PASS",
                       "fixture_commit": head, "fixture_tree": value["source_tree"]})
        def rejected(name, expected, expected_message):
            try:
                bind(expected)
            except ValueError as exc:
                assert str(exc) == expected_message, (name, str(exc))
                checks.append({"name": name, "status": "PASS",
                               "exception_class": type(exc).__name__,
                               "exception_message": str(exc)})
            else:
                raise AssertionError(name + ":FALSE_ACCEPT")
        rejected("wrong_expected_commit", "0"*40, "R3R_EXPECTED_COMMIT_MISMATCH")
        (fixture / "runtime.py").write_bytes(b"CHANGED\n")
        rejected("uncommitted_runtime_byte_change", head,
                 "R3R_RUNTIME_NOT_AT_EXPECTED_COMMIT:runtime.py")
        (fixture / "runtime.py").write_bytes(runtime)
        (fixture / "alias.py").write_bytes(physics)
        (fixture / "physics.py").unlink()
        (fixture / "physics.py").symlink_to(fixture / "alias.py")
        rejected("same_content_symlink", head,
                 "R3R_RUNTIME_NOT_AT_EXPECTED_COMMIT:physics.py")
        (fixture / "physics.py").unlink()
        (fixture / "physics.py").write_bytes(physics)
        manifest["files"]["physics.py"] = "0"*64
        (fixture / "manifest.json").write_text(json.dumps(manifest, sort_keys=True)+"\n")
        git("add", "manifest.json")
        git("commit", "-q", "-m", "Synthetic inconsistent frozen digest")
        bad_head = git("rev-parse", "HEAD")
        rejected("committed_manifest_with_wrong_frozen_digest", bad_head,
                 "R3R_FROZEN_SOURCE_CHANGED:physics.py")
    result = {"schema": "rec.r3r.independent-source-binding-probe.v1",
              "status": "PASS", "checks": checks, "unique_checks": len(checks),
              "solver_integrations": 0,
              "scientific_validation": "NOT_PERFORMED_BY_SYNTHETIC_IDENTITY_FIXTURE",
              "actual_launcher_sha256": actual, "python": sys.version,
              "executable": sys.executable, "platform": platform.platform(),
              "fixture_git_commands": commands}
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
