#!/usr/bin/env python3
"""Build and compare two original-HyRec FLRW endpoint extractions (stdlib only)."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES = ["hyrectools.c", "helium.c", "hydrogen.c", "history.c", "endpoint_driver.c"]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_contract():
    return json.loads((HERE / "CONTRACT.json").read_text())


def checked_members(archive, contract):
    if digest(archive.read_bytes()) != contract["archive_sha256"]:
        raise ValueError("IMMUTABLE_ARCHIVE_SHA_MISMATCH")
    with zipfile.ZipFile(archive) as zf:
        members = {name: zf.read(name) for name in zf.namelist()
                   if name.startswith("HyRec/") and not name.endswith("/")}
    if digest(members[contract["input_member"]]) != contract["input_sha256"]:
        raise ValueError("IMMUTABLE_INPUT_SHA_MISMATCH")
    return members


def refinement_header(data):
    old = b"#define DLNA          8.49e-5"
    if data.count(old) != 1:
        raise ValueError("REFINEMENT_HEADER_CONTEXT_MISMATCH")
    return data.replace(old, b"#define DLNA          4.245e-5", 1)


def record_command(command, cwd, output, tag, stdin=None, timeout=300):
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.run(command, cwd=cwd, input=stdin, capture_output=True,
                              timeout=timeout, check=False)
        stdout, stderr, code = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, code = exc.stdout or b"", exc.stderr or b"", None
        timed_out = True
    wall = time.monotonic() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    (output / (tag + ".stdout")).write_bytes(stdout)
    (output / (tag + ".stderr")).write_bytes(stderr)
    receipt = {"command": command, "cwd": str(cwd), "exit_code": code,
               "timeout": timed_out, "wall_seconds": wall,
               "cpu_seconds": after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
               "wall_limit_seconds": timeout, "stdout_sha256": digest(stdout),
               "stderr_sha256": digest(stderr),
               "stdin_sha256": digest(stdin) if stdin is not None else None}
    (output / (tag + ".receipt.json")).write_text(json.dumps(receipt, indent=2) + "\n")
    if code != 0 or timed_out:
        raise RuntimeError(f"{tag}: {'TIME_LIMIT' if timed_out else 'EXIT_' + str(code)}")
    return stdout, receipt


def validate_endpoint(result, contract):
    e, grid = result["endpoint"], result["grid"]
    if result["cosmology"] != contract["cosmology"]:
        raise ValueError("COSMOLOGY_MISMATCH")
    if e["z"] != contract["endpoint_z"]:
        raise ValueError("ENDPOINT_Z_MISMATCH")
    if result["helium_mapping"] != "neutral-after-original-HyRec-cutoff":
        raise ValueError("HELIUM_MAPPING_MISMATCH")
    if result["native_history_domain_check"] != "PASS":
        raise ValueError("NATIVE_HISTORY_DOMAIN_CHECK_FAILED")
    if not all(math.isfinite(v) for v in e.values()):
        raise ValueError("NONFINITE_ENDPOINT")
    if not (0 <= e["xe_per_H"] <= 1 and 0 < e["Tm_K"] < e["Tgamma_K"]):
        raise ValueError("ENDPOINT_DOMAIN")
    eps = contract["export_cubic_epsilon_multiplier"] * sys.float_info.epsilon
    p = contract["cosmology"]
    ainv = 1 + e["z"]
    nH = 11.223846333047 * p["obh2"] * (1 - p["Y"]) * ainv**3
    fHe = p["Y"] / (1 - p["Y"]) / 3.97153
    ogh2 = 4.48162687719e-7 * p["T0_K"]**4
    rho = (p["omh2"] * ainv**3 + p["okh2"] * ainv**2
           + p["odeh2"] * ainv**(3 * (1 + p["w0"]))
           * math.exp(3 * p["wa"] * (math.log(ainv) - 1 + 1 / ainv))
           + ogh2 * ainv**4 * (1 + 0.227107317660239 * p["Nnueff"]))
    expected = {"a": 1 / ainv, "ln_a": -math.log1p(e["z"]),
                "Tgamma_K": p["T0_K"] * ainv, "nH_m3": nH,
                "fHe": fHe, "nHe_m3": nH * fHe,
                "H_s1": 3.2407792896393e-18 * math.sqrt(rho),
                "ne_m3": nH * e["xe_per_H"], "xHII": e["xe_per_H"],
                "xHI": 1 - e["xe_per_H"], "xHeI": 1, "xHeII": 0, "xHeIII": 0}
    for field, target in expected.items():
        if abs(e[field] - target) > eps * abs(target):
            raise ValueError("MAPPING_MISMATCH:" + field)
    center = grid["interpolation_center"]
    support = result["support"]
    if [s["index"] for s in support] != list(range(center - 1, center + 3)):
        raise ValueError("SUPPORT_INDEX_MISMATCH")
    for s in support:
        target = grid["ln_a_start"] + s["index"] * grid["DLNA"]
        if s["ln_a"] != target or not all(math.isfinite(v) for v in s.values()):
            raise ValueError("SUPPORT_COORDINATE_MISMATCH")
    # Independent four-node Lagrange polynomial in dimensionless grid coordinate.
    f = (e["ln_a"] - grid["ln_a_start"]) / grid["DLNA"] - center
    offsets = (-1, 0, 1, 2)
    errors = {}
    for field in ("xe_per_H", "Tm_K"):
        terms = []
        for i, oi in enumerate(offsets):
            weight = math.prod((f - oj) / (oi - oj) for oj in offsets if oj != oi)
            terms.append(support[i][field] * weight)
        reconstructed = math.fsum(terms)
        scale = max(abs(s[field]) for s in support)
        errors[field] = abs(reconstructed - e[field]) / scale
        if errors[field] > eps:
            raise ValueError("CUBIC_EXPORT_MISMATCH:" + field)
    return {"domain": "PASS", "SI_mapping": "PASS", "cubic_scaled_errors": errors,
            "cubic_scaled_limit": eps}


def compare_endpoints(baseline, refined, contract):
    errors = {}
    for field in ("xe_per_H", "Tm_K", "ne_m3"):
        a, b = baseline["endpoint"][field], refined["endpoint"][field]
        errors[field] = abs(a - b) / abs(b)
    if max(errors.values()) > contract["endpoint_relative_tolerance"]:
        raise ValueError("ENDPOINT_REFINEMENT_FAILED:" + json.dumps(errors))
    return errors


def run(output):
    output.mkdir(parents=True, exist_ok=False)
    contract = load_contract()
    members = checked_members(ROOT / contract["archive"], contract)
    compiler = shutil.which("cc")
    if compiler is None:
        raise RuntimeError("COMPILER_UNAVAILABLE")
    version, _ = record_command([compiler, "--version"], ROOT, output, "compiler", timeout=30)
    source_manifest = {
        "archive_sha256": contract["archive_sha256"],
        "input_sha256": contract["input_sha256"],
        "members": {name: digest(data) for name, data in members.items()},
        "contract_sha256": digest((HERE / "CONTRACT.json").read_bytes()),
        "driver_sha256": digest((HERE / "endpoint_driver.c").read_bytes()),
        "runner_sha256": digest(Path(__file__).read_bytes()),
        "compiler": compiler, "compiler_realpath": str(Path(compiler).resolve()),
        "compiler_sha256": digest(Path(compiler).read_bytes()),
        "compiler_version": version.decode(),
        "source_base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_base_tree": subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip(),
        "source_status": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
        "identity_note": "Base commit is not the uncommitted driver identity; exact driver, runner, contract and effective member hashes bind this execution."
    }
    (output / "SOURCE_MANIFEST.json").write_text(json.dumps(source_manifest, indent=2) + "\n")
    results, checks, receipts = {}, {}, {}
    with tempfile.TemporaryDirectory(prefix="p02b-hyrec-") as tmp:
        for lane in ("baseline", "refined"):
            directory = Path(tmp) / lane
            directory.mkdir()
            for name, data in members.items():
                relative = Path(name).relative_to("HyRec")
                path = directory / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                if lane == "refined" and relative.name == "hyrec_params.h":
                    data = refinement_header(data)
                path.write_bytes(data)
            shutil.copyfile(HERE / "endpoint_driver.c", directory / "endpoint_driver.c")
            effective_hashes = {p.name: digest(p.read_bytes()) for p in sorted(directory.iterdir()) if p.is_file()}
            (output / (lane + ".effective_sources.json")).write_text(json.dumps(effective_hashes, indent=2) + "\n")
            build = [compiler, "-O2", *SOURCES, "-lm", "-o", "endpoint"]
            _, build_receipt = record_command(build, directory, output, lane + ".build")
            executable_hash = digest((directory / "endpoint").read_bytes())
            stdout, run_receipt = record_command([str(directory / "endpoint")], directory,
                output, lane + ".run", stdin=members[contract["input_member"]],
                timeout=contract["run_wall_limit_seconds_each"])
            result = json.loads(stdout)
            if result["grid"]["DLNA"] != contract[lane + "_DLNA"]:
                raise ValueError("DLNA_MISMATCH:" + lane)
            results[lane] = result
            checks[lane] = validate_endpoint(result, contract)
            receipts[lane] = {"executable_sha256": executable_hash, "build": build_receipt, "run": run_receipt}
            (output / (lane + ".json")).write_text(json.dumps(result, indent=2) + "\n")
    errors = compare_endpoints(results["baseline"], results["refined"], contract)
    validation = {"status": "PASS_SCOPED", "scope": contract["scope"],
                  "endpoint_checks": checks, "relative_endpoint_differences": errors,
                  "relative_limit": contract["endpoint_relative_tolerance"],
                  "receipts": receipts, "science_runs": 2,
                  "numerical_claim": "One time-step halving comparison; no observed convergence order or global model error certificate.",
                  "REI_Bianchi_IC_adoption": "HOLD", "independent_review": "PENDING"}
    (output / "VALIDATION.json").write_text(json.dumps(validation, indent=2) + "\n")
    print(json.dumps({"status": validation["status"], "relative_endpoint_differences": errors,
                      "output": str(output)}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True, help="New evidence directory; existing directories are refused")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("evidence directory already exists; refusing to modify it")
    try:
        run(args.output.resolve())
    except Exception as exc:
        if args.output.exists() and not (args.output / "FAILURE.json").exists():
            (args.output / "FAILURE.json").write_text(json.dumps({"status": "FAIL", "error": repr(exc)}, indent=2) + "\n")
        raise


if __name__ == "__main__":
    main()
