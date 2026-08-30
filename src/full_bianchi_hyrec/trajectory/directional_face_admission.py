"""Fail-closed research admission for a 26-ordinate directional face.

This module is deliberately outside the production coupled path.  It binds an
explicit hydrogen-frame quadrature, demonstrates that the existing
characteristic geometry can execute all 52 red/blue rays on a manufactured
zero-source problem, and records the source/remap authorities still missing.
It never promotes the manufactured result to a physical or source-identical
directional face.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
import hashlib
import json
import math
import re
from typing import Any

import numpy as np

from full_bianchi_hyrec.background.characteristics import (
    aberrate_direction,
    hydrogen_frame_characteristic,
    normal_frame_characteristic,
)
from full_bianchi_hyrec.background.snapshot import BackgroundSnapshot
from full_bianchi_hyrec.recoil.frequency_liouville import doppler_coordinate_speed
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import LineBoundaryConfig
from full_bianchi_hyrec.trajectory.characteristic_angular import (
    BianchiCharacteristicFaceSolver,
)


SOURCE_IDENTICAL_SCALAR_PRIMITIVE = "SOURCE_IDENTICAL_SCALAR_PRIMITIVE"
THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1 = (
    "THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1"
)
CLOSURE_DEFINED_DIRECTIONAL_SURROGATE_V1 = (
    "CLOSURE_DEFINED_DIRECTIONAL_SURROGATE_V1"
)
SOURCE_IDENTICAL_DIRECTIONAL_FACE = "SOURCE_IDENTICAL_DIRECTIONAL_FACE"

HYDROGEN_FRAME = "HYDROGEN_ORTHONORMAL_FRAME_V1"
HYDROGEN_TETRAD = "HYDROGEN_REST_ORTHONORMAL_TETRAD_V1"
ORDINARY_FREQUENCY_HZ = "ORDINARY_FREQUENCY_HZ"
LAGRANGIAN_SAMPLER = "LAGRANGIAN_BACKTRACED_FACE_SAMPLER_V1"
FIXED_NODE_COUPLED = "FIXED_NODE_COUPLED"

BLOCKED_ANGULAR_FRAME_CONTRACT = "BLOCKED_ANGULAR_FRAME_CONTRACT"
BLOCKED_DIRECTIONAL_SOURCE_COEFFICIENT_AUTHORITY = (
    "BLOCKED_DIRECTIONAL_SOURCE_COEFFICIENT_AUTHORITY"
)
BLOCKED_ANGULAR_REMAP_AUTHORITY = "BLOCKED_ANGULAR_REMAP_AUTHORITY"
BLOCKED_FREQUENCY_SPEED_ZERO_EVENT_RESTART_CONTRACT = (
    "BLOCKED_FREQUENCY_SPEED_ZERO_EVENT_RESTART_CONTRACT"
)
BLOCKED_EXTERNAL_DIRECTIONAL_AUTHORITY_VERIFICATION = (
    "BLOCKED_EXTERNAL_DIRECTIONAL_AUTHORITY_VERIFICATION"
)
SOURCE_FACE_ABSENT = "SOURCE_DEFINED_26_DIRECTION_FACE_RECONSTRUCTION_ABSENT"

REQUIRED_SOURCE_CHANNELS = (
    "virtual_spike",
    "one_photon",
    "two_photon",
    "raman",
)
_SHA256 = re.compile(r"[0-9a-f]{64}")


def _readonly(value: np.ndarray, *, dtype: Any = float) -> np.ndarray:
    result = np.array(value, dtype=dtype, copy=True)
    result.setflags(write=False)
    return result


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class AngularQuadratureContract:
    directions: np.ndarray
    weights: np.ndarray
    frame: str
    tetrad: str
    frequency_measure: str
    source_sha256: str

    def __post_init__(self) -> None:
        directions = np.asarray(self.directions, dtype=float)
        weights = np.asarray(self.weights, dtype=float)
        if self.frame != HYDROGEN_FRAME:
            raise ValueError(
                f"{BLOCKED_ANGULAR_FRAME_CONTRACT}: explicit hydrogen frame required"
            )
        if self.tetrad != HYDROGEN_TETRAD:
            raise ValueError(
                f"{BLOCKED_ANGULAR_FRAME_CONTRACT}: hydrogen tetrad mismatch"
            )
        if self.frequency_measure != ORDINARY_FREQUENCY_HZ:
            raise ValueError(
                f"{BLOCKED_ANGULAR_FRAME_CONTRACT}: frequency measure mismatch"
            )
        if directions.shape != (26, 3) or weights.shape != (26,):
            raise ValueError("directional face requires the ordered 26-point grid")
        if (
            not np.all(np.isfinite(directions))
            or not np.all(np.isfinite(weights))
            or np.any(weights <= 0.0)
        ):
            raise ValueError("quadrature directions/weights must be finite and positive")
        norms = np.linalg.norm(directions, axis=1)
        if np.max(np.abs(norms - 1.0)) > 3.0e-14:
            raise ValueError("quadrature directions must be unit vectors")
        if abs(float(np.sum(weights)) - 1.0) > 3.0e-14:
            raise ValueError("quadrature weights must be normalized")
        source_hash = str(self.source_sha256).lower()
        if _SHA256.fullmatch(source_hash) is None:
            raise ValueError("source_sha256 must be a SHA-256 digest")
        object.__setattr__(self, "directions", _readonly(directions))
        object.__setattr__(self, "weights", _readonly(weights))
        object.__setattr__(self, "source_sha256", source_hash)

    @property
    def semantic_sha256(self) -> str:
        metadata = _canonical_json(
            {
                "schema": "ANGULAR_QUADRATURE_CONTRACT_V1",
                "frame": self.frame,
                "tetrad": self.tetrad,
                "frequency_measure": self.frequency_measure,
                "source_sha256": self.source_sha256,
                "direction_dtype": "<f8",
                "direction_shape": [26, 3],
                "weight_dtype": "<f8",
                "weight_shape": [26],
                "order": "C",
            }
        )
        payload = (
            metadata
            + np.asarray(self.directions, dtype="<f8").tobytes(order="C")
            + np.asarray(self.weights, dtype="<f8").tobytes(order="C")
        )
        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class FaceKinematics:
    red_speed_x_s_inv: np.ndarray
    blue_speed_x_s_inv: np.ndarray
    red_inflow: np.ndarray
    blue_inflow: np.ndarray
    red_outflow: np.ndarray
    blue_outflow: np.ndarray
    red_grazing: np.ndarray
    blue_grazing: np.ndarray
    direction_normal: np.ndarray
    direction_hydrogen: np.ndarray
    interpretation: str

    def __post_init__(self) -> None:
        for name in (
            "red_speed_x_s_inv",
            "blue_speed_x_s_inv",
            "red_inflow",
            "blue_inflow",
            "red_outflow",
            "blue_outflow",
            "red_grazing",
            "blue_grazing",
            "direction_normal",
            "direction_hydrogen",
        ):
            value = np.asarray(getattr(self, name))
            object.__setattr__(
                self,
                name,
                _readonly(value, dtype=(bool if value.dtype == bool else float)),
            )


def _face_kinematics(
    *,
    snapshot: BackgroundSnapshot,
    line: LineBoundaryConfig,
    quadrature: AngularQuadratureContract,
    input_is_hydrogen_frame: bool,
) -> FaceKinematics:
    normal_directions = np.empty_like(quadrature.directions)
    hydrogen_directions = np.empty_like(quadrature.directions)
    rates = np.empty(26, dtype=float)
    for index, direction in enumerate(quadrature.directions):
        direction_normal = (
            aberrate_direction(-snapshot.beta_H, direction)
            if input_is_hydrogen_frame
            else direction
        )
        normal = normal_frame_characteristic(snapshot, direction_normal)
        hydrogen = hydrogen_frame_characteristic(snapshot, normal)
        normal_directions[index] = direction_normal
        hydrogen_directions[index] = hydrogen.direction_hydrogen
        rates[index] = hydrogen.R_hydrogen_s_inv
    red = np.asarray(
        doppler_coordinate_speed(
            rates,
            line.x_red,
            nu_abs_Hz=line.nu_abs_Hz,
            Doppler_width_Hz=line.Doppler_width_Hz,
            D0_nu_abs_Hz_s=line.D0_nu_abs_Hz_s,
            D0_log_Doppler_width_s_inv=line.D0_log_Doppler_width_s_inv,
            D0_x_boundary_s_inv=line.D0_x_red_s_inv,
        ),
        dtype=float,
    )
    blue = np.asarray(
        doppler_coordinate_speed(
            rates,
            line.x_blue,
            nu_abs_Hz=line.nu_abs_Hz,
            Doppler_width_Hz=line.Doppler_width_Hz,
            D0_nu_abs_Hz_s=line.D0_nu_abs_Hz_s,
            D0_log_Doppler_width_s_inv=line.D0_log_Doppler_width_s_inv,
            D0_x_boundary_s_inv=line.D0_x_blue_s_inv,
        ),
        dtype=float,
    )
    red_grazing = red == 0.0
    blue_grazing = blue == 0.0
    return FaceKinematics(
        red_speed_x_s_inv=red,
        blue_speed_x_s_inv=blue,
        red_inflow=red > 0.0,
        blue_inflow=blue < 0.0,
        red_outflow=red < 0.0,
        blue_outflow=blue > 0.0,
        red_grazing=red_grazing,
        blue_grazing=blue_grazing,
        direction_normal=normal_directions,
        direction_hydrogen=hydrogen_directions,
        interpretation=(
            HYDROGEN_FRAME if input_is_hydrogen_frame else "LEGACY_UNTAGGED_NORMAL"
        ),
    )


def compute_hydrogen_frame_face_kinematics(
    *,
    snapshot: BackgroundSnapshot,
    line: LineBoundaryConfig,
    quadrature: AngularQuadratureContract,
) -> FaceKinematics:
    return _face_kinematics(
        snapshot=snapshot,
        line=line,
        quadrature=quadrature,
        input_is_hydrogen_frame=True,
    )


def compute_legacy_untagged_normal_face_kinematics(
    *,
    snapshot: BackgroundSnapshot,
    line: LineBoundaryConfig,
    quadrature: AngularQuadratureContract,
) -> FaceKinematics:
    """Research comparator for the legacy normal-frame interpretation only."""

    return _face_kinematics(
        snapshot=snapshot,
        line=line,
        quadrature=quadrature,
        input_is_hydrogen_frame=False,
    )


@dataclass(frozen=True)
class ManufacturedGeometryWitness:
    authority_label: str
    ray_count: int
    red_ray_count: int
    blue_ray_count: int
    maximum_frequency_relative_residual: float
    maximum_occupation_residual: float
    minimum_doppler_factor: float
    minimum_abs_frequency_speed_s_inv: float
    result_sha256: str
    physical_face_admitted: bool
    blockers: tuple[str, ...]


class FrequencySpeedZeroEventRequired(ValueError):
    """Fail-closed signal carrying every ordered zero-drift node."""

    def __init__(self, node_indices: Sequence[int]) -> None:
        self.node_indices = tuple(int(index) for index in node_indices)
        super().__init__(
            "frequency-speed zero at ordered nodes "
            f"{list(self.node_indices)} requires an explicit event/restart contract"
        )


def run_manufactured_52_ray_geometry_witness(
    *,
    snapshot: BackgroundSnapshot,
    line: LineBoundaryConfig,
    quadrature: AngularQuadratureContract,
    logarithmic_frequency_offset: float = 1.0e-4,
    n_steps: int = 64,
) -> ManufacturedGeometryWitness:
    """Execute both faces for all nodes with zero source and fixed occupation."""

    offset = float(logarithmic_frequency_offset)
    if not math.isfinite(offset) or offset <= 0.0:
        raise ValueError("logarithmic_frequency_offset must be positive and finite")
    kinematics = compute_hydrogen_frame_face_kinematics(
        snapshot=snapshot,
        line=line,
        quadrature=quadrature,
    )
    solver = BianchiCharacteristicFaceSolver(snapshot)
    targets = (
        line.nu_abs_Hz + line.x_red * line.Doppler_width_Hz,
        line.nu_abs_Hz + line.x_blue * line.Doppler_width_Hz,
    )
    rows: list[list[float]] = []
    frequency_residuals: list[float] = []
    occupation_residuals: list[float] = []
    dopplers: list[float] = []
    frequency_speeds: list[float] = []
    local_rates = np.asarray(
        [
            solver.local_characteristic(direction_normal).R_hydrogen_s_inv
            for direction_normal in kinematics.direction_normal
        ],
        dtype=float,
    )
    zero_nodes = tuple(int(index) for index in np.flatnonzero(local_rates == 0.0))
    if zero_nodes:
        raise FrequencySpeedZeroEventRequired(zero_nodes)
    for side_index, target in enumerate(targets):
        for node, direction_normal in enumerate(kinematics.direction_normal):
            rate = float(local_rates[node])
            initial_frequency = float(
                target * math.exp(-math.copysign(offset, rate))
            )
            result = solver.trace_to_frequency_face(
                direction_normal=direction_normal,
                frequency_initial_Hz=initial_frequency,
                frequency_target_Hz=float(target),
                f_initial=0.2,
                emissivity_s_inv=0.0,
                opacity_s_inv=0.0,
                n_steps=n_steps,
            )
            rows.append(
                [
                    float(side_index),
                    float(node),
                    result.travel_time_s,
                    result.frequency_face_Hz,
                    result.frequency_relative_residual,
                    result.f_face,
                    result.minimum_doppler_factor,
                    result.minimum_abs_frequency_speed_s_inv,
                    *result.direction_normal,
                    *result.direction_hydrogen,
                ]
            )
            frequency_residuals.append(result.frequency_relative_residual)
            occupation_residuals.append(abs(result.f_face - 0.2))
            dopplers.append(result.minimum_doppler_factor)
            frequency_speeds.append(result.minimum_abs_frequency_speed_s_inv)
    result_array = np.asarray(rows, dtype="<f8")
    digest = hashlib.sha256(
        quadrature.semantic_sha256.encode("ascii")
        + result_array.tobytes(order="C")
    ).hexdigest()
    return ManufacturedGeometryWitness(
        authority_label="GEOMETRY_ONLY_MANUFACTURED",
        ray_count=len(rows),
        red_ray_count=26,
        blue_ray_count=26,
        maximum_frequency_relative_residual=max(frequency_residuals),
        maximum_occupation_residual=max(occupation_residuals),
        minimum_doppler_factor=min(dopplers),
        minimum_abs_frequency_speed_s_inv=min(frequency_speeds),
        result_sha256=digest,
        physical_face_admitted=False,
        blockers=(
            BLOCKED_DIRECTIONAL_SOURCE_COEFFICIENT_AUTHORITY,
            BLOCKED_EXTERNAL_DIRECTIONAL_AUTHORITY_VERIFICATION,
        ),
    )


@dataclass(frozen=True)
class DirectionalSourceChannel:
    name: str
    owner_label: str
    coefficient_units: str
    source_sha256: str

    def __post_init__(self) -> None:
        if self.coefficient_units != "s^-1":
            raise ValueError("directional source coefficient units must be s^-1")
        source_hash = str(self.source_sha256).lower()
        if _SHA256.fullmatch(source_hash) is None:
            raise ValueError("source_sha256 must be a SHA-256 digest")
        if self.owner_label not in {
            SOURCE_IDENTICAL_SCALAR_PRIMITIVE,
            THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1,
        }:
            raise ValueError("directional source owner label is invalid")
        object.__setattr__(self, "source_sha256", source_hash)


def audit_directional_source_manifest(
    channels: Sequence[DirectionalSourceChannel],
) -> dict[str, Any]:
    """Audit declarations only; SHA-shaped strings do not verify source bytes."""

    names = [channel.name for channel in channels]
    counts = Counter(names)
    missing = [name for name in REQUIRED_SOURCE_CHANNELS if counts[name] == 0]
    duplicate = sorted(name for name, count in counts.items() if count > 1)
    unexpected = sorted(set(names).difference(REQUIRED_SOURCE_CHANNELS))
    return {
        "required_channels": list(REQUIRED_SOURCE_CHANNELS),
        "missing_channels": missing,
        "duplicate_channels": duplicate,
        "unexpected_channels": unexpected,
        "declared_complete": not missing and not duplicate and not unexpected,
        "channel_declarations": [
            {
                "name": channel.name,
                "owner_label": channel.owner_label,
                "coefficient_units": channel.coefficient_units,
                "source_sha256": channel.source_sha256,
            }
            for channel in channels
        ],
    }


@dataclass(frozen=True)
class DirectionalFaceReadiness:
    requested_authority_label: str
    declared_contract_complete: bool
    physical_face_admitted: bool
    production_integration_authorized: bool
    blockers: tuple[str, ...]
    source_manifest: dict[str, Any]
    evolution_mode: str


def audit_directional_face_readiness(
    *,
    quadrature: AngularQuadratureContract | None = None,
    source_channels: Sequence[DirectionalSourceChannel],
    incoming_authority_present: bool,
    evolution_mode: str,
    angular_remap_contract_sha256: str | None,
    speed_zero_event_restart_contract_sha256: str | None,
) -> DirectionalFaceReadiness:
    """Audit contract readiness without constructing or promoting a face array."""

    manifest = audit_directional_source_manifest(source_channels)
    blockers: list[str] = []
    if not isinstance(quadrature, AngularQuadratureContract):
        blockers.append(BLOCKED_ANGULAR_FRAME_CONTRACT)
    if not manifest["declared_complete"]:
        blockers.append(BLOCKED_DIRECTIONAL_SOURCE_COEFFICIENT_AUTHORITY)
    if not incoming_authority_present:
        blockers.append(SOURCE_FACE_ABSENT)
    event_hash = (
        str(speed_zero_event_restart_contract_sha256).lower()
        if speed_zero_event_restart_contract_sha256 is not None
        else ""
    )
    if _SHA256.fullmatch(event_hash) is None:
        blockers.append(BLOCKED_FREQUENCY_SPEED_ZERO_EVENT_RESTART_CONTRACT)
    if evolution_mode == FIXED_NODE_COUPLED:
        remap_hash = (
            str(angular_remap_contract_sha256).lower()
            if angular_remap_contract_sha256 is not None
            else ""
        )
        if _SHA256.fullmatch(remap_hash) is None:
            blockers.append(BLOCKED_ANGULAR_REMAP_AUTHORITY)
    elif evolution_mode != LAGRANGIAN_SAMPLER:
        raise ValueError("unknown directional evolution mode")
    # This research module validates declaration shape only.  It has no source
    # authority package/verifier and therefore cannot promote arbitrary digest
    # strings, booleans, or arrays into physical authority.
    blockers.append(BLOCKED_EXTERNAL_DIRECTIONAL_AUTHORITY_VERIFICATION)
    return DirectionalFaceReadiness(
        requested_authority_label=(
            THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1
        ),
        declared_contract_complete=(
            isinstance(quadrature, AngularQuadratureContract)
            and manifest["declared_complete"]
            and incoming_authority_present
            and _SHA256.fullmatch(event_hash) is not None
            and (
                evolution_mode == LAGRANGIAN_SAMPLER
                or BLOCKED_ANGULAR_REMAP_AUTHORITY not in blockers
            )
        ),
        physical_face_admitted=False,
        production_integration_authorized=False,
        blockers=tuple(blockers),
        source_manifest=manifest,
        evolution_mode=evolution_mode,
    )


__all__ = [
    "AngularQuadratureContract",
    "FaceKinematics",
    "ManufacturedGeometryWitness",
    "FrequencySpeedZeroEventRequired",
    "DirectionalSourceChannel",
    "DirectionalFaceReadiness",
    "compute_hydrogen_frame_face_kinematics",
    "compute_legacy_untagged_normal_face_kinematics",
    "run_manufactured_52_ray_geometry_witness",
    "audit_directional_source_manifest",
    "audit_directional_face_readiness",
    "SOURCE_IDENTICAL_SCALAR_PRIMITIVE",
    "THEORY_CONTRACT_DERIVED_26_ORDINATE_FACE_V1",
    "CLOSURE_DEFINED_DIRECTIONAL_SURROGATE_V1",
    "SOURCE_IDENTICAL_DIRECTIONAL_FACE",
    "HYDROGEN_FRAME",
    "HYDROGEN_TETRAD",
    "ORDINARY_FREQUENCY_HZ",
    "REQUIRED_SOURCE_CHANNELS",
    "BLOCKED_ANGULAR_FRAME_CONTRACT",
    "BLOCKED_DIRECTIONAL_SOURCE_COEFFICIENT_AUTHORITY",
    "BLOCKED_ANGULAR_REMAP_AUTHORITY",
    "BLOCKED_FREQUENCY_SPEED_ZERO_EVENT_RESTART_CONTRACT",
    "BLOCKED_EXTERNAL_DIRECTIONAL_AUTHORITY_VERIFICATION",
]
