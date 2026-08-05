"""Original-HyRec source lock and native Ly-alpha diffusion diagnostics.

This module is the bounded PR-04B1 bridge from the user-supplied October-2012
original-HyRec archive to the positive common-measure work of PR-04A.  It
reconstructs the *primitive native diffusion block* exactly, including the
unresolved 2p line-centre state, and records what can and cannot be identified
with a physical photon finite-volume measure.

Conventions
-----------
* metric signature ``(-,+,+,+)`` (only the local hydrogen-frame scalar block
  appears here);
* original HyRec uses cgs lengths and energies/temperatures in eV;
* the project adapter uses ordinary frequency ``nu`` in Hz, not angular
  frequency;
* ``Delta nu = nu_target - nu_source``;
* ``Delta E_gamma = h Delta nu`` and ``Delta E_H = -h Delta nu``;
* ``c``, ``h`` and ``k_B`` are retained explicitly;
* native matrix coefficients have units ``s^-1``;
* the reversible native proxy measure is dimensionless and is *not* silently
  promoted to the physical ``m^-3`` photon common measure of PR-04A.

The original C variable is a virtual-level proxy ``x_b = x_1s f_nu_b`` (or its
nonthermal departure).  The primitive sparse block is an algebraic
radiative-transfer system with escape compression.  Consequently, direct use
of ``Aup/Adn`` as photon-cell rates is forbidden.  A physical bin number map is
provided only as an explicitly labelled diagnostic.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from pathlib import Path, PurePosixPath
import stat
from typing import Iterable
import zipfile

import numpy as np
from scipy.constants import c, electron_volt, h, k


ORIGINAL_HYREC_ARCHIVE_SHA256 = (
    "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27"
)
ORIGINAL_HYREC_ARCHIVE_BYTES = 726_954
ORIGINAL_HYREC_ARCHIVE_ENTRY_COUNT = 29
ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256 = (
    "9fdee53a363aeb3b7c6963564543089e1b5ed91e39b0d4471efd052aa66b6485"
)
ORIGINAL_HYREC_PORTABLE_BINARY_SHA256 = (
    "a5ebb0e67b58f5d85f3387458eb96025f93b5b53b1ce4fd76c3a160c51d4b733"
)

NVIRT = 311
NSUBLYA = 140
NDIFF = 80
DIFFUSION_START = NSUBLYA - NDIFF // 2
DIFFUSION_STOP = DIFFUSION_START + NDIFF
LINE_CENTRE_LOCAL_INDEX = NDIFF
NATIVE_STATE_COUNT = NDIFF + 1

E21_EV = 10.198714553953742
M_H_EV_C2 = 0.93878299831e9
K_B_EV_K = 8.617343e-5
H_PLANCK_EV_S = h / electron_volt


@dataclass(frozen=True)
class ArchiveAudit:
    """Byte-level safety and provenance audit for an original-HyRec ZIP."""

    path: Path
    size_bytes: int
    sha256: str
    entry_count: int
    file_count: int
    directory_count: int
    total_uncompressed_bytes: int
    total_compressed_bytes: int
    unsafe_paths: tuple[str, ...]
    duplicate_names: tuple[str, ...]
    symlinks: tuple[str, ...]

    @property
    def safe(self) -> bool:
        return not (self.unsafe_paths or self.duplicate_names or self.symlinks)


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_original_hyrec_archive(path: str | Path) -> ArchiveAudit:
    """Audit a ZIP without extracting it.

    Absolute paths, ``..`` traversal, backslash paths, duplicate names and
    symlinks are rejected by the durable stage before extraction.
    """

    path = Path(path)
    unsafe: list[str] = []
    duplicates: list[str] = []
    symlinks: list[str] = []
    seen: set[str] = set()
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        bad_member = archive.testzip()
        if bad_member is not None:
            raise ValueError(f"ZIP integrity failure at {bad_member!r}")
        for info in infos:
            name = info.filename
            pure = PurePosixPath(name)
            if name in seen:
                duplicates.append(name)
            seen.add(name)
            if (
                pure.is_absolute()
                or ".." in pure.parts
                or "\\" in name
                or "\x00" in name
            ):
                unsafe.append(name)
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                symlinks.append(name)
        result = ArchiveAudit(
            path=path,
            size_bytes=path.stat().st_size,
            sha256=sha256_file(path),
            entry_count=len(infos),
            file_count=sum(not item.is_dir() for item in infos),
            directory_count=sum(item.is_dir() for item in infos),
            total_uncompressed_bytes=sum(item.file_size for item in infos),
            total_compressed_bytes=sum(item.compress_size for item in infos),
            unsafe_paths=tuple(unsafe),
            duplicate_names=tuple(duplicates),
            symlinks=tuple(symlinks),
        )
    return result


def safe_extract_original_hyrec_archive(
    archive_path: str | Path,
    destination: str | Path,
) -> ArchiveAudit:
    audit = audit_original_hyrec_archive(archive_path)
    if not audit.safe:
        raise ValueError(f"unsafe original-HyRec archive: {audit}")
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(destination)
    return audit


def read_two_photon_table(path: str | Path) -> np.ndarray:
    table = np.loadtxt(Path(path), dtype=float)
    if table.shape != (NVIRT, 5):
        raise ValueError(f"expected a {(NVIRT, 5)} table, got {table.shape}")
    if not np.all(np.isfinite(table)):
        raise ValueError("two-photon table contains nonfinite entries")
    if not np.all(np.diff(table[:, 0]) > 0.0):
        raise ValueError("virtual-state energies must be strictly increasing")
    table.setflags(write=False)
    return table


@dataclass(frozen=True)
class NativeDiffusionRates:
    """Exact Python reconstruction of original HyRec ``populate_Diffusion``."""

    temperature_K: float
    energy_eV: np.ndarray
    Aup_s_inv: np.ndarray
    Adn_s_inv: np.ndarray
    A2p_up_s_inv: float
    A2p_dn_s_inv: float

    def __post_init__(self) -> None:
        for name in ("energy_eV", "Aup_s_inv", "Adn_s_inv"):
            value = np.asarray(getattr(self, name), dtype=float)
            if value.shape != (NVIRT,):
                raise ValueError(f"{name} must have shape {(NVIRT,)}")
            if not np.all(np.isfinite(value)):
                raise ValueError(f"{name} contains nonfinite entries")
            value.setflags(write=False)
            object.__setattr__(self, name, value)
        if self.temperature_K <= 0.0 or not math.isfinite(self.temperature_K):
            raise ValueError("temperature_K must be positive and finite")
        if np.min(self.Aup_s_inv) < 0.0 or np.min(self.Adn_s_inv) < 0.0:
            raise ValueError("native diffusion rates must be nonnegative")
        if self.A2p_up_s_inv < 0.0 or self.A2p_dn_s_inv < 0.0:
            raise ValueError("line-centre rates must be nonnegative")

    @property
    def temperature_eV(self) -> float:
        return self.temperature_K * K_B_EV_K

    @property
    def diffusion_slice(self) -> slice:
        return slice(DIFFUSION_START, DIFFUSION_STOP)


def populate_original_hyrec_diffusion(
    two_photon_table: np.ndarray,
    temperature_K: float,
) -> NativeDiffusionRates:
    """Reproduce original-HyRec ``hydrogen.c:populate_Diffusion`` exactly."""

    table = np.asarray(two_photon_table, dtype=float)
    if table.shape != (NVIRT, 5):
        raise ValueError(f"two_photon_table must have shape {(NVIRT, 5)}")
    if temperature_K <= 0.0 or not math.isfinite(temperature_K):
        raise ValueError("temperature_K must be positive and finite")

    energy = table[:, 0].copy()
    A1s = table[:, 1]
    Aup = np.zeros(NVIRT, dtype=float)
    Adn = np.zeros(NVIRT, dtype=float)
    temperature_eV = temperature_K * K_B_EV_K
    delta_energy_squared = E21_EV**2 * 2.0 * temperature_eV / M_H_EV_C2

    b = DIFFUSION_START
    Aup[b] = (
        delta_energy_squared
        / (energy[b + 1] - energy[b]) ** 2
        * A1s[b]
    )
    for b in range(DIFFUSION_START + 1, NSUBLYA - 1):
        Adn[b] = math.exp((energy[b] - energy[b - 1]) / temperature_eV) * Aup[
            b - 1
        ]
        Aup[b] = (
            delta_energy_squared * A1s[b]
            - (energy[b] - energy[b - 1]) ** 2 * Adn[b]
        ) / (energy[b + 1] - energy[b]) ** 2

    b = NSUBLYA - 1
    Adn[b] = math.exp((energy[b] - energy[b - 1]) / temperature_eV) * Aup[
        b - 1
    ]
    Aup[b] = (
        delta_energy_squared * A1s[b]
        - (energy[b] - energy[b - 1]) ** 2 * Adn[b]
    ) / (E21_EV - energy[b]) ** 2
    A2p_dn = math.exp((E21_EV - energy[b]) / temperature_eV) * Aup[b] / 3.0

    b = DIFFUSION_STOP - 1
    Adn[b] = (
        delta_energy_squared
        / (energy[b] - energy[b - 1]) ** 2
        * A1s[b]
    )
    for b in range(DIFFUSION_STOP - 2, NSUBLYA, -1):
        Aup[b] = math.exp((energy[b] - energy[b + 1]) / temperature_eV) * Adn[
            b + 1
        ]
        Adn[b] = (
            delta_energy_squared * A1s[b]
            - (energy[b + 1] - energy[b]) ** 2 * Aup[b]
        ) / (energy[b] - energy[b - 1]) ** 2

    b = NSUBLYA
    Aup[b] = math.exp((energy[b] - energy[b + 1]) / temperature_eV) * Adn[
        b + 1
    ]
    Adn[b] = (
        delta_energy_squared * A1s[b]
        - (energy[b + 1] - energy[b]) ** 2 * Aup[b]
    ) / (energy[b] - E21_EV) ** 2
    A2p_up = math.exp((E21_EV - energy[b]) / temperature_eV) * Adn[b] / 3.0

    # Original C leaves unused entries unspecified; zero is the durable adapter
    # convention and never changes the active 80-state block.
    tiny = 256.0 * np.finfo(float).eps * max(
        float(np.max(Aup)), float(np.max(Adn)), A2p_up, A2p_dn, 1.0
    )
    if np.min(Aup) < -tiny or np.min(Adn) < -tiny:
        raise FloatingPointError("negative native diffusion rate")
    Aup[Aup < 0.0] = 0.0
    Adn[Adn < 0.0] = 0.0

    return NativeDiffusionRates(
        temperature_K=float(temperature_K),
        energy_eV=energy,
        Aup_s_inv=Aup,
        Adn_s_inv=Adn,
        A2p_up_s_inv=float(A2p_up),
        A2p_dn_s_inv=float(A2p_dn),
    )


@dataclass(frozen=True)
class NativeDiffusionNetwork:
    """81-state reversible proxy network (80 virtual bins plus 2p)."""

    temperature_K: float
    source_indices: np.ndarray
    labels: np.ndarray
    energy_eV: np.ndarray
    frequency_Hz: np.ndarray
    equilibrium_proxy: np.ndarray
    generator_s_inv: np.ndarray
    proxy_moments_Hz: np.ndarray

    def __post_init__(self) -> None:
        n = NATIVE_STATE_COUNT
        expected = {
            "source_indices": (n,),
            "labels": (n,),
            "energy_eV": (n,),
            "frequency_Hz": (n,),
            "equilibrium_proxy": (n,),
            "generator_s_inv": (n, n),
            "proxy_moments_Hz": (5, n, n),
        }
        for name, shape in expected.items():
            value = np.asarray(getattr(self, name))
            if value.shape != shape:
                raise ValueError(f"{name} must have shape {shape}, got {value.shape}")
            if value.dtype.kind in "fc" and not np.all(np.isfinite(value)):
                raise ValueError(f"{name} contains nonfinite entries")
            value.setflags(write=False)
            object.__setattr__(self, name, value)
        if np.any(self.equilibrium_proxy <= 0.0):
            raise ValueError("equilibrium proxy must be positive")
        off_diagonal = self.generator_s_inv.copy()
        np.fill_diagonal(off_diagonal, 0.0)
        if np.min(off_diagonal) < -1e-13:
            raise ValueError("generator has a negative off-diagonal rate")
        scale = max(float(np.max(np.abs(self.generator_s_inv))), 1.0)
        if np.max(np.abs(self.generator_s_inv.sum(axis=0))) > 5e-13 * scale:
            raise ValueError("native generator is not column-conservative")
        if np.max(np.abs(self.generator_s_inv @ self.equilibrium_proxy)) > (
            5e-13 * scale * np.max(self.equilibrium_proxy)
        ):
            raise ValueError("native proxy equilibrium is not a right null vector")

    @property
    def state_count(self) -> int:
        return NATIVE_STATE_COUNT

    @property
    def line_centre_index(self) -> int:
        return LINE_CENTRE_LOCAL_INDEX

    def apply(self, state: Iterable[float]) -> np.ndarray:
        state = np.asarray(state, dtype=float)
        if state.shape != (self.state_count,):
            raise ValueError("state shape mismatch")
        return self.generator_s_inv @ state

    def backward_euler(self, state: Iterable[float], dt_s: float) -> np.ndarray:
        state = np.asarray(state, dtype=float)
        if state.shape != (self.state_count,):
            raise ValueError("state shape mismatch")
        if dt_s < 0.0 or not math.isfinite(dt_s):
            raise ValueError("dt_s must be finite and nonnegative")
        matrix = np.eye(self.state_count) - dt_s * self.generator_s_inv
        return np.linalg.solve(matrix, state)


def build_native_diffusion_network(
    rates: NativeDiffusionRates,
) -> NativeDiffusionNetwork:
    indices = np.concatenate(
        [np.arange(DIFFUSION_START, DIFFUSION_STOP), np.asarray([-1])]
    )
    labels = np.asarray(
        [f"virtual_{index}" for index in range(DIFFUSION_START, DIFFUSION_STOP)]
        + ["2p_line_centre"]
    )
    energy = np.concatenate(
        [rates.energy_eV[DIFFUSION_START:DIFFUSION_STOP], [E21_EV]]
    )
    frequency = energy / H_PLANCK_EV_S
    temperature_eV = rates.temperature_eV
    equilibrium = np.exp(-energy / temperature_eV)
    equilibrium[-1] *= 3.0

    generator = np.zeros((NATIVE_STATE_COUNT, NATIVE_STATE_COUNT), dtype=float)

    # Adjacent virtual-bin jumps.  Q[target,source] is positive off diagonal.
    for global_index in range(DIFFUSION_START, DIFFUSION_STOP):
        source = global_index - DIFFUSION_START
        if global_index < NSUBLYA - 1:
            generator[source + 1, source] += rates.Aup_s_inv[global_index]
        elif global_index == NSUBLYA - 1:
            generator[LINE_CENTRE_LOCAL_INDEX, source] += rates.Aup_s_inv[
                global_index
            ]
        elif global_index >= NSUBLYA and global_index < DIFFUSION_STOP - 1:
            generator[source + 1, source] += rates.Aup_s_inv[global_index]

        if global_index > NSUBLYA:
            generator[source - 1, source] += rates.Adn_s_inv[global_index]
        elif global_index == NSUBLYA:
            generator[LINE_CENTRE_LOCAL_INDEX, source] += rates.Adn_s_inv[
                global_index
            ]
        elif global_index > DIFFUSION_START:
            generator[source - 1, source] += rates.Adn_s_inv[global_index]

    red = NSUBLYA - 1 - DIFFUSION_START
    blue = NSUBLYA - DIFFUSION_START
    generator[red, LINE_CENTRE_LOCAL_INDEX] += rates.A2p_dn_s_inv
    generator[blue, LINE_CENTRE_LOCAL_INDEX] += rates.A2p_up_s_inv
    np.fill_diagonal(generator, -generator.sum(axis=0))

    delta_frequency = frequency[:, None] - frequency[None, :]
    conductance = generator * equilibrium[None, :]
    np.fill_diagonal(conductance, 0.0)
    moments = np.stack(
        [conductance * delta_frequency**order for order in range(5)], axis=0
    )

    # Hard reversible parity; report residuals rather than symmetrizing.
    scales = np.maximum(np.max(np.abs(moments), axis=(1, 2)), 1e-300)
    parity = np.asarray([1.0, -1.0, 1.0, -1.0, 1.0])[:, None, None]
    residual = np.max(
        np.abs(moments - parity * np.swapaxes(moments, 1, 2))
        / scales[:, None, None]
    )
    if residual > 5e-12:
        raise FloatingPointError(f"native detailed-balance parity failed: {residual}")

    return NativeDiffusionNetwork(
        temperature_K=rates.temperature_K,
        source_indices=indices,
        labels=labels,
        energy_eV=energy,
        frequency_Hz=frequency,
        equilibrium_proxy=equilibrium,
        generator_s_inv=generator,
        proxy_moments_Hz=moments,
    )


@dataclass(frozen=True)
class SchurReducedDiffusion:
    """Exact steady elimination of the unresolved 2p proxy state."""

    generator_s_inv: np.ndarray
    equilibrium_proxy: np.ndarray
    direct_bridge_red_to_blue_s_inv: float
    direct_bridge_blue_to_red_s_inv: float

    def __post_init__(self) -> None:
        q = np.asarray(self.generator_s_inv, dtype=float)
        pi = np.asarray(self.equilibrium_proxy, dtype=float)
        if q.shape != (NDIFF, NDIFF) or pi.shape != (NDIFF,):
            raise ValueError("Schur-reduced shape mismatch")
        scale = max(float(np.max(np.abs(q))), 1.0)
        if np.max(np.abs(q.sum(axis=0))) > 1e-12 * scale:
            raise ValueError("Schur-reduced generator is not conservative")
        if np.max(np.abs(q @ pi)) > 1e-12 * scale * np.max(pi):
            raise ValueError("Schur-reduced equilibrium null failed")
        q.setflags(write=False)
        pi.setflags(write=False)
        object.__setattr__(self, "generator_s_inv", q)
        object.__setattr__(self, "equilibrium_proxy", pi)


def schur_reduce_line_centre(
    network: NativeDiffusionNetwork,
) -> SchurReducedDiffusion:
    q = network.generator_s_inv
    virtual = np.arange(NDIFF)
    centre = network.line_centre_index
    # T=-Q is the original-HyRec sign convention.  Eliminate the 1x1 2p block.
    t_vv = -q[np.ix_(virtual, virtual)]
    t_vp = -q[np.ix_(virtual, [centre])]
    t_pv = -q[np.ix_([centre], virtual)]
    t_pp = float(-q[centre, centre])
    if t_pp <= 0.0:
        raise ValueError("line-centre outgoing rate must be positive")
    t_effective = t_vv - (t_vp @ t_pv) / t_pp
    q_effective = -t_effective
    red = NSUBLYA - 1 - DIFFUSION_START
    blue = NSUBLYA - DIFFUSION_START
    return SchurReducedDiffusion(
        generator_s_inv=q_effective,
        equilibrium_proxy=network.equilibrium_proxy[:NDIFF],
        direct_bridge_red_to_blue_s_inv=float(q_effective[blue, red]),
        direct_bridge_blue_to_red_s_inv=float(q_effective[red, blue]),
    )


def inferred_log_cell_edges_eV(energy_eV: np.ndarray) -> np.ndarray:
    """Source-consistent diagnostic edges for the 80 diffusion centres.

    Original HyRec stores centres and bin-integrated rates, not a standalone
    physical finite-volume edge registry.  The source redshifts distortions in
    logarithmic frequency and treats the Ly-alpha centre as an explicit
    boundary.  These edges therefore use geometric midpoints, the exact line
    centre, and adjacent table centres outside the 80-bin block.  They are
    labelled *inferred*, never official native edges.
    """

    energy = np.asarray(energy_eV, dtype=float)
    if energy.shape != (NVIRT,):
        raise ValueError(f"energy_eV must have shape {(NVIRT,)}")
    edges = np.empty(NDIFF + 1, dtype=float)
    edges[0] = math.sqrt(
        energy[DIFFUSION_START - 1] * energy[DIFFUSION_START]
    )
    for local in range(1, NSUBLYA - DIFFUSION_START):
        left = DIFFUSION_START + local - 1
        right = left + 1
        edges[local] = math.sqrt(energy[left] * energy[right])
    edges[NSUBLYA - DIFFUSION_START] = E21_EV
    for local in range(NSUBLYA - DIFFUSION_START + 1, NDIFF):
        left = DIFFUSION_START + local - 1
        right = left + 1
        edges[local] = math.sqrt(energy[left] * energy[right])
    edges[-1] = math.sqrt(
        energy[DIFFUSION_STOP - 1] * energy[DIFFUSION_STOP]
    )
    if not np.all(np.diff(edges) > 0.0):
        raise FloatingPointError("inferred log-cell edges are not increasing")
    edges.setflags(write=False)
    return edges


def inferred_photon_mode_measure_m3(energy_edges_eV: np.ndarray) -> np.ndarray:
    """Return ``8 pi/c^3 int nu^2 dnu`` for inferred virtual photon cells."""

    edges = np.asarray(energy_edges_eV, dtype=float)
    if edges.shape != (NDIFF + 1,):
        raise ValueError(f"energy_edges_eV must have shape {(NDIFF + 1,)}")
    frequency_edges = edges / H_PLANCK_EV_S
    measure = (8.0 * math.pi / (3.0 * c**3)) * (
        frequency_edges[1:] ** 3 - frequency_edges[:-1] ** 3
    )
    if np.any(measure <= 0.0) or not np.all(np.isfinite(measure)):
        raise FloatingPointError("invalid inferred photon mode measure")
    measure.setflags(write=False)
    return measure


def physical_number_map_residual(
    reduced: SchurReducedDiffusion,
    mode_measure_m3: np.ndarray,
) -> float:
    """Quantify why the native proxy generator is not a photon FV generator.

    A physical finite-volume photon generator would obey ``g^T Q = 0`` for the
    cell mode measure ``g``.  Original HyRec's primitive algebraic diffusion
    block instead obeys ``1^T Q = 0`` in the virtual proxy coordinate.  This
    function returns the dimensionless weighted-left-null residual.
    """

    weights = np.asarray(mode_measure_m3, dtype=float)
    if weights.shape != (NDIFF,):
        raise ValueError(f"mode_measure_m3 must have shape {(NDIFF,)}")
    numerator = np.linalg.norm(weights @ reduced.generator_s_inv, ord=np.inf)
    denominator = (
        np.linalg.norm(weights, ord=np.inf)
        * np.linalg.norm(reduced.generator_s_inv, ord=np.inf)
    )
    return float(numerator / max(denominator, 1e-300))


def central_difference_jvp_residual(
    matrix: np.ndarray,
    state: np.ndarray,
    direction: np.ndarray,
    epsilon: float = 2e-7,
) -> float:
    """Independent linear-JVP regression used in the immutable stage."""

    matrix = np.asarray(matrix, dtype=float)
    state = np.asarray(state, dtype=float)
    direction = np.asarray(direction, dtype=float)
    exact = matrix @ direction
    finite = (
        matrix @ (state + epsilon * direction)
        - matrix @ (state - epsilon * direction)
    ) / (2.0 * epsilon)
    return float(
        np.linalg.norm(finite - exact)
        / max(np.linalg.norm(exact), 1e-300)
    )


__all__ = [
    "ArchiveAudit",
    "NativeDiffusionNetwork",
    "NativeDiffusionRates",
    "SchurReducedDiffusion",
    "ORIGINAL_HYREC_ARCHIVE_SHA256",
    "ORIGINAL_HYREC_ARCHIVE_BYTES",
    "ORIGINAL_HYREC_BASELINE_OUTPUT_SHA256",
    "ORIGINAL_HYREC_PORTABLE_BINARY_SHA256",
    "NVIRT",
    "NSUBLYA",
    "NDIFF",
    "DIFFUSION_START",
    "DIFFUSION_STOP",
    "E21_EV",
    "M_H_EV_C2",
    "K_B_EV_K",
    "H_PLANCK_EV_S",
    "audit_original_hyrec_archive",
    "safe_extract_original_hyrec_archive",
    "read_two_photon_table",
    "populate_original_hyrec_diffusion",
    "build_native_diffusion_network",
    "schur_reduce_line_centre",
    "inferred_log_cell_edges_eV",
    "inferred_photon_mode_measure_m3",
    "physical_number_map_residual",
    "central_difference_jvp_residual",
    "sha256_file",
]
