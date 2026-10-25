"""Read the literal LAMDA rows independently and audit the new adapter only.

The reference arithmetic uses Fraction for units/gaps and Decimal(80) for
Boltzmann factors. No existing compiler, trajectory or campaign is rerun.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("module", type=Path)
    parser.add_argument("wu_module", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
    resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    begin = time.perf_counter()
    raw = args.source.read_bytes()
    assert len(raw) == 2289
    assert hashlib.sha256(raw).hexdigest() == "0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb"
    literal = raw.decode("ascii").splitlines()
    first_level = literal.index("!LEVEL + ENERGIES(cm^-1) + WEIGHT + J (or other quantum numbers)") + 1
    levels = {int(t[0]): t for t in (line.split() for line in literal[first_level:first_level+9])}
    first_line = literal.index("!TRANS + U + L + A(s^-1) + FREQ(GHz) + E_u/k(K)") + 1
    lines = [line.split() for line in literal[first_line:first_line+8]]
    collision_headers = [i for i, line in enumerate(literal) if line == "!TRANS + UP + LOW + RATES [cm3 s-1]"]
    collision_rows = {collider: [line.split() for line in literal[start+1:start+10]]
                      for collider, start in zip((2, 3), collision_headers)}
    hd = load(args.module, "reviewed_hd")
    dataset = hd.parse_hd(raw)
    c, h, kb = Fraction(299792458), Fraction("6.62607015e-34"), Fraction("1.380649e-23")
    checks = []
    checks.append({"id": "raw_roundtrip", "pass": dataset.source_roundtrip() == raw})
    for identity, tokens in levels.items():
        record = dataset.level(identity)
        assert record.energy_cm_inverse.literal == tokens[1]
        assert record.degeneracy.literal == tokens[2]
        assert record.J == int(tokens[3])
        assert Fraction(record.energy_J) == h*c*100*Fraction(tokens[1])
    checks.append({"id": "nine_literal_levels_exact_SI", "pass": True})
    frequency_gaps = []
    for row in lines:
        number, upper, lower = map(int, row[:3])
        exact_gap = abs(c*100*(Fraction(levels[upper][1])-Fraction(levels[lower][1]))-10**9*Fraction(row[4]))
        assert Fraction(hd.line_frequency_gap_Hz(dataset, number)) == exact_gap
        assert dataset.line(number).A_per_s.literal == row[3]
        frequency_gaps.append({"line_id": number, "upper_J": upper-1, "lower_J": lower-1,
                               "absolute_gap_Hz": str(exact_gap), "float_Hz": float(exact_gap),
                               "frozen_35Hz_gate_pass": exact_gap <= 35})
    checks.append({"id": "eight_literal_line_gaps_exact_rationals", "pass": True})
    residuals = []
    with localcontext() as context:
        context.prec = 80
        for collider, rows in collision_rows.items():
            for row in rows:
                upper, lower = int(row[1]), int(row[2])
                gap = h*c*100*(Fraction(levels[upper][1])-Fraction(levels[lower][1]))
                g_ratio = Fraction(levels[upper][2])/Fraction(levels[lower][2])
                for column, temperature in enumerate((50, 100, 200), start=3):
                    downward = Fraction(row[column])/10**6
                    assert Fraction(dataset.downward_rate(collider, upper, lower, temperature)) == downward
                    exponent = -gap/(kb*temperature)
                    prefactor = downward*g_ratio
                    expected = (Decimal(prefactor.numerator)/Decimal(prefactor.denominator)
                                *(Decimal(exponent.numerator)/Decimal(exponent.denominator)).exp())
                    actual = dataset.upward_rate(collider, lower, upper, temperature)
                    residual = abs(actual-float(expected))/(abs(actual)+abs(float(expected)))
                    assert residual <= 128*sys.float_info.epsilon
                    residuals.append(residual)
    checks.append({"id": "54_literal_collider_rates_exact_SI_and_independent_DB", "pass": True,
                   "maximum_normalized_error": max(residuals)})
    thermal_residuals = []
    with localcontext() as context:
        context.prec = 80
        for row in lines:
            number = int(row[0])
            nu = Fraction(row[4])*10**9
            prefactor = 2*h*nu**3/c**2
            for temperature in (50, 100, 200):
                exponent = h*nu/(kb*temperature)
                expected_planck = ((Decimal(prefactor.numerator)/Decimal(prefactor.denominator))
                                   /((Decimal(exponent.numerator)/Decimal(exponent.denominator)).exp()-1))
                actual = hd.thermal_line(dataset, number, temperature)
                j, alpha = actual["j_nu_J_s_m3_sr_Hz"], actual["alpha_nu_per_m"]
                assert alpha > 0
                reverse = alpha*float(expected_planck)
                residual = abs(j-reverse)/(abs(j)+abs(reverse))
                assert residual <= 128*sys.float_info.epsilon
                thermal_residuals.append(residual)
    checks.append({"id": "24_Kirchhoff_checks_against_independent_Decimal_Planck", "pass": True,
                   "maximum_normalized_error": max(thermal_residuals),
                   "scope": "catalog photon energy used consistently; not an energy-level/frequency compatibility certificate"})
    refusals = [lambda: dataset.downward_rate(2, 2, 1, 75),
                lambda: dataset.downward_rate(2, 2, 1, 201),
                lambda: dataset.downward_rate("H2", 2, 1, 100),
                lambda: dataset.downward_rate((2, 3), 2, 1, 100),
                lambda: dataset.downward_rate(2, 4, 1, 100),
                lambda: hd.thermal_line(dataset, 1, 100, "1e-1000", 1),
                lambda: hd.line_coefficients(dataset, 1, 1, 1, "1e-1000"),
                lambda: hd.line_coefficients(dataset, 1, "1e-320", 0, 1),
                lambda: hd.thermal_line(dataset, 1, "1e-310")]
    for call in refusals:
        try:
            call()
        except hd.AdapterError:
            pass
        else:
            raise AssertionError("unsupported or underflow input was accepted")
    checks.append({"id": "nine_domain_and_nonzero_underflow_refusals", "pass": True})
    inversion = hd.line_coefficients(dataset, 1, 1, 4, 1)
    assert inversion["alpha_nu_per_m"] < 0 and inversion["population_inversion"]
    zero = hd.thermal_line(dataset, 1, 100, 0, 1)
    assert zero["classification"] == "ANALYTIC_ZERO" and zero["normalized_Kirchhoff_residual"] is None
    checks.append({"id": "inversion_and_analytic_zero_distinct", "pass": True})
    canonical = hd.bind_wu_species(dataset, args.wu_module)
    assert len(canonical) == 9 and len({species.key() for species in canonical}) == 9
    for species in canonical:
        assert species.composition == (((1, 1, "ground"), 1), ((1, 2, "ground"), 1))
        assert species.charge == 0 and species.baryon_count() == 3 and "v=UNSPECIFIED" in species.state
    checks.append({"id": "actual_WU_Species_mapping_9_states", "pass": True})
    usage = resource.getrusage(resource.RUSAGE_SELF)
    frequency_ok = all(row["frozen_35Hz_gate_pass"] for row in frequency_gaps)
    result = {"schema": "REC_HD_INDEPENDENT_REFERENCE_CHECK_V1", "status": "PASS_IMPLEMENTATION_REFERENCE_CHECK",
              "source_sha256": hashlib.sha256(raw).hexdigest(),
              "reviewed_code_sha256": hashlib.sha256(args.module.read_bytes()).hexdigest(),
              "WU_source_sha256": hashlib.sha256(args.wu_module.read_bytes()).hexdigest(),
              "review_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "method": "literal header/row extraction; exact Fraction unit and frequency arithmetic; independent 80-digit Decimal exponent",
              "checks": checks, "frequency_gaps": frequency_gaps,
              "frozen_35Hz_gate": "PASS" if frequency_ok else "FAIL_SOURCE_INTERNAL_ENERGY_FREQUENCY_MISMATCH",
              "frequency_gate_passing_lines": [row["line_id"] for row in frequency_gaps if row["frozen_35Hz_gate_pass"]],
              "frequency_gate_failing_lines": [row["line_id"] for row in frequency_gaps if not row["frozen_35Hz_gate_pass"]],
              "consistent_internal_energy_photon_binding_approved": frequency_ok,
              "maximum_independent_Planck_Kirchhoff_residual": max(thermal_residuals),
              "maximum_normalized_DB_error": max(residuals), "DB_records": len(residuals),
              "controlled_scientific_replay": {"old_compiler": 0, "IVP": 0, "RHS": 0, "native": 0},
              "resource": {"cpu_seconds": usage.ru_utime+usage.ru_stime,
                           "execution_wall_seconds": time.perf_counter()-begin,
                           "max_RSS_KiB": usage.ru_maxrss},
              "command_argv": sys.argv,
              "claim_scope": "implementation correctness for the pinned HD source; physical input uncertainty remains unassigned"}
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "maximum_normalized_DB_error": max(residuals),
                      "resource": result["resource"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
