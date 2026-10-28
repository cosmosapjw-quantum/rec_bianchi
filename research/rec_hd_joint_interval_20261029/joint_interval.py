#!/usr/bin/env python3
"""Exact shared-level closed-enclosure diagnostic; no source/rate correction.

All decisions use Fraction.  A scale other than one is a diagnostic distance,
never a replacement for the frozen 35 Hz source gate.  Closed half-quantum
intervals enclose rounding-tie conventions; they do not encode tie-to-even.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

C_M_S = 299792458
SOURCE_SHA256 = '0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb'
SOURCE_BYTES = 2289
_DECIMAL = re.compile(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z')


def decimal_token(token: str) -> Decimal:
    """Parse a finite, explicitly printed decimal without losing trailing zeros."""
    if not isinstance(token, str) or not _DECIMAL.fullmatch(token):
        raise ValueError('expected a finite decimal string')
    try:
        d = Decimal(token)
    except InvalidOperation as err:
        raise ValueError('malformed decimal literal') from err
    if not d.is_finite():
        raise ValueError('nonfinite decimal literal')
    return d


def half_quantum(token: str) -> Fraction:
    exponent = decimal_token(token).as_tuple().exponent
    return (Fraction(10 ** exponent, 2) if exponent >= 0
            else Fraction(1, 2 * 10 ** (-exponent)))


def exact(value) -> Fraction:
    """Accept exact rational inputs; reject floats and booleans explicitly."""
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError('use exact rational input, not float/bool')
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError('nonfinite rational input')
        return Fraction(value)
    if isinstance(value, str):
        if '/' not in value:
            return Fraction(decimal_token(value))
        if re.fullmatch(r'[+-]?[0-9]+/[0-9]+', value):
            try:
                return Fraction(value)
            except ZeroDivisionError as err:
                raise ValueError('zero rational denominator') from err
    raise ValueError('unsupported exact rational input')


def model(deltas, radii, line_radii):
    d, r, s = ([exact(v) for v in seq]
               for seq in (deltas, radii, line_radii))
    if not r or len(r) != len(d) + 1 or len(s) != len(d):
        raise ValueError('model requires n deltas, n+1 term radii, n line radii')
    if any(v < 0 for v in r + s):
        raise ValueError('radii must be nonnegative')
    return d, r, s


def reachability(deltas, radii, line_radii, scale=1) -> dict:
    """O(n) exact decision plus backward primal witness if feasible."""
    d, r, s = model(deltas, radii, line_radii)
    lam = exact(scale)
    if lam < 0:
        raise ValueError('scale must be nonnegative')
    intervals = [(-lam * r[0], lam * r[0])]
    for j, delta in enumerate(d, start=1):
        lo, hi = intervals[-1]
        next_lo = max(-lam * r[j], lo - delta - lam * s[j - 1])
        next_hi = min(lam * r[j], hi - delta + lam * s[j - 1])
        if next_lo > next_hi:
            return {'feasible': False, 'first_empty_level': j,
                    'empty_interval': [next_lo, next_hi],
                    'reachable_intervals': intervals, 'x': None, 'y': None,
                    'scale': lam}
        intervals.append((next_lo, next_hi))
    x = [Fraction(0)] * len(r)
    x[-1] = sum(intervals[-1]) / 2
    for j in range(len(d), 0, -1):
        lo, hi = intervals[j - 1]
        lo = max(lo, x[j] + d[j - 1] - lam * s[j - 1])
        hi = min(hi, x[j] + d[j - 1] + lam * s[j - 1])
        if lo > hi:
            raise AssertionError('backward witness violates reachability invariant')
        x[j - 1] = (lo + hi) / 2
    y = [delta + x[j + 1] - x[j] for j, delta in enumerate(d)]
    assert all(abs(v) <= lam * radius for v, radius in zip(x, r))
    assert all(abs(v) <= lam * radius for v, radius in zip(y, s))
    residuals = [delta + x[j + 1] - x[j] - y[j]
                 for j, delta in enumerate(d)]
    assert all(v == 0 for v in residuals)
    return {'feasible': True, 'first_empty_level': None,
            'reachable_intervals': intervals, 'x': x, 'y': y,
            'equality_residuals': residuals, 'scale': lam}


def segment_certificate(deltas, radii, line_radii, scale=1) -> dict:
    """Independent O(n^2) all-segment inequalities and sharp common scale.

    lambda_min=None with minimum_scale_kind='INFINITE' denotes an obstruction
    of nonzero defect and zero total radius, not a missing or zero value.
    """
    d, r, s = model(deltas, radii, line_radii)
    lam = exact(scale)
    if lam < 0:
        raise ValueError('scale must be nonnegative')
    rows, maximum, maximizers, infinite = [], Fraction(0), [], []
    for p in range(len(d)):
        defect, photons = Fraction(0), Fraction(0)
        for q in range(p + 1, len(d) + 1):
            defect += d[q - 1]
            photons += s[q - 1]
            denominator = r[p] + r[q] + photons
            required = abs(defect) / denominator if denominator else None
            row = {'p': p, 'q': q, 'signed_defect_Hz': defect,
                   'radius_at_unit_scale_Hz': denominator,
                   'required_scale': required,
                   'satisfied': abs(defect) <= lam * denominator}
            rows.append(row)
            if denominator == 0:
                if defect:
                    infinite.append(row)
            elif required > maximum:
                maximum, maximizers = required, [row]
            elif required == maximum:
                maximizers.append(row)
    return {'feasible': all(row['satisfied'] for row in rows),
            'segment_count': len(rows), 'segments': rows,
            'lambda_min': None if infinite else maximum,
            'minimum_scale_kind': 'INFINITE' if infinite else 'FINITE',
            'maximizing_segments': infinite if infinite else maximizers,
            'scale': lam}


def source_model(fixture: dict):
    levels, lines = fixture['levels'], fixture['radiative_lines']
    if len(levels) != 9 or len(lines) != 8:
        raise ValueError('fixed HD fixture requires 9 terms and 8 lines')
    if any(type(x.get('J')) is not int for x in levels) or [x['J'] for x in levels] != list(range(9)):
        raise ValueError('term J ordering must be 0..8')
    if any(type(x.get('J_up')) is not int for x in lines) or [x['J_up'] for x in lines] != list(range(1, 9)):
        raise ValueError('line J ordering must be 1..8')
    w = [Fraction(decimal_token(x['w_cm_minus_1'])) for x in levels]
    frequencies = [Fraction(decimal_token(x['nu_GHz'])) * 10**9 for x in lines]
    if any(b <= a for a, b in zip(w, w[1:])) or any(f <= 0 for f in frequencies):
        raise ValueError('terms must increase and photon frequencies be positive')
    deltas = [100 * C_M_S * (w[j + 1] - w[j]) - frequencies[j]
              for j in range(8)]
    r = [100 * C_M_S * half_quantum(x['w_cm_minus_1']) for x in levels]
    s = [10**9 * half_quantum(x['nu_GHz']) for x in lines]
    return deltas, r, s


def extract_pinned_lamda(path: Path) -> dict:
    b = path.read_bytes()
    if len(b) != SOURCE_BYTES or hashlib.sha256(b).hexdigest() != SOURCE_SHA256:
        raise ValueError('LAMDA raw size/SHA256 mismatch')
    try:
        rows = b.decode('ascii').splitlines()
        marker = '!LEVEL + ENERGIES(cm^-1) + WEIGHT + J (or other quantum numbers)'
        start = rows.index(marker) + 1
        level_rows = [r.split() for r in rows[start:start + 9]]
        start = rows.index('!TRANS + U + L + A(s^-1) + FREQ(GHz) + E_u/k(K)') + 1
        photon_rows = [r.split() for r in rows[start:start + 8]]
        levels = [{'J': int(r[3]), 'w_cm_minus_1': r[1]} for r in level_rows]
        lines = [{'J_up': int(r[1]) - 1, 'nu_GHz': r[4]} for r in photon_rows]
    except (UnicodeError, ValueError, IndexError) as err:
        raise ValueError('invalid pinned LAMDA layout') from err
    return {'levels': levels, 'radiative_lines': lines}


def source_certificate(fixture: dict, lamda: Path | None = None) -> dict:
    if (fixture.get('source_sha256') != SOURCE_SHA256
            or fixture.get('source_bytes') != SOURCE_BYTES):
        raise ValueError('fixture must retain the fixed source identity')
    if lamda is not None:
        raw = extract_pinned_lamda(lamda)
        if any(raw[k] != fixture[k] for k in ('levels', 'radiative_lines')):
            raise ValueError('fixture literals differ from pinned raw source')
    d, r, s = source_model(fixture)
    nominal = reachability(d, r, s)
    segments = segment_certificate(d, r, s)
    if nominal['feasible'] != segments['feasible']:
        raise AssertionError('independent exact algorithms disagree')
    minimum = segments['lambda_min']
    witness = None if minimum is None else reachability(d, r, s, minimum)
    if witness is not None and not witness['feasible']:
        raise AssertionError('minimum-scale certificate lacks primal witness')
    row_pass = [abs(delta) <= r[j] + r[j + 1] + s[j]
                for j, delta in enumerate(d)]
    with localcontext() as context:
        context.prec = 60
        minimum_decimal = (None if minimum is None else
                           str(Decimal(minimum.numerator) / Decimal(minimum.denominator)))
    return {'schema': 'REC_HD_JOINT_CLOSED_ENCLOSURE_V1',
            'source_identity': {'sha256': SOURCE_SHA256, 'bytes': SOURCE_BYTES,
                                'raw_verified_this_execution': lamda is not None,
                                'input_mode': 'PINNED_RAW_PLUS_FIXTURE' if lamda is not None
                                              else 'EXTRACTED_LITERAL_FIXTURE_ONLY'},
            'enclosure': 'closed half-quantum for all nine terms, including J0',
            'units': 'delta,r,s,x,y: Hz; scale: dimensionless',
            'physical_admission': False, 'original_35Hz_gate': 'FAIL_7_OF_8_PRESERVED',
            'CDMS_2011_v2': 'NOT_ACQUIRED',
            'deltas_Hz': d, 'term_radii_Hz': r, 'line_radii_Hz': s,
            'rowwise_pass': row_pass, 'rowwise_fail_count': row_pass.count(False),
            'nominal_reachability': nominal, 'all_segments': segments,
            'minimum_scale_decimal_display': minimum_decimal,
            'minimum_scale_witness': witness}


def json_exact(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {k: json_exact(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_exact(v) for v in value]
    return value


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fixture', type=Path, default=Path(__file__).with_name('source_literals.json'))
    p.add_argument('--lamda', type=Path, help='optional original 2289-byte SHA-pinned hd.dat')
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    fixture = json.loads(args.fixture.read_text(encoding='utf-8'))
    result = source_certificate(fixture, args.lamda)
    result['fixture_sha256'] = hashlib.sha256(args.fixture.read_bytes()).hexdigest()
    payload = json.dumps(json_exact(result), indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding='utf-8')
    else:
        print(payload, end='')


if __name__ == '__main__':
    main()
