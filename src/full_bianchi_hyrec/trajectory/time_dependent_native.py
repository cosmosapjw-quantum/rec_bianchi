"""PR-05B1 source-identifiable original-HyRec DAE and no-go audit.

The October-2012 source does not evolve the 2s/2p and virtual-spike variables
as local differential states.  It solves them in steady state, while the
free-electron fraction is differential in ``eta = ln(a)`` and the radiation
field carries time dependence through causal redshift-history arrays.  This
module exposes that source-identifiable split and deliberately refuses to
invent a finite virtual-spike mass/time measure.

Conventions
-----------
Metric signature is ``(-,+,+,+)``.  Frequency is ordinary frequency in Hz.
The source adapter retains eV and cgs only where the original C formula uses
them; public state variables are dimensionless and rates are explicit.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
import math
from types import MappingProxyType
from typing import Mapping, Sequence

import numpy as np

from full_bianchi_hyrec.recoil.original_hyrec_native import NVIRT
from full_bianchi_hyrec.trajectory.primitive_rates import (
    IONIZATION_ENERGY_EV,
    LYMAN_ALPHA_ENERGY_EV,
    SAHA_COEFFICIENT_CGS,
)
from full_bianchi_hyrec.trajectory.primitive_trajectory import (
    AtomicRadiationState,
    PrimitiveTrajectoryProblem,
)


class OriginalHyRecStateRole(str, Enum):
    """Source-identifiable role of an original-HyRec state block."""

    DIFFERENTIAL = "differential"
    ALGEBRAIC = "algebraic"
    ACCEPTED_STEP_MEMORY = "accepted_step_memory"
    EXTERNAL = "external"


@dataclass(frozen=True)
class OriginalHyRecStateBlock:
    name: str
    size: int
    role: OriginalHyRecStateRole
    unit: str
    source_owner: str
    source_evidence: str

    def __post_init__(self) -> None:
        if not self.name or self.size <= 0 or not self.unit or not self.source_owner:
            raise ValueError("state-block fields must be nonempty and size positive")
        if not isinstance(self.role, OriginalHyRecStateRole):
            raise TypeError("role must be an OriginalHyRecStateRole")
        if not self.source_evidence:
            raise ValueError("source evidence must be explicit")


@dataclass(frozen=True)
class OriginalHyRecStateLayout:
    blocks: tuple[OriginalHyRecStateBlock, ...]

    def __post_init__(self) -> None:
        names = [block.name for block in self.blocks]
        if len(names) != len(set(names)):
            raise ValueError("state-block names must be unique")

    @property
    def local_blocks(self) -> tuple[OriginalHyRecStateBlock, ...]:
        return tuple(
            block
            for block in self.blocks
            if block.role in {
                OriginalHyRecStateRole.DIFFERENTIAL,
                OriginalHyRecStateRole.ALGEBRAIC,
            }
        )

    @property
    def local_size(self) -> int:
        return sum(block.size for block in self.local_blocks)

    @property
    def differential_size(self) -> int:
        return sum(
            block.size
            for block in self.blocks
            if block.role is OriginalHyRecStateRole.DIFFERENTIAL
        )

    @property
    def algebraic_size(self) -> int:
        return sum(
            block.size
            for block in self.blocks
            if block.role is OriginalHyRecStateRole.ALGEBRAIC
        )

    @property
    def history_size(self) -> int:
        return sum(
            block.size
            for block in self.blocks
            if block.role is OriginalHyRecStateRole.ACCEPTED_STEP_MEMORY
        )

    @property
    def mass_diagonal(self) -> np.ndarray:
        values: list[float] = []
        for block in self.local_blocks:
            mass = 1.0 if block.role is OriginalHyRecStateRole.DIFFERENTIAL else 0.0
            values.extend([mass] * block.size)
        result = np.asarray(values, dtype=float)
        result.setflags(write=False)
        return result

    def require_virtual_differential_measure(self, audit: "NativeRadiationTimeMeasureAudit") -> None:
        if not audit.identifiable:
            raise NativeRadiationTimeMeasureNotIdentifiable(audit.reason)


def source_identifiable_original_hyrec_layout() -> OriginalHyRecStateLayout:
    """Return the fixed local-DAE and causal-memory roles in the canonical source."""

    return OriginalHyRecStateLayout(
        blocks=(
            OriginalHyRecStateBlock(
                "free_electron_fraction",
                1,
                OriginalHyRecStateRole.DIFFERENTIAL,
                "dimensionless; derivative with respect to eta=ln(a)",
                "rec_HMLA_2photon_dxHIIdlna",
                "hydrogen.c:769-775 and technical supplement Eq. (10)",
            ),
            OriginalHyRecStateBlock(
                "real_departures_2s_2p",
                2,
                OriginalHyRecStateRole.ALGEBRAIC,
                "dimensionless abundance departure",
                "solve_real_virt",
                "hydrogen.c:565-625; HyRec steady-state excited-level approximation",
            ),
            OriginalHyRecStateBlock(
                "virtual_departures",
                NVIRT,
                OriginalHyRecStateRole.ALGEBRAIC,
                "dimensionless x_1s Delta f_nu",
                "solve_real_virt",
                "hydrogen.c:616-619; zero-width virtual-spike steady-state equation",
            ),
            OriginalHyRecStateBlock(
                "outgoing_virtual_history",
                NVIRT,
                OriginalHyRecStateRole.ACCEPTED_STEP_MEMORY,
                "dimensionless photon occupation departure",
                "Dfminus_hist",
                "hydrogen.c:657-718 and 777-792",
            ),
            OriginalHyRecStateBlock(
                "outgoing_lyman_history",
                3,
                OriginalHyRecStateRole.ACCEPTED_STEP_MEMORY,
                "dimensionless photon occupation departure",
                "Dfminus_Ly_hist",
                "hydrogen.c:660-661 and 794-796",
            ),
            OriginalHyRecStateBlock(
                "average_virtual_history",
                NVIRT,
                OriginalHyRecStateRole.ACCEPTED_STEP_MEMORY,
                "dimensionless photon occupation departure",
                "Dfnu_hist",
                "hydrogen.c:727 and 798-799",
            ),
            OriginalHyRecStateBlock(
                "background_snapshot",
                1,
                OriginalHyRecStateRole.EXTERNAL,
                "typed SI/tetrad snapshot",
                "host_background_solver",
                "PR-01C/PR-05A BackgroundSnapshot firewall",
            ),
        )
    )


class NativeRadiationTimeMeasureNotIdentifiable(RuntimeError):
    """Raised when a finite virtual-spike mass is requested without source evidence."""


@dataclass(frozen=True)
class NativeRadiationTimeMeasureAudit:
    identifiable: bool
    canonical_virtual_role: OriginalHyRecStateRole
    finite_support_widths_present: bool
    cell_edges_present: bool
    spike_shape_present: bool
    candidate_mass_a: np.ndarray
    candidate_mass_b: np.ndarray
    maximum_relative_candidate_difference: float
    reason: str

    def __post_init__(self) -> None:
        a = np.asarray(self.candidate_mass_a, dtype=float)
        b = np.asarray(self.candidate_mass_b, dtype=float)
        if a.shape != (NVIRT,) or b.shape != (NVIRT,):
            raise ValueError("candidate mass vectors must have NVIRT entries")
        if np.any(a <= 0.0) or np.any(b <= 0.0) or not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
            raise ValueError("candidate mass vectors must be finite and positive")
        a = np.array(a, copy=True); a.setflags(write=False)
        b = np.array(b, copy=True); b.setflags(write=False)
        object.__setattr__(self, "candidate_mass_a", a)
        object.__setattr__(self, "candidate_mass_b", b)
        value = float(self.maximum_relative_candidate_difference)
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError("candidate difference must be positive and finite")
        object.__setattr__(self, "maximum_relative_candidate_difference", value)
        if not self.reason:
            raise ValueError("audit reason must be explicit")


def audit_canonical_native_radiation_time_measure(
    energy_eV: Sequence[float],
    *,
    x_1s: float,
) -> NativeRadiationTimeMeasureAudit:
    """Construct a no-go witness for a finite local virtual-spike mass.

    The continuum equation contains a time-derivative measure proportional to
    ``d ln(nu)`` (and, for ``Delta x_b=x_1s Delta f_b``, inversely to ``x_1s``
    on a frozen background).  The canonical archive supplies spike centres and
    integrated rates but no finite support width, edge array or spike shape.

    Two nonoverlapping top-hat supports, both centred on every canonical energy,
    are constructed with widths 0.2 and 0.4 times the nearest log-frequency
    separation.  They are equally compatible with the centre-only evidence but
    give mass vectors differing by a factor of two.  Neither is promoted.
    """

    energies = np.asarray(energy_eV, dtype=float)
    if energies.shape != (NVIRT,) or not np.all(np.isfinite(energies)) or np.any(energies <= 0.0):
        raise ValueError("energy_eV must contain NVIRT positive finite centres")
    if np.any(np.diff(energies) <= 0.0):
        raise ValueError("energy centres must be strictly increasing")
    x1s = float(x_1s)
    if not math.isfinite(x1s) or x1s <= 0.0:
        raise ValueError("x_1s must be positive")
    log_energy = np.log(energies)
    gaps = np.diff(log_energy)
    nearest = np.empty(NVIRT, dtype=float)
    nearest[0] = gaps[0]
    nearest[-1] = gaps[-1]
    nearest[1:-1] = np.minimum(gaps[:-1], gaps[1:])
    width_a = 0.2 * nearest
    width_b = 0.4 * nearest
    mass_a = width_a / x1s
    mass_b = width_b / x1s
    relative = float(np.max(np.abs(mass_b - mass_a) / np.maximum(np.abs(mass_b), np.abs(mass_a))))
    return NativeRadiationTimeMeasureAudit(
        identifiable=False,
        canonical_virtual_role=OriginalHyRecStateRole.ALGEBRAIC,
        finite_support_widths_present=False,
        cell_edges_present=False,
        spike_shape_present=False,
        candidate_mass_a=mass_a,
        candidate_mass_b=mass_b,
        maximum_relative_candidate_difference=relative,
        reason=(
            "canonical original-HyRec takes the virtual-spike support to zero and neglects "
            "the local time derivative; centre frequencies and integrated rates do not fix "
            "a finite dln(nu) mass, cell edges, or spike shape"
        ),
    )


@dataclass(frozen=True)
class CausalRadiationHistoryState:
    """One accepted-step slice of the source-identifiable radiation memory."""

    accepted_index: int
    outgoing_virtual: np.ndarray
    outgoing_lyman: np.ndarray
    average_virtual: np.ndarray

    def __post_init__(self) -> None:
        if int(self.accepted_index) != self.accepted_index or self.accepted_index < 0:
            raise ValueError("accepted_index must be a nonnegative integer")
        object.__setattr__(self, "accepted_index", int(self.accepted_index))
        for name, shape in (
            ("outgoing_virtual", (NVIRT,)),
            ("outgoing_lyman", (3,)),
            ("average_virtual", (NVIRT,)),
        ):
            array = np.asarray(getattr(self, name), dtype=float)
            if array.shape != shape or not np.all(np.isfinite(array)):
                raise ValueError(f"{name} must have shape {shape} and be finite")
            array = np.array(array, copy=True); array.setflags(write=False)
            object.__setattr__(self, name, array)

    def assert_endpoint_is_available(self, endpoint_index: int) -> None:
        endpoint = int(endpoint_index)
        if endpoint > self.accepted_index:
            raise ValueError(
                f"future history endpoint {endpoint} exceeds accepted index {self.accepted_index}"
            )
        if endpoint < 0:
            raise ValueError("history endpoint must be nonnegative")

    def to_json(self) -> str:
        return json.dumps(
            {
                "schema": "PR05B1_CAUSAL_RADIATION_HISTORY_V1",
                "accepted_index": self.accepted_index,
                "outgoing_virtual": self.outgoing_virtual.tolist(),
                "outgoing_lyman": self.outgoing_lyman.tolist(),
                "average_virtual": self.average_virtual.tolist(),
            },
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )

    @classmethod
    def from_json(cls, payload: str) -> "CausalRadiationHistoryState":
        data = json.loads(payload)
        if data.get("schema") != "PR05B1_CAUSAL_RADIATION_HISTORY_V1":
            raise ValueError("unknown causal-radiation history schema")
        return cls(
            accepted_index=data["accepted_index"],
            outgoing_virtual=data["outgoing_virtual"],
            outgoing_lyman=data["outgoing_lyman"],
            average_virtual=data["average_virtual"],
        )


@dataclass(frozen=True)
class ReplacementTerm:
    name: str
    current_owner: str
    requested_replacement_owner: str
    source_identifiable: bool
    replacement_complete: bool
    removed: bool
    blocker: str
    source_evidence: str

    def __post_init__(self) -> None:
        if not all((self.name, self.current_owner, self.requested_replacement_owner, self.blocker, self.source_evidence)):
            raise ValueError("replacement term fields must be nonempty")
        if self.removed and not self.replacement_complete:
            raise ValueError("a compressed term cannot be removed without complete replacement")


@dataclass(frozen=True)
class ReplacementAudit:
    duplicate_owner_count: int
    unowned_term_count: int
    removed_without_complete_replacement_count: int
    completed_replacement_count: int
    requested_replacement_count: int
    pr05b_complete: bool


@dataclass(frozen=True)
class ReplacementRegistry:
    terms: tuple[ReplacementTerm, ...]

    def __post_init__(self) -> None:
        names = [term.name for term in self.terms]
        if not names or len(names) != len(set(names)):
            raise ValueError("replacement names must be nonempty and unique")

    def audit(self) -> ReplacementAudit:
        duplicate = sum("," in term.current_owner or "+" in term.current_owner for term in self.terms)
        unowned = sum(not term.current_owner.strip() for term in self.terms)
        removed_without = sum(term.removed and not term.replacement_complete for term in self.terms)
        completed = sum(term.replacement_complete for term in self.terms)
        requested = len(self.terms)
        return ReplacementAudit(
            duplicate_owner_count=int(duplicate),
            unowned_term_count=int(unowned),
            removed_without_complete_replacement_count=int(removed_without),
            completed_replacement_count=int(completed),
            requested_replacement_count=requested,
            pr05b_complete=bool(completed == requested and removed_without == 0),
        )


def default_pr05b1_replacement_registry() -> ReplacementRegistry:
    common = (
        "finite virtual-spike support/mass and a causal accepted-step transport state are "
        "absent from the canonical local algebraic block"
    )
    return ReplacementRegistry(
        terms=(
            ReplacementTerm(
                "sobolev_lya_escape",
                "original_hyrec_zero_width_spike_and_history",
                "primitive_characteristic_transport",
                False,
                False,
                False,
                common,
                "hydrogen.c:521-526, 779-796; HyRec Eq. (75) zero-width steady limit",
            ),
            ReplacementTerm(
                "native_A1s_diffusion",
                "original_hyrec_algebraic_virtual_block",
                "finite_measure_frequency_diffusion",
                False,
                False,
                False,
                common,
                "hydrogen.c:480-519; diffusion rates are source-locked but the transient mass is not",
            ),
            ReplacementTerm(
                "completed_Tvv_schur",
                "original_hyrec_algebraic_virtual_block",
                "primitive_virtual_radiation_DAE",
                False,
                False,
                False,
                common,
                "hydrogen.c:525-526, 586-619",
            ),
            ReplacementTerm(
                "scalar_Dfplus_history_feedback",
                "original_hyrec_causal_history",
                "typed_characteristic_history_state",
                True,
                False,
                False,
                "schema is now identified, but accepted-step update/restart integration is PR-05B2",
                "hydrogen.c:627-718, 777-799",
            ),
        )
    )


@dataclass(frozen=True)
class FrozenCoefficientBackwardEulerResult:
    state_vector: np.ndarray
    converged: bool
    backward_error: float
    algebraic_residual_relative: float
    minimum_physical_population: float

    def __post_init__(self) -> None:
        vector = np.asarray(self.state_vector, dtype=float)
        if vector.shape != (1 + 2 + NVIRT,) or not np.all(np.isfinite(vector)):
            raise ValueError("state_vector has invalid shape or values")
        vector = np.array(vector, copy=True); vector.setflags(write=False)
        object.__setattr__(self, "state_vector", vector)
        for name in ("backward_error", "algebraic_residual_relative", "minimum_physical_population"):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        if not self.converged or self.backward_error < 0.0 or self.algebraic_residual_relative < 0.0:
            raise ValueError("backward-Euler result must be converged with nonnegative diagnostics")
        if self.minimum_physical_population <= 0.0:
            raise ValueError("physical populations must remain positive")


@dataclass(frozen=True)
class SourceIdentifiableOriginalHyRecDAE:
    """Frozen-background source-identifiable local DAE in ``eta=ln(a)``.

    The only local differential row is ``x_e``.  The real and virtual departure
    equations remain the canonical algebraic solve.  Causal history is a
    separate accepted-step state and is not smuggled into a local mass matrix.
    """

    primitive_problem: PrimitiveTrajectoryProblem
    layout: OriginalHyRecStateLayout

    @classmethod
    def from_primitive_problem(
        cls, primitive_problem: PrimitiveTrajectoryProblem
    ) -> "SourceIdentifiableOriginalHyRecDAE":
        return cls(
            primitive_problem=primitive_problem,
            layout=source_identifiable_original_hyrec_layout(),
        )

    @property
    def source_snapshot(self):
        return self.primitive_problem.source_snapshot

    @property
    def rates(self):
        return self.primitive_problem.rates

    @property
    def native_matrix_s_inv(self) -> np.ndarray:
        return self.primitive_problem.native_matrix_s_inv

    @property
    def native_rhs_s_inv(self) -> np.ndarray:
        return self.primitive_problem.native_rhs_s_inv

    @property
    def steady_native_solution(self) -> np.ndarray:
        solution = np.linalg.solve(self.native_matrix_s_inv, self.native_rhs_s_inv)
        solution.setflags(write=False)
        return solution

    @property
    def mass_diagonal(self) -> np.ndarray:
        return self.layout.mass_diagonal

    def source_state_vector(self, state: AtomicRadiationState) -> np.ndarray:
        self.primitive_problem._validate_state(state)
        vector = np.concatenate((np.asarray([state.x_e]), state.native_solution))
        vector.setflags(write=False)
        return vector

    def source_derivative_vector(self) -> np.ndarray:
        vector = np.zeros(self.layout.local_size, dtype=float)
        vector[0] = self.source_snapshot.dxHIIdlna
        vector.setflags(write=False)
        return vector

    def _saha_fraction(self) -> float:
        source = self.source_snapshot
        Tr = source.TR_eV_rescaled
        return (
            SAHA_COEFFICIENT_CGS
            * (source.fsR * source.meR) ** 3
            * Tr
            * math.sqrt(Tr)
            * math.exp(-IONIZATION_ENERGY_EV / Tr)
            / source.nH_cm3
        )

    def electron_rate_per_lna(self, x_e: float, real_departure: Sequence[float]) -> float:
        """Evaluate canonical ``dx_HII/dln(a)`` with frozen source coefficients.

        ``x_HII`` and ``x_1s`` are source-conditioned external reservoirs in this
        bounded audit.  Promoting them and the history state is PR-05B2/C.
        """

        xe = float(x_e)
        real = np.asarray(real_departure, dtype=float)
        if not math.isfinite(xe) or real.shape != (2,) or not np.all(np.isfinite(real)):
            raise ValueError("electron-rate arguments are invalid")
        source = self.source_snapshot
        saha = self._saha_fraction()
        dxe2 = xe * source.xHII - saha * source.x1s
        alpha_cgs = self.rates.alpha_m3_s * 1.0e6
        delta_alpha_cgs = self.rates.delta_alpha_m3_s * 1.0e6
        contributions = (
            source.nH_cm3
            * (saha * source.x1s * delta_alpha_cgs + alpha_cgs * dxe2)
            - real * self.rates.beta_s_inv
        )
        return -float(np.sum(contributions)) / source.H_s_inv

    def _electron_rate_derivatives(self) -> tuple[float, np.ndarray]:
        source = self.source_snapshot
        alpha_cgs = self.rates.alpha_m3_s * 1.0e6
        derivative_xe = -source.nH_cm3 * source.xHII * float(np.sum(alpha_cgs)) / source.H_s_inv
        derivative_real = self.rates.beta_s_inv / source.H_s_inv
        return float(derivative_xe), np.asarray(derivative_real, dtype=float)

    def residual(self, state_vector: Sequence[float], state_derivative: Sequence[float]) -> np.ndarray:
        state = np.asarray(state_vector, dtype=float)
        derivative = np.asarray(state_derivative, dtype=float)
        if state.shape != (self.layout.local_size,) or derivative.shape != state.shape:
            raise ValueError("state and derivative must have the local DAE size")
        if not np.all(np.isfinite(state)) or not np.all(np.isfinite(derivative)):
            raise ValueError("state and derivative must be finite")
        result = np.empty_like(state)
        result[0] = derivative[0] - self.electron_rate_per_lna(state[0], state[1:3])
        result[1:] = self.native_matrix_s_inv @ state[1:] - self.native_rhs_s_inv
        return result

    def shifted_ijacobian(self, shift: float) -> np.ndarray:
        value = float(shift)
        if not math.isfinite(value):
            raise ValueError("shift must be finite")
        matrix = np.zeros((self.layout.local_size, self.layout.local_size), dtype=float)
        d_rate_xe, d_rate_real = self._electron_rate_derivatives()
        matrix[0, 0] = value - d_rate_xe
        matrix[0, 1:3] = -d_rate_real
        matrix[1:, 1:] = self.native_matrix_s_inv
        return matrix

    def shifted_ijacobian_action(self, direction: Sequence[float], *, shift: float) -> np.ndarray:
        vector = np.asarray(direction, dtype=float)
        if vector.shape != (self.layout.local_size,) or not np.all(np.isfinite(vector)):
            raise ValueError("direction has invalid shape or values")
        return self.shifted_ijacobian(shift) @ vector

    def central_difference_shifted_ijacobian_error(
        self,
        state_vector: Sequence[float],
        state_derivative: Sequence[float],
        *,
        direction: Sequence[float],
        shift: float,
        step: float = 1.0e-7,
    ) -> float:
        state = np.asarray(state_vector, dtype=float)
        derivative = np.asarray(state_derivative, dtype=float)
        vector = np.asarray(direction, dtype=float)
        if step <= 0.0 or not math.isfinite(step):
            raise ValueError("step must be positive and finite")
        plus = self.residual(state + step * vector, derivative + step * shift * vector)
        minus = self.residual(state - step * vector, derivative - step * shift * vector)
        finite = (plus - minus) / (2.0 * step)
        analytic = self.shifted_ijacobian_action(vector, shift=shift)
        return float(
            np.max(np.abs(finite - analytic))
            / max(float(np.max(np.abs(finite))), float(np.max(np.abs(analytic))), 1.0e-300)
        )

    def scaled_residual(
        self,
        residual: Sequence[float],
        state_vector: Sequence[float],
        state_derivative: Sequence[float],
    ) -> float:
        value = np.asarray(residual, dtype=float)
        state = np.asarray(state_vector, dtype=float)
        derivative = np.asarray(state_derivative, dtype=float)
        if value.shape != (self.layout.local_size,) or state.shape != value.shape or derivative.shape != value.shape:
            raise ValueError("scaled-residual inputs have invalid shape")
        rate = self.electron_rate_per_lna(state[0], state[1:3])
        electron_scale = max(abs(derivative[0]), abs(rate), 1.0e-300)
        native_action = self.native_matrix_s_inv @ state[1:]
        native_scale = max(
            float(np.max(np.abs(native_action))),
            float(np.max(np.abs(self.native_rhs_s_inv))),
            1.0e-300,
        )
        return max(abs(float(value[0])) / electron_scale, float(np.max(np.abs(value[1:]))) / native_scale)

    def frozen_coefficient_backward_euler_step(
        self,
        old_state_vector: Sequence[float],
        *,
        delta_lna: float,
    ) -> FrozenCoefficientBackwardEulerResult:
        old = np.asarray(old_state_vector, dtype=float)
        deta = float(delta_lna)
        if old.shape != (self.layout.local_size,) or not np.all(np.isfinite(old)):
            raise ValueError("old state has invalid shape or values")
        if not math.isfinite(deta) or deta <= 0.0:
            raise ValueError("delta_lna must be positive and finite")
        native = np.array(self.steady_native_solution, copy=True)
        d_rate_xe, _ = self._electron_rate_derivatives()
        intercept = self.electron_rate_per_lna(0.0, native[:2])
        denominator = 1.0 / deta - d_rate_xe
        if denominator <= 0.0:
            raise RuntimeError("frozen electron backward-Euler denominator is nonpositive")
        xe_new = (old[0] / deta + intercept) / denominator
        new = np.concatenate((np.asarray([xe_new]), native))
        derivative = np.zeros_like(new)
        derivative[0] = (new[0] - old[0]) / deta
        residual = self.residual(new, derivative)
        backward = self.scaled_residual(residual, new, derivative)
        native_action = self.native_matrix_s_inv @ native
        native_scale = max(
            float(np.max(np.abs(native_action))),
            float(np.max(np.abs(self.native_rhs_s_inv))),
            1.0e-300,
        )
        algebraic = float(np.max(np.abs(residual[1:])) / native_scale)
        equilibrium = np.asarray([1.0, 3.0]) * self.source_snapshot.x1s * math.exp(
            -LYMAN_ALPHA_ENERGY_EV / self.source_snapshot.TR_eV_rescaled
        )
        physical = native[:2] + equilibrium
        minimum = min(float(xe_new), self.source_snapshot.x1s, float(np.min(physical)))
        return FrozenCoefficientBackwardEulerResult(
            state_vector=new,
            converged=bool(backward < 1.0e-11 and minimum > 0.0),
            backward_error=backward,
            algebraic_residual_relative=algebraic,
            minimum_physical_population=minimum,
        )

    def restart_payload(
        self,
        state_vector: Sequence[float],
        history: CausalRadiationHistoryState,
    ) -> str:
        state = np.asarray(state_vector, dtype=float)
        if state.shape != (self.layout.local_size,) or not np.all(np.isfinite(state)):
            raise ValueError("restart state has invalid shape or values")
        return json.dumps(
            {
                "schema": "PR05B1_SOURCE_IDENTIFIABLE_DAE_RESTART_V1",
                "state_vector": state.tolist(),
                "history": json.loads(history.to_json()),
            },
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )

    def from_restart_payload(self, payload: str) -> tuple[np.ndarray, CausalRadiationHistoryState]:
        data = json.loads(payload)
        if data.get("schema") != "PR05B1_SOURCE_IDENTIFIABLE_DAE_RESTART_V1":
            raise ValueError("unknown PR05B1 restart schema")
        state = np.asarray(data["state_vector"], dtype=float)
        if state.shape != (self.layout.local_size,) or not np.all(np.isfinite(state)):
            raise ValueError("restart state has invalid shape or values")
        history = CausalRadiationHistoryState.from_json(
            json.dumps(data["history"], sort_keys=True, separators=(",", ":"))
        )
        state = np.array(state, copy=True); state.setflags(write=False)
        return state, history
