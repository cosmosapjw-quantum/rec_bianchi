"""Independent sparse Decimal reconstruction of saved electron-point outputs.

validate_record(record, precision=80) and validate_all(records, outdir) perform
no native calls. plot_all(records, validation_summary, outdir) uses saved data.
"""
from decimal import Decimal, localcontext
from pathlib import Path
import copy
import json
import math
import struct

N = 311
EPS = Decimal.from_float(2.0 ** -52)
PARITY_FACTOR = 512
RESIDUAL_FACTOR = 4096


def _d(value):
    if not isinstance(value, str):
        raise ValueError('expected a binary64 hexadecimal string')
    x = float.fromhex(value)
    if not math.isfinite(x):
        raise ValueError('nonfinite binary64 value')
    return Decimal.from_float(x)


def _bits(value):
    x = float.fromhex(value)
    if not math.isfinite(x):
        raise ValueError('nonfinite binary64 value')
    return struct.pack('>d', x)


def _vector(value, size, name):
    if not isinstance(value, list) or len(value) != size:
        raise ValueError(f'{name} must have length {size}')
    return [_d(x) for x in value]


def _matrix(value, rows, cols, name):
    if not isinstance(value, list) or len(value) != rows:
        raise ValueError(f'{name} must have {rows} rows')
    return [_vector(row, cols, f'{name}[{i}]') for i, row in enumerate(value)]


def _ratio(terms, source):
    numerator = abs(sum(terms, Decimal(0)) - source)
    denominator = sum((abs(t) for t in terms), Decimal(0)) + abs(source)
    if denominator == 0:
        return Decimal(0) if numerator == 0 else Decimal('Infinity')
    return numerator / denominator


def validate_record(record, precision=80):
    """Return parity and direct block-residual checks for one frozen record.

    Decimal precision applies to all reconstruction arithmetic; binary64
    values are converted exactly by Decimal.from_float. Malformed or nonfinite
    inputs raise ValueError instead of being admitted.
    """
    with localcontext() as ctx:
        ctx.prec = precision
        o, saved = record['output'], record['saved']
        xr = _vector(o['xr'], 2, 'xr')
        xv = _vector(o['xv'], N, 'xv')
        _vector(saved['xr'], 2, 'saved.xr')
        _vector(saved['xv'], N, 'saved.xv')
        A = _matrix(o['A'], 2, 2, 'A')
        B = _matrix(o['B'], 2, N, 'B')
        C = _matrix(o['C'], 2, N, 'C')
        V = _matrix(o['V'], 3, N, 'V')
        sr = _vector(o['sr'], 2, 'sr')
        sv = _vector(o['sv'], N, 'sv')
        alpha = _vector(o['Alpha'], 2, 'Alpha')
        dalpha = _vector(o['DAlpha'], 2, 'DAlpha')
        beta = _vector(o['Beta'], 2, 'Beta')
        s, x1, delta, H, nH = (_d(o[k]) for k in ('s', 'x1', 'Delta', 'H', 'nH'))
        if H <= 0 or nH <= 0:
            raise ValueError('H and nH must be positive')
        fh, old_fh = _d(o['FH']), _d(saved['FH'])
        sf = sum((nH * (abs(s * x1 * dalpha[i]) + abs(alpha[i] * delta))
                  + abs(xr[i] * beta[i]) for i in range(2)), Decimal(0)) / H
        difference = abs(fh - old_fh)
        parity_pass = difference <= PARITY_FACTOR * EPS * sf if sf else difference == 0
        parity_units = difference / (EPS * sf) if sf else (Decimal(0) if difference == 0 else Decimal('Infinity'))
        rows = []
        for i in range(2):
            rows.append(_ratio([A[i][j] * xr[j] for j in range(2)] +
                               [B[i][j] * xv[j] for j in range(N)], sr[i]))
        for i in range(N):
            terms = [C[j][i] * xr[j] for j in range(2)] + [V[0][i] * xv[i]]
            if i > 0:
                terms.append(V[1][i] * xv[i - 1])
            if i + 1 < N:
                terms.append(V[2][i] * xv[i + 1])
            rows.append(_ratio(terms, sv[i]))
        maximum = max(rows)
        max_index = rows.index(maximum)
        residual_pass = maximum <= RESIDUAL_FACTOR * EPS
        return {
            'index': record['index'], 'call_id': record['call_id'], 'slot': record['slot'],
            'pass': bool(parity_pass and residual_pass), 'parity_pass': bool(parity_pass),
            'residual_pass': bool(residual_pass), 'max_normalized_residual': str(maximum),
            'S_F': str(sf), 'abs_FH_difference': str(difference),
            'parity_eps_units': str(parity_units),
            'FH_bitwise_equal': _bits(o['FH']) == _bits(saved['FH']),
            'xr_bitwise_equal_count': sum(_bits(a) == _bits(b) for a, b in zip(o['xr'], saved['xr'])),
            'xv_bitwise_equal_count': sum(_bits(a) == _bits(b) for a, b in zip(o['xv'], saved['xv'])),
            'residual_details': {'max_row': max_index, 'real_rows': [str(x) for x in rows[:2]],
                                 'virtual_rows': [str(x) for x in rows[2:]]},
        }


def _write_json(path, data):
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(data, indent=2, allow_nan=False) + '\n')
    if path.stat().st_size >= 5 * 1024 * 1024:
        raise ValueError(f'output exceeds 5 MiB: {path}')


def _mutations(record):
    """Apply three explicit saved-output corruptions, never invoking the solver."""
    bc = copy.deepcopy(record)
    bc['output']['B'], bc['output']['C'] = bc['output']['C'], bc['output']['B']
    band = copy.deepcopy(record)
    band['output']['V'][1], band['output']['V'][2] = band['output']['V'][2], band['output']['V'][1]
    solution = copy.deepcopy(record)
    # Perturb the represented solution at its largest absolute component, so
    # the control is meaningful even when individual radiation bins are zero.
    candidates = [('xr', i, abs(float.fromhex(x))) for i, x in enumerate(solution['output']['xr'])]
    candidates += [('xv', i, abs(float.fromhex(x))) for i, x in enumerate(solution['output']['xv'])]
    key, i, magnitude = max(candidates, key=lambda x: x[2])
    old = float.fromhex(solution['output'][key][i])
    new = old * 2 if magnitude and math.isfinite(old * 2) else (1.0 if not magnitude else old / 2)
    solution['output'][key][i] = new.hex()
    return {'B_C_swap': bc, 'band_swap': band, 'changed_solution': solution}


def validate_all(records, outdir):
    """Validate 132 saved records and persist bounded JSON reports.

    Returns a JSON-serializable summary, including output paths. Acceptance is
    the frozen parity and residual gates plus the stated mutation controls.
    Invalid schema raises; failed gates and controls are recorded, not hidden.
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    if len(records) != 132 or [r['index'] for r in records] != list(range(132)):
        raise ValueError('expected 132 records in index order 0..131')
    if len({(r['call_id'], r['slot']) for r in records}) != 132:
        raise ValueError('duplicate call_id/slot binding')
    results = [validate_record(r) for r in records]
    comparisons = []
    for i in (0, 66, 131):
        p40 = validate_record(records[i], 40)
        p80 = results[i]
        comparisons.append({'index': i, 'precision_40': {
            k: p40[k] for k in ('max_normalized_residual', 'S_F', 'abs_FH_difference', 'parity_eps_units', 'parity_pass', 'residual_pass')},
            'precision_80': {k: p80[k] for k in ('max_normalized_residual', 'S_F', 'abs_FH_difference', 'parity_eps_units', 'parity_pass', 'residual_pass')}})
    controls = {}
    for name, mutated in _mutations(records[0]).items():
        result = validate_record(mutated)
        controls[name] = {'max_normalized_residual': result['max_normalized_residual'],
                          'residual_pass': result['residual_pass'],
                          'detected': not result['residual_pass']}
    # Small batches leave substantial room below the per-file size limit.
    result_paths = []
    for start in range(0, len(results), 20):
        path = outdir / f'validation_records_{start:03d}_{min(start + 19, 131):03d}.json'
        _write_json(path, results[start:start + 20])
        result_paths.append(str(path))
    precision_path = outdir / 'precision_40_80.json'
    _write_json(precision_path, comparisons)
    summary = {
        'count': len(results), 'precision': 80, 'eps64': str(EPS),
        'parity_threshold_eps_units': PARITY_FACTOR,
        'residual_threshold': str(RESIDUAL_FACTOR * EPS),
        'parity_pass_count': sum(x['parity_pass'] for x in results),
        'residual_pass_count': sum(x['residual_pass'] for x in results),
        'FH_bitwise_equal_count': sum(x['FH_bitwise_equal'] for x in results),
        'xr_bitwise_equal_count': sum(x['xr_bitwise_equal_count'] for x in results),
        'xv_bitwise_equal_count': sum(x['xv_bitwise_equal_count'] for x in results),
        'max_normalized_residual': str(max(Decimal(x['max_normalized_residual']) for x in results)),
        'max_parity_eps_units': str(max(Decimal(x['parity_eps_units']) for x in results)),
        'mutation_controls': controls, 'record_paths': result_paths,
        'precision_comparison_path': str(precision_path),
        'pass': all(x['pass'] for x in results) and all(c['detected'] for c in controls.values()),
    }
    summary['summary_path'] = str(outdir / 'validation_summary.json')
    _write_json(Path(summary['summary_path']), summary)
    return summary


def plot_all(records, validation_summary, outdir):
    """Generate two PNGs and a two-page PDF using saved data only."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    if len(records) != 132:
        raise ValueError('expected 132 saved records')
    results = []
    for path in validation_summary['record_paths']:
        results.extend(json.loads(Path(path).read_text(encoding='utf-8')))
    if len(results) != len(records) or any(a['index'] != b['index'] for a, b in zip(records, results)):
        raise ValueError('validation results do not match records')
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    ix = [r['index'] for r in records]
    fh = [float.fromhex(r['output']['FH']) for r in records]
    saved_fh = [float.fromhex(r['saved']['FH']) for r in records]
    diffs = [float(Decimal(r['abs_FH_difference'])) for r in results]
    thresholds = [float(Decimal(r['S_F']) * EPS * PARITY_FACTOR) for r in results]
    residuals = [float(Decimal(r['max_normalized_residual'])) for r in results]
    if not all(math.isfinite(v) for v in fh + saved_fh + diffs + thresholds + residuals):
        raise ValueError('cannot plot nonfinite saved/validated values')
    def linthresh(values):
        positive = [v for v in values if v > 0]
        return max(min(positive) * 0.1, math.ulp(0.0)) if positive else 1.0

    fig1, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True, constrained_layout=True)
    axes[0].plot(ix, saved_fh, label='Saved FH', linewidth=1.2)
    axes[0].plot(ix, fh, label='New FH', linewidth=0.9, linestyle='--')
    axes[0].set_ylabel('FH'); axes[0].legend(); axes[0].grid(alpha=.2)
    axes[1].plot(ix, diffs, label='Absolute FH difference')
    axes[1].plot(ix, thresholds, label='512 ε64 S_F threshold')
    axes[1].set_yscale('symlog', linthresh=linthresh(diffs + thresholds))
    axes[1].set_ylabel('Absolute magnitude'); axes[1].set_xlabel('Writer index')
    axes[1].legend(); axes[1].grid(alpha=.2)
    fig2, ax = plt.subplots(figsize=(10, 4.5), constrained_layout=True)
    ax.plot(ix, residuals, label='Maximum normalized residual')
    ax.axhline(float(RESIDUAL_FACTOR * EPS), color='tab:red', linestyle='--', label='4096 ε64 threshold')
    ax.set_yscale('symlog', linthresh=linthresh(residuals + [float(RESIDUAL_FACTOR * EPS)]))
    ax.set_xlabel('Writer index'); ax.set_ylabel('Normalized residual')
    ax.legend(); ax.grid(alpha=.2)
    p1, p2, pdf = (outdir / 'fh_parity.png', outdir / 'normalized_residual.png', outdir / 'validation_plots.pdf')
    fig1.savefig(p1, dpi=150); fig2.savefig(p2, dpi=150)
    with PdfPages(pdf) as pages:
        pages.savefig(fig1); pages.savefig(fig2)
    plt.close(fig1); plt.close(fig2)
    return {'fh_parity_png': str(p1), 'normalized_residual_png': str(p2), 'pdf': str(pdf)}
