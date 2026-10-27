"""Finite controls for new callable only; historical suites are not imported."""
import math
from joint_diagnostic import DiagnosticDomainError, joint_thermal
from decimal_reference import decimal_reference


def run_controls():
    rows = []
    def record(name, passed, details):
        rows.append({'name': name, 'passed': bool(passed), 'details': details})
    for t in (50, 100, 200):
        out = joint_thermal('1', '0', '29.9792458', t)
        ref = decimal_reference('1', '0', '29.9792458', t)
        record('synthetic_exact_coherence_' + str(t), out['analytic_zero'] and out['paired_flux_imbalance_I'] == 0 and out['source_planck_deviation_D'] == 0 and out['source_planck_ratio'] == 1 and float(ref['paired_flux_imbalance_I']) == 0 and float(ref['source_planck_deviation_D']) == 0, 'SYNTHETIC exact cm^-1 to GHz coherence; not a catalog line')
    for nu, expected_sign in [('29.9', 1), ('30.1', -1)]:
        out = joint_thermal('1', '0', nu, 100)
        record('synthetic_opposite_sign_' + nu, math.copysign(1, out['paired_flux_imbalance_I']) == expected_sign and math.copysign(1, out['source_planck_deviation_D']) == -expected_sign, 'SYNTHETIC positive energies/frequency with signed mismatch')
    cases = [
        ('zero_gap', ('1', '1', '30', 50)), ('negative_gap', ('0', '1', '30', 50)),
        ('negative_lower_energy', ('1', '-1', '30', 50)), ('zero_frequency', ('1', '0', '0', 50)),
        ('negative_frequency', ('1', '0', '-1', 50)), ('nan_energy', ('NaN', '0', '30', 50)),
        ('infinite_frequency', ('1', '0', 'Infinity', 50)), ('nan_temperature', ('1', '0', '30', float('nan'))),
        ('zero_temperature', ('1', '0', '30', 0)), ('negative_temperature', ('1', '0', '30', -50)),
        ('unsupported_temperature', ('1', '0', '30', 75)), ('boolean_input', (True, '0', '30', 50)),
        ('binary64_exponent_overflow', ('1e1000', '0', '30', 50)),
    ]
    for name, args in cases:
        try:
            joint_thermal(*args)
        except DiagnosticDomainError as exc:
            record(name, True, str(exc))
        else:
            record(name, False, 'expected DiagnosticDomainError')
    return rows
