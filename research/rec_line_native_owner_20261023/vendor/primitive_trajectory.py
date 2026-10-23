"""Typed PR-05A primitive original-HyRec one-step trajectory contract.

This bounded stage exposes source-derived native algebra, the existing COM--KHW
collision action, and chart-independent radiation feedback through one public
schema.  It deliberately does not claim a native-derived COM trajectory and it
does not remove any original-HyRec compressed term before a replacement is
present in the same residual and conservation ledger.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace as dataclass_replace
from enum import Enum
import json
import math
from types import MappingProxyType
from typing import Mapping, Sequence

import numpy as np
from scipy.constants import c, electron_volt, h, k

from full_bianchi_hyrec.background.snapshot import BackgroundSnapshot
from full_bianchi_hyrec.recoil.nonlinear_bose_release import (
    HarmonicGrid,
    apply_nonlinear_bose_jvp,
    apply_nonlinear_bose_operator,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import (
    CollisionNetwork,
    LineBoundaryConfig,
)
from full_bianchi_hyrec.recoil.coupled_interface import CoupledInterfaceProblem
from full_bianchi_hyrec.recoil.original_hyrec_native import NVIRT
from full_bianchi_hyrec.recoil.original_hyrec_physical_flux import (
    OriginalHyRecTrajectorySnapshot,
    dense_original_hyrec_matrix,
)

from .primitive_rates import (
    LYMAN_ALPHA_ENERGY_EV,
    PrimitiveRateSnapshot,
)


class StateClassification(str, Enum):
    SOURCE_DERIVED = "source_derived"
    OPERATOR_VERIFICATION = "operator_verification"
    NATIVE_DERIVED_TRAJECTORY = "native_derived_trajectory"


def _finite_scalar(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _readonly(value, shape: tuple[int, ...], name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, got {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains nonfinite values")
    result = np.array(array, copy=True)
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class AtomicRadiationState:
    """Representation-local atomic/radiation state.

    ``real_departure`` and ``native_departure`` are signed original-HyRec
    departure variables.  Only absolute populations and COM occupations are
    positivity constrained.
    """

    real_departure: np.ndarray
    native_departure: np.ndarray
    com_occupation: np.ndarray
    x_1s: float
    x_2s: float
    x_2p: float
    x_e: float
    x_HII: float
    T_m_K: float
    beta_H: np.ndarray
    interface_accumulators: Mapping[str, float] = field(default_factory=dict)
    classification: StateClassification = StateClassification.SOURCE_DERIVED

    def __post_init__(self) -> None:
        object.__setattr__(self, "real_departure", _readonly(self.real_departure, (2,), "real_departure"))
        object.__setattr__(self, "native_departure", _readonly(self.native_departure, (NVIRT,), "native_departure"))
        occupation = np.asarray(self.com_occupation, dtype=float)
        if occupation.ndim != 2 or not np.all(np.isfinite(occupation)):
            raise ValueError("com_occupation must be a finite two-dimensional array")
        if np.any(occupation <= 0.0):
            raise ValueError("COM occupations must be strictly positive")
        occupation = np.array(occupation, copy=True)
        occupation.setflags(write=False)
        object.__setattr__(self, "com_occupation", occupation)
        object.__setattr__(self, "beta_H", _readonly(self.beta_H, (3,), "beta_H"))
        if float(self.beta_H @ self.beta_H) >= 1.0:
            raise ValueError("|beta_H| must be strictly less than one")

        for name in ("x_1s", "x_2s", "x_2p", "x_e", "x_HII", "T_m_K"):
            value = _finite_scalar(getattr(self, name), name)
            object.__setattr__(self, name, value)
        if min(self.x_1s, self.x_2s, self.x_2p, self.x_e, self.x_HII) < 0.0:
            raise ValueError("physical populations must be nonnegative")
        if self.T_m_K <= 0.0:
            raise ValueError("T_m_K must be positive")
        if not isinstance(self.classification, StateClassification):
            raise TypeError("classification must be a StateClassification")
        accumulators = {str(key): _finite_scalar(value, str(key)) for key, value in self.interface_accumulators.items()}
        if any(value < 0.0 for value in accumulators.values()):
            raise ValueError("interface accumulators must be nonnegative")
        object.__setattr__(self, "interface_accumulators", MappingProxyType(accumulators))

    @property
    def native_solution(self) -> np.ndarray:
        vector = np.concatenate((self.real_departure, self.native_departure))
        vector.setflags(write=False)
        return vector

    def replace(self, **changes) -> "AtomicRadiationState":
        return dataclass_replace(self, **changes)


@dataclass(frozen=True)
class RadiationFeedback:
    rho_gamma_J_m3: float
    p_gamma_Pa: float
    q_gamma_a_W_m2: np.ndarray
    pi_gamma_ab_Pa: np.ndarray
    Q_atom_mu_W_m3: np.ndarray
    boundary_red_number_flux_per_H_s: float
    boundary_blue_number_flux_per_H_s: float

    def __post_init__(self) -> None:
        for name in (
            "rho_gamma_J_m3",
            "p_gamma_Pa",
            "boundary_red_number_flux_per_H_s",
            "boundary_blue_number_flux_per_H_s",
        ):
            value = _finite_scalar(getattr(self, name), name)
            object.__setattr__(self, name, value)
        if self.rho_gamma_J_m3 < 0.0 or self.p_gamma_Pa < 0.0:
            raise ValueError("radiation energy density and pressure must be nonnegative")
        object.__setattr__(self, "q_gamma_a_W_m2", _readonly(self.q_gamma_a_W_m2, (3,), "q_gamma_a_W_m2"))
        object.__setattr__(self, "pi_gamma_ab_Pa", _readonly(self.pi_gamma_ab_Pa, (3, 3), "pi_gamma_ab_Pa"))
        object.__setattr__(self, "Q_atom_mu_W_m3", _readonly(self.Q_atom_mu_W_m3, (4,), "Q_atom_mu_W_m3"))
        if np.max(np.abs(self.pi_gamma_ab_Pa - self.pi_gamma_ab_Pa.T)) > 1.0e-12 * max(self.rho_gamma_J_m3, 1.0e-300):
            raise ValueError("pi_gamma_ab_Pa must be symmetric")
        if abs(float(np.trace(self.pi_gamma_ab_Pa))) > 2.0e-12 * max(self.rho_gamma_J_m3, 1.0e-300):
            raise ValueError("pi_gamma_ab_Pa must be trace-free")


@dataclass(frozen=True)
class TrajectoryStepLedger:
    number_residual: float
    photon_atom_energy_residual_W_m3: float
    four_force_residual: float
    minimum_physical_state: float
    entropy_production: float
    source_hashes: Mapping[str, str]
    state_classification: StateClassification

    def __post_init__(self) -> None:
        for name in (
            "number_residual",
            "photon_atom_energy_residual_W_m3",
            "four_force_residual",
            "minimum_physical_state",
            "entropy_production",
        ):
            object.__setattr__(self, name, _finite_scalar(getattr(self, name), name))
        if self.number_residual < 0.0 or self.four_force_residual < 0.0:
            raise ValueError("residual diagnostics must be nonnegative")
        if self.minimum_physical_state <= 0.0:
            raise ValueError("minimum physical state must be strictly positive")
        if not isinstance(self.state_classification, StateClassification):
            raise TypeError("invalid state classification")
        object.__setattr__(
            self,
            "source_hashes",
            MappingProxyType({str(k): str(v) for k, v in self.source_hashes.items()}),
        )


@dataclass(frozen=True)
class PrimitiveOwnershipTerm:
    name: str
    current_owner: str
    replacement_owner: str | None
    removal_condition: str
    conservation: str
    removed: bool = False
    evaluation_count: int = 0
    application_count: int = 0
    pure_interface_atom_source_W_m3: float = 0.0

    def __post_init__(self) -> None:
        if not self.name or not self.current_owner or not self.removal_condition or not self.conservation:
            raise ValueError("ownership term fields must be nonempty")
        if self.evaluation_count < 0 or self.application_count < 0:
            raise ValueError("ownership counts must be nonnegative")
        _finite_scalar(self.pure_interface_atom_source_W_m3, "pure_interface_atom_source_W_m3")


@dataclass(frozen=True)
class OwnershipAudit:
    duplicate_owner_count: int
    unowned_term_count: int
    removed_without_replacement_count: int
    interface_evaluation_count: int
    interface_application_count: int
    pure_interface_atom_source_W_m3: float

    @property
    def passed(self) -> bool:
        return (
            self.duplicate_owner_count == 0
            and self.unowned_term_count == 0
            and self.removed_without_replacement_count == 0
            and self.interface_evaluation_count == 1
            and self.interface_application_count == 2
            and self.pure_interface_atom_source_W_m3 == 0.0
        )


@dataclass(frozen=True)
class PrimitiveOwnershipRegistry:
    terms: tuple[PrimitiveOwnershipTerm, ...]

    def __post_init__(self) -> None:
        if not self.terms:
            raise ValueError("ownership registry must be nonempty")
        names = [term.name for term in self.terms]
        if len(names) != len(set(names)):
            raise ValueError("ownership term names must be unique")

    def audit(self) -> OwnershipAudit:
        # current_owner is a scalar by construction; commas are explicitly
        # forbidden as an attempted multi-owner encoding.
        duplicate = sum("," in term.current_owner or "+" in term.current_owner for term in self.terms)
        unowned = sum(not term.current_owner.strip() for term in self.terms)
        removed_without = sum(term.removed and not term.replacement_owner for term in self.terms)
        interface = [term for term in self.terms if term.name == "red_blue_interface_packets"]
        return OwnershipAudit(
            duplicate_owner_count=int(duplicate),
            unowned_term_count=int(unowned),
            removed_without_replacement_count=int(removed_without),
            interface_evaluation_count=sum(term.evaluation_count for term in interface),
            interface_application_count=sum(term.application_count for term in interface),
            pure_interface_atom_source_W_m3=float(sum(term.pure_interface_atom_source_W_m3 for term in interface)),
        )


def default_pr05a_ownership_registry() -> PrimitiveOwnershipRegistry:
    keep = "remove only when the explicit replacement is present in the same residual and ledger"
    return PrimitiveOwnershipRegistry(
        terms=(
            PrimitiveOwnershipTerm("sobolev_lya_escape", "original_hyrec_native", "primitive_lya_transport", keep, "photon number and energy", False),
            PrimitiveOwnershipTerm("native_A1s_diffusion", "original_hyrec_native", "primitive_frequency_diffusion", keep, "photon number, recoil energy", False),
            PrimitiveOwnershipTerm("completed_Tvv_schur", "original_hyrec_native", "primitive_virtual_state_time_derivative", keep, "native algebra and source parity", False),
            PrimitiveOwnershipTerm("scalar_Dfplus_history_feedback", "original_hyrec_native", "primitive_radiation_history", keep, "causal history, no future endpoint", False),
            PrimitiveOwnershipTerm("COM_KHW_collision_recoil", "com_khw_collision", None, "not removable in PR-05A", "photon/atom four-force", False),
            PrimitiveOwnershipTerm("red_blue_interface_packets", "split_domain_interface", None, "single owner fixed by PR-04", "opposite number/face-energy application; zero atom source", False, 1, 2, 0.0),
            PrimitiveOwnershipTerm("hubble_redshift_free_streaming", "original_hyrec_native", "background_characteristic_transport", keep, "boundary flux and event localization", False),
        )
    )


@dataclass(frozen=True)
class MMatrixAudit:
    diagonal_min: float
    off_diagonal_max: float
    column_dominance_margin_min: float
    minimum_real_eigenvalue: float
    nonsingular_m_matrix: bool


def audit_native_m_matrix(matrix_s_inv: np.ndarray) -> MMatrixAudit:
    matrix = np.asarray(matrix_s_inv, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("matrix must be square")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("matrix contains nonfinite entries")
    diagonal = np.diag(matrix)
    off = np.array(matrix, copy=True)
    np.fill_diagonal(off, 0.0)
    margin = diagonal - np.sum(np.abs(off), axis=0)
    eigenvalues = np.linalg.eigvals(matrix)
    min_real = float(np.min(eigenvalues.real))
    scale = max(float(np.max(np.abs(matrix))), 1.0)
    off_max = float(np.max(off))
    is_m = (
        float(np.min(diagonal)) > 0.0
        and off_max <= 64.0 * np.finfo(float).eps * scale
        and float(np.min(margin)) > 0.0
        and min_real > 0.0
    )
    return MMatrixAudit(
        diagonal_min=float(np.min(diagonal)),
        off_diagonal_max=off_max,
        column_dominance_margin_min=float(np.min(margin)),
        minimum_real_eigenvalue=min_real,
        nonsingular_m_matrix=bool(is_m),
    )


def atomic_state_from_source_snapshot(
    snapshot: OriginalHyRecTrajectorySnapshot,
    *,
    com_occupation: np.ndarray,
    beta_H: Sequence[float],
) -> AtomicRadiationState:
    equilibrium = np.asarray([1.0, 3.0]) * snapshot.x1s * math.exp(
        -LYMAN_ALPHA_ENERGY_EV / snapshot.TR_eV_rescaled
    )
    physical = snapshot.xr + equilibrium
    physical_temperature_eV = snapshot.TM_eV_rescaled * snapshot.fsR**2 * snapshot.meR
    temperature_K = physical_temperature_eV * electron_volt / k
    return AtomicRadiationState(
        real_departure=snapshot.xr,
        native_departure=snapshot.xv,
        com_occupation=com_occupation,
        x_1s=snapshot.x1s,
        x_2s=float(physical[0]),
        x_2p=float(physical[1]),
        x_e=snapshot.xe,
        x_HII=snapshot.xHII,
        T_m_K=temperature_K,
        beta_H=beta_H,
        interface_accumulators={
            "red_photons_per_H": 0.0,
            "blue_photons_per_H": 0.0,
            "red_face_energy_J_per_H": 0.0,
            "blue_face_energy_J_per_H": 0.0,
        },
        classification=StateClassification.SOURCE_DERIVED,
    )


@dataclass(frozen=True)
class PrimitiveOneStepResult:
    native_residual: np.ndarray
    com_collision_action: np.ndarray
    native_residual_relative: float
    com_collision_relative: float
    feedback: RadiationFeedback
    ledger: TrajectoryStepLedger

    def __post_init__(self) -> None:
        native = np.asarray(self.native_residual, dtype=float)
        collision = np.asarray(self.com_collision_action, dtype=float)
        if native.ndim != 1 or collision.ndim != 2:
            raise ValueError("result arrays have invalid rank")
        if not np.all(np.isfinite(native)) or not np.all(np.isfinite(collision)):
            raise ValueError("result contains nonfinite entries")
        native = np.array(native, copy=True); native.setflags(write=False)
        collision = np.array(collision, copy=True); collision.setflags(write=False)
        object.__setattr__(self, "native_residual", native)
        object.__setattr__(self, "com_collision_action", collision)
        object.__setattr__(self, "native_residual_relative", _finite_scalar(self.native_residual_relative, "native_residual_relative"))
        object.__setattr__(self, "com_collision_relative", _finite_scalar(self.com_collision_relative, "com_collision_relative"))


@dataclass(frozen=True)
class PrimitiveImplicitStepResult:
    state: AtomicRadiationState
    converged: bool
    backward_error: float
    native_residual_relative: float
    com_residual_relative: float
    number_relative_change: float
    free_energy_change: float
    minimum_physical_state: float

    def __post_init__(self) -> None:
        for name in (
            "backward_error",
            "native_residual_relative",
            "com_residual_relative",
            "number_relative_change",
            "free_energy_change",
            "minimum_physical_state",
        ):
            object.__setattr__(self, name, _finite_scalar(getattr(self, name), name))
        if not self.converged:
            raise ValueError("implicit step result must be converged")
        if min(
            self.backward_error,
            self.native_residual_relative,
            self.com_residual_relative,
            self.number_relative_change,
        ) < 0.0:
            raise ValueError("implicit residual diagnostics must be nonnegative")
        if self.minimum_physical_state <= 0.0:
            raise ValueError("implicit state must remain strictly positive")


@dataclass(frozen=True)
class PrimitiveTrajectoryProblem:
    background: BackgroundSnapshot
    source_snapshot: OriginalHyRecTrajectorySnapshot
    rates: PrimitiveRateSnapshot
    network: CollisionNetwork
    grid: HarmonicGrid
    line: LineBoundaryConfig
    interface_enabled: bool = False

    def __post_init__(self) -> None:
        if self.network.n_state != len(self.network.mode_measure):
            raise ValueError("invalid collision network")
        if not math.isclose(self.background.H_s_inv, self.source_snapshot.H_s_inv, rel_tol=3e-13, abs_tol=0.0):
            raise ValueError("BackgroundSnapshot H does not match source-conditioned snapshot")
        source_alpha_si = self.source_snapshot.Alpha * 1.0e-6
        source_delta_si = self.source_snapshot.DAlpha * 1.0e-6
        if np.max(np.abs(source_alpha_si - self.rates.alpha_m3_s) / np.maximum(np.abs(source_alpha_si), 1e-300)) > 2e-11:
            raise ValueError("primitive Alpha rates do not match source snapshot")
        if np.max(np.abs(source_delta_si - self.rates.delta_alpha_m3_s) / np.maximum(np.abs(source_delta_si), 1e-300)) > 2e-10:
            raise ValueError("primitive delta-Alpha rates do not match source snapshot")
        if np.max(np.abs(self.source_snapshot.Beta - self.rates.beta_s_inv) / np.maximum(np.abs(self.source_snapshot.Beta), 1e-300)) > 2e-11:
            raise ValueError("primitive Beta rates do not match source snapshot")

    @property
    def native_matrix_s_inv(self) -> np.ndarray:
        matrix = dense_original_hyrec_matrix(self.source_snapshot)
        matrix.setflags(write=False)
        return matrix

    @property
    def native_rhs_s_inv(self) -> np.ndarray:
        rhs = np.concatenate((self.source_snapshot.sr, self.source_snapshot.sv))
        rhs.setflags(write=False)
        return rhs

    def _validate_state(self, state: AtomicRadiationState) -> None:
        if state.native_solution.shape != (2 + NVIRT,):
            raise ValueError("native state shape mismatch")
        if state.com_occupation.shape != (self.network.n_state, self.grid.n_angle):
            raise ValueError("COM occupation shape mismatch")
        if not np.array_equal(state.beta_H, self.background.beta_H):
            raise ValueError("state beta_H must match BackgroundSnapshot")

    def native_residual(self, native_solution: np.ndarray) -> np.ndarray:
        solution = np.asarray(native_solution, dtype=float)
        if solution.shape != (2 + NVIRT,):
            raise ValueError("native solution shape mismatch")
        return self.native_matrix_s_inv @ solution - self.native_rhs_s_inv

    def native_jvp(self, direction: np.ndarray) -> np.ndarray:
        vector = np.asarray(direction, dtype=float)
        if vector.shape != (2 + NVIRT,):
            raise ValueError("native direction shape mismatch")
        return self.native_matrix_s_inv @ vector

    def _collision(self, occupation: np.ndarray):
        return apply_nonlinear_bose_operator(
            occupation,
            mode_measure=self.network.mode_measure,
            equilibrium_weight=self.network.equilibrium_weight,
            pair_moments=self.network.pair_moments,
            same_cell_rates=self.network.same_cell_rates,
            grid=self.grid,
            photon_momentum_scale=self.network.momentum_scale,
        )

    def _feedback(self, state: AtomicRadiationState, collision) -> RadiationFeedback:
        frequencies = self.line.nu_abs_Hz + self.network.centers * self.line.Doppler_width_Hz
        if np.any(frequencies <= 0.0):
            raise ValueError("COM state frequency is nonpositive")
        angular_energy = (
            self.network.mode_measure[:, None]
            * (h * frequencies)[:, None]
            * state.com_occupation
            * self.grid.weights[None, :]
        )
        rho = float(np.sum(angular_energy))
        q = c * np.sum(
            angular_energy[:, :, None] * self.grid.directions[None, :, :],
            axis=(0, 1),
        )
        pressure_tensor = np.sum(
            angular_energy[:, :, None, None]
            * self.grid.directions[None, :, :, None]
            * self.grid.directions[None, :, None, :],
            axis=(0, 1),
        )
        pressure = rho / 3.0
        pi = pressure_tensor - pressure * np.eye(3)
        # The collision four-force is represented in momentum-density-rate
        # units in the COM operator. Multiplication by c expresses every tetrad
        # component in energy-source units W m^-3.
        q_atom = c * np.asarray(collision.Q_atom, dtype=float)
        red = state.interface_accumulators.get("red_photons_per_H", 0.0)
        blue = state.interface_accumulators.get("blue_photons_per_H", 0.0)
        if not self.interface_enabled:
            red = 0.0
            blue = 0.0
        return RadiationFeedback(
            rho_gamma_J_m3=rho,
            p_gamma_Pa=pressure,
            q_gamma_a_W_m2=q,
            pi_gamma_ab_Pa=pi,
            Q_atom_mu_W_m3=q_atom,
            boundary_red_number_flux_per_H_s=float(red),
            boundary_blue_number_flux_per_H_s=float(blue),
        )

    def evaluate(self, state: AtomicRadiationState) -> PrimitiveOneStepResult:
        self._validate_state(state)
        native = self.native_residual(state.native_solution)
        native_scale = max(
            float(np.max(np.abs(self.native_matrix_s_inv @ state.native_solution))),
            float(np.max(np.abs(self.native_rhs_s_inv))),
            1.0e-300,
        )
        native_relative = float(np.max(np.abs(native)) / native_scale)
        collision = self._collision(state.com_occupation)
        collision_scale = max(float(collision.gross_action_scale), 1.0e-300)
        collision_relative = float(np.max(np.abs(collision.occupation_action)) / collision_scale)
        number_scale = max(
            float(np.sum(np.abs(collision.number_action) * self.grid.weights[None, :])),
            1.0e-300,
        )
        number_residual = abs(float(collision.number_residual)) / number_scale
        four_sum = np.asarray(collision.Q_gamma) + np.asarray(collision.Q_atom)
        four_scale = max(
            float(np.max(np.abs(collision.Q_gamma))),
            float(np.max(np.abs(collision.Q_atom))),
            1.0e-300,
        )
        four_residual = float(np.max(np.abs(four_sum)) / four_scale)
        energy_residual = float(c * four_sum[0])
        feedback = self._feedback(state, collision)
        minimum = min(
            float(np.min(state.com_occupation)),
            state.x_1s,
            state.x_2s,
            state.x_2p,
            state.x_e,
            state.x_HII,
            state.T_m_K,
        )
        ledger = TrajectoryStepLedger(
            number_residual=number_residual,
            photon_atom_energy_residual_W_m3=energy_residual,
            four_force_residual=four_residual,
            minimum_physical_state=minimum,
            entropy_production=float(collision.entropy_production),
            source_hashes=self.rates.source_hashes,
            state_classification=state.classification,
        )
        return PrimitiveOneStepResult(
            native_residual=native,
            com_collision_action=collision.occupation_action,
            native_residual_relative=native_relative,
            com_collision_relative=collision_relative,
            feedback=feedback,
            ledger=ledger,
        )

    def analytic_jvp(
        self,
        state: AtomicRadiationState,
        *,
        native_direction: np.ndarray,
        log_com_direction: np.ndarray,
    ) -> np.ndarray:
        self._validate_state(state)
        native = self.native_jvp(native_direction)
        log_direction = np.asarray(log_com_direction, dtype=float)
        if log_direction.shape != state.com_occupation.shape:
            raise ValueError("log COM direction shape mismatch")
        occupation_direction = state.com_occupation * log_direction
        collision = apply_nonlinear_bose_jvp(
            state.com_occupation,
            occupation_direction,
            mode_measure=self.network.mode_measure,
            equilibrium_weight=self.network.equilibrium_weight,
            pair_moments=self.network.pair_moments,
            same_cell_rates=self.network.same_cell_rates,
            grid=self.grid,
        ).occupation_action_jvp
        return np.concatenate((native, collision.ravel()))

    def central_difference_jvp_residual(
        self,
        state: AtomicRadiationState,
        *,
        native_direction: np.ndarray,
        log_com_direction: np.ndarray,
        step: float = 1.0e-6,
    ) -> float:
        if step <= 0.0:
            raise ValueError("step must be positive")
        native_direction = np.asarray(native_direction, dtype=float)
        log_direction = np.asarray(log_com_direction, dtype=float)
        if native_direction.shape != (2 + NVIRT,) or log_direction.shape != state.com_occupation.shape:
            raise ValueError("JVP direction shape mismatch")
        native0 = state.native_solution

        def residual(sign: float) -> np.ndarray:
            native = native0 + sign * step * native_direction
            com = state.com_occupation * np.exp(sign * step * log_direction)
            native_res = self.native_residual(native)
            collision = self._collision(com).occupation_action
            return np.concatenate((native_res, collision.ravel()))

        finite = (residual(1.0) - residual(-1.0)) / (2.0 * step)
        analytic = self.analytic_jvp(
            state,
            native_direction=native_direction,
            log_com_direction=log_direction,
        )
        return float(
            np.max(np.abs(finite - analytic))
            / max(float(np.max(np.abs(finite))), float(np.max(np.abs(analytic))), 1.0e-300)
        )

    def implicit_step(
        self,
        state: AtomicRadiationState,
        *,
        dt_s: float,
    ) -> PrimitiveImplicitStepResult:
        """Project the native algebraic block and advance COM collisions implicitly.

        PR-05A keeps the original native block algebraic.  The direct solve is
        therefore the DAE constraint projection; it is not yet the primitive
        radiation time derivative introduced in PR-05B.  COM occupations use
        the existing log-positive backward-Euler Newton--GMRES update.
        """

        self._validate_state(state)
        if self.interface_enabled:
            raise NotImplementedError(
                "PR-05A implicit projection is interface-off; coupled trajectory is PR-05B"
            )
        if not math.isfinite(dt_s) or dt_s <= 0.0:
            raise ValueError("dt_s must be positive and finite")
        native_solution = np.linalg.solve(self.native_matrix_s_inv, self.native_rhs_s_inv)
        native_residual = self.native_residual(native_solution)
        native_scale = max(
            float(np.max(np.abs(self.native_matrix_s_inv @ native_solution))),
            float(np.max(np.abs(self.native_rhs_s_inv))),
            1.0e-300,
        )
        native_relative = float(np.max(np.abs(native_residual)) / native_scale)
        # The exact v0.57 COM Bose--Einstein lane is already a collision
        # equilibrium.  Evaluate its backward-Euler residual through the v0.56
        # gross-term/number-closure metric instead of forcing a Newton update
        # below the known dilute float64 net-residual floor.
        com_problem = CoupledInterfaceProblem(
            network=self.network,
            grid=self.grid,
            packets=tuple(),
            n_H_m3=self.source_snapshot.nH_cm3 * 1.0e6,
            dt_s=dt_s,
            enabled=False,
        )
        com_vector = com_problem.pack(
            np.log(state.com_occupation), np.empty(0, dtype=float)
        )
        com_metrics = com_problem.residual_metrics(com_vector, state.com_occupation)
        com_converged = (
            com_metrics.scaled_relative <= 1.0e-11
            or (
                com_metrics.backward_error_relative <= 1.0e-11
                and com_metrics.number_relative_residual <= 1.0e-11
            )
        )
        if not com_converged:
            raise RuntimeError(
                "interface-off COM equilibrium fails both scaled and gross backward gates"
            )
        equilibrium = np.asarray([1.0, 3.0]) * state.x_1s * math.exp(
            -LYMAN_ALPHA_ENERGY_EV / self.source_snapshot.TR_eV_rescaled
        )
        physical = native_solution[:2] + equilibrium
        updated = state.replace(
            real_departure=native_solution[:2],
            native_departure=native_solution[2:],
            com_occupation=state.com_occupation,
            x_2s=float(physical[0]),
            x_2p=float(physical[1]),
            classification=StateClassification.OPERATOR_VERIFICATION,
        )
        minimum = min(
            float(np.min(updated.com_occupation)),
            updated.x_1s,
            updated.x_2s,
            updated.x_2p,
            updated.x_e,
            updated.x_HII,
        )
        backward = max(native_relative, float(com_metrics.backward_error_relative))
        return PrimitiveImplicitStepResult(
            state=updated,
            converged=True,
            backward_error=backward,
            native_residual_relative=native_relative,
            com_residual_relative=float(com_metrics.backward_error_relative),
            number_relative_change=float(com_metrics.number_relative_residual),
            free_energy_change=0.0,
            minimum_physical_state=minimum,
        )

    def restart_payload(self, state: AtomicRadiationState) -> str:
        self._validate_state(state)
        payload = {
            "schema": "PR05A_ATOMIC_RADIATION_RESTART_V1",
            "real_departure": state.real_departure.tolist(),
            "native_departure": state.native_departure.tolist(),
            "com_occupation": state.com_occupation.tolist(),
            "x_1s": state.x_1s,
            "x_2s": state.x_2s,
            "x_2p": state.x_2p,
            "x_e": state.x_e,
            "x_HII": state.x_HII,
            "T_m_K": state.T_m_K,
            "beta_H": state.beta_H.tolist(),
            "interface_accumulators": dict(state.interface_accumulators),
            "classification": state.classification.value,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)

    def state_from_restart_payload(self, payload: str) -> AtomicRadiationState:
        data = json.loads(payload)
        if data.get("schema") != "PR05A_ATOMIC_RADIATION_RESTART_V1":
            raise ValueError("unknown restart schema")
        state = AtomicRadiationState(
            real_departure=data["real_departure"],
            native_departure=data["native_departure"],
            com_occupation=data["com_occupation"],
            x_1s=data["x_1s"],
            x_2s=data["x_2s"],
            x_2p=data["x_2p"],
            x_e=data["x_e"],
            x_HII=data["x_HII"],
            T_m_K=data["T_m_K"],
            beta_H=data["beta_H"],
            interface_accumulators=data["interface_accumulators"],
            classification=StateClassification(data["classification"]),
        )
        self._validate_state(state)
        return state
