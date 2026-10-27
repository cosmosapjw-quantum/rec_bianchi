"""Independent 80-digit positive-flux/original-exponential reference.

No production diagnostic or production transformed formula is imported.
"""
from decimal import Decimal, localcontext


def decimal_reference(upper_cm_inverse, lower_cm_inverse, frequency_GHz, temperature_K):
    with localcontext() as ctx:
        ctx.prec = 80
        h, c, k_B = Decimal('6.62607015e-34'), Decimal('299792458'), Decimal('1.380649e-23')
        energy_gap = h * c * Decimal(100) * (Decimal(str(upper_cm_inverse)) - Decimal(str(lower_cm_inverse)))
        photon_energy = h * Decimal('1e9') * Decimal(str(frequency_GHz))
        kT = k_B * Decimal(str(temperature_K))
        x_E, x_nu = energy_gap / kT, photon_energy / kT
        b, r = (-x_nu).exp(), (-x_E).exp()
        up, down = b / (1 - b), r / (1 - b)
        imbalance = (up - down) / (up + down)
        ratio = (x_nu.exp() - 1) / (x_E.exp() - 1)
        return {'precision_digits': 80, 'positive_up_flux': str(up), 'positive_down_flux': str(down),
                'paired_flux_imbalance_I': str(imbalance), 'source_planck_ratio': str(ratio),
                'source_planck_deviation_D': str(ratio - 1)}
