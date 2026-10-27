"""Independent original point evaluation from raw binary64 source scalars.

No import from the production interval implementation. Bridges are original
point differences and the native absolute interpolant is evaluated directly.
"""
from decimal import Decimal, localcontext, InvalidOperation, Overflow, Underflow, Subnormal
from fractions import Fraction

PRECISION = 140

def evaluate(raw):
    with localcontext() as c:
        c.prec = PRECISION
        for s in (InvalidOperation, Overflow, Underflow, Subnormal): c.traps[s] = True
        def original(v):
            if isinstance(v, Fraction): return Decimal(v.numerator)/Decimal(v.denominator)
            if isinstance(v, str) and ('0x' in v):
                n, d = float.fromhex(v).as_integer_ratio()
            elif isinstance(v, float): n, d = v.as_integer_ratio()
            else: return Decimal(v)
            return Decimal(n)/Decimal(d)
        a, b, q = (original(raw[k]) for k in ('a', 'b', 'q'))
        E, Et, k, T0, z, TR = (original(raw[k]) for k in ('Es', 'Et', 'kN', 'T0', 'z', 'TR'))
        yL, yR, u = (original(raw[k]) for k in ('yL', 'yR', 'u'))
        alpha = (q-a)/(b-a)
        def occupation(t): return (-(E*t.exp()/(k*T0))).exp()
        xa, xb, xq = (E*t.exp()/(k*T0) for t in (a,b,q))
        wa, wb, wq = (occupation(t) for t in (a,b,q))
        # Evaluate original analytic point formulas without production helpers.
        m1c = [xa*(-xa).exp(), xb*(-xb).exp()]
        m2c = [abs((xa**2-xa)*(-xa).exp()), abs((xb**2-xb)*(-xb).exp())]
        if xa <= 1 <= xb: m1c.append((-Decimal(1)).exp())
        for r in ((3-Decimal(5).sqrt())/2, (3+Decimal(5).sqrt())/2):
            if xa <= r <= xb: m2c.append(abs((r**2-r)*(-r).exp()))
        ideal_w = (-(Et/(k*T0*(1+z)))).exp()
        native_w = (-(Et/TR)).exp()
        reference_interpolant = (1-alpha)*wa+alpha*wb
        departure_interpolant = (1-alpha)*yL+alpha*yR
        anchor = u-departure_interpolant
        direct = (u+native_w)-((1-alpha)*(yL+wa)+alpha*(yR+wb))
        chord = reference_interpolant-wq
        coefficient = (q-a)*(b-q)/2
        return {
            'x_left': xa, 'x_right': xb, 'x_query': xq,
            'w_left': wa, 'w_right': wb, 'w_query': wq,
            'w_prime_query': -xq*wq,
            'w_second_query': (xq**2-xq)*wq,
            'w_third_query': (-xq**3+3*xq**2-xq)*wq,
            'G_f':Decimal(1),'G_ff':Decimal(0),'G_eta_f':Decimal(0),
            'G_eta': xq*wq, 'G_etaeta': -(xq**2-xq)*wq,
            'scalar_occupation_K': Decimal(1),
            'M1_ref': max(m1c), 'M2_ref': max(m2c),
            'qstar': -((1+z)*E/Et).ln(),
            'delta_q': q+((1+z)*E/Et).ln(),
            'w_ideal': ideal_w, 'w_native': native_w,
            'B_char': wq-ideal_w, 'B_TR': ideal_w-native_w,
            'B_total': wq-native_w,'B_total_direct':wq-native_w, 'J_ref': chord,
            'chord_coefficient': coefficient,
            'chord_bound': max(m2c)*coefficient,
            'r_anchor': anchor,
            'direct_bridge': direct,
            'decomposed_bridge': anchor-chord-(wq-native_w),
            'represented_occupation_lower_bound': min(yL,yR)+wb,
        }
