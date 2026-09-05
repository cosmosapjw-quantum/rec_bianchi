"""Bounded representation-neutral REC source protocol, not provider admission.

Only the local constant bosonic affine law is evaluated as a source primitive.
The companion-frequency weighted sum is a manufactured linear packet probe,
NOT the original-HyRec two-photon/Raman collision law. All provenance is a
validated declaration, not authenticated source data. Unresolved deposition
raises rather than fabricating an execution receipt.

SI: occupation dimensionless; energy joules; source-frame time seconds. No
implicit c, hbar, k_B, angular quadrature, moment closure or observer boost.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields, is_dataclass
import hashlib
import json
import math
from types import MappingProxyType
from typing import NoReturn

PHOTON = "PHOTON"
BOSON = "BOSON"
HYDROGEN_REST_FRAME = "HYDROGEN_REST_FRAME"
PHYSICAL_SECONDS = "PHYSICAL_SECONDS"
PHOTON_ENERGY_J = "PHOTON_ENERGY_J"
ZERO_OUTSIDE_SUPPORT = "ZERO_OUTSIDE_SUPPORT"
ANALYTIC_JVP = "ANALYTIC_JVP"
NO_JVP_FAIL_CLOSED = "NO_JVP_FAIL_CLOSED"
TWO_PHOTON = "TWO_PHOTON"
RAMAN = "RAMAN"
FULL_SPECTRAL_ANGULAR_GRID = "FULL_SPECTRAL_ANGULAR_GRID"
SPECTRAL_PSTF_COEFFICIENTS = "SPECTRAL_PSTF_COEFFICIENTS"
FIXED_DIRECTIONAL_FACE = "FIXED_DIRECTIONAL_FACE"
DECLARED_SUBSPACE_ONLY = "DECLARED_SUBSPACE_ONLY"
ARBITRARY_HIGH_RANK = "ARBITRARY_HIGH_RANK"
G_ANGULAR_ENERGY = "G_ANGULAR_ENERGY"
J_PSTF_ENERGY = "J_PSTF_ENERGY"
EXPLICIT_PROJECTION_ONLY = "EXPLICIT_PROJECTION_ONLY"


class SourceContractError(ValueError):
    """Invalid declared source domain or metadata."""


class SourceArithmeticError(ArithmeticError):
    """Binary64 calculation cannot return a finite result."""


class NoFiniteEquilibriumError(SourceContractError):
    """The interior affine law has no finite nonnegative equilibrium."""


class NonUniqueEquilibriumError(SourceContractError):
    """Every occupation is an equilibrium; no distinguished one exists."""


class SourceJVPUnavailableError(SourceContractError):
    """No derivative contract is available for this request."""


class NonlocalKernelIsNotLocalPairError(SourceContractError):
    """A companion-frequency probe cannot be cast to a local pair."""


class DepositionAuthorityError(SourceContractError):
    """Deposition declarations do not resolve an executable operator."""


class TrajectoryBindingError(SourceContractError):
    """A source is being reused on a different trajectory/event/restart."""


class MomentMapBindingRequiredError(SourceContractError):
    """The target-specific source/moment binding is missing or inconsistent."""


class FixedAngularFaceAuthorityError(SourceContractError):
    """A finite angular declaration overstates its represented domain."""


class LocalObserverBoostForbiddenError(SourceContractError):
    """Observer processing does not belong in REC source physics."""


def _real(value: object, name: str, *, nonnegative: bool = False,
          positive: bool = False) -> float:
    if type(value) not in (float, int):
        raise SourceContractError(f"{name}: expected a real int/float, not bool or text")
    try:
        result = float(value)
    except (ValueError, OverflowError) as exc:
        raise SourceContractError(f"{name}: invalid binary64 value") from exc
    if not math.isfinite(result) or (nonnegative and result < 0) or (positive and result <= 0):
        raise SourceContractError(f"{name}: outside finite physical domain")
    return 0.0 if result == 0.0 else result


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise SourceContractError(f"{name}: nonempty canonical string required")
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise SourceContractError(f"{name}: control character")
    return value


def _digest(value: object, n: int, name: str) -> str:
    text = _text(value, name)
    if len(text) != n or any(c not in "0123456789abcdef" for c in text):
        raise SourceContractError(f"{name}: lowercase {n}-digit digest required")
    return text


def _require_type(value: object, cls: type, name: str) -> None:
    if type(value) is not cls:
        raise SourceContractError(f"{name}: expected {cls.__name__}")


def _plain(value):
    if is_dataclass(value):
        return {field.name: _plain(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return {key: _plain(val) for key, val in sorted(value.items())}
    if isinstance(value, tuple):
        return [_plain(val) for val in value]
    return value


class _Semantic:
    @property
    def semantic_payload(self) -> str:
        return json.dumps({"schema": "rec-source-protocol/v1", "kind": type(self).__name__,
                           "declaration_only": True, "fields": _plain(self)},
                          sort_keys=True, separators=(",", ":"), allow_nan=False)

    @property
    def semantic_sha256(self) -> str:
        return hashlib.sha256(self.semantic_payload.encode("utf-8")).hexdigest()

    @property
    def physical_authority_admitted(self) -> bool:
        return False

    @property
    def provider_export_authorized(self) -> bool:
        return False


def _finite_sum(terms: Sequence[float]) -> float:
    if not all(math.isfinite(x) for x in terms):
        raise SourceArithmeticError("Nonfinite source intermediate; no clipping")
    try:
        value = math.fsum(terms)
    except (ValueError, OverflowError) as exc:
        raise SourceArithmeticError("Source sum overflow") from exc
    if not math.isfinite(value):
        raise SourceArithmeticError("Nonfinite source result")
    return 0.0 if value == 0.0 else value


@dataclass(frozen=True)
class SpectralSupport(_Semantic):
    coordinate: str
    lower_j: float
    upper_j: float
    lower_inclusive: bool
    upper_inclusive: bool
    outside_policy: str

    def __post_init__(self):
        if self.coordinate != PHOTON_ENERGY_J or self.outside_policy != ZERO_OUTSIDE_SUPPORT:
            raise SourceContractError("Only explicit joule/zero-outside support is implemented")
        lower = _real(self.lower_j, "lower_j", nonnegative=True)
        upper = _real(self.upper_j, "upper_j", positive=True)
        if lower >= upper or type(self.lower_inclusive) is not bool or type(self.upper_inclusive) is not bool:
            raise SourceContractError("Invalid support endpoints")
        object.__setattr__(self, "lower_j", lower)
        object.__setattr__(self, "upper_j", upper)

    def contains(self, energy_j: float) -> bool:
        energy = _real(energy_j, "energy_j", nonnegative=True)
        left = energy >= self.lower_j if self.lower_inclusive else energy > self.lower_j
        right = energy <= self.upper_j if self.upper_inclusive else energy < self.upper_j
        return left and right


@dataclass(frozen=True)
class SourceProvenance(_Semantic):
    repository: str
    source_commit_sha: str
    source_path: str
    source_blob_sha: str
    payload_sha256: str
    dependency_sha256: Mapping[str, str]
    algorithm_id: str

    def __post_init__(self):
        repo = _text(self.repository, "repository")
        if len(repo.split("/")) != 2 or any(not s or s in (".", "..") for s in repo.split("/")):
            raise SourceContractError("Repository must be owner/name")
        path = _text(self.source_path, "source_path")
        if "\\" in path or any(s in ("", ".", "..") for s in path.split("/")):
            raise SourceContractError("Canonical relative source path required")
        _digest(self.source_commit_sha, 40, "source_commit_sha")
        _digest(self.source_blob_sha, 40, "source_blob_sha")
        _digest(self.payload_sha256, 64, "payload_sha256")
        _text(self.algorithm_id, "algorithm_id")
        if not isinstance(self.dependency_sha256, Mapping) or not self.dependency_sha256:
            raise SourceContractError("Nonempty input dependency mapping required")
        copied = {_text(k, "dependency name"): _digest(v, 64, "dependency digest")
                  for k, v in self.dependency_sha256.items()}
        object.__setattr__(self, "dependency_sha256", MappingProxyType(dict(sorted(copied.items()))))

    @property
    def verification_status(self) -> str:
        return "DECLARED_NOT_AUTHENTICATED"


@dataclass(frozen=True)
class TrajectoryBinding(_Semantic):
    background_snapshot_sha256: str
    trajectory_id: str
    event_surface_id: str
    restart_certificate_sha256: str
    time_basis: str

    def __post_init__(self):
        _digest(self.background_snapshot_sha256, 64, "background_snapshot_sha256")
        _digest(self.restart_certificate_sha256, 64, "restart_certificate_sha256")
        _text(self.trajectory_id, "trajectory_id")
        _text(self.event_surface_id, "event_surface_id")
        if self.time_basis != PHYSICAL_SECONDS:
            raise TrajectoryBindingError("Source time basis must be physical seconds")


@dataclass(frozen=True)
class AngularRepresentation(_Semantic):
    kind: str
    identity_sha256: str
    rank_limit: int | None
    node_count: int | None
    rank_claim: str

    def __post_init__(self):
        _digest(self.identity_sha256, 64, "identity_sha256")
        if self.kind not in (FULL_SPECTRAL_ANGULAR_GRID, SPECTRAL_PSTF_COEFFICIENTS, FIXED_DIRECTIONAL_FACE):
            raise FixedAngularFaceAuthorityError("Unknown angular representation")
        if self.rank_claim != DECLARED_SUBSPACE_ONLY:
            raise FixedAngularFaceAuthorityError("No arbitrary-high-rank authority in this protocol")
        for name, minimum in (("rank_limit", 0), ("node_count", 1)):
            val = getattr(self, name)
            if val is not None and (type(val) is not int or val < minimum):
                raise FixedAngularFaceAuthorityError(f"Invalid {name}")
        if self.kind == SPECTRAL_PSTF_COEFFICIENTS and self.rank_limit is None:
            raise FixedAngularFaceAuthorityError("PSTF declaration requires a finite rank")
        if self.kind == FIXED_DIRECTIONAL_FACE and (self.node_count is None or self.rank_limit is None):
            raise FixedAngularFaceAuthorityError("Fixed face requires count and rank; still not a certificate")


@dataclass(frozen=True)
class MomentMapBinding(_Semantic):
    target: str
    source_semantic_sha256: str
    radial_weight_sha256: str
    angular_measure_sha256: str
    closure_status: str

    def __post_init__(self):
        if self.target not in (G_ANGULAR_ENERGY, J_PSTF_ENERGY) or self.closure_status != EXPLICIT_PROJECTION_ONLY:
            raise MomentMapBindingRequiredError("Explicit named moment projection required")
        for name in ("source_semantic_sha256", "radial_weight_sha256", "angular_measure_sha256"):
            _digest(getattr(self, name), 64, name)

    @property
    def numerically_executed(self) -> bool:
        return False


@dataclass(frozen=True)
class PacketDepositionBinding(_Semantic):
    """Validated declaration ONLY; this legacy schema has no operator values."""
    n_H_m3: float
    phase_space_measure_si: float
    deposition_matrix_sha256: str
    normalization_sha256: str
    application_count: int

    def __post_init__(self):
        try:
            density = _real(self.n_H_m3, "n_H_m3", nonnegative=True)
            measure = _real(self.phase_space_measure_si, "phase_space_measure_si", positive=True)
            _digest(self.deposition_matrix_sha256, 64, "deposition_matrix_sha256")
            _digest(self.normalization_sha256, 64, "normalization_sha256")
            if type(self.application_count) is not int or self.application_count != 1:
                raise SourceContractError("Exactly one declared application required")
        except SourceContractError as exc:
            raise DepositionAuthorityError(str(exc)) from exc
        object.__setattr__(self, "n_H_m3", density)
        object.__setattr__(self, "phase_space_measure_si", measure)

    @property
    def numerically_executed(self) -> bool:
        return False


@dataclass(frozen=True, init=False)
class _SourceCommon(_Semantic):
    support: SpectralSupport
    provenance: SourceProvenance
    trajectory: TrajectoryBinding
    species: str
    statistics: str
    frame: str
    time_basis: str
    jvp_status: str

    def __init__(self, *args, **kwargs):
        raise SourceContractError("Use a validated source factory")

    @property
    def construction_status(self) -> str:
        return "VALIDATED_FACTORY_ONLY"

    @property
    def spectral_coordinate(self) -> str:
        return self.support.coordinate

    def require_trajectory(self, trajectory: TrajectoryBinding) -> None:
        if type(trajectory) is not TrajectoryBinding or trajectory.semantic_sha256 != self.trajectory.semantic_sha256:
            raise TrajectoryBindingError("Source trajectory/event/restart mismatch")

    def bind_integrated_target(self, *, target: str, moment_map: MomentMapBinding | None) -> MomentMapBinding:
        if (type(moment_map) is not MomentMapBinding or moment_map.target != target
                or moment_map.source_semantic_sha256 != self.semantic_sha256):
            raise MomentMapBindingRequiredError("Missing or mismatched source-specific moment map")
        return moment_map  # Binding only, not numerical closure or projection.


@dataclass(frozen=True, init=False)
class _LocalSource(_SourceCommon):
    emission_s_inv: float
    absorption_s_inv: float

    @property
    def rate_units(self) -> str:
        return "s^-1"

    @property
    def chi_affine_s_inv(self) -> float:
        return self.absorption_s_inv - self.emission_s_inv

    @property
    def jvp_method(self) -> str:
        return self.jvp_status

    @property
    def uses_finite_difference_jvp(self) -> bool:
        return False

    def action(self, *, energy_j: float, occupation: float) -> float:
        f = _real(occupation, "occupation", nonnegative=True)
        active = self.support.contains(energy_j)
        if not active:
            return 0.0
        return _finite_sum((self.emission_s_inv, -self.chi_affine_s_inv * f))

    def jvp(self, *, energy_j: float, occupation: float, d_occupation: float,
            d_emission_s_inv: float, d_absorption_s_inv: float) -> float:
        """Partial JVP at FIXED energy/support/trajectory, not an event JVP."""
        if self.jvp_status != ANALYTIC_JVP:
            raise SourceJVPUnavailableError("No analytic derivative contract")
        f = _real(occupation, "occupation", nonnegative=True)
        df = _real(d_occupation, "d_occupation")
        de = _real(d_emission_s_inv, "d_emission_s_inv")
        da = _real(d_absorption_s_inv, "d_absorption_s_inv")
        if not self.support.contains(energy_j):
            return 0.0
        return _finite_sum(((1.0 + f) * de, -f * da, -self.chi_affine_s_inv * df))

    def equilibrium_occupation(self) -> float:
        """Unique finite equilibrium of the active interior law, not LTE proof."""
        if self.emission_s_inv == self.absorption_s_inv == 0.0:
            raise NonUniqueEquilibriumError("Source off: every nonnegative occupation is stationary")
        chi = self.chi_affine_s_inv
        if chi <= 0.0:
            raise NoFiniteEquilibriumError("No finite nonnegative interior equilibrium")
        value = self.emission_s_inv / chi
        if not math.isfinite(value):
            raise SourceArithmeticError("Equilibrium is not representable in binary64")
        return value


@dataclass(frozen=True, init=False)
class _PacketKernel(_SourceCommon):
    process: str
    companion_energy_nodes_j: tuple[float, ...]
    kernel_per_H_s: tuple[float, ...]

    @property
    def packet_rate_units(self) -> str:
        return "photon_packet H^-1 s^-1"

    @property
    def evaluation_scope(self) -> str:
        return "MANUFACTURED_LINEAR_PACKET_PROBE"

    def evaluate_packet_rate(self, *, companion_occupation: Sequence[float]) -> float:
        values = _vector(companion_occupation, "companion_occupation", nonnegative=True)
        if len(values) != len(self.kernel_per_H_s):
            raise SourceContractError("Companion occupation shape mismatch")
        return _finite_sum(tuple(k * f for k, f in zip(self.kernel_per_H_s, values, strict=True)))

    def as_local_affine_pair(self) -> NoReturn:
        raise NonlocalKernelIsNotLocalPairError("Companion-frequency dependence is not a local pair")

    def jvp(self, **kwargs) -> NoReturn:
        raise SourceJVPUnavailableError("Physical nonlocal kernel JVP remains unimplemented")


def _vector(values: object, name: str, *, nonnegative: bool = False) -> tuple[float, ...]:
    if not isinstance(values, (tuple, list)) or not values:
        raise SourceContractError(f"{name}: nonempty list or tuple required")
    return tuple(_real(v, name, nonnegative=nonnegative) for v in values)


def _common(support, provenance, trajectory, species, statistics, frame, time_basis, jvp_status):
    _require_type(support, SpectralSupport, "support")
    _require_type(provenance, SourceProvenance, "provenance")
    _require_type(trajectory, TrajectoryBinding, "trajectory")
    if (species, statistics, frame, time_basis) != (PHOTON, BOSON, HYDROGEN_REST_FRAME, PHYSICAL_SECONDS):
        raise SourceContractError("Only source-rest photon/boson rates per physical second are supported")
    if jvp_status not in (ANALYTIC_JVP, NO_JVP_FAIL_CLOSED):
        raise SourceContractError("Unknown JVP status")
    return dict(support=support, provenance=provenance, trajectory=trajectory,
                species=species, statistics=statistics, frame=frame,
                time_basis=time_basis, jvp_status=jvp_status)


def _construct(cls, values):
    obj = object.__new__(cls)
    for name, value in values.items():
        object.__setattr__(obj, name, value)
    return obj


def build_local_bosonic_affine_source(*, emission_s_inv: float, absorption_s_inv: float,
        species: str, statistics: str, frame: str, time_basis: str,
        support: SpectralSupport, provenance: SourceProvenance,
        trajectory: TrajectoryBinding, jvp_status: str) -> _LocalSource:
    values = _common(support, provenance, trajectory, species, statistics, frame, time_basis, jvp_status)
    values.update(emission_s_inv=_real(emission_s_inv, "emission_s_inv", nonnegative=True),
                  absorption_s_inv=_real(absorption_s_inv, "absorption_s_inv", nonnegative=True))
    return _construct(_LocalSource, values)


def build_nonlocal_packet_kernel(*, process: str, companion_energy_nodes_j: Sequence[float],
        kernel_per_H_s: Sequence[float], support: SpectralSupport,
        provenance: SourceProvenance, trajectory: TrajectoryBinding,
        jvp_status: str) -> _PacketKernel:
    """Construct a manufactured finite weighted probe, not an atomic kernel."""
    values = _common(support, provenance, trajectory, PHOTON, BOSON,
                     HYDROGEN_REST_FRAME, PHYSICAL_SECONDS, jvp_status)
    if process not in (TWO_PHOTON, RAMAN) or jvp_status != NO_JVP_FAIL_CLOSED:
        raise SourceContractError("Only named nonlocal no-JVP probes are implemented")
    nodes = _vector(companion_energy_nodes_j, "companion_energy_nodes_j", nonnegative=True)
    weights = _vector(kernel_per_H_s, "kernel_per_H_s")
    if len(nodes) != len(weights) or any(b <= a for a, b in zip(nodes, nodes[1:])):
        raise SourceContractError("Kernel nodes must be ordered, unique and shape-matched")
    # This bounded probe uses a common declared energy support; a physical
    # two-frequency kernel needs a separate target/companion support contract.
    if not all(support.contains(e) for e in nodes):
        raise SourceContractError("Companion node outside the manufactured probe support")
    values.update(process=process, companion_energy_nodes_j=nodes, kernel_per_H_s=weights)
    return _construct(_PacketKernel, values)


@dataclass(frozen=True)
class AngularBinding(_Semantic):
    source_semantic_sha256: str
    representation_sha256: str
    representation_declaration_sha256: str

    def __post_init__(self):
        for name in ("source_semantic_sha256", "representation_sha256", "representation_declaration_sha256"):
            _digest(getattr(self, name), 64, name)

    @property
    def numerically_executed(self) -> bool:
        return False


def bind_angular_representation(source: _SourceCommon, representation: AngularRepresentation) -> AngularBinding:
    if type(source) not in (_LocalSource, _PacketKernel):
        raise SourceContractError("Factory-created source required")
    _require_type(representation, AngularRepresentation, "representation")
    return AngularBinding(source.semantic_sha256, representation.identity_sha256,
                          representation.semantic_sha256)


def deposit_packet_rate(*, kernel: _PacketKernel, deposition: PacketDepositionBinding | None,
                        companion_occupation: Sequence[float]) -> NoReturn:
    """Fail closed: the legacy binding cannot resolve B, channels or target measure.

    Neither a source rate nor an application-count declaration is used to invent
    numerical deposition. No receipt, state change, or apparent s^-1 output is
    returned. A future resolved-payload contract is required.
    """
    if type(kernel) is not _PacketKernel or type(deposition) is not PacketDepositionBinding:
        raise DepositionAuthorityError("Missing typed kernel/deposition binding")
    raise DepositionAuthorityError(
        "UNRESOLVED_DEPOSITION_OPERATOR: matrix and target/channel measure bytes are absent; "
        "application_count is a declaration, not an execution receipt"
    )


def apply_local_observer_boost(*, source: _SourceCommon, beta: Sequence[float]) -> NoReturn:
    raise LocalObserverBoostForbiddenError("Local observer pullback belongs downstream in HTT")
