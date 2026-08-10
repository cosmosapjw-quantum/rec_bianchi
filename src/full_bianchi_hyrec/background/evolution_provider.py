"""Audited background-evolution provider boundary for Full Bianchi--HyRec.

The initial implementation deliberately supports one validated lane only:
orthogonal perfect-fluid Bianchi II in the Wainwright--Hsu/WE Hubble-normalized
chart.  The equations are a dependency-free NumPy/SciPy transcription of the
uploaded ``bianchireview87`` ``bianchi/charts/class_a.py`` source identified by
content hash below.  Other family labels fail closed instead of falling back to
an identity or stale snapshot.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Mapping, Protocol, Sequence

import numpy as np
from scipy.integrate import solve_ivp

from .sequence import BackgroundSnapshotSequence
from .snapshot import BackgroundSnapshot


BIANCHI_REVIEW_ARCHIVE_SHA256 = (
    "6bb094d30a6d24b3feee11a1d9ae2827049945dae8281ed37d0d0796a6e9ea84"
)
BIANCHI_REVIEW_CLASS_A_SOURCE_SHA256 = (
    "bfe18d8978e92aae1de6d3a122eded61ffd3c02988a55dc7e160ec9de214b1df"
)
BIANCHI_REVIEW_TYPE_IX_D_SOURCE_SHA256 = (
    "77cd524cbfde04d020843ace9f6e140a7b659f53dbadbe945eaf661a1bf11dcb"
)


class BackgroundProviderError(RuntimeError):
    """Base class for fail-closed provider errors."""


@dataclass(frozen=True)
class BackgroundProviderEvent:
    family: str
    event_type: str
    required_chart: str
    reason: str


class BackgroundChartEventRequired(BackgroundProviderError):
    def __init__(self, event: BackgroundProviderEvent):
        self.event = event
        super().__init__(
            f"{event.family} requires {event.event_type} handling in "
            f"{event.required_chart}: {event.reason}"
        )


class BackgroundFamilyNotValidatedError(BackgroundProviderError):
    pass


class UnsupportedBackgroundBranchError(BackgroundProviderError):
    pass


@dataclass(frozen=True)
class BianchiIINormalizedState:
    Sigma_plus: float
    Sigma_minus: float
    N1: float

    def __post_init__(self) -> None:
        values = tuple(float(value) for value in (self.Sigma_plus, self.Sigma_minus, self.N1))
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Bianchi-II normalized state must be finite")
        if values[2] <= 0.0:
            raise ValueError("Bianchi-II N1 must be positive on the validated branch")
        object.__setattr__(self, "Sigma_plus", values[0])
        object.__setattr__(self, "Sigma_minus", values[1])
        object.__setattr__(self, "N1", values[2])

    @classmethod
    def from_snapshot(cls, snapshot: BackgroundSnapshot) -> "BianchiIINormalizedState":
        if snapshot.bianchi_type != "II" or np.any(snapshot.beta_H != 0.0):
            raise ValueError("snapshot is not an orthogonal Bianchi-II state")
        H = snapshot.H_s_inv
        sigma = snapshot.sigma_s_inv / H
        curvature = snapshot.N_s_inv / H
        return cls(
            Sigma_plus=float(-0.5 * sigma[0, 0]),
            Sigma_minus=float((sigma[1, 1] - sigma[2, 2]) / (2.0 * math.sqrt(3.0))),
            N1=float(curvature[0, 0]),
        )


@dataclass(frozen=True)
class OrthogonalGammaLawMatter:
    gamma: float

    def __post_init__(self) -> None:
        value = float(self.gamma)
        if not math.isfinite(value) or not (0.0 < value <= 2.0):
            raise ValueError("gamma must satisfy 0 < gamma <= 2")
        object.__setattr__(self, "gamma", value)


@dataclass(frozen=True)
class TiltedPerfectFluidRequest:
    gamma: float
    beta: np.ndarray

    def __post_init__(self) -> None:
        gamma = float(self.gamma)
        beta = np.asarray(self.beta, dtype=float)
        if not math.isfinite(gamma) or not (0.0 < gamma <= 2.0):
            raise ValueError("gamma must satisfy 0 < gamma <= 2")
        if beta.shape != (3,) or not np.all(np.isfinite(beta)) or float(beta @ beta) >= 1.0:
            raise ValueError("beta must be a finite subluminal three-vector")
        beta = np.array(beta, copy=True)
        beta.setflags(write=False)
        object.__setattr__(self, "gamma", gamma)
        object.__setattr__(self, "beta", beta)


class BackgroundEvolutionProvider(Protocol):
    provider_name: str
    source_sha256: str
    supported_family_matrix: Mapping[str, str]

    def snapshots(
        self,
        *,
        family: str,
        eta_grid: Sequence[float],
        initial_state: object,
        matter_parameters: object,
        H_anchor_s_inv: float,
        eta_anchor: float,
        cosmic_time_anchor_s: float = 0.0,
    ) -> BackgroundSnapshotSequence: ...


def _canonical_family(family: str) -> str:
    text = str(family).strip().replace("Bianchi", "").replace(" ", "")
    text = text.replace("type", "").replace("TYPE", "")
    aliases = {
        "II": "II",
        "_II": "II",
        "IX": "IX",
        "_IX": "IX",
        "VI_-1/9": "VI_-1/9",
        "VI*_-1/9": "VI_-1/9",
        "VIminus1over9": "VI_-1/9",
        "VI_h": "VI_h",
    }
    return aliases.get(text, text)


def _bianchi_ii_aux(state: np.ndarray, gamma: float) -> tuple[float, float, float, float]:
    Sigma_plus, Sigma_minus, N1 = (float(value) for value in state[:3])
    Sigma2 = Sigma_plus * Sigma_plus + Sigma_minus * Sigma_minus
    curvature = N1 * N1 / 12.0
    Omega = 1.0 - Sigma2 - curvature
    q = 2.0 * Sigma2 + 0.5 * (3.0 * gamma - 2.0) * Omega
    return Sigma2, curvature, Omega, q


def _bianchi_ii_rhs(_eta: float, state: np.ndarray, gamma: float) -> np.ndarray:
    Sigma_plus, Sigma_minus, N1, log_H_ratio, _time_hat = state
    _Sigma2, _curvature, _Omega, q = _bianchi_ii_aux(state, gamma)
    return np.asarray(
        [
            -(2.0 - q) * Sigma_plus + N1 * N1 / 3.0,
            -(2.0 - q) * Sigma_minus,
            (q - 4.0 * Sigma_plus) * N1,
            -(1.0 + q),
            math.exp(-float(log_H_ratio)),
        ],
        dtype=float,
    )


def _omega_identity_residual(state: np.ndarray, derivative: np.ndarray, gamma: float) -> float:
    Sigma_plus, Sigma_minus, N1 = state[:3]
    dSigma_plus, dSigma_minus, dN1 = derivative[:3]
    _Sigma2, _curvature, Omega, q = _bianchi_ii_aux(state, gamma)
    dOmega = -2.0 * Sigma_plus * dSigma_plus - 2.0 * Sigma_minus * dSigma_minus - N1 * dN1 / 6.0
    expected = (2.0 * q - (3.0 * gamma - 2.0)) * Omega
    return float(dOmega - expected)


@dataclass(frozen=True)
class BianchiReviewBianchiIIProvider:
    """Read-only audited provider for the orthogonal Bianchi-II pilot."""

    rtol: float = 1.0e-12
    atol: float = 1.0e-14
    provider_name: str = "bianchireview87_class_a_numpy_adapter_v1"
    source_sha256: str = BIANCHI_REVIEW_CLASS_A_SOURCE_SHA256

    @property
    def supported_family_matrix(self) -> Mapping[str, str]:
        return MappingProxyType(
            {
                "II:orthogonal": "PROVIDER_VALIDATED_PILOT",
                "IX:orthogonal": "D_NORMALIZED_H_ZERO_EVENT_REQUIRED",
                "VI_-1/9:tilted": "UNSUPPORTED_FAIL_CLOSED",
                "all_other_families": "REGISTRY_OR_SMOKE_ONLY_NOT_VALIDATED",
            }
        )

    def snapshots(
        self,
        *,
        family: str,
        eta_grid: Sequence[float],
        initial_state: object,
        matter_parameters: object,
        H_anchor_s_inv: float,
        eta_anchor: float,
        cosmic_time_anchor_s: float = 0.0,
    ) -> BackgroundSnapshotSequence:
        canonical = _canonical_family(family)
        if canonical == "IX":
            raise BackgroundChartEventRequired(
                BackgroundProviderEvent(
                    family="IX",
                    event_type="H_ZERO_RECOLLAPSE",
                    required_chart="type_ix_D_normalized",
                    reason="H-normalized interpolation must not cross H=0",
                )
            )
        if canonical == "VI_-1/9" and isinstance(matter_parameters, TiltedPerfectFluidRequest):
            raise UnsupportedBackgroundBranchError(
                "tilted exceptional VI_-1/9 provider is not validated; no fallback permitted"
            )
        if canonical != "II":
            raise BackgroundFamilyNotValidatedError(
                f"family {family!r} is not provider-validated; registry/smoke evidence is insufficient"
            )
        if not isinstance(initial_state, BianchiIINormalizedState):
            raise TypeError("Bianchi II provider requires BianchiIINormalizedState")
        if not isinstance(matter_parameters, OrthogonalGammaLawMatter):
            raise TypeError("Bianchi II provider requires OrthogonalGammaLawMatter")

        eta = np.asarray(eta_grid, dtype=float)
        if eta.ndim != 1 or eta.size < 2 or not np.all(np.isfinite(eta)) or np.any(np.diff(eta) <= 0.0):
            raise ValueError("eta_grid must be finite and strictly increasing")
        eta0 = float(eta_anchor)
        if not math.isfinite(eta0) or abs(float(eta[0]) - eta0) > 8.0 * np.finfo(float).eps * max(1.0, abs(eta0)):
            raise ValueError("eta_grid must start at eta_anchor for the audited pilot")
        H0 = float(H_anchor_s_inv)
        time0 = float(cosmic_time_anchor_s)
        if not math.isfinite(H0) or H0 <= 0.0 or not math.isfinite(time0):
            raise ValueError("H anchor must be positive and cosmic-time anchor finite")

        y0 = np.asarray(
            [
                initial_state.Sigma_plus,
                initial_state.Sigma_minus,
                initial_state.N1,
                0.0,
                0.0,
            ],
            dtype=float,
        )
        solution = solve_ivp(
            lambda t, y: _bianchi_ii_rhs(t, y, matter_parameters.gamma),
            (float(eta[0]), float(eta[-1])),
            y0,
            method="DOP853",
            t_eval=eta,
            rtol=float(self.rtol),
            atol=float(self.atol),
        )
        if not solution.success or solution.y.shape != (5, eta.size):
            raise BackgroundProviderError(f"Bianchi-II integration failed: {solution.message}")

        states = solution.y.T
        H = H0 * np.exp(states[:, 3])
        cosmic_time = time0 + states[:, 4] / H0
        q = np.empty(eta.size, dtype=float)
        sigma = np.zeros((eta.size, 3, 3), dtype=float)
        N = np.zeros_like(sigma)
        A = np.zeros((eta.size, 3), dtype=float)
        rotation = np.zeros_like(A)
        beta = np.zeros_like(A)
        dbeta = np.zeros_like(A)
        gauss = np.zeros(eta.size, dtype=float)
        omega_negative = np.empty(eta.size, dtype=float)
        omega_identity = np.empty(eta.size, dtype=float)

        root3 = math.sqrt(3.0)
        for index, state in enumerate(states):
            Sigma_plus, Sigma_minus, N1 = state[:3]
            _Sigma2, _curvature, Omega, q_value = _bianchi_ii_aux(state, matter_parameters.gamma)
            derivative = _bianchi_ii_rhs(float(eta[index]), state, matter_parameters.gamma)
            q[index] = q_value
            sigma[index] = H[index] * np.diag(
                [
                    -2.0 * Sigma_plus,
                    Sigma_plus + root3 * Sigma_minus,
                    Sigma_plus - root3 * Sigma_minus,
                ]
            )
            N[index, 0, 0] = H[index] * N1
            omega_negative[index] = max(0.0, -Omega)
            omega_identity[index] = _omega_identity_residual(
                state, derivative, matter_parameters.gamma
            )

        provenance = {
            "provider_name": self.provider_name,
            "archive_sha256": BIANCHI_REVIEW_ARCHIVE_SHA256,
            "equation_source": "bianchi/charts/class_a.py",
            "equation_source_sha256": BIANCHI_REVIEW_CLASS_A_SOURCE_SHA256,
            "normalization": "Wainwright-Ellis Hubble-normalized",
            "time_coordinate": "eta=tau=ln(ell/ell0)",
            "matter_model": f"orthogonal gamma-law gamma={matter_parameters.gamma:.17g}",
        }
        return BackgroundSnapshotSequence(
            model_name="Bianchi_II_provider_pilot",
            chart_id="class_a_bianchi_review_provider",
            bianchi_type="II",
            tau=eta,
            cosmic_time_s=cosmic_time,
            H_s_inv=H,
            q=q,
            sigma_s_inv=sigma,
            N_s_inv=N,
            A_s_inv=A,
            frame_rotation_s_inv=rotation,
            beta_H=beta,
            D0_beta_H_s_inv=dbeta,
            source_path="archive://bianchireview87/bianchi/charts/class_a.py",
            source_sha256=BIANCHI_REVIEW_CLASS_A_SOURCE_SHA256,
            provenance=provenance,
            constraint_residual_series={
                "gauss": gauss,
                "Omega_negative": omega_negative,
                "omega_identity": omega_identity,
            },
            provider_branch_flags={
                "expanding_H_normalized": True,
                "orthogonal": True,
                "dynamic_background": True,
                "provider_validated_bianchi_ii": True,
            },
        )


__all__ = [
    "BackgroundChartEventRequired",
    "BackgroundEvolutionProvider",
    "BackgroundFamilyNotValidatedError",
    "BackgroundProviderError",
    "BackgroundProviderEvent",
    "BianchiIINormalizedState",
    "BianchiReviewBianchiIIProvider",
    "OrthogonalGammaLawMatter",
    "TiltedPerfectFluidRequest",
    "UnsupportedBackgroundBranchError",
]
