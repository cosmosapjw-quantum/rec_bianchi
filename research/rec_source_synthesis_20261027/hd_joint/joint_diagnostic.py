"""Source-preserving joint thermal diagnostics; no production qualification."""
from fractions import Fraction
import math

C = Fraction('299792458')
H = Fraction('6.62607015e-34')
KB = Fraction('1.380649e-23')
TEMPERATURES_K = (50, 100, 200)


class DiagnosticDomainError(ValueError):
    pass


def exact_number(value, label):
    if isinstance(value, bool):
        raise DiagnosticDomainError(label + ': boolean is unsupported')
    try:
        return value if isinstance(value, Fraction) else Fraction(str(value))
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
        raise DiagnosticDomainError(label + ': expected finite rational/decimal') from exc


def rational_record(value):
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator)}


def joint_thermal(upper_energy_cm_inverse, lower_energy_cm_inverse, frequency_GHz, temperature_K):
    """Return Eq.(1)/(2) diagnostics with exact source delta and SI constants.

    Source energies are wavenumbers in cm^-1, frequency GHz, temperature K.
    This callable does not call or replace a qualified production line consumer.
    """
    upper = exact_number(upper_energy_cm_inverse, 'upper energy')
    lower = exact_number(lower_energy_cm_inverse, 'lower energy')
    nu = exact_number(frequency_GHz, 'frequency')
    temperature = exact_number(temperature_K, 'temperature')
    if lower < 0 or upper <= lower or nu <= 0:
        raise DiagnosticDomainError('require nonnegative lower energy, positive level gap and frequency')
    if temperature not in TEMPERATURES_K:
        raise DiagnosticDomainError('only original 50/100/200 K nodes are supported')
    gap_Hz = C * 100 * (upper - lower) - 10**9 * nu
    x_E_exact = H * C * 100 * (upper - lower) / (KB * temperature)
    x_nu_exact = H * 10**9 * nu / (KB * temperature)
    delta_exact = H * gap_Hz / (KB * temperature)
    # No subtraction of rounded x_E and x_nu occurs here.
    try:
        x_E, x_nu, delta = map(float, (x_E_exact, x_nu_exact, delta_exact))
        if not all(math.isfinite(x) for x in (x_E, x_nu, delta)) or min(x_E, x_nu) <= 0:
            raise DiagnosticDomainError('positive exponents are outside finite binary64 representation')
        if delta_exact == 0:
            imbalance = deviation = 0.0
        else:
            imbalance = math.tanh(delta / 2)
            denominator = -math.expm1(-x_E)
            deviation = math.expm1(-delta) / denominator
            if imbalance == 0 or deviation == 0:
                raise DiagnosticDomainError('nonzero diagnostic underflow')
        ratio = 1.0 + deviation
        if not all(math.isfinite(x) for x in (imbalance, deviation, ratio)) or ratio <= 0:
            raise DiagnosticDomainError('diagnostic outside finite positive-ratio binary64 domain')
    except (OverflowError, ZeroDivisionError) as exc:
        raise DiagnosticDomainError('binary64 diagnostic overflow/underflow') from exc
    return {'signed_frequency_gap_Hz_exact': rational_record(gap_Hz),
            'delta_exact': rational_record(delta_exact), 'x_E_exact': rational_record(x_E_exact),
            'x_nu_exact': rational_record(x_nu_exact), 'delta': delta, 'x_E': x_E, 'x_nu': x_nu,
            'paired_flux_imbalance_I': imbalance, 'source_planck_deviation_D': deviation,
            'source_planck_ratio': ratio, 'analytic_zero': delta_exact == 0}
