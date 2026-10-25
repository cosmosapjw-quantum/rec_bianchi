"""Source-bound H5 candidate evaluator; physical admission is a separate decision.

All enclosure arithmetic below is exact rational arithmetic. The exponential
upper bound uses a finite positive Taylor sum and a geometric tail. Stored
binary64 inputs enter through their exact hexadecimal representation. This
module never calls an RHS, integrates a trajectory, or infers a continuous
bound from sampled differences.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path


class BoundInputError(ValueError):
    """A named input/domain obligation prevents evaluation."""


def rational(value: str | int | Fraction) -> Fraction:
    """Explicit decimal/fraction tokens; floats must use binary64() instead."""
    if isinstance(value, bool) or isinstance(value, float):
        raise BoundInputError("EXPLICIT_BOUND_DECIMAL_REQUIRED")
    try:
        result = Fraction(value)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
        raise BoundInputError("INVALID_FINITE_RATIONAL") from exc
    return result


def nonnegative(value: str | int | Fraction, name: str) -> Fraction:
    result = rational(value)
    if result < 0:
        raise BoundInputError("NEGATIVE_BOUND:" + name)
    return result


def binary64(value: str) -> Fraction:
    try:
        number = float.fromhex(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise BoundInputError("INVALID_BINARY64_HEX") from exc
    if not math.isfinite(number):
        raise BoundInputError("NONFINITE_BINARY64")
    return Fraction.from_float(number)


def exp_upper(x: Fraction) -> Fraction:
    """Exact exp(x) upper bound for 0 <= x <= 64.

    Reduce x to z <= 1. For N=48, t_n=z**n/n!,
    sum(n>N)t_n <= t_(N+1)/(1-z/(N+2)). Each ratio in that
    tail is at most z/(N+2). Repeated squaring preserves the upper bound.
    The finite supported exponent range is an implementation bound, not a
    physical constraint or a proof that a larger exponent cannot be handled.
    """
    x = nonnegative(x, "exponent")
    if x > 64:
        raise BoundInputError("EXPONENT_RANGE_UNSUPPORTED")
    z, squares = x, 0
    while z > 1:
        z /= 2
        squares += 1
    term = Fraction(1)
    partial = term
    for n in range(1, 49):
        term *= z / n
        partial += term
    next_term = term * z / 49
    upper = partial + next_term / (1 - z / 50)
    for _ in range(squares):
        upper *= upper
    return upper


def decimal_bound_token(value: Fraction, *, upper: bool, digits: int = 64) -> str:
    """Finite decimal token enclosing a nonnegative rational on the named side.

    Integer arithmetic locates the decimal order and floors/ceils onto a
    significant-digit grid. This avoids Python's large-integer string limit
    without changing interpreter settings or using a rounded logarithm in the
    enclosure. The bit-length estimate is corrected by exact comparisons.
    """
    value = nonnegative(value, "serialized_bound")
    if not value:
        return "0"
    if not isinstance(digits, int) or isinstance(digits, bool) or digits < 1:
        raise BoundInputError("POSITIVE_SERIALIZATION_PRECISION_REQUIRED")
    n, d = value.numerator, value.denominator
    order = ((n.bit_length() - d.bit_length()) * 30103) // 100000
    def below_power(power):
        return n < d * 10**power if power >= 0 else n * 10**(-power) < d
    while below_power(order):
        order -= 1
    while not below_power(order + 1):
        order += 1
    power = order - digits + 1
    numerator, denominator = (n, d * 10**power) if power >= 0 else (n * 10**(-power), d)
    coefficient, remainder = divmod(numerator, denominator)
    if upper and remainder:
        coefficient += 1
    while coefficient and coefficient % 10 == 0:
        coefficient //= 10
        power += 1
    return str(coefficient) + "e" + str(power)


def gronwall_upper(e0, defect, stability, duration) -> Fraction:
    """Uniform-envelope E(s) for the positive path-length clock s >= 0."""
    e0 = nonnegative(e0, "initial_error")
    d = nonnegative(defect, "defect")
    L = nonnegative(stability, "stability_L")
    s = nonnegative(duration, "path_length")
    if not L:
        return e0 + d * s
    exponential = exp_upper(L * s)
    return exponential * e0 + d * (exponential - 1) / L


def interpolation_upper(left, query, right, e_left, e_right, curvature,
                        representation=Fraction(0)) -> Fraction:
    """Exact fixed-query absolute radius, including actual anchor arithmetic."""
    l, q, r = map(rational, (left, query, right))
    if not l < r or not l <= q <= r:
        raise BoundInputError("QUERY_OUTSIDE_CELL")
    e_l = nonnegative(e_left, "left_endpoint")
    e_r = nonnegative(e_right, "right_endpoint")
    m2 = nonnegative(curvature, "curvature")
    rep = nonnegative(representation, "representation")
    a = (q - l) / (r - l)
    return (1 - a) * e_l + a * e_r + m2 * (q - l) * (r - q) / 2 + rep


def frozen_box_upper(klo, khi, epsilon) -> list[Fraction]:
    """Exact W*epsilon; inputs must already be admitted entrywise bounds.

    This consumes intervals, never regenerates the prior KS01 certificate.
    Matrices are finite sequences of rational tokens or Fraction values.
    """
    eps = [nonnegative(x, "epsilon") for x in epsilon]
    if len(klo) != len(khi) or not klo:
        raise BoundInputError("OPERATOR_SHAPE")
    result = []
    for lo, hi in zip(klo, khi):
        if len(lo) != len(eps) or len(hi) != len(eps):
            raise BoundInputError("OPERATOR_SHAPE")
        total = Fraction(0)
        for a, b, e in zip(lo, hi, eps):
            a, b = rational(a), rational(b)
            if a > b:
                raise BoundInputError("REVERSED_OPERATOR_INTERVAL")
            total += max(abs(a), abs(b)) * e
        result.append(total)
    return result


def validate_context(context: dict) -> None:
    if context.get("schema") != "REC_H5_FIXED_QUERY_CONTEXT_V1":
        raise BoundInputError("SOURCE_CONTEXT_SCHEMA")
    rows = context["queries"]
    if len(rows) != context["source_identity"]["query_count"]:
        raise BoundInputError("SOURCE_QUERY_COUNT")
    slots = []
    for j, row in enumerate(rows):
        if row["incoming_index"] != j:
            raise BoundInputError("SOURCE_QUERY_ORDER")
        l, q, r = [binary64(row[key]) for key in
                   ("eta_left_hex", "query_hex", "eta_right_hex")]
        if not l < q < r:
            raise BoundInputError("SOURCE_QUERY_NOT_INTERIOR")
        cell, source = row["cell"], row["source_index"]
        if isinstance(cell, bool) or not isinstance(cell, int) or cell < 0:
            raise BoundInputError("SOURCE_CELL_INDEX")
        if cell + 1 >= context["source_identity"]["prefix"]:
            raise BoundInputError("SOURCE_CELL_PREFIX")
        a = (q - l) / (r - l)
        if rational(row["geometric_alpha_exact"]) != a:
            raise BoundInputError("SOURCE_ALPHA_MISMATCH")
        yl, yr, nominal = [binary64(row[key]) for key in
                           ("sample_left_hex", "sample_right_hex",
                            "nominal_incoming_hex")]
        anchor = abs(nominal - ((1 - a) * yl + a * yr))
        if rational(row["anchor_representation_radius_exact"]) != anchor:
            raise BoundInputError("SOURCE_ANCHOR_MISMATCH")
        slots.extend(((source, cell), (source, cell + 1)))
    if len(set(slots)) != context["source_identity"]["active_endpoint_slots"]:
        raise BoundInputError("SOURCE_ENDPOINT_COUNT")


def _proofs(packet: dict, proof_root: Path | None) -> tuple[set[str], list[dict]]:
    verified = set()
    receipts = []
    for artifact in packet.get("proof_artifacts", []):
        name = artifact["id"]
        if name in verified:
            raise BoundInputError("DUPLICATE_PROOF_ID")
        if proof_root is None:
            raise BoundInputError("PROOF_ROOT_REQUIRED")
        path = proof_root / artifact["path"]
        if not path.is_file():
            raise BoundInputError("PROOF_ARTIFACT_MISSING:" + name)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != artifact["sha256"]:
            raise BoundInputError("PROOF_ARTIFACT_BYTE_MISMATCH:" + name)
        verified.add(name)
        receipts.append({"id": name, "sha256": digest,
                         "status": "BYTES_READ_CONTENT_REVIEW_REQUIRED"})
    return verified, receipts


def _scalar(owner: dict, field: str, proofs: set[str]) -> Fraction:
    item = owner[field]
    refs = item.get("proof_refs", [])
    if not refs or not set(refs) <= proofs:
        raise BoundInputError("BOUND_PROOF_REFERENCE_MISSING:" + field)
    return nonnegative(item["upper"], field)


def _tube_radius_lower(state: dict, proofs: set[str]) -> Fraction:
    """Certified safe radius from below, in the declared reconstruction/norm/domain.

    The referenced proof must cover the entire open tube of at least this radius.
    Byte checks do not establish that proof's scientific content. An upper bound
    on a safe radius cannot justify the bootstrap inclusion and is not consumed.
    """
    item = state["tube_radius"]
    if not isinstance(item, dict) or "lower" not in item:
        raise BoundInputError("TUBE_RADIUS_CERTIFIED_LOWER_REQUIRED")
    refs = item.get("proof_refs", [])
    if not refs or not set(refs) <= proofs:
        raise BoundInputError("BOUND_PROOF_REFERENCE_MISSING:tube_radius")
    lower = rational(item["lower"])
    if lower <= 0:
        raise BoundInputError("POSITIVE_TUBE_RADIUS_LOWER_REQUIRED")
    return lower


def evaluate_candidate(context: dict, packet: dict, *, proof_root: Path | None = None,
                       context_sha256: str | None = None) -> dict:
    """Evaluate a conditional candidate; never grant physical admission.

    The source packet's physical epsilon stays null even with supplied bounds.
    Existence and byte identity of proof artifacts do not establish their truth.
    A later scientific review must assess continuous coverage, the state/G
    mapping, source error and the intended observable error allocation.
    """
    validate_context(context)
    if packet.get("schema") != "REC_H5_BOUND_INPUT_PACKET_V1":
        raise BoundInputError("BOUND_PACKET_SCHEMA")
    if packet.get("source_identity") != context["source_identity"]:
        raise BoundInputError("SOURCE_IDENTITY_MISMATCH")
    if context_sha256 is not None and packet.get("context_sha256") != context_sha256:
        raise BoundInputError("QUERY_CONTEXT_BYTE_MISMATCH")
    if packet.get("clock") != "eta=ln(a)":
        raise BoundInputError("CLOCK_MISMATCH")
    if packet.get("native_reference") != context["native_reference"]:
        raise BoundInputError("NATIVE_REFERENCE_MISMATCH")
    if packet.get("query_policy") != "fixed_represented_binary64_queries":
        raise BoundInputError("QUERY_RETEMING_NOT_H5_FIXED_QUERY")
    if packet.get("enclosure_kind") != "continuous_source_ode_tube":
        raise BoundInputError("WRONG_DEFECT_OR_TUBE_SEMANTICS")
    state = packet.get("state_enclosure")
    channel = packet.get("query_bounds")
    missing = []
    required = ("initial_error", "defect", "stability_L", "tube_radius",
                "model_discrepancy")
    if state is None:
        missing.extend("state_enclosure." + key for key in
                       ("norm", "reconstruction", "eta_origin",
                        "eta_domain", *required))
    else:
        missing.extend("state_enclosure." + key for key in required
                       if state.get(key) is None)
    if channel is None:
        missing.extend(("query_bounds.K_left_right",
                        "query_bounds.reference_and_endpoint_representation",
                        "query_bounds.whole_cell_curvature"))
    base = {"schema": "REC_H5_BOUND_CONSUMPTION_V1",
            "actual_query_count": len(context["queries"]),
            "physical_epsilon": None, "physical_outgoing_bound": None,
            "physical_H5_status": "INPUT_DEPENDENT_UNCALIBRATED",
            "new_rhs": 0, "new_ivp": 0, "old_matrix_rebuild": 0,
            "conditional_epsilon": None,
            "missing_inputs": missing}
    if missing:
        return {**base, "status": "BLOCKED_ACTUAL_BOUND_INPUTS",
                "bound_input_query_coverage": 0,
                "proof_artifact_review": "NO_ACTUAL_BOUND_PROOFS_SUPPLIED"}
    proofs, proof_receipts = _proofs(packet, proof_root)
    if not proofs:
        raise BoundInputError("CONTINUOUS_BOUND_PROOFS_REQUIRED")
    norm = state["norm"]
    if norm.get("kind") != "fixed_weighted_infinity" or not norm.get("coordinates"):
        raise BoundInputError("FIXED_DIMENSIONAL_NORM_REQUIRED")
    names = []
    for coordinate in norm["coordinates"]:
        if rational(coordinate["scale"]) <= 0 or not coordinate.get("unit"):
            raise BoundInputError("POSITIVE_DIMENSIONAL_SCALE_REQUIRED")
        names.append(coordinate["name"])
    if len(names) != len(set(names)):
        raise BoundInputError("NORM_COORDINATES_DUPLICATED")
    if state.get("reconstruction") != "continuous_piecewise_absolutely_continuous":
        raise BoundInputError("RECONSTRUCTION_CONTINUITY_OR_JUMP_BUDGET_REQUIRED")
    if state.get("bound_support") != "whole_eta_domain_ess_sup":
        raise BoundInputError("SAMPLED_BOUND_NOT_CONTINUOUS_ENCLOSURE")
    if state.get("tube_definition") != "uniform_open_scaled_radius_about_reconstruction":
        raise BoundInputError("UNIFORM_RECONSTRUCTION_TUBE_REQUIRED")
    if state.get("state_proof_refs") is None or not state["state_proof_refs"] or not set(state["state_proof_refs"]) <= proofs:
        raise BoundInputError("STATE_DOMAIN_PROOF_REQUIRED")
    sigma = state["orientation"]
    if isinstance(sigma, bool) or sigma not in (-1, 1):
        raise BoundInputError("ORIENTATION_REQUIRED")
    origin = rational(state["eta_origin"])
    domain = [rational(x) for x in state["eta_domain"]]
    if len(domain) != 2 or not domain[0] <= origin <= domain[1]:
        raise BoundInputError("ORIGIN_OUTSIDE_ENCLOSURE_DOMAIN")
    e0, defect, L, model = [_scalar(state, key, proofs) for key in
                           ("initial_error", "defect", "stability_L", "model_discrepancy")]
    rho_lower = _tube_radius_lower(state, proofs)
    if len(channel) != len(context["queries"]):
        raise BoundInputError("BOUND_QUERY_COVERAGE")
    epsilon, endpoints = [], []
    emax = e0
    for row, bounds in zip(context["queries"], channel):
        for key in ("incoming_index", "source_index", "cell"):
            if bounds.get(key) != row[key]:
                raise BoundInputError("BOUND_QUERY_IDENTITY:" + key)
        if bounds.get("curvature_support") != "ess_sup_whole_cell":
            raise BoundInputError("CURVATURE_NOT_WHOLE_CELL")
        if bounds.get("regularity") not in ("C2", "AC_first_derivative_ess_bounded_second"):
            raise BoundInputError("CELL_REGULARITY_REQUIRED")
        l, q, r = [binary64(row[key]) for key in
                   ("eta_left_hex", "query_hex", "eta_right_hex")]
        if not domain[0] <= l < r <= domain[1]:
            raise BoundInputError("CELL_OUTSIDE_ENCLOSURE_DOMAIN")
        distances = [sigma * (endpoint - origin) for endpoint in (l, r)]
        if min(distances) < 0:
            raise BoundInputError("ENDPOINT_BEFORE_ORIENTED_ORIGIN")
        E = [gronwall_upper(e0, defect + model, L, t) for t in distances]
        emax = max(emax, *E)
        radii = []
        for side, state_error in zip(("left", "right"), E):
            K = _scalar(bounds, "K_" + side, proofs)
            b = _scalar(bounds, "reference_" + side, proofs)
            rep = _scalar(bounds, "endpoint_representation_" + side, proofs)
            radii.append(K * state_error + b + rep)
        m2 = _scalar(bounds, "curvature_M2", proofs)
        eps = interpolation_upper(l, q, r, *radii, m2,
                                  rational(row["anchor_representation_radius_exact"]))
        epsilon.append(decimal_bound_token(eps, upper=True))
        endpoints.append([decimal_bound_token(x, upper=True) for x in radii])
    # L,d,e0 are nonnegative, so E is monotone in the oriented path length.
    # Compare an upper error bound to a lower certified safe radius. The proof
    # must cover that full tube on this reconstruction, norm and eta domain.
    # Strictness validates the scalar inclusion over earlier cells, conditional
    # on the supplied existence/domain proof; equality does not suffice.
    if emax >= rho_lower:
        raise BoundInputError("TUBE_BOOTSTRAP_FAILED")
    return {**base, "status": "CONDITIONAL_BOUND_CANDIDATE_REVIEW_REQUIRED",
            "bound_input_query_coverage": len(epsilon),
            "conditional_epsilon": epsilon,
            "conditional_endpoint_radii": endpoints,
            "state_error_upper_max": decimal_bound_token(emax, upper=True),
            "tube_margin_lower": decimal_bound_token(rho_lower - emax, upper=False),
            "proof_artifacts": proof_receipts,
            "proof_artifact_review": "BYTES_ONLY_SCIENTIFIC_CONTENT_REVIEW_PENDING",
            "arithmetic": "exact rational with proved positive-series exp upper; outward 64-significant-digit decimal output",
            "physical_admission_obligations": [
                "Independent review of actual continuous-domain proof artifacts",
                "Correct source F, native-reference G, units and initial-error mapping",
                "Source/model and nonlinear outgoing remainder allocation",
                "Owner supplied observable tolerance, separate from mathematical validity"]}


def evaluate_files(context_path: Path, packet_path: Path, *, proof_root=None) -> dict:
    data = context_path.read_bytes()
    return evaluate_candidate(json.loads(data), json.loads(packet_path.read_text()),
                              proof_root=proof_root,
                              context_sha256=hashlib.sha256(data).hexdigest())
