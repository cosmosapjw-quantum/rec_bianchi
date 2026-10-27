"""One bounded reviewer continuation: eight original-delay Newton roots.

Does not import production code or replay any donor source routine.
Run only through run_probe.py after root authorization.
"""
import hashlib
import json
from decimal import Decimal as D, localcontext
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
UNIT = HERE.parent.parent
OUT = HERE / "probe001"


def exact_float(value):
    numerator, denominator = float(value).as_integer_ratio()
    return D(numerator) / D(denominator)


def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + "\n")


def main():
    OUT.mkdir(exist_ok=False)
    source = UNIT / "results/primary001/SOURCE_BINDING.npz"
    archive = np.load(source, allow_pickle=False)
    cases = [(37, (Fraction(4, 9), Fraction(1, 9), Fraction(4, 9))),
             (289, (Fraction(1, 35), Fraction(9, 35), Fraction(25, 35)))]
    roots = []
    checks = []
    charged = 0
    save("SOURCE.json", {"binding_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                         "cases": [{"query": j, "squared_direction": list(map(str, w))}
                                   for j, w in cases],
                         "method": "Decimal90 original-delay Newton; independent implementation",
                         "max_roots": 8, "max_iterations": 16,
                         "production_imports": 0, "RHS": 0, "IVP": 0, "matvecs": 0})
    try:
        with localcontext() as context:
            context.prec = 90
            v = (D(1), -D(1) / 2, -D(1) / 2)
            for query, rational_weights in cases:
                weights = tuple(D(w.numerator) / D(w.denominator) for w in rational_weights)
                length, x, slope, h = map(exact_float,
                    (archive["Lambda"][query], archive["x_target"][query],
                     archive["slope"][query], archive["h"]))
                reference = (-x).exp()
                first_moment = sum(w * vi for w, vi in zip(weights, v))
                second_moment = sum(w * vi * vi for w, vi in zip(weights, v))
                absolute_moment = sum(w * abs(vi) for w, vi in zip(weights, v))
                retimed_first = length * first_moment
                retimed_second = -2 * length * first_moment ** 2 + 2 * length ** 2 * (second_moment - first_moment ** 2)
                a1 = (slope - x * reference) * retimed_first
                a2 = (slope - x * reference) * retimed_second + (x * x - x) * reference * retimed_first ** 2
                gross1 = (abs(slope) + x * reference) * length * absolute_moment
                gross2 = ((abs(slope) + x * reference) *
                          (2 * length * absolute_moment ** 2 + 2 * length ** 2 * (second_moment + absolute_moment ** 2)) +
                          (x * x + x) * reference * length ** 2 * absolute_moment ** 2)
                for divisor in (1, 2):
                    step = h / divisor
                    values = {}
                    for sign in (-1, 1):
                        charged += 1
                        if charged > 8:
                            raise RuntimeError("REVIEW_ROOT_CAP")
                        save("COUNTERS.json", {"roots_charged": charged, "cap": 8})
                        parameter = sign * step
                        distance = length
                        for iteration in range(1, 17):
                            factors = [(2 * parameter * vi * distance).exp() for vi in v]
                            total = sum(w * factor for w, factor in zip(weights, factors))
                            residual = distance + total.ln() / 2 - length
                            if abs(residual) <= D("1e-70") * abs(length):
                                break
                            derivative = 1 + parameter * sum(w * vi * factor for w, vi, factor in zip(weights, v, factors)) / total
                            if derivative <= 0:
                                raise RuntimeError("NONPOSITIVE_ROOT_DERIVATIVE")
                            distance -= residual / derivative
                        else:
                            raise RuntimeError("REVIEW_NEWTON_ITERATION_CAP")
                        shift = length - distance
                        values[sign] = slope * shift + (-x * shift.exp()).exp()
                        roots.append({"query": query, "squared_direction": list(map(str, rational_weights)),
                                      "step_divisor": divisor, "sign": sign, "parameter": str(parameter),
                                      "distance": str(distance), "shift": str(shift),
                                      "full_value": str(values[sign]), "residual": str(residual),
                                      "iterations": iteration})
                        save("ROOTS.json", roots)
                    fd1 = (values[1] - values[-1]) / (2 * step)
                    fd2 = (values[1] + values[-1] - 2 * reference) / (step * step)
                    error1 = abs(fd1 - a1) / gross1
                    error2 = abs(fd2 - a2) / gross2
                    checks.append({"query": query, "step_divisor": divisor,
                                   "analytic_first": str(a1), "analytic_second": str(a2),
                                   "finite_first": str(fd1), "finite_second": str(fd2),
                                   "first_gross": str(gross1), "second_gross": str(gross2),
                                   "first_normalized_error": str(error1), "second_normalized_error": str(error2),
                                   "pass": error1 <= D("2e-7") and error2 <= D("2e-7")})
                    save("CHECKS.json", checks)
                    if not checks[-1]["pass"]:
                        raise RuntimeError("FROZEN_FINITE_DERIVATIVE_TOLERANCE")
        save("SUMMARY.json", {"status": "PASS", "roots_charged": charged,
                              "checks": len(checks), "precision_digits": 90,
                              "max_first_normalized_error": max(float(c["first_normalized_error"]) for c in checks),
                              "max_second_normalized_error": max(float(c["second_normalized_error"]) for c in checks),
                              "tolerance": 2e-7,
                              "scope": "Two off-grid configurations of represented controlled chart; finite numerical evidence"})
    except BaseException as error:
        save("FAILURE.json", {"type": type(error).__name__, "message": str(error),
                              "roots_charged": charged, "prefix_preserved": True})
        raise


if __name__ == "__main__":
    main()
