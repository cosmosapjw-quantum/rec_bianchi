"""Bounded source-native continuation of the R3G FULL H+He start history.

The continuation begins at the accepted U2 node j=8 (global HyRec index
18231).  It consumes the eight accepted photon columns and derivative tails
from that reviewed checkpoint.  This module is deliberately not an execution
receipt: a caller must supply the reviewed checkpoint identity and a C oracle
before a science run is admitted.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Callable

import numpy as np

from full_bianchi_hyrec.trajectory.causal_virtual_redshift import (
    SOURCE_DLNA, causal_incoming_from_accepted_histories,
)
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import (
    NVIRT, _canonical_twophoton_table, complete_original_full_atomic,
    populate_original_full_atomic,
)
from full_bianchi_hyrec.trajectory.primordial_2012_helium import (
    HyRec2012Cosmology, helium_rhs, saha_xH1s, tm_steady_K,
)
from full_bianchi_hyrec.trajectory.primordial_2012_full_start import (
    FullStartHistory,
)

U2_ACCEPTED_STEPS = 8
U2_START_IZ = 18223
U3_START_IZ = U2_START_IZ + U2_ACCEPTED_STEPS
MAX_EXTRA_ACCEPTED = 2048
MAX_HISTORY_COLUMNS = U2_ACCEPTED_STEPS + MAX_EXTRA_ACCEPTED
MAX_FULL_EVALUATIONS = 8192
XHEII_MIN = 1.0e-6
DXHII_MAX = 3.0e-4
DLNT_MAX = 5.0e-4
NVIRTUAL = 311
NLYMAN = 3
REVIEWED_U2_PRODUCER_SHA256 = "22e68ae6eef25c24ce7fb79b520edd5f953afa0fb74cb0b87da6f4737a655a31"
REVIEWED_U2_RECEIPT_SHA256 = "93d192707a4f0b00f27b2cf85905c412cda32fe94c1ba33a45fce55219ee20e8"
REVIEWED_U2_CHECKPOINT_SHA256 = "6b486c7819388146fcae255cfc66c2b91564af6f12f88e88c9246c25d3f5a528"


@dataclass(frozen=True)
class ContinuationCheckpoint:
    """Validated immutable U2 state needed to resume without resetting history."""

    start: FullStartHistory
    reviewed_u2_sha256: str
    receipt_sha256: str = REVIEWED_U2_RECEIPT_SHA256
    checkpoint_sha256: str = REVIEWED_U2_CHECKPOINT_SHA256

    def __post_init__(self):
        if not re.fullmatch(r"[0-9a-f]{64}", self.reviewed_u2_sha256):
            raise ValueError("reviewed U2 SHA-256 identity is required")
        if self.reviewed_u2_sha256 != REVIEWED_U2_PRODUCER_SHA256:
            raise ValueError("U2 producer SHA does not match independently reviewed identity")
        if self.receipt_sha256 != REVIEWED_U2_RECEIPT_SHA256:
            raise ValueError("U2 review receipt SHA mismatch")
        if self.checkpoint_sha256 != REVIEWED_U2_CHECKPOINT_SHA256:
            raise ValueError("U2 accepted checkpoint SHA mismatch")
        s = self.start
        if len(s.iz) != U2_ACCEPTED_STEPS + 1:
            raise ValueError("U2 checkpoint must contain nodes j=0..8")
        if int(s.iz[0]) != U2_START_IZ or int(s.iz[-1]) != U3_START_IZ:
            raise ValueError("U2 checkpoint does not end at global index 18231")
        if s.virtual_out.shape != (NVIRTUAL, U2_ACCEPTED_STEPS):
            raise ValueError("U2 checkpoint must carry accepted virtual columns 0..7")
        if s.average_virtual.shape != (NVIRTUAL, U2_ACCEPTED_STEPS):
            raise ValueError("U2 checkpoint must carry accepted average columns 0..7")
        if s.lyman_out.shape != (NLYMAN, U2_ACCEPTED_STEPS):
            raise ValueError("U2 checkpoint must carry accepted Lyman columns 0..7")
        if s.hydrogen_rhs_dln_a.shape != (U2_ACCEPTED_STEPS,):
            raise ValueError("U2 hydrogen RHS tail f7/f6 is absent")
        if s.helium_rhs_dln_a.shape != (U2_ACCEPTED_STEPS,):
            raise ValueError("U2 helium RHS tail f7/f6 is absent")
        for a in (s.virtual_out, s.average_virtual, s.lyman_out):
            if not np.all(np.isfinite(a)):
                raise ValueError("U2 accepted photon checkpoint contains nonfinite values")
        if not math.isclose(float(s.xe[-1]),
                            float(s.xHII[-1] + s.xHeII[-1]),
                            rel_tol=0.0, abs_tol=5e-13):
            raise ValueError("U2 endpoint electron ledger does not close")
        if not math.isclose(SOURCE_DLNA, 8.49e-5, rel_tol=0.0, abs_tol=0.0):
            raise ValueError("native source clock changed")

    @property
    def endpoint(self) -> dict[str, float | int | bool]:
        s = self.start
        return {
            "iz": int(s.iz[-1]), "z": float(s.z[-1]),
            "xH1s": float(s.xH1s[-1]), "xHII": float(s.xHII[-1]),
            "xHeII": float(s.xHeII[-1]), "xe": float(s.xe[-1]),
            "Tm_K": float(s.Tm_K[-1]), "post_saha": bool(s.post_saha[-1]),
            "hydrogen_rhs_f7": float(s.hydrogen_rhs_dln_a[-1]),
            "hydrogen_rhs_f6": float(s.hydrogen_rhs_dln_a[-2]),
            "helium_rhs_f7": float(s.helium_rhs_dln_a[-1]),
            "helium_rhs_f6": float(s.helium_rhs_dln_a[-2]),
        }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_reviewed_u2_checkpoint(
    checkpoint_npz: Path,
    review_receipt: Path,
    producer_source: Path,
) -> ContinuationCheckpoint:
    """Load the exact U2 artifacts reviewed by Astra; reject any byte drift."""
    checkpoint_npz = Path(checkpoint_npz)
    review_receipt = Path(review_receipt)
    producer_source = Path(producer_source)
    actual = (_sha256(checkpoint_npz), _sha256(review_receipt), _sha256(producer_source))
    expected = (REVIEWED_U2_CHECKPOINT_SHA256, REVIEWED_U2_RECEIPT_SHA256,
                REVIEWED_U2_PRODUCER_SHA256)
    if actual != expected:
        raise ValueError(f"U2_REVIEWED_ARTIFACT_IDENTITY_MISMATCH:{actual!r}")
    report = json.loads(review_receipt.read_text())
    if report.get("status") != "PASS":
        raise ValueError("U2 review receipt is not PASS")
    with np.load(checkpoint_npz, allow_pickle=False) as arrays:
        expected_fields = {
            "iz", "z", "xH1s", "xHII", "xHeII", "xe", "Tm_K",
            "helium_rhs_dln_a", "hydrogen_rhs_dln_a", "post_saha",
            "virtual_out", "average_virtual", "lyman_out", "matrix_residual",
        }
        if set(arrays.files) != expected_fields:
            raise ValueError("U2 checkpoint NPZ field set mismatch")
        values = {key: np.array(arrays[key], copy=True) for key in expected_fields}
    history = FullStartHistory(**values, full_evaluations=int(report["python_full_evaluations"]))
    return ContinuationCheckpoint(
        history, REVIEWED_U2_PRODUCER_SHA256,
        REVIEWED_U2_RECEIPT_SHA256, REVIEWED_U2_CHECKPOINT_SHA256,
    )


@dataclass(frozen=True)
class ContinuationHistory:
    """U2 checkpoint plus newly accepted U3 rows, with fixed-cap storage."""

    iz: np.ndarray
    z: np.ndarray
    xH1s: np.ndarray
    xHII: np.ndarray
    xHeII: np.ndarray
    xe: np.ndarray
    Tm_K: np.ndarray
    post_saha: np.ndarray
    source_branch_h_only: np.ndarray
    helium_cutoff_crossed: np.ndarray
    hydrogen_post_saha_off_crossed: np.ndarray
    hydrogen_rhs_dln_a: np.ndarray
    helium_rhs_dln_a: np.ndarray
    virtual_out: np.ndarray
    average_virtual: np.ndarray
    lyman_out: np.ndarray
    matrix_residual: np.ndarray
    accepted_extra: int
    full_evaluations: int
    event: str
    branch_steps_after_event: int
    status: str
    reviewed_u2_sha256: str
    common_input_evaluations: int
    common_input_sample_columns: tuple[int, ...]
    common_input_max_rhs_scaled: float
    common_input_max_virtual_ratio: float
    common_input_max_average_ratio: float
    common_input_max_lyman_ratio: float
    endpoint_diagnostic_column: int | None = None
    endpoint_diagnostic_rhs: float | None = None
    endpoint_diagnostic_matrix_residual: float | None = None

    def __post_init__(self):
        if not (0 <= self.accepted_extra <= MAX_EXTRA_ACCEPTED):
            raise ValueError("U3 accepted-step cap exceeded")
        cols = U2_ACCEPTED_STEPS + self.accepted_extra
        if cols > MAX_HISTORY_COLUMNS:
            raise ValueError("photon-history column cap exceeded")
        for name in ("iz", "z", "xH1s", "xHII", "xHeII", "xe", "Tm_K", "post_saha",
                     "source_branch_h_only", "helium_cutoff_crossed",
                     "hydrogen_post_saha_off_crossed"):
            a = np.asarray(getattr(self, name))
            if a.shape != (cols + 1,):
                raise ValueError(f"{name} must have {cols+1} endpoint-inclusive rows")
            if name != "post_saha" and not np.all(np.isfinite(a)):
                raise ValueError(f"nonfinite {name}")
            a = np.array(a, copy=True); a.setflags(write=False)
            object.__setattr__(self, name, a)
        for name in ("hydrogen_rhs_dln_a", "helium_rhs_dln_a", "matrix_residual"):
            a = np.asarray(getattr(self, name), dtype=float)
            if a.shape != (cols,) or not np.all(np.isfinite(a)):
                raise ValueError(f"{name} must have one finite value per committed column")
            a = np.array(a, copy=True); a.setflags(write=False)
            object.__setattr__(self, name, a)
        for name, shape in (("virtual_out", (NVIRTUAL, cols)),
                            ("average_virtual", (NVIRTUAL, cols)),
                            ("lyman_out", (NLYMAN, cols))):
            a = np.asarray(getattr(self, name), dtype=float)
            if a.shape != shape or not np.all(np.isfinite(a)):
                raise ValueError(f"invalid accepted {name} shape or values")
            a = np.array(a, copy=True); a.setflags(write=False)
            object.__setattr__(self, name, a)
        if self.full_evaluations > MAX_FULL_EVALUATIONS:
            raise ValueError("Python FULL evaluation cap exceeded")
        if not 0 <= self.common_input_evaluations <= 64:
            raise ValueError("common-input C sample cap exceeded")
        if self.common_input_evaluations != len(self.common_input_sample_columns):
            raise ValueError("common-input sample column ledger mismatch")
        if len(set(self.common_input_sample_columns)) != len(self.common_input_sample_columns):
            raise ValueError("duplicate common-input sample column")
        if not all(math.isfinite(float(v)) for v in (
                self.common_input_max_rhs_scaled, self.common_input_max_virtual_ratio,
                self.common_input_max_average_ratio, self.common_input_max_lyman_ratio)):
            raise ValueError("common-input maxima must be finite")
        allowed_status = {"EVENT_TWO_STEPS_COMPLETE", "BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED",
                          "HOLD_NEXT_STAGE_REQUIRED:THERMAL_BOUNDARY",
                          "HOLD_NEXT_STAGE_REQUIRED:RT_TABLE_BOUNDARY",
                          "HOLD_NEXT_STAGE_REQUIRED:EVENT_TWO_STEPS_INCOMPLETE",
                          "HOLD_NEXT_STAGE_REQUIRED:FULL_EVALUATION_CAP",
                          "HOLD_NEXT_STAGE_REQUIRED:COMMON_INPUT_SAMPLE_CAP"}
        if self.status not in allowed_status:
            raise ValueError("unknown bounded continuation result status")
        if self.event not in {"NONE", "HELIUM_CUTOFF", "HYDROGEN_POST_SAHA_OFF",
                              "HELIUM_CUTOFF+HYDROGEN_POST_SAHA_OFF"}:
            raise ValueError("unknown source event")
        if self.event == "NONE":
            if self.branch_steps_after_event != 0:
                raise ValueError("no-event interval has event branch steps")
            if self.status not in {"BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED",
                                   "HOLD_NEXT_STAGE_REQUIRED:THERMAL_BOUNDARY",
                                   "HOLD_NEXT_STAGE_REQUIRED:RT_TABLE_BOUNDARY"}:
                raise ValueError("no-event interval cannot claim event completion")
        elif self.status == "EVENT_TWO_STEPS_COMPLETE" and self.branch_steps_after_event != 2:
            raise ValueError("branch event requires exactly two accepted steps afterward")
        if self.event != "NONE" and self.status == "EVENT_TWO_STEPS_COMPLETE":
            if not (bool(np.any(self.helium_cutoff_crossed)) or
                    bool(np.any(self.hydrogen_post_saha_off_crossed))):
                raise ValueError("event completion lacks an accepted crossing flag")
            if self.endpoint_diagnostic_column is None:
                raise ValueError("event completion requires the uncommitted j_event+2 diagnostic")
            endpoint_sample_column = self.endpoint_diagnostic_column - U2_START_IZ
            if endpoint_sample_column not in self.common_input_sample_columns:
                raise ValueError("endpoint diagnostic lacks its common-input C oracle sample")
            crossing_rows = np.flatnonzero(self.helium_cutoff_crossed |
                                           self.hydrogen_post_saha_off_crossed)
            if not len(crossing_rows) or crossing_rows[0] + 2 >= len(self.iz):
                raise ValueError("event endpoint is missing two accepted post-event steps")
            if int(self.iz[crossing_rows[0] + 2]) != self.endpoint_diagnostic_column:
                raise ValueError("endpoint diagnostic is not at j_event+2")
        if not np.all(np.isfinite(self.z)) or np.any(np.diff(self.z) >= 0):
            raise ValueError("redshift grid must be finite and strictly decreasing")
        if np.any(np.diff(self.iz) != 1):
            raise ValueError("source indices must be contiguous")
        if self.accepted_extra != cols - U2_ACCEPTED_STEPS:
            raise ValueError("accepted continuation count disagrees with column ledger")
        if self.endpoint_diagnostic_column is None:
            if self.endpoint_diagnostic_rhs is not None or self.endpoint_diagnostic_matrix_residual is not None:
                raise ValueError("partial endpoint diagnostic metadata")
        else:
            if self.endpoint_diagnostic_column != int(self.iz[-1]):
                raise ValueError("endpoint diagnostic must be at the last accepted node")
            if (self.endpoint_diagnostic_rhs is None or
                    self.endpoint_diagnostic_matrix_residual is None or
                    not math.isfinite(self.endpoint_diagnostic_rhs) or
                    not math.isfinite(self.endpoint_diagnostic_matrix_residual)):
                raise ValueError("endpoint diagnostic values must be finite")


def _validate_live_limits(max_extra_accepted: int, max_full_evaluations: int):
    if not isinstance(max_extra_accepted, int) or not 1 <= max_extra_accepted <= MAX_EXTRA_ACCEPTED:
        raise ValueError("max_extra_accepted must be in [1,2048]")
    if not isinstance(max_full_evaluations, int) or not 1 <= max_full_evaluations <= MAX_FULL_EVALUATIONS:
        raise ValueError("max_full_evaluations must be in [1,8192]")


def _hydrogen_saha_helium_coupling(c: HyRec2012Cosmology, xhe: float, z: float) -> float:
    """Source finite difference for d(xH1s,Saha)/d(xHeII), when HeII is present.

    HyRec's perturbation may cross xHeII=0. That negative trial is part of the
    original finite-difference stencil; it is not an accepted species state.
    The C source omits this coupling exactly when xHeII is zero.
    """
    if xhe == 0.0:
        return 0.0
    delta = 0.01 * (c.fHe - xhe)
    if not math.isfinite(delta) or delta == 0.0:
        raise ArithmeticError("POST_SAHA_HELIUM_PROBE_INVALID")
    return (saha_xH1s(c, xhe + delta, z) - saha_xH1s(c, xhe - delta, z)) / (2.0 * delta)


def continue_full_hhe(
    u2_checkpoint: ContinuationCheckpoint,
    c: HyRec2012Cosmology,
    source,
    *,
    common_input_oracle: Callable,
    max_extra_accepted: int = MAX_EXTRA_ACCEPTED,
    max_full_evaluations: int = MAX_FULL_EVALUATIONS,
    rt_limit_relative_index: int | None = None,
    checkpoint_callback: Callable[[dict], None] | None = None,
) -> ContinuationHistory:
    """Continue the independent Python source-native H+He FULL trajectory.

    This is the science execution entry point. It requires a common-input C
    oracle and a reviewed U2 checkpoint. Do not call it until the controller
    has recorded the U2 producer/checkpoint SHA identities and authorized U3.
    It preserves the U2 eight columns, commits only accepted outgoing columns,
    and stops on the first branch event after two accepted steps in the new
    branch. Reaching a thermal/RT boundary first raises HOLD.
    """
    if common_input_oracle is None or not callable(common_input_oracle):
        raise ValueError("independent original-C common-input oracle is required")
    _validate_live_limits(max_extra_accepted, max_full_evaluations)
    s = u2_checkpoint.start
    expected_z = np.asarray([c.redshift(int(i)) for i in s.iz], dtype=float)
    if (not np.all(np.isfinite(expected_z)) or
            not np.allclose(np.asarray(s.z, dtype=float), expected_z, rtol=0.0, atol=2e-12)):
        raise ValueError("U2_CHECKPOINT_SOURCE_REDSHIFT_GRID_MISMATCH")
    table = _canonical_twophoton_table(source.table.archive_path)
    cols_cap = U2_ACCEPTED_STEPS + max_extra_accepted
    nodes_cap = cols_cap + 1
    # Every history block is preallocated exactly once; no append/reallocation.
    iz = np.empty(nodes_cap, dtype=np.int64)
    z = np.empty(nodes_cap); x1 = np.empty(nodes_cap); xh = np.empty(nodes_cap)
    xhe = np.empty(nodes_cap); xe = np.empty(nodes_cap); tm = np.empty(nodes_cap)
    post = np.empty(nodes_cap, dtype=bool)
    branch_h_only = np.empty(nodes_cap, dtype=bool)
    he_crossed = np.zeros(nodes_cap, dtype=bool)
    post_crossed = np.zeros(nodes_cap, dtype=bool)
    h_rhs = np.zeros(cols_cap); he_rhs = np.zeros(cols_cap)
    residual = np.zeros(cols_cap)
    vout = np.full((NVIRTUAL, cols_cap), np.nan)
    avgout = np.full((NVIRTUAL, cols_cap), np.nan)
    lyout = np.full((NLYMAN, cols_cap), np.nan)
    seed_nodes = U2_ACCEPTED_STEPS + 1
    for dst, srcarr in ((iz, s.iz), (z, s.z), (x1, s.xH1s), (xh, s.xHII),
                        (xhe, s.xHeII), (xe, s.xe), (tm, s.Tm_K),
                        (post, s.post_saha)):
        dst[:seed_nodes] = srcarr
    branch_h_only[:seed_nodes] = np.asarray(s.xHeII) <= XHEII_MIN
    vout[:, :U2_ACCEPTED_STEPS] = s.virtual_out
    avgout[:, :U2_ACCEPTED_STEPS] = s.average_virtual
    lyout[:, :U2_ACCEPTED_STEPS] = s.lyman_out
    h_rhs[:U2_ACCEPTED_STEPS] = s.hydrogen_rhs_dln_a
    he_rhs[:U2_ACCEPTED_STEPS] = s.helium_rhs_dln_a
    residual[:U2_ACCEPTED_STEPS] = s.matrix_residual
    accepted = U2_ACCEPTED_STEPS
    full_evals = 0
    event = "NONE"
    event_he_cross = False
    event_post_cross = False
    post_event_steps = 0
    first_event_accepted_col = None
    hold_reason = None
    fixed_sample_columns = {8, 9, 16, 32, 64, 128, 256, 512, 1024, 2048}
    event_sample_columns: set[int] = set()
    sampled_columns: list[int] = []
    common_calls = 0
    common_max_rhs = common_max_v = common_max_a = common_max_l = 0.0
    endpoint_diag_column = None
    endpoint_diag_rhs = None
    endpoint_diag_residual = None

    def checkpoint(phase: str, failure: dict | None = None):
        if checkpoint_callback is None:
            return
        n = accepted
        checkpoint_callback({
            "phase": phase,
            "accepted_extra": n - U2_ACCEPTED_STEPS,
            "global_iz": iz[:n+1].copy(), "z": z[:n+1].copy(),
            "xH1s": x1[:n+1].copy(), "xHII": xh[:n+1].copy(),
            "xHeII": xhe[:n+1].copy(), "xe": xe[:n+1].copy(),
            "Tm_K": tm[:n+1].copy(), "post_saha": post[:n+1].copy(),
            "hydrogen_rhs_dln_a": h_rhs[:n].copy(),
            "helium_rhs_dln_a": he_rhs[:n].copy(),
            "virtual_out": vout[:, :n].copy(),
            "average_virtual": avgout[:, :n].copy(),
            "lyman_out": lyout[:, :n].copy(),
            "matrix_residual": residual[:n].copy(),
            "full_evaluations": full_evals, "event": event,
            "branch_steps_after_event": post_event_steps,
            "source_branch_h_only": branch_h_only[:n+1].copy(),
            "helium_cutoff_crossed": he_crossed[:n+1].copy(),
            "hydrogen_post_saha_off_crossed": post_crossed[:n+1].copy(),
            "common_input_evaluations": common_calls,
            "common_input_sample_columns": tuple(sampled_columns),
            "common_input_max_rhs_scaled": common_max_rhs,
            "common_input_max_virtual_ratio": common_max_v,
            "common_input_max_average_ratio": common_max_a,
            "common_input_max_lyman_ratio": common_max_l,
            "endpoint_diagnostic_column": endpoint_diag_column,
            "endpoint_diagnostic_rhs": endpoint_diag_rhs,
            "endpoint_diagnostic_matrix_residual": endpoint_diag_residual,
            "reviewed_u2_sha256": u2_checkpoint.reviewed_u2_sha256,
            "failure": failure,
        })
    checkpoint("START")

    def incoming(col: int):
        if col < 2:
            return np.zeros(NVIRTUAL), np.zeros(2)
        got = causal_incoming_from_accepted_histories(
            energies_eV=table.energy_eV,
            virtual_history=vout[:, :col], lyman_history=lyout[:, :col],
            z_start=float(z[0]), iz=col, z_face=float(z[col]),
            dlna=SOURCE_DLNA, shear_q=0.0)
        return got.virtual_distortion[0], got.lya_lyb_incoming_distortion[0]

    def compare_common(out, node: int, hstate: float, hestate: float, tstate: float):
        nonlocal common_calls, common_max_rhs, common_max_v, common_max_a, common_max_l
        if node in sampled_columns:
            return
        if common_calls >= 64:
            raise RuntimeError("HOLD_NEXT_STAGE_REQUIRED:COMMON_INPUT_SAMPLE_CAP")
        common_calls += 1
        sampled_columns.append(int(node))
        ref = common_input_oracle(
            int(node), float(z[node]), float(hstate), float(hestate), float(tstate),
            vout[:, :node], lyout[:, :node])
        rhs_c = float(ref["rhs"])
        if not math.isfinite(rhs_c) or not math.isfinite(float(out.dxHII_dln_a)):
            raise ArithmeticError(f"COMMON_INPUT_RHS_NONFINITE:col={node}")
        rhs_scaled = abs(float(out.dxHII_dln_a) - rhs_c) / max(1.0, abs(rhs_c))
        if not math.isfinite(rhs_scaled):
            raise ArithmeticError(f"COMMON_INPUT_RHS_NONFINITE:col={node}")
        common_max_rhs = max(common_max_rhs, rhs_scaled)
        if rhs_scaled > 2.0e-10:
            raise ArithmeticError(f"COMMON_INPUT_FULL_RHS_PARITY col={node} scaled={rhs_scaled:.17g}")
        cv = np.asarray(ref["virtual"], dtype=float)
        ca = np.asarray(ref["average"], dtype=float)
        cl = np.asarray(ref["lyman"], dtype=float)
        if cv.shape != (NVIRTUAL,) or ca.shape != (NVIRTUAL,) or cl.shape != (NLYMAN,):
            raise ValueError("C oracle must return all 311+311+3 spectrum entries")
        tr_ev = 8.617343e-5 * c.T0_K * (1.0 + float(z[node]))
        fbbv = 1.0 / np.expm1(table.energy_eV / tr_ev)
        line_e = np.array((10.198714553953742, 12.087365397278509, 12.748393192442178))
        fbbl = 1.0 / np.expm1(line_e / tr_ev)
        ratios = []
        for pyv, cvv, fb in ((out.outgoing_virtual, cv, fbbv),
                             (out.average_virtual, ca, fbbv),
                             (out.outgoing_lyman, cl, fbbl)):
            tol = 1.0e-7 * np.maximum(np.abs(pyv), np.abs(cvv)) + 1.0e-10 * fb
            ratio = np.abs(pyv - cvv) / tol
            if not np.all(np.isfinite(ratio)) or np.any(ratio > 1.0):
                b = int(np.flatnonzero((~np.isfinite(ratio)) | (ratio > 1.0))[0])
                raise ArithmeticError(f"COMMON_INPUT_PHOTON_PARITY col={node} bin={b}")
            ratios.append(float(np.max(ratio)))
        common_max_v = max(common_max_v, ratios[0])
        common_max_a = max(common_max_a, ratios[1])
        common_max_l = max(common_max_l, ratios[2])

    def rhs_full(node: int, hstate: float, hestate: float, tstate: float,
                 *, common_sample: bool = False):
        nonlocal full_evals
        if full_evals >= max_full_evaluations:
            raise RuntimeError("HOLD_NEXT_STAGE_REQUIRED:FULL_EVALUATION_CAP")
        # Original FULL RT is only admitted while the source index remains in
        # the validated radiative-transfer interval.
        rel = int(iz[node]) - U2_START_IZ
        if rt_limit_relative_index is None:
            raise RuntimeError("HOLD_RT_LIMIT_NOT_BOUND_TO_REVIEWED_SOURCE")
        if rel >= rt_limit_relative_index:
            raise RuntimeError("HOLD_NEXT_STAGE_REQUIRED:RT_TABLE_BOUNDARY")
        fv, fl = incoming(node)
        t_eval = float(tstate)
        tr = c.T0_K * (1.0 + float(z[node]))
        if t_eval == tr:
            t_eval = math.nextafter(t_eval, 0.0)
        snap = populate_original_full_atomic(
            source, z=float(z[node]), xHII=float(hstate),
            xe=float(hstate + hestate), Tm_K=t_eval,
            incoming_virtual=fv, incoming_lyman=fl)
        out = complete_original_full_atomic(snap)
        full_evals += 1
        if float(out.normalized_matrix_residual) > 2.0e-10:
            raise ArithmeticError(f"SCHUR_RESIDUAL col={node}")
        if common_sample:
            compare_common(out, node, hstate, hestate, t_eval)
        return out

    # The checkpoint endpoint is node/column 8: its photons are accepted
    # columns 0..7, and its source derivative tails are f7/f6.
    # Source helper arguments are (prev=f7, prev2=f6); its native update
    # consumes prev2 first, then shifts the newly evaluated input RHS.
    h_prev, h_prev2 = float(h_rhs[7]), float(h_rhs[6])
    he_prev, he_prev2 = float(he_rhs[7]), float(he_rhs[6])

    try:
      while accepted - U2_ACCEPTED_STEPS < max_extra_accepted:
        node = accepted
        global_iz = int(iz[node])
        if global_iz != U3_START_IZ + (node - U2_ACCEPTED_STEPS):
            raise ArithmeticError("NONCONTIGUOUS_SOURCE_INDEX")
        if accepted >= MAX_HISTORY_COLUMNS:
            break
        if not (0.0 <= xhe[node] <= c.fHe and 0.0 <= xh[node] <= 1.0):
            raise FloatingPointError(f"NONPHYSICAL_INPUT_STATE col={node}")
        # HyRec keeps Tm on rec_Tmss throughout the joint H+He stage. The
        # thermal threshold only gates the following H-only stage.
        tr_k = c.T0_K * (1.0 + z[node])
        if not (0.0 < tm[node] <= tr_k):
            raise RuntimeError("HOLD_NEXT_STAGE_REQUIRED:THERMAL_STATE_DOMAIN")
        h_only = bool(xhe[node] <= XHEII_MIN)
        if h_only and 1.0 - tm[node] / tr_k >= DLNT_MAX:
            hold_reason = "HOLD_NEXT_STAGE_REQUIRED:THERMAL_BOUNDARY"
            checkpoint("STOP_THERMAL_BOUNDARY")
            break
        rel = global_iz - U2_START_IZ
        if rt_limit_relative_index is None:
            raise RuntimeError("HOLD_NEXT_STAGE_REQUIRED:RT_LIMIT_UNBOUND")
        if rel + 1 >= rt_limit_relative_index:
            hold_reason = "HOLD_NEXT_STAGE_REQUIRED:RT_TABLE_BOUNDARY"
            checkpoint("STOP_RT_TABLE_BOUNDARY")
            break
        H = c.hubble_s(float(z[node]))
        # history.c hands the previous total electron fraction to the
        # hydrogen-only source as xHII at this branch boundary; the recorded
        # prior node retains its actual split H/He species values.
        h_input = float(xe[node]) if h_only else float(xh[node])
        he_input = 0.0 if h_only else float(xhe[node])
        fHe = 0.0 if h_only else helium_rhs(c, float(x1[node]), float(xhe[node]), H, float(z[node]))
        sample_this = node in fixed_sample_columns or node in event_sample_columns
        fH = rhs_full(node, h_input, he_input, float(tm[node]), common_sample=sample_this)
        he_rhs[node] = fHe
        h_rhs[node] = float(fH.dxHII_dln_a)
        vout[:, node] = fH.outgoing_virtual
        avgout[:, node] = fH.average_virtual
        lyout[:, node] = fH.outgoing_lyman
        residual[node] = fH.normalized_matrix_residual

        # He follows get_rec_next2_HHe's historical two-step update.
        xhe_candidate = (0.0 if h_only else float(
            xhe[node] + SOURCE_DLNA * (1.25 * fHe - 0.25 * he_prev2)))
        next_node = node + 1
        iz[next_node] = global_iz + 1
        z[next_node] = c.redshift(int(iz[next_node]))
        if post[node]:
            q = saha_xH1s(c, xhe_candidate, float(z[next_node]))
            qprime = (1.0 + z[next_node]) * (
                saha_xH1s(c, xhe_candidate, z[next_node] - 0.5)
                - saha_xH1s(c, xhe_candidate, z[next_node] + 0.5))
            deriv = _hydrogen_saha_helium_coupling(c, xhe_candidate, float(z[next_node]))
            if deriv != 0.0:
                fHe_next = helium_rhs(c, q, xhe_candidate,
                                      c.hubble_s(float(z[next_node])), float(z[next_node]))
                qprime += deriv * fHe_next
            # Corrected H post-Saha source expression uses FULL rates and
            # accepted photon history. The candidate spectra of these probes
            # are intentionally discarded.
            Tr = c.T0_K * (1.0 + z[next_node])
            def hprobe(hii):
                return rhs_full(next_node, float(hii), xhe_candidate, Tr).dxHII_dln_a
            X = 1.0 - q
            f0 = hprobe(X)
            delta_h = 0.01 * q
            if not (delta_h > 0 and delta_h < X and X + delta_h < 1.0):
                raise ArithmeticError("POST_SAHA_HYDROGEN_PROBE_DOMAIN")
            jac = (hprobe(X + delta_h) - hprobe(X - delta_h)) / (2.0 * delta_h)
            if jac == 0.0 or not math.isfinite(jac):
                raise ArithmeticError("POST_SAHA_HYDROGEN_JACOBIAN")
            x1[next_node] = q + (qprime + f0) / jac
            post[next_node] = abs(x1[next_node] - q) <= DXHII_MAX
        else:
            # Native state is neutral H; integrate xHII with source f at input.
            xh[next_node] = float(h_input + SOURCE_DLNA *
                (1.25 * h_rhs[node] - 0.25 * h_prev2))
            x1[next_node] = 1.0 - xh[next_node]
            post[next_node] = False
        xhe[next_node] = xhe_candidate
        xh[next_node] = 1.0 - x1[next_node]
        xe[next_node] = xh[next_node] + xhe[next_node]
        tm[next_node] = tm_steady_K(c, float(xe[next_node]), float(z[next_node]),
                                    c.hubble_s(float(z[next_node])))
        if (not all(math.isfinite(float(v)) for v in
                    (x1[next_node], xh[next_node], xhe[next_node], xe[next_node], tm[next_node]))
                or not (0.0 <= xh[next_node] <= 1.0 and 0.0 <= xhe[next_node] <= c.fHe
                        and tm[next_node] > 0.0)):
            raise FloatingPointError(f"NONPHYSICAL_ACCEPTED_STATE col={node}")
        if abs(xe[next_node] - (xh[next_node] + xhe[next_node])) > 5.0e-13:
            raise ArithmeticError("ELECTRON_LEDGER")
        he_crossed[next_node] = xhe[node] > XHEII_MIN and xhe[next_node] <= XHEII_MIN
        post_crossed[next_node] = bool(post[node]) and not bool(post[next_node])
        branch_h_only[next_node] = xhe[next_node] <= XHEII_MIN
        if he_crossed[next_node] or post_crossed[next_node]:
            if event == "NONE":
                event_he_cross = bool(he_crossed[next_node])
                event_post_cross = bool(post_crossed[next_node])
                event = ("HELIUM_CUTOFF+HYDROGEN_POST_SAHA_OFF" if event_he_cross and event_post_cross
                         else "HELIUM_CUTOFF" if event_he_cross else "HYDROGEN_POST_SAHA_OFF")
                first_event_accepted_col = next_node
                event_sample_columns.update(range(max(U2_ACCEPTED_STEPS, next_node-1), next_node+3))
                if node not in sampled_columns and common_calls < 64:
                    compare_common(fH, node, h_input, he_input, float(tm[node]))

        # The source branch event is the first accepted state crossing either
        # native threshold. Count two subsequent accepted steps in that branch.
        if event != "NONE" and first_event_accepted_col is not None and next_node > first_event_accepted_col:
            post_event_steps += 1
        accepted += 1
        h_prev2, h_prev = h_prev, float(h_rhs[node])
        he_prev2, he_prev = he_prev, float(he_rhs[node])
        if event != "NONE" and first_event_accepted_col == next_node:
            checkpoint("EVENT")
        if (accepted - U2_ACCEPTED_STEPS) % 128 == 0:
            checkpoint(f"ACCEPTED_{accepted-U2_ACCEPTED_STEPS:04d}")
        if event != "NONE" and post_event_steps >= 2:
            break

      if event != "NONE" and post_event_steps >= 2:
        endpoint_node = accepted
        endpoint_h_only = bool(xhe[endpoint_node] <= XHEII_MIN)
        endpoint_tr = c.T0_K * (1.0 + float(z[endpoint_node]))
        endpoint_rel = int(iz[endpoint_node]) - U2_START_IZ
        if endpoint_rel >= rt_limit_relative_index:
            hold_reason = "HOLD_NEXT_STAGE_REQUIRED:RT_TABLE_BOUNDARY"
            checkpoint("HOLD_ENDPOINT_RT_BOUNDARY")
        elif endpoint_h_only and 1.0 - tm[endpoint_node] / endpoint_tr >= DLNT_MAX:
            hold_reason = "HOLD_NEXT_STAGE_REQUIRED:THERMAL_BOUNDARY"
            checkpoint("HOLD_ENDPOINT_THERMAL_BOUNDARY")
        elif full_evals >= max_full_evaluations:
            hold_reason = "HOLD_NEXT_STAGE_REQUIRED:FULL_EVALUATION_CAP"
            checkpoint("HOLD_ENDPOINT_FULL_EVALUATION_CAP")
        elif common_calls >= 64 and endpoint_node not in sampled_columns:
            hold_reason = "HOLD_NEXT_STAGE_REQUIRED:COMMON_INPUT_SAMPLE_CAP"
            checkpoint("HOLD_ENDPOINT_COMMON_SAMPLE_CAP")
        else:
            endpoint_h = float(xe[endpoint_node]) if endpoint_h_only else float(xh[endpoint_node])
            endpoint_he = 0.0 if endpoint_h_only else float(xhe[endpoint_node])
            endpoint_out = rhs_full(endpoint_node, endpoint_h, endpoint_he,
                                    float(tm[endpoint_node]), common_sample=True)
            endpoint_diag_column = int(iz[endpoint_node])
            endpoint_diag_rhs = float(endpoint_out.dxHII_dln_a)
            endpoint_diag_residual = float(endpoint_out.normalized_matrix_residual)
            checkpoint("ENDPOINT_DIAGNOSTIC")
    except BaseException as exc:
        checkpoint("EXCEPTION", {"type": type(exc).__name__, "message": str(exc),
                                  "last_accepted_global_iz": int(iz[accepted])})
        raise
    status = hold_reason if hold_reason is not None else \
        "EVENT_TWO_STEPS_COMPLETE" if event != "NONE" and post_event_steps >= 2 else \
        "BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED"
    if accepted - U2_ACCEPTED_STEPS >= max_extra_accepted and event == "NONE":
        status = "BOUNDED_INTERVAL_COMPLETE_EVENT_NOT_REACHED"
    # An event reached too late to accrue two branch steps is an incomplete
    # execution, not a success-shaped artifact.
    if event != "NONE" and post_event_steps < 2 and hold_reason is None:
        status = "HOLD_NEXT_STAGE_REQUIRED:EVENT_TWO_STEPS_INCOMPLETE"
    checkpoint("STOP")
    return ContinuationHistory(
        iz=iz[:accepted+1], z=z[:accepted+1], xH1s=x1[:accepted+1],
        xHII=xh[:accepted+1], xHeII=xhe[:accepted+1], xe=xe[:accepted+1],
        Tm_K=tm[:accepted+1], post_saha=post[:accepted+1],
        source_branch_h_only=branch_h_only[:accepted+1],
        helium_cutoff_crossed=he_crossed[:accepted+1],
        hydrogen_post_saha_off_crossed=post_crossed[:accepted+1],
        hydrogen_rhs_dln_a=h_rhs[:accepted], helium_rhs_dln_a=he_rhs[:accepted],
        virtual_out=vout[:,:accepted], average_virtual=avgout[:,:accepted],
        lyman_out=lyout[:,:accepted], matrix_residual=residual[:accepted],
        accepted_extra=accepted-U2_ACCEPTED_STEPS, full_evaluations=full_evals,
        event=event, branch_steps_after_event=post_event_steps, status=status,
        reviewed_u2_sha256=u2_checkpoint.reviewed_u2_sha256,
        common_input_evaluations=common_calls,
        common_input_sample_columns=tuple(sampled_columns),
        common_input_max_rhs_scaled=common_max_rhs,
        common_input_max_virtual_ratio=common_max_v,
        common_input_max_average_ratio=common_max_a,
        common_input_max_lyman_ratio=common_max_l,
        endpoint_diagnostic_column=endpoint_diag_column,
        endpoint_diagnostic_rhs=endpoint_diag_rhs,
        endpoint_diagnostic_matrix_residual=endpoint_diag_residual,
    )
