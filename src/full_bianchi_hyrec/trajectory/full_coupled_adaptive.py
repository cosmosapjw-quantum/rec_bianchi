"""Bounded coupled COM collision plus source-derived frequency transport.

This is the PR-05C2A reference nonlinear block.  It closes the local COM
collision/transport/interface residual in log occupation variables while the
scalar original-HyRec history remains representation-local.  Directional
native feedback that cannot be represented by the scalar history is retained
as an explicit bounded blocker rather than silently averaged.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import time
from typing import Sequence

import numpy as np
from scipy.constants import c, h
from scipy.sparse.linalg import LinearOperator, gmres

from full_bianchi_hyrec.recoil.frequency_liouville import (
    ConservativeFrequencyLiouville,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_release import (
    HarmonicGrid,
    apply_nonlinear_bose_action,
    apply_nonlinear_bose_jvp,
    apply_nonlinear_bose_jvp_batched,
    apply_nonlinear_bose_operator,
    bose_photon_number,
)
from full_bianchi_hyrec.recoil.nonlinear_bose_runtime import (
    CollisionNetwork,
    LineBoundaryConfig,
)




@dataclass(frozen=True)
class FullCouplingIdentifiabilityAudit:
    native_history_angular_rank: int
    minimum_number_momentum_rank: int
    exact_face_trace_rank: int
    required_angular_rank: int
    com_face_trace_source_defined: bool
    p0_face_trace_is_new_closure: bool
    fully_source_derived_coupling_identified: bool
    bounded_no_go: bool


@dataclass(frozen=True)
class CollisionStiffnessAudit:
    spectral_radius_s_inv: float
    macro_dt_s: float
    stiffness_number: float
    near_null_mode_count: int
    requires_block_preconditioner: bool
    unpreconditioned_full_macro_production_claim: bool


def audit_full_coupling_identifiability(
    grid: HarmonicGrid,
) -> FullCouplingIdentifiabilityAudit:
    """Audit whether the locked scalar native history identifies angular flux.

    Original HyRec stores one scalar occupation departure per native frequency
    state, whereas the COM boundary has one value per angular node.  In
    addition, the COM registry stores finite-volume cell averages and no
    source-defined face reconstruction.  A P0 upwind trace is therefore a new
    numerical closure, not a source-identical mapping.
    """

    return FullCouplingIdentifiabilityAudit(
        native_history_angular_rank=1,
        minimum_number_momentum_rank=4,
        exact_face_trace_rank=int(grid.n_angle),
        required_angular_rank=int(grid.n_angle),
        com_face_trace_source_defined=False,
        p0_face_trace_is_new_closure=True,
        fully_source_derived_coupling_identified=False,
        bounded_no_go=bool(grid.n_angle > 1),
    )


def audit_collision_stiffness(
    network: CollisionNetwork,
    *,
    H_s_inv: float,
    canonical_dlna: float,
    null_tolerance_s_inv: float = 1.0e-14,
    preconditioner_threshold: float = 1.0e6,
) -> CollisionStiffnessAudit:
    """Linearize the isotropic Bose collision block at equilibrium.

    The scalar ell=0 block is a conservative lower-dimensional stiffness
    diagnostic.  It does not replace the full anisotropic Jacobian; it answers
    whether an unpreconditioned cosmological macro solve is a defensible
    production claim.
    """

    H = float(H_s_inv)
    dlna = float(canonical_dlna)
    if not math.isfinite(H) or H <= 0.0 or not math.isfinite(dlna) or dlna <= 0.0:
        raise ValueError("H_s_inv and canonical_dlna must be positive and finite")
    grid = HarmonicGrid.from_directions(
        np.asarray([[0.0, 0.0, 1.0]]), np.asarray([1.0]), ell_max=0
    )
    activity = network.equilibrium_weight / network.mode_measure
    equilibrium = (activity / (1.0 - activity))[:, None]
    size = network.n_state
    jacobian = np.empty((size, size), dtype=float)
    for column in range(size):
        direction = np.zeros((size, 1), dtype=float)
        direction[column, 0] = 1.0
        jacobian[:, column] = apply_nonlinear_bose_jvp(
            equilibrium,
            direction,
            mode_measure=network.mode_measure,
            equilibrium_weight=network.equilibrium_weight,
            pair_moments=network.pair_moments,
            same_cell_rates=network.same_cell_rates,
            grid=grid,
        ).occupation_action_jvp[:, 0]
    eigenvalues = np.linalg.eigvals(jacobian)
    magnitudes = np.abs(eigenvalues)
    radius = float(np.max(magnitudes, initial=0.0))
    near_null = int(np.count_nonzero(magnitudes <= float(null_tolerance_s_inv)))
    macro_dt = dlna / H
    stiffness = radius * macro_dt
    requires = bool(stiffness > float(preconditioner_threshold))
    return CollisionStiffnessAudit(
        spectral_radius_s_inv=radius,
        macro_dt_s=macro_dt,
        stiffness_number=stiffness,
        near_null_mode_count=near_null,
        requires_block_preconditioner=requires,
        unpreconditioned_full_macro_production_claim=not requires,
    )


@dataclass(frozen=True)
class ThermodynamicGridConsistencyAudit:
    locked_doppler_width_Hz: float
    source_doppler_width_Hz: float
    mode_measure_relative_residual: float
    outer_face_frequency_relative_mismatch: float
    source_conditioned_dynamic_measure_identified: bool
    requires_network_recompilation: bool
    requires_explicit_frequency_remap: bool
    bounded_no_go: bool


def audit_thermodynamic_grid_consistency(
    network: CollisionNetwork,
    *,
    source_line: LineBoundaryConfig,
    identification_tolerance: float = 2.0e-8,
) -> ThermodynamicGridConsistencyAudit:
    """Audit whether the frozen COM measure matches a source-temperature grid.

    The v0.50 COM network carries a fixed finite-volume mode measure.  Changing
    the Doppler width changes the physical frequency measure represented by the
    same dimensionless ``x`` cells.  A source-conditioned trajectory therefore
    needs an explicit dynamic measure/kernel adapter or a recompiled network;
    conservation on the frozen grid alone does not establish physical parity.
    """

    tolerance = float(identification_tolerance)
    if not math.isfinite(tolerance) or tolerance < 0.0:
        raise ValueError("identification_tolerance must be finite and nonnegative")
    locked = ConservativeFrequencyLiouville.from_network(network)
    intervals = np.asarray(network.state_intervals, dtype=float)
    order = np.argsort(intervals[:, 0], kind="stable")
    sorted_intervals = intervals[order]
    faces = np.concatenate(([sorted_intervals[0, 0]], sorted_intervals[:, 1]))
    source_frequency = (
        source_line.nu_abs_Hz + faces * source_line.Doppler_width_Hz
    )
    source_mode = (
        8.0
        * math.pi
        * (source_frequency[1:] ** 3 - source_frequency[:-1] ** 3)
        / (3.0 * c**3)
    )
    locked_mode = np.asarray(network.mode_measure, dtype=float)[order]
    residual = float(np.max(np.abs(source_mode - locked_mode) / locked_mode))
    locked_faces = np.asarray(locked.face_frequency_Hz, dtype=float)
    outer_mismatch = float(
        np.max(
            np.abs(
                np.asarray([source_frequency[0], source_frequency[-1]])
                - np.asarray([locked_faces[0], locked_faces[-1]])
            )
            / np.asarray([locked_faces[0], locked_faces[-1]])
        )
    )
    identified = bool(residual <= tolerance and outer_mismatch <= tolerance)
    return ThermodynamicGridConsistencyAudit(
        locked_doppler_width_Hz=float(locked.reference_line.Doppler_width_Hz),
        source_doppler_width_Hz=float(source_line.Doppler_width_Hz),
        mode_measure_relative_residual=residual,
        outer_face_frequency_relative_mismatch=outer_mismatch,
        source_conditioned_dynamic_measure_identified=identified,
        requires_network_recompilation=not identified,
        requires_explicit_frequency_remap=not identified,
        bounded_no_go=not identified,
    )


@dataclass(frozen=True)
class CoupledResidualMetrics:
    net_scaled_residual: float
    gross_backward_error: float
    number_relative_residual: float
    net_scale: float
    gross_scale: float


@dataclass(frozen=True)
class CoupledCollisionTransportStepResult:
    occupation: np.ndarray
    converged: bool
    convergence_basis: str
    linear_solver: str
    preconditioner: str
    newton_iterations: int
    total_gmres_iterations: int
    dense_jacobian_assemblies: int
    residual_relative: float
    net_scaled_residual: float
    gross_backward_error: float
    used_roundoff_floor_fallback: bool
    jacobian_assembly_elapsed_s: float
    linear_solve_elapsed_s: float
    minimum_occupation: float
    global_number_residual_m3: float
    global_number_relative_residual: float
    energy_identity_residual_J_m3: float
    energy_identity_relative_residual: float
    interface_atom_source_J_m3: float
    collision_four_force_residual: float
    collision_entropy_production: float
    interface_number_change_m3: float
    exact_interface_energy_change_J_m3: float
    cosmological_redshift_work_J_m3: float


@dataclass(frozen=True)
class CoupledCollisionTransportProblem:
    network: CollisionNetwork
    grid: HarmonicGrid
    transport: ConservativeFrequencyLiouville
    face_speeds_x_s_inv: np.ndarray
    native_red_occupation: np.ndarray | Sequence[float] | float
    native_blue_occupation: np.ndarray | Sequence[float] | float
    dt_s: float

    def __post_init__(self) -> None:
        if self.transport.network is not self.network:
            # Identity is intentional: one immutable network owns mode measures
            # for both collision and transport.
            raise ValueError("transport and collision must share one network instance")
        speeds = np.asarray(self.face_speeds_x_s_inv, dtype=float)
        if speeds.shape != (self.network.n_state + 1, self.grid.n_angle):
            raise ValueError("face_speeds_x_s_inv shape mismatch")
        if not np.all(np.isfinite(speeds)):
            raise ValueError("face speeds must be finite")
        speeds = np.array(speeds, copy=True); speeds.setflags(write=False)
        object.__setattr__(self, "face_speeds_x_s_inv", speeds)
        dt = float(self.dt_s)
        if not math.isfinite(dt) or dt <= 0.0:
            raise ValueError("dt_s must be positive and finite")
        object.__setattr__(self, "dt_s", dt)

    @property
    def shape(self) -> tuple[int, int]:
        return self.network.n_state, self.grid.n_angle

    def _transport(self, occupation: np.ndarray):
        return self.transport.evaluate(
            occupation,
            face_speeds_x_s_inv=self.face_speeds_x_s_inv,
            native_red_occupation=self.native_red_occupation,
            native_blue_occupation=self.native_blue_occupation,
            grid=self.grid,
        )

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

    def _collision_action(self, occupation: np.ndarray) -> np.ndarray:
        return apply_nonlinear_bose_action(
            occupation,
            mode_measure=self.network.mode_measure,
            equilibrium_weight=self.network.equilibrium_weight,
            pair_moments=self.network.pair_moments,
            same_cell_rates=self.network.same_cell_rates,
            grid=self.grid,
        )

    def _approximate_loss_rate_s_inv(self) -> np.ndarray:
        """Positive diagonal loss used only as a Newton--Krylov preconditioner."""

        pair_loss = np.sum(self.network.pair_moments[0], axis=1) / self.network.equilibrium_weight
        same_loss = np.maximum(-self.network.same_cell_rates[0], 0.0)
        collision_loss = pair_loss + same_loss

        order = self.transport.sorted_indices
        mode = self.network.mode_measure[order]
        speeds = self.face_speeds_x_s_inv
        density = self.transport.face_mode_density_m3
        transport_sorted = (
            np.maximum(-speeds[:-1], 0.0) * density[:-1, None]
            + np.maximum(speeds[1:], 0.0) * density[1:, None]
        ) / mode[:, None]
        transport_loss = np.empty_like(transport_sorted)
        transport_loss[order] = transport_sorted
        return collision_loss[:, None] + transport_loss

    def _number_closure_metrics(
        self,
        old_occupation: np.ndarray,
        new_occupation: np.ndarray,
        transport_result,
    ) -> tuple[float, float]:
        weights = np.asarray(self.grid.weights, dtype=np.longdouble)
        measure = np.asarray(self.network.mode_measure, dtype=np.longdouble)
        old = np.asarray(old_occupation, dtype=np.longdouble)
        new = np.asarray(new_occupation, dtype=np.longdouble)
        before = np.sum(measure[:, None] * old * weights[None, :])
        after = np.sum(measure[:, None] * new * weights[None, :])
        native_rate = np.sum(
            np.asarray(transport_result.native_number_action_m3_s, dtype=np.longdouble)
            * weights
        )
        interface_change = -np.longdouble(self.dt_s) * native_rate
        residual = after - before - interface_change
        scale = max(
            abs(float(before)),
            abs(float(after)),
            abs(float(interface_change)),
            1.0e-300,
        )
        return float(residual), abs(float(residual)) / scale

    def residual_metrics(
        self,
        log_occupation: np.ndarray,
        old_occupation: np.ndarray,
    ) -> CoupledResidualMetrics:
        old = np.asarray(old_occupation, dtype=float)
        u = np.asarray(log_occupation, dtype=float)
        if old.shape != self.shape or u.shape != self.shape:
            raise ValueError("occupation shape mismatch")
        if np.any(old <= 0.0) or not np.all(np.isfinite(old)) or not np.all(np.isfinite(u)):
            raise ValueError("old occupation must be positive and log state finite")
        if np.max(u) > 700.0 or np.min(u) < -745.0:
            raise FloatingPointError("log occupation outside finite exponential range")
        occupation = np.exp(u)
        collision = self._collision_action(occupation)
        transport = self._transport(occupation)
        collision_increment = self.dt_s * collision
        transport_increment = self.dt_s * transport.occupation_action
        residual = occupation - old - collision_increment - transport_increment
        residual_max = float(np.max(np.abs(residual)))
        net_scale = max(
            float(np.max(np.abs(old))),
            float(np.max(np.abs(occupation))),
            1.0e-300,
        )
        gross_scale = max(
            net_scale,
            float(np.max(np.abs(collision_increment))),
            float(np.max(np.abs(transport_increment))),
            1.0e-300,
        )
        _number_residual, number_relative = self._number_closure_metrics(
            old, occupation, transport
        )
        return CoupledResidualMetrics(
            net_scaled_residual=residual_max / net_scale,
            gross_backward_error=residual_max / gross_scale,
            number_relative_residual=number_relative,
            net_scale=net_scale,
            gross_scale=gross_scale,
        )

    def residual(self, log_occupation: np.ndarray, old_occupation: np.ndarray) -> np.ndarray:
        old = np.asarray(old_occupation, dtype=float)
        u = np.asarray(log_occupation, dtype=float)
        if old.shape != self.shape or u.shape != self.shape:
            raise ValueError("occupation shape mismatch")
        if np.any(old <= 0.0) or not np.all(np.isfinite(old)) or not np.all(np.isfinite(u)):
            raise ValueError("old occupation must be positive and log state finite")
        if np.max(u) > 700.0 or np.min(u) < -745.0:
            raise FloatingPointError("log occupation outside finite exponential range")
        f = np.exp(u)
        collision_action = self._collision_action(f)
        transport = self._transport(f)
        return f - old - self.dt_s * (
            collision_action + transport.occupation_action
        )

    def residual_jvp(
        self,
        log_occupation: np.ndarray,
        log_direction: np.ndarray,
    ) -> np.ndarray:
        u = np.asarray(log_occupation, dtype=float)
        du = np.asarray(log_direction, dtype=float)
        if u.shape != self.shape or du.shape != self.shape:
            raise ValueError("log direction shape mismatch")
        f = np.exp(u)
        df = f * du
        collision = apply_nonlinear_bose_jvp(
            f,
            df,
            mode_measure=self.network.mode_measure,
            equilibrium_weight=self.network.equilibrium_weight,
            pair_moments=self.network.pair_moments,
            same_cell_rates=self.network.same_cell_rates,
            grid=self.grid,
        ).occupation_action_jvp
        transport = self.transport.jvp(
            f,
            df,
            face_speeds_x_s_inv=self.face_speeds_x_s_inv,
            grid=self.grid,
        ).occupation_action_jvp
        return df - self.dt_s * (collision + transport)

    def residual_jvp_batched(
        self,
        log_occupation: np.ndarray,
        log_directions: np.ndarray,
    ) -> np.ndarray:
        """Apply the shifted residual JVP to a batch of log directions."""

        u = np.asarray(log_occupation, dtype=float)
        directions = np.asarray(log_directions, dtype=float)
        if directions.ndim == 2:
            directions = directions[None, ...]
        if u.shape != self.shape or directions.ndim != 3 or directions.shape[1:] != self.shape:
            raise ValueError("batched log direction shape mismatch")
        f = np.exp(u)
        df = f[None, :, :] * directions
        collision = apply_nonlinear_bose_jvp_batched(
            f,
            df,
            mode_measure=self.network.mode_measure,
            equilibrium_weight=self.network.equilibrium_weight,
            pair_moments=self.network.pair_moments,
            same_cell_rates=self.network.same_cell_rates,
            grid=self.grid,
        ).occupation_action_jvp
        transport = np.stack(
            [
                self.transport.jvp(
                    f,
                    item,
                    face_speeds_x_s_inv=self.face_speeds_x_s_inv,
                    grid=self.grid,
                ).occupation_action_jvp
                for item in df
            ]
        )
        return df - self.dt_s * (collision + transport)

    def dense_jacobian(
        self,
        log_occupation: np.ndarray,
        *,
        method: str = "batched",
        chunk_size: int = 64,
    ) -> np.ndarray:
        """Assemble a dense residual Jacobian for bounded audit/hot lanes."""

        u = np.asarray(log_occupation, dtype=float)
        if u.shape != self.shape:
            raise ValueError("log occupation shape mismatch")
        size = u.size
        matrix = np.empty((size, size), dtype=float)
        if method == "scalar_columns":
            for column in range(size):
                direction = np.zeros(self.shape, dtype=float)
                direction.ravel()[column] = 1.0
                matrix[:, column] = self.residual_jvp(u, direction).ravel()
            return matrix
        if method != "batched":
            raise ValueError("method must be 'scalar_columns' or 'batched'")
        if int(chunk_size) <= 0:
            raise ValueError("chunk_size must be positive")
        chunk = int(chunk_size)
        for start in range(0, size, chunk):
            stop = min(start + chunk, size)
            directions = np.zeros((stop - start, size), dtype=float)
            directions[np.arange(stop - start), np.arange(start, stop)] = 1.0
            result = self.residual_jvp_batched(
                u, directions.reshape((stop - start,) + self.shape)
            )
            matrix[:, start:stop] = result.reshape(stop - start, size).T
        return matrix

    def implicit_step(
        self,
        old_occupation: np.ndarray,
        *,
        nonlinear_rtol: float = 2.0e-10,
        max_newton: int = 14,
        gmres_rtol: float = 2.0e-9,
        gmres_restart: int = 40,
        gmres_maxiter: int = 160,
        linear_solver: str = "gmres",
        dense_chunk_size: int = 64,
    ) -> CoupledCollisionTransportStepResult:
        old = np.asarray(old_occupation, dtype=float)
        if old.shape != self.shape or np.any(old <= 0.0) or not np.all(np.isfinite(old)):
            raise ValueError("old occupation must be finite and strictly positive")
        if linear_solver not in {"gmres", "dense_batched"}:
            raise ValueError("linear_solver must be 'gmres' or 'dense_batched'")
        if int(dense_chunk_size) <= 0:
            raise ValueError("dense_chunk_size must be positive")
        log_f = np.log(old)
        scale = max(float(np.max(np.abs(old))), 1.0e-300)
        total_gmres = 0
        dense_assemblies = 0
        jacobian_elapsed = 0.0
        linear_elapsed = 0.0
        converged = False
        convergence_basis = "none"
        used_roundoff_floor_fallback = False
        residual_relative = math.inf
        newton_index = 0
        for newton_index in range(max_newton + 1):
            residual = self.residual(log_f, old)
            residual_relative = float(np.max(np.abs(residual))) / scale
            if residual_relative <= nonlinear_rtol:
                converged = True
                convergence_basis = "scaled_residual"
                break
            if newton_index == max_newton:
                break
            size = old.size
            if linear_solver == "gmres":
                def matvec(flat):
                    return self.residual_jvp(
                        log_f, np.asarray(flat).reshape(self.shape)
                    ).ravel()

                operator = LinearOperator((size, size), matvec=matvec, dtype=float)
                f = np.exp(log_f)
                diagonal = f * (
                    1.0 + self.dt_s * self._approximate_loss_rate_s_inv()
                )
                preconditioner = LinearOperator(
                    (size, size),
                    matvec=lambda flat: np.asarray(flat, dtype=float)
                    / np.maximum(diagonal.ravel(), 1.0e-300),
                    dtype=float,
                )
                counter = {"iterations": 0}

                def callback(_):
                    counter["iterations"] += 1

                started = time.perf_counter()
                step, info = gmres(
                    operator,
                    -residual.ravel(),
                    M=preconditioner,
                    rtol=gmres_rtol,
                    atol=0.0,
                    restart=gmres_restart,
                    maxiter=gmres_maxiter,
                    callback=callback,
                    callback_type="pr_norm",
                )
                linear_elapsed += time.perf_counter() - started
                total_gmres += counter["iterations"]
                if info != 0 or not np.all(np.isfinite(step)):
                    break
            else:
                started = time.perf_counter()
                jacobian = self.dense_jacobian(
                    log_f, method="batched", chunk_size=int(dense_chunk_size)
                )
                jacobian_elapsed += time.perf_counter() - started
                dense_assemblies += 1
                started = time.perf_counter()
                try:
                    step = np.linalg.solve(jacobian, -residual.ravel())
                except np.linalg.LinAlgError:
                    break
                linear_elapsed += time.perf_counter() - started
                if not np.all(np.isfinite(step)):
                    break
            step = step.reshape(self.shape)
            base = float(np.max(np.abs(residual)))
            accepted = False
            damping = 1.0
            for _ in range(24):
                candidate = log_f + damping * step
                if np.max(candidate) < 700.0 and np.min(candidate) > -745.0:
                    candidate_residual = self.residual(candidate, old)
                    if float(np.max(np.abs(candidate_residual))) < base:
                        log_f = candidate
                        accepted = True
                        break
                damping *= 0.5
            if not accepted:
                stalled = self.residual_metrics(log_f, old)
                if (
                    stalled.gross_backward_error <= nonlinear_rtol
                    and stalled.number_relative_residual <= nonlinear_rtol
                ):
                    converged = True
                    convergence_basis = "gross_backward_error"
                    used_roundoff_floor_fallback = True
                break

        final_metrics = self.residual_metrics(log_f, old)
        if (
            not converged
            and final_metrics.gross_backward_error <= nonlinear_rtol
            and final_metrics.number_relative_residual <= nonlinear_rtol
        ):
            converged = True
            convergence_basis = "gross_backward_error"
            used_roundoff_floor_fallback = True
        final = np.exp(log_f)
        collision = self._collision(final)
        transport = self._transport(final)
        number_before = bose_photon_number(
            old, mode_measure=self.network.mode_measure, grid=self.grid
        )
        number_after = bose_photon_number(
            final, mode_measure=self.network.mode_measure, grid=self.grid
        )
        native_number_rate = float(
            np.sum(transport.native_number_action_m3_s * self.grid.weights)
        )
        com_interface_number_rate = -native_number_rate
        global_number_residual, global_number_relative = self._number_closure_metrics(
            old, final, transport
        )

        cell_energy_before = float(
            np.sum(
                h
                * self.transport.cell_centroid_frequency_Hz[:, None]
                * old[self.transport.sorted_indices]
                * self.network.mode_measure[self.transport.sorted_indices, None]
                * self.grid.weights[None, :]
            )
        )
        cell_energy_after = float(
            np.sum(
                h
                * self.transport.cell_centroid_frequency_Hz[:, None]
                * final[self.transport.sorted_indices]
                * self.network.mode_measure[self.transport.sorted_indices, None]
                * self.grid.weights[None, :]
            )
        )
        collision_energy_rate = c * float(collision.Q_gamma[0])
        expected_energy_change = self.dt_s * (
            transport.com_energy_action_W_m3 + collision_energy_rate
        )
        energy_residual = cell_energy_after - cell_energy_before - expected_energy_change
        energy_scale = max(
            abs(cell_energy_before),
            abs(cell_energy_after),
            abs(expected_energy_change),
            1.0e-300,
        )
        energy_relative = abs(energy_residual) / energy_scale
        return CoupledCollisionTransportStepResult(
            occupation=np.array(final, copy=True),
            converged=converged,
            convergence_basis=convergence_basis,
            linear_solver=linear_solver,
            preconditioner="diagonal" if linear_solver == "gmres" else "none",
            newton_iterations=newton_index,
            total_gmres_iterations=total_gmres,
            dense_jacobian_assemblies=dense_assemblies,
            residual_relative=final_metrics.net_scaled_residual,
            net_scaled_residual=final_metrics.net_scaled_residual,
            gross_backward_error=final_metrics.gross_backward_error,
            used_roundoff_floor_fallback=used_roundoff_floor_fallback,
            jacobian_assembly_elapsed_s=jacobian_elapsed,
            linear_solve_elapsed_s=linear_elapsed,
            minimum_occupation=float(np.min(final)),
            global_number_residual_m3=float(global_number_residual),
            global_number_relative_residual=float(global_number_relative),
            energy_identity_residual_J_m3=float(energy_residual),
            energy_identity_relative_residual=float(energy_relative),
            interface_atom_source_J_m3=0.0,
            collision_four_force_residual=float(np.linalg.norm(collision.Q_gamma + collision.Q_atom)),
            collision_entropy_production=float(collision.entropy_production),
            interface_number_change_m3=float(self.dt_s * com_interface_number_rate),
            exact_interface_energy_change_J_m3=float(
                self.dt_s * transport.exact_interface_energy_action_W_m3
            ),
            cosmological_redshift_work_J_m3=float(
                self.dt_s
                * (
                    transport.outer_centroid_correction_W_m3
                    + transport.cosmological_redshift_work_W_m3
                )
            ),
        )


__all__ = [
    "CollisionStiffnessAudit",
    "CoupledCollisionTransportProblem",
    "CoupledCollisionTransportStepResult",
    "CoupledResidualMetrics",
    "FullCouplingIdentifiabilityAudit",
    "ThermodynamicGridConsistencyAudit",
    "audit_collision_stiffness",
    "audit_full_coupling_identifiability",
    "audit_thermodynamic_grid_consistency",
]
