"""Fixed-coefficient incoming-radiation response for REC ELECTRON-FIELD01.

This module never loads the native library or executes a history.  It lifts
saved finite binary64 coefficients into Decimal and solves their real linear
system at the requested working precision.  Decimal results are numerical
approximations, not outward intervals or derivatives of a rounding map.

Ordering:
    state/source = (2s, 2p, virtual[0:311])
    incoming     = (virtual[0:311], Ly[0], Ly[1])
    M = [[A, B], [C, V]], with saved C_storage[i][b] = C[b][i].

The source-column coefficient list has source rows (2, ..., 312, 1, 0).
Its last two entries couple the two Lyman inputs to different real rows.

Public functions accept a FrozenPoint or, where documented, a raw record.
No public function mutates its arguments.  There is no implicit execution.
"""

from dataclasses import dataclass
from decimal import Decimal, localcontext
import math
import struct
from typing import Mapping


N = 311
DIM = N + 2
ZERO = Decimal(0)
ONE = Decimal(1)
TWO = Decimal(2)
THREE = Decimal(3)
SIX = Decimal(6)
SOURCE_SHA256 = "94b454c75b51f7c7af38126510cec609f5d7cfb2eb69ca78a491def54b31791c"
TABLES_SHA256 = "5a427c83e7b80891919d60ff33b8a3332580c0d4054379579a1628cd476c0448"
LIBRARY_SHA256 = "9a1b1586faa55af1899746b51005e2c7309175e904a1f7bc15fa57801442b40b"
P_KEYS = ("xe", "xHII", "nH_cm3", "H_s_inv", "TM_eV", "TR_eV", "fsR", "meR")
TAU_SWITCH = Decimal.from_float(1e-6)
K_LYA = Decimal.from_float(4.662899067555897e15)
K_LYB = Decimal.from_float(1.664786871919931)
SOURCE_ROWS = tuple(range(2, DIM)) + (1, 0)


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _hex_float(value):
    _require(isinstance(value, str), "expected a binary64 hexadecimal string")
    _require(value.lstrip("+-").lower().startswith("0x"), "hexadecimal prefix required")
    number = float.fromhex(value)
    _require(math.isfinite(number), "nonfinite binary64 value")
    return number


def from_hex(value):
    """Exact Decimal lift of a finite represented binary64 input."""
    return Decimal.from_float(_hex_float(value))


def _same_bits(a, b):
    return struct.pack(">d", _hex_float(a)) == struct.pack(">d", _hex_float(b))


def _hex_vector(values, size, name):
    _require(isinstance(values, (list, tuple)) and len(values) == size,
             f"{name}: expected length {size}")
    return tuple(from_hex(value) for value in values)


def _hex_matrix(values, rows, cols, name):
    _require(isinstance(values, (list, tuple)) and len(values) == rows,
             f"{name}: expected {rows} rows")
    return tuple(_hex_vector(row, cols, f"{name}[{i}]")
                 for i, row in enumerate(values))


def _vector(values, size, name):
    """Arithmetic inputs must already have an explicit decimal meaning."""
    _require(isinstance(values, (list, tuple)) and len(values) == size,
             f"{name}: expected length {size}")
    result = []
    for value in values:
        _require(isinstance(value, (Decimal, int, str)) and not isinstance(value, bool),
                 f"{name}: use Decimal, integer, or decimal string; binary floats are ambiguous")
        number = value if isinstance(value, Decimal) else Decimal(value)
        _require(number.is_finite(), f"{name}: nonfinite arithmetic input")
        result.append(number)
    return tuple(result)


def _precision(value):
    _require(isinstance(value, int) and not isinstance(value, bool) and value >= 30,
             "working precision must be an integer at least 30")
    return value


@dataclass(frozen=True)
class FrozenPoint:
    """Immutable parsed snapshot; arrays contain exact Decimal input lifts."""

    index: int
    call_id: int
    slot: int
    A: tuple
    B: tuple
    C_storage: tuple
    V: tuple
    beta: tuple
    tau: tuple
    H: Decimal
    nH: Decimal
    x1: Decimal
    s: Decimal
    delta: Decimal
    alpha: tuple
    dalpha: tuple
    incoming: tuple
    saved_source: tuple
    saved_state: tuple
    saved_FH: Decimal
    P: tuple
    z: Decimal


def parse_record(record):
    """Validate one original primary/control record and copy its coefficients.

    Source identity, native successful-call metadata, original fixed-P labels,
    P/call binding, array shapes and finite/domain restrictions are checked.
    A control's changed incoming is legitimate; its call and P remain fixed.
    Parent file/ZIP hashes are an additional file-level obligation of callers.
    """
    if isinstance(record, FrozenPoint):
        return record
    _require(isinstance(record, Mapping), "record must be a mapping")
    for key in ("index", "call_id", "slot"):
        _require(isinstance(record.get(key), int) and not isinstance(record[key], bool),
                 f"{key}: integer required")
    _require(0 <= record["index"] < 132 and record["call_id"] >= 0 and record["slot"] >= 0,
             "writer identity outside the admitted 132-point scope")
    _require(record.get("source_sha256") == SOURCE_SHA256, "foreign source archive")
    call, out = record["call"], record["output"]
    actual, identity = out["actual_input"], out["identity"]
    _require(record["call_id"] == call["id"] and record["slot"] == call["slot"],
             "call_id/slot binding mismatch")
    _require(out["status"] == 0 and out["kernel_calls"] == 1,
             "saved native point was not successful")
    _require(out["input_nonmutation"] is True and out["table_nonmutation"] is True,
             "saved nonmutation checks did not pass")
    _require(out["electron_scope"] == "FULL_H_STEADY_He_neutral_xe_equals_xHII",
             "foreign electron scope")
    _require(identity["source_archive_sha256"] == SOURCE_SHA256
             and identity["library_sha256"] == LIBRARY_SHA256
             and identity["initialized_tables_sha256"] == TABLES_SHA256,
             "saved source/library/table identity mismatch")
    _require(actual["source_sha256"] == SOURCE_SHA256,
             "actual input source identity mismatch")
    _require(call["model"] == actual["model"] == 3
             and call["phase"] == actual["phase"] == "H_STEADY"
             and actual["helium_neutral"] == 1
             and actual["units"] == "native_cm3_s_eV_eta"
             and actual["temperature_origin"] == "dispatcher",
             "fixed physical/units/temperature-origin labels differ")
    _require(tuple(actual["P_keys"]) == P_KEYS, "P coordinate order mismatch")
    p = _hex_vector(actual["P"], 8, "P")
    _require(all(_same_bits(actual["P"][i], call[key]) for i, key in enumerate(P_KEYS)),
             "actual P does not match recorded dispatcher P")
    _require(p[0] == p[1] and ZERO <= p[1] < ONE
             and all(p[i] > ZERO for i in (2, 3, 4, 5))
             and p[6] == p[7] == ONE,
             "fixed-P domain requires neutral He, xe=xHII, positive scales, fsR=meR=1")
    diag = out["diagnostics"]
    _require(diag["events"] == 472 and all(diag[k] == 0 for k in ("zero", "nonfinite", "overflow")),
             "saved native divisor diagnostics did not pass")

    A = _hex_matrix(out["A"], 2, 2, "A")
    B = _hex_matrix(out["B"], 2, N, "B")
    C = _hex_matrix(out["C"], 2, N, "C_storage")
    V = _hex_matrix(out["V"], 3, N, "V")
    tau = _hex_vector(out["Dtau"], N, "Dtau")
    _require(V[1][0] == V[2][-1] == ZERO, "nonzero off-domain virtual band entry")
    _require(all(value > ZERO for value in V[0]), "nonpositive virtual diagonal")
    _require(all(value >= ZERO for value in tau), "negative optical depth outside model domain")
    H, nH, x1 = (from_hex(out[k]) for k in ("H", "nH", "x1"))
    _require(H == p[3] and nH == p[2] and ZERO < x1 <= ONE,
             "saved H/nH/x1 domain or binding mismatch")
    native_x1 = Decimal.from_float(1.0 - _hex_float(actual["P"][1]))
    _require(x1 == native_x1, "saved x1 does not match the native binary64 subtraction")
    coefficient_TR = from_hex(out["coefficient_TR_eV"])
    coefficient_TM = from_hex(out["coefficient_TM_eV"])
    _require(coefficient_TR == p[5], "coefficient TR disagrees with fsR=meR=1 prelude")
    native_TM = Decimal.from_float((_hex_float(actual["P"][4]) / _hex_float(actual["P"][5]))
                                  * _hex_float(actual["P"][5]))
    _require(coefficient_TM == native_TM, "coefficient TM roundtrip mismatch")
    _require(Decimal.from_float(0.004) <= coefficient_TR <= Decimal.from_float(0.4),
             "coefficient TR outside the frozen table domain")
    native_ratio = _hex_float(out["coefficient_TM_eV"]) / _hex_float(out["coefficient_TR_eV"])
    _require(0.1 <= native_ratio <= 1.0, "coefficient temperature ratio outside frozen table domain")
    beta = _hex_vector(out["Beta"], 2, "Beta")
    _require(all(value >= ZERO for value in beta), "negative photoionization coefficient")
    return FrozenPoint(
        index=record["index"], call_id=record["call_id"], slot=record["slot"],
        A=A, B=B, C_storage=C, V=V, beta=beta, tau=tau, H=H, nH=nH, x1=x1,
        s=from_hex(out["s"]), delta=from_hex(out["Delta"]),
        alpha=_hex_vector(out["Alpha"], 2, "Alpha"),
        dalpha=_hex_vector(out["DAlpha"], 2, "DAlpha"),
        incoming=(_hex_vector(actual["incoming_virtual"], N, "incoming_virtual")
                  + _hex_vector(actual["incoming_lyman"], 2, "incoming_lyman")),
        saved_source=_hex_vector(out["sr"], 2, "sr") + _hex_vector(out["sv"], N, "sv"),
        saved_state=_hex_vector(out["xr"], 2, "xr") + _hex_vector(out["xv"], N, "xv"),
        saved_FH=from_hex(out["FH"]), P=p, z=from_hex(call["z"]),
    )


def _dot(a, b):
    return sum((x * y for x, y in zip(a, b)), ZERO)


def _factor_tridiagonal(diagonal, lower, upper):
    pivots = [diagonal[0]]
    multipliers = [ZERO]
    _require(pivots[0] != ZERO, "zero virtual elimination pivot 0")
    for i in range(1, N):
        multiplier = lower[i] / pivots[-1]
        pivot = diagonal[i] - multiplier * upper[i - 1]
        _require(pivot.is_finite() and pivot != ZERO,
                 f"nonfinite or zero virtual elimination pivot {i}")
        multipliers.append(multiplier)
        pivots.append(pivot)
    return tuple(pivots), tuple(multipliers)


def _solve_tridiagonal(pivots, multipliers, upper, rhs):
    transformed = [rhs[0]]
    for i in range(1, N):
        transformed.append(rhs[i] - multipliers[i] * transformed[-1])
    solution = [ZERO] * N
    solution[-1] = transformed[-1] / pivots[-1]
    for i in range(N - 2, -1, -1):
        solution[i] = (transformed[i] - upper[i] * solution[i + 1]) / pivots[i]
    return tuple(solution)


def solve_block(point, rhs, transpose=False, precision=80):
    """Solve M x=rhs or M^T x=rhs using V elimination and a 2x2 Schur solve.

    Returns (tuple[Decimal], diagnostics-with-Decimal-values).  The full saved
    virtual tridiagonal matrix is used, including its zero-band disconnected
    portions.  No inverse is explicitly formed.  Nonzero numerical pivots and
    determinant are execution diagnostics, not a box nonsingularity proof.
    """
    point = parse_record(point)
    rhs = _vector(rhs, DIM, "rhs")
    _require(isinstance(transpose, bool), "transpose must be Boolean")
    with localcontext() as ctx:
        ctx.prec = _precision(precision)
        if transpose:
            top = tuple(tuple(point.A[j][i] for j in range(2)) for i in range(2))
            top_right, bottom_columns = point.C_storage, point.B
            lower = (ZERO,) + point.V[2][:-1]
            upper = point.V[1][1:] + (ZERO,)
        else:
            top = point.A
            top_right, bottom_columns = point.B, point.C_storage
            lower, upper = point.V[1], point.V[2]
        pivots, multipliers = _factor_tridiagonal(point.V[0], lower, upper)
        virtual_rhs = _solve_tridiagonal(pivots, multipliers, upper, rhs[2:])
        columns = tuple(_solve_tridiagonal(pivots, multipliers, upper, column)
                        for column in bottom_columns)
        schur = tuple(tuple(top[i][j] - _dot(top_right[i], columns[j])
                            for j in range(2)) for i in range(2))
        reduced = tuple(rhs[i] - _dot(top_right[i], virtual_rhs) for i in range(2))
        determinant = schur[0][0] * schur[1][1] - schur[0][1] * schur[1][0]
        _require(determinant.is_finite() and determinant != ZERO,
                 "nonfinite or zero numerical Schur determinant")
        real = ((schur[1][1] * reduced[0] - schur[0][1] * reduced[1]) / determinant,
                (schur[0][0] * reduced[1] - schur[1][0] * reduced[0]) / determinant)
        virtual = tuple(virtual_rhs[b] - columns[0][b] * real[0] - columns[1][b] * real[1]
                        for b in range(N))
        solution = real + virtual
        _require(all(value.is_finite() for value in solution), "nonfinite solved state")
        return solution, {
            "precision": precision,
            "transpose": transpose,
            "virtual_pivot_count": N,
            "min_abs_virtual_pivot": min(abs(value) for value in pivots),
            "schur_determinant": determinant,
            "schur": schur,
            "interpretation": "numerical elimination diagnostics only",
        }


def row_terms(point, vector, transpose=False):
    """Direct sparse multiplication terms, independent of Schur construction.

    Uses the caller's current Decimal context.  transpose=True shifts bands:
    (V^T)[b,b-1]=V_upper[b-1], (V^T)[b,b+1]=V_lower[b+1].
    """
    point = parse_record(point)
    vector = _vector(vector, DIM, "vector")
    _require(isinstance(transpose, bool), "transpose must be Boolean")
    real, virtual = vector[:2], vector[2:]
    rows = []
    for i in range(2):
        if transpose:
            terms = [point.A[j][i] * real[j] for j in range(2)]
            terms += [point.C_storage[i][b] * virtual[b] for b in range(N)]
        else:
            terms = [point.A[i][j] * real[j] for j in range(2)]
            terms += [point.B[i][b] * virtual[b] for b in range(N)]
        rows.append(tuple(terms))
    for b in range(N):
        coupling = point.B if transpose else point.C_storage
        terms = [coupling[i][b] * real[i] for i in range(2)]
        terms.append(point.V[0][b] * virtual[b])
        if b > 0:
            coefficient = point.V[2][b - 1] if transpose else point.V[1][b]
            terms.append(coefficient * virtual[b - 1])
        if b + 1 < N:
            coefficient = point.V[1][b + 1] if transpose else point.V[2][b]
            terms.append(coefficient * virtual[b + 1])
        rows.append(tuple(terms))
    return tuple(rows)


def multiply(point, vector, transpose=False, precision=80):
    """Direct sparse M/M^T multiplication, returning Decimal values."""
    with localcontext() as ctx:
        ctx.prec = _precision(precision)
        return tuple(sum(terms, ZERO) for terms in row_terms(point, vector, transpose))


def residual(point, vector, rhs, transpose=False, precision=80):
    """Return signed and componentwise normalized direct linear residuals."""
    rhs = _vector(rhs, DIM, "rhs")
    with localcontext() as ctx:
        ctx.prec = _precision(precision)
        terms = row_terms(point, vector, transpose)
        signed = tuple(sum(row, ZERO) - source for row, source in zip(terms, rhs))
        scales = tuple(sum((abs(value) for value in row), ZERO) + abs(source)
                       for row, source in zip(terms, rhs))
        normalized = tuple(abs(value) / scale if scale else
                           (ZERO if value == ZERO else Decimal("Infinity"))
                           for value, scale in zip(signed, scales))
        maximum = max(normalized)
        return {"signed": signed, "scales": scales, "normalized": normalized,
                "maximum": maximum, "worst_row": normalized.index(maximum)}


def scalar_row(point, precision=80):
    """q for FH=d+q^T X, in state ordering."""
    point = parse_record(point)
    with localcontext() as ctx:
        ctx.prec = _precision(precision)
        return tuple(beta / point.H for beta in point.beta) + (ZERO,) * N


def source_constant(point, precision=80):
    """Incoming-independent real source a(P), not the stored baseline source."""
    point = parse_record(point)
    with localcontext() as ctx:
        ctx.prec = _precision(precision)
        return tuple(point.nH * (point.s * point.x1 * point.dalpha[i]
                                 + point.alpha[i] * point.delta) for i in range(2)) + (ZERO,) * N


def scalar_constant(point, precision=80):
    """Incoming-independent scalar d(P) in the defined real coefficient model."""
    point = parse_record(point)
    with localcontext() as ctx:
        ctx.prec = _precision(precision)
        constants = source_constant(point, precision)
        return -(constants[0] + constants[1]) / point.H


def incoming_coefficients(point, precision=80):
    """313 G coefficients in incoming order; support is SOURCE_ROWS.

    The original branch formula is evaluated in real Decimal arithmetic at
    the represented saved tau.  Missing native RLya/omega intermediates are
    not asserted to have been recovered.  Lyman x1 cancellation is an exact
    real identity in the declared model.  These are not native bitwise G.
    """
    point = parse_record(point)
    with localcontext() as ctx:
        ctx.prec = _precision(precision)
        coefficients = []
        for diagonal, tau in zip(point.V[0], point.tau):
            if tau > TAU_SWITCH:
                probability = (ONE - (-tau).exp()) / tau
            else:
                probability = ONE - tau / TWO + tau * tau / SIX
            coefficients.append(diagonal * point.x1 * probability)
        lyman = THREE * K_LYA * point.H / point.nH
        coefficients.extend((lyman, lyman * K_LYB))
        _require(all(value.is_finite() for value in coefficients), "nonfinite G coefficient")
        return tuple(coefficients)


def apply_incoming_source(point, direction, precision=80):
    """Map an incoming direction to G delta_u in state/source order."""
    direction = _vector(direction, DIM, "incoming direction")
    with localcontext() as ctx:
        ctx.prec = _precision(precision)
        coefficients = incoming_coefficients(point, precision)
        result = [ZERO] * DIM
        for source_row, coefficient, value in zip(SOURCE_ROWS, coefficients, direction):
            result[source_row] = coefficient * value
        return tuple(result)


def native_prefix_data(point):
    """Reconstruct binary64 source prefixes; no native library is invoked.

    This is an additional explicitly named coefficient model.  Its missing
    native intermediate bits are not claimed to be recovered.  The study
    separately compares reconstructed sr/sv with all saved source entries.
    """
    point = parse_record(point)
    virtual = []
    for diagonal, tau in zip(point.V[0], point.tau):
        t = float(tau)
        if t > 1e-6:
            omega = 1.0 - (1.0 - math.exp(-t)) / t
        else:
            omega = t / 2.0 - (t * t) / 6.0
        virtual.append((float(diagonal) * float(point.x1), 1.0 - omega))
    rlya = ((float(K_LYA) * float(point.H)) / float(point.nH)) / float(point.x1)
    ly0 = (3.0 * rlya) * float(point.x1)
    ly1 = ly0 * float(K_LYB)
    _require(all(math.isfinite(v) for pair in virtual for v in pair)
             and math.isfinite(ly0) and math.isfinite(ly1), "nonfinite reconstructed source prefix")
    return tuple(virtual), (ly0, ly1)


def prefix_coefficients(point, precision=80):
    """Exact lifts of rounded prefixes, multiplied at requested precision."""
    virtual, lyman = native_prefix_data(point)
    with localcontext() as ctx:
        ctx.prec = _precision(precision)
        return tuple(Decimal.from_float(a) * Decimal.from_float(p) for a, p in virtual) + tuple(
            Decimal.from_float(g) for g in lyman)


def reconstructed_source64(point):
    """Source arithmetic only, for observed parity with immutable saved data."""
    point = parse_record(point)
    virtual, lyman = native_prefix_data(point)
    constants = [float(point.nH) * ((float(point.s) * float(point.x1)) * float(point.dalpha[i])
                 + float(point.alpha[i]) * float(point.delta)) for i in range(2)]
    real = (constants[0] + lyman[1] * float(point.incoming[312]),
            constants[1] + lyman[0] * float(point.incoming[311]))
    return real + tuple((a * float(u)) * pi for (a, pi), u in zip(virtual, point.incoming[:311]))


def apply_response(j, direction, precision=80):
    """J dot delta_u; j may be response()['j313'] or Decimal values."""
    j = _vector(j, DIM, "response coefficients")
    direction = _vector(direction, DIM, "incoming direction")
    with localcontext() as ctx:
        ctx.prec = _precision(precision)
        return _dot(j, direction)


def _json_value(value):
    if isinstance(value, Decimal):
        _require(value.is_finite(), "nonfinite output cannot be serialized")
        return str(value)
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    return value


def response(record, precision=80):
    """Return a JSON-friendly adjoint response for one validated fixed point.

    The response and elimination diagnostic do not certify inverse gain,
    forward error, a continuous coefficient box, or a physical ODE tube.
    j1_norm is the scalar functional's frozen-point l-infinity-to-absolute
    sensitivity, not an inverse-matrix norm or whole-domain Lipschitz bound.
    """
    point = parse_record(record)
    with localcontext() as ctx:
        ctx.prec = _precision(precision)
        q = scalar_row(point, precision)
        adjoint, diagnostics = solve_block(point, q, transpose=True, precision=precision)
        coefficients = incoming_coefficients(point, precision)
        j = tuple(coefficient * adjoint[row] for row, coefficient in zip(SOURCE_ROWS, coefficients))
        checks = residual(point, adjoint, q, transpose=True, precision=precision)
        return _json_value({
            "schema": "REC_H5_ELECTRON_RESPONSE01_POINT_V1",
            "index": point.index, "call_id": point.call_id, "slot": point.slot,
            "source_sha256": SOURCE_SHA256,
            "model": "source-structured frozen represented-coefficient real model",
            "precision": precision,
            "incoming_order": "virtual[0:311], Ly0, Ly1",
            "state_order": "2s, 2p, virtual[0:311]",
            "j313": j, "lambda313": adjoint,
            "G_coefficients313": coefficients, "G_source_rows313": SOURCE_ROWS,
            "j1_norm": sum((abs(value) for value in j), ZERO),
            "incoming_response_Ju": _dot(j, point.incoming),
            "adjoint_residual": checks,
            "elimination": diagnostics,
            "new_native_calls": 0,
        })
