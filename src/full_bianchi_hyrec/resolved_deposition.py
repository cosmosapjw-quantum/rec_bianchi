"""Typed numerical deposition through the existing COM operator.

All labels and raw packet units are declarations, never physical authentication.
The ordered labels bind B columns, target rows and angular grid rows explicitly;
matching lengths alone cannot authorize reuse of a packet on another layout.

Only fixed-map/measure/energy/angular-grid JVP is available. One method call
per evaluation applies the density/measure conversion once. There is no global
one-shot token, accepted-state update, event derivative or provider export.
Arrays are binary64 snapshots with little-endian C-order byte identities.
An explicit conversion of a tagged occupation array to a plain array followed
by a false packet-unit declaration is outside this typed API's guarantees.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
import hashlib
import json
import math

import numpy as np

from .physical_source_authority import HYDROGEN_REST_FRAME, PHYSICAL_SECONDS
from .trajectory.com_source_deposition import COMSourceDepositionPlan

PACKET_UNITS = "photon_packet H^-1 s^-1"
FIXED_SCOPE = "FIXED_MAP_MEASURE_ENERGY_ANGULAR_GRID"
PROVENANCE = "DECLARED_NUMERICAL_INPUTS_NOT_AUTHENTICATED"
_PLAN_ARRAYS = ("number_fractions", "mode_measure_m3", "cell_energy_J",
                "source_energy_J", "angular_weights", "directions")


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _text(value: object) -> str:
    if (type(value) is not str or not value or value != value.strip()
            or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise ValueError("nonempty canonical identity string required")
    return value


def _array(value: object) -> np.ndarray:
    # Reject typed occupation outputs before NumPy can erase quantity metadata.
    if type(value) not in (list, tuple, np.ndarray):
        raise TypeError("plain declared packet/plan array required; not occupation rate")
    if isinstance(value, (list, tuple)):
        elements = np.asarray(value, dtype=object).flat
        if any(isinstance(x, (bool, np.bool_, complex, np.complexfloating)) for x in elements):
            raise ValueError("bool/complex array elements forbidden")
    raw = np.asarray(value)
    if raw.dtype.kind not in "fiu":
        raise ValueError("real numeric array required")
    with np.errstate(over="ignore", invalid="ignore"):
        copied = np.array(raw, dtype="<f8", order="C", copy=True)
    if not np.isfinite(copied).all():
        raise ValueError("array must be finite")
    # bytes-backed storage cannot have its WRITEABLE flag re-enabled.
    return np.frombuffer(copied.tobytes(), dtype="<f8").reshape(copied.shape)


def _scalar(value: object, *, positive: bool = False) -> float:
    if (isinstance(value, (bool, np.bool_))
            or not isinstance(value, (int, float, np.integer, np.floating))):
        raise ValueError("finite real density scalar required")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError("unrepresentable density scalar") from exc
    if not math.isfinite(result) or (positive and result <= 0):
        raise ValueError("density outside finite domain")
    return result


def _descriptor(value: np.ndarray) -> dict:
    return {"shape": list(value.shape), "dtype": "<f8", "order": "C",
            "sha256": hashlib.sha256(np.asarray(value, dtype="<f8").tobytes(order="C")).hexdigest()}


@dataclass(frozen=True, slots=True)
class DepositionLayout:
    """Declared axis-to-identity association; physical validation is separate."""
    source_identity: str
    source_channel_ids: tuple[str, ...]
    target_identity: str
    target_ids: tuple[str, ...]
    angular_channel_ids: tuple[str, ...]
    measure_identity: str
    frame_identity: str
    time_basis: str
    rate_units: str

    def __post_init__(self):
        ordered = ("source_channel_ids", "target_ids", "angular_channel_ids")
        for name in ordered:
            values = getattr(self, name)
            if type(values) not in (list, tuple) or not values:
                raise ValueError("nonempty ordered channel IDs required")
            ids = tuple(_text(x) for x in values)
            if len(ids) != len(set(ids)):
                raise ValueError("duplicate channel IDs")
            object.__setattr__(self, name, ids)
        for f in fields(self):
            if f.name not in ordered:
                _text(getattr(self, f.name))
        if (self.frame_identity, self.time_basis, self.rate_units) != (
                HYDROGEN_REST_FRAME, PHYSICAL_SECONDS, PACKET_UNITS):
            raise ValueError("packet rates require hydrogen-rest frame and SI physical seconds")


@dataclass(frozen=True, slots=True, eq=False, init=False)
class PacketRates:
    """Signed packet rate, or its tangent, with a defensive immutable snapshot."""
    _data: bytes
    _shape: tuple[int, ...]
    layout: DepositionLayout

    def __init__(self, values: np.ndarray, layout: DepositionLayout):
        if type(layout) is not DepositionLayout:
            raise TypeError("typed deposition layout required")
        rates = _array(values)
        ns, na = len(layout.source_channel_ids), len(layout.angular_channel_ids)
        if rates.shape not in ((ns,), (ns, na)):
            raise ValueError("packet shape must be (S,) isotropic or (S,A) directional")
        object.__setattr__(self, "_data", rates.tobytes())
        object.__setattr__(self, "_shape", rates.shape)
        object.__setattr__(self, "layout", layout)

    @property
    def values(self) -> np.ndarray:
        # Each access owns a new header; dtype/shape mutation cannot rebind us.
        return np.frombuffer(self._data, dtype="<f8").reshape(self._shape)


@dataclass(frozen=True, slots=True)
class NumericalDepositionReceipt:
    operation_kind: str
    input_identity: str
    plan_identity: str
    result_identity: str
    source_identity: str
    output_array_digest: str
    units: str
    provenance_class: str
    derivative_scope: str
    input_payload_json: str
    plan_payload_json: str
    result_payload_json: str
    numerical_deposition_executed: bool = field(default=True, init=False)
    physical_source_authenticated: bool = field(default=False, init=False)
    provider_admitted: bool = field(default=False, init=False)


class _OccupationArray(np.ndarray):
    """A quantity marker retained by slices/copies; no packet coercion hook."""
    rate_units = "s^-1"


@dataclass(frozen=True, slots=True, eq=False, init=False)
class OccupationRates:
    _data: bytes
    _shape: tuple[int, ...]
    receipt: NumericalDepositionReceipt

    def __init__(self, values: np.ndarray, receipt: NumericalDepositionReceipt):
        object.__setattr__(self, "_data", values.tobytes())
        object.__setattr__(self, "_shape", values.shape)
        object.__setattr__(self, "receipt", receipt)

    @property
    def values(self) -> np.ndarray:
        return np.frombuffer(self._data, dtype="<f8").reshape(self._shape).view(_OccupationArray)


@dataclass(frozen=True, slots=True, eq=False, init=False)
class ResolvedDeposition:
    _plan_data: tuple[tuple[str, bytes, tuple[int, ...]], ...]
    _measure_id: str
    _map_id: str
    layout: DepositionLayout

    def __init__(self, plan: COMSourceDepositionPlan, layout: DepositionLayout):
        if type(plan) is not COMSourceDepositionPlan:
            raise TypeError("actual COMSourceDepositionPlan required, not hash-only declaration")
        if type(layout) is not DepositionLayout:
            raise TypeError("typed deposition layout required")
        # Snapshot even the supplied plan so later caller field rebinding cannot
        # alter the actual arrays associated with this numerical binding.
        copied = COMSourceDepositionPlan(**{f.name: getattr(plan, f.name)
                                            for f in fields(plan)})
        _text(copied.map_id)
        _text(copied.measure_id)
        if layout.measure_identity != copied.measure_id:
            raise ValueError("plan/layout measure identity mismatch")
        if (len(layout.source_channel_ids), len(layout.target_ids),
            len(layout.angular_channel_ids)) != (len(copied.source_energy_J),
                len(copied.cell_energy_J), len(copied.angular_weights)):
            raise ValueError("plan/layout axis length mismatch")
        snapshots = tuple((name, _array(getattr(copied, name)).tobytes(),
                           getattr(copied, name).shape) for name in _PLAN_ARRAYS)
        object.__setattr__(self, "_plan_data", snapshots)
        object.__setattr__(self, "_measure_id", copied.measure_id)
        object.__setattr__(self, "_map_id", copied.map_id)
        object.__setattr__(self, "layout", layout)

    @property
    def plan(self) -> COMSourceDepositionPlan:
        # Public plan headers are also disposable. Core validation and algebra
        # remain in COMSourceDepositionPlan, never duplicated in this adapter.
        arrays = {name: np.frombuffer(data, dtype="<f8").reshape(shape)
                  for name, data, shape in self._plan_data}
        return COMSourceDepositionPlan(**arrays, measure_id=self._measure_id, map_id=self._map_id)

    @property
    def plan_payload_json(self) -> str:
        plan = self.plan
        return _json({"schema": "rec-resolved-plan/v1", "layout": asdict(self.layout),
                      "map_id": plan.map_id, "measure_id": plan.measure_id,
                      "units": {"energy": "J", "measure": "m^-3", "density": "m^-3",
                                "B": "dimensionless", "metric_signature": "(-,+,+,+)"},
                      "arrays": {k: _descriptor(getattr(plan, k)) for k in _PLAN_ARRAYS}})

    @property
    def plan_identity(self) -> str:
        return _hash(self.plan_payload_json)

    def _require_packet(self, rates: PacketRates) -> None:
        if type(rates) is not PacketRates:
            raise TypeError("PacketRates required; occupation-rate redeposition forbidden")
        if rates.layout != self.layout:
            raise ValueError("packet/plan layout identity or ordered-channel mismatch")

    def _input(self, rates: PacketRates, density: float) -> dict:
        return {"schema": "rec-resolved-input/v1", "layout": asdict(rates.layout),
                "rates": _descriptor(rates.values), "n_H_m3": density.hex()}

    def _finish(self, operation: str, output: np.ndarray, payload: dict) -> OccupationRates:
        # Entered only after the existing numerical method returned successfully.
        values = _array(output)
        if values.shape != (len(self.layout.target_ids), len(self.layout.angular_channel_ids)):
            raise ValueError("invalid deposition output shape")
        scope = FIXED_SCOPE if operation == "jvp" else "NOT_A_DERIVATIVE"
        inputs, plan = _json(payload), self.plan_payload_json
        descriptor = _descriptor(values)
        result = _json({"schema": "rec-resolved-result/v1", "operation": operation,
                        "input_identity": _hash(inputs), "plan_identity": _hash(plan),
                        "output": descriptor, "units": "s^-1", "derivative_scope": scope,
                        "provenance_class": PROVENANCE, "numerical_deposition_executed": True,
                        "physical_source_authenticated": False, "provider_admitted": False})
        receipt = NumericalDepositionReceipt(
            operation, _hash(inputs), _hash(plan), _hash(result), self.layout.source_identity,
            descriptor["sha256"], "s^-1", PROVENANCE, scope, inputs, plan, result)
        return OccupationRates(values, receipt)

    def apply(self, rates: PacketRates, *, n_H_m3: float) -> OccupationRates:
        self._require_packet(rates)
        density = _scalar(n_H_m3, positive=True)
        payload = self._input(rates, density)
        result = self.plan.apply(rates.values, density)
        return self._finish("apply", result, payload)

    def jvp(self, rates: PacketRates, tangent: PacketRates, *, n_H_m3: float,
            dn_H_m3: float = 0.) -> OccupationRates:
        """Partial derivative only; unsupported moving-map/event keywords raise."""
        self._require_packet(rates)
        self._require_packet(tangent)
        density, dn = _scalar(n_H_m3, positive=True), _scalar(dn_H_m3)
        payload = self._input(rates, density)
        payload.update(rate_tangent=_descriptor(tangent.values), dn_H_m3=dn.hex(),
                       derivative_scope=FIXED_SCOPE)
        result = self.plan.jvp(rates.values, tangent.values, density, dn)
        return self._finish("jvp", result, payload)
