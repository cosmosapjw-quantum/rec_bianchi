"""Locate frozen scientific artifacts shipped with the repository.

The historical runs read their kernels from the authoring sandbox at
``/mnt/data``.  Those absolute paths do not exist on any other machine, so
code that hardcoded them could only ever run where it was written.  The same
files are committed under ``archive/expanded/`` using the identical bundle and
file names, so resolution prefers the in-repo copy and falls back to the
legacy location for the authoring environment.
"""
from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARCHIVE = _REPO_ROOT / "archive" / "expanded"
_LEGACY_ROOT = Path("/mnt/data")


def artifact_path(bundle: str, filename: str) -> Path:
    """Return the path to ``filename`` inside the frozen bundle ``bundle``.

    The in-repo copy under ``archive/expanded/`` wins when present.  Neither
    candidate is read here; a missing artifact surfaces as the loader's own
    ``FileNotFoundError`` against the legacy path, which names the bundle the
    caller expected.
    """
    in_repo = _ARCHIVE / bundle / filename
    if in_repo.is_file():
        return in_repo
    return _LEGACY_ROOT / bundle / filename


V032_LEGENDRE_KERNEL = artifact_path(
    "Full_Bianchi_HyRec_C3B2B1C_finite_volume_ellmax_v0_32",
    "finite_volume_legendre_kernel.npz",
)
V033_COMPLETED_KERNEL = artifact_path(
    "Full_Bianchi_HyRec_C3B2B1D0_thermodynamic_completion_v0_33",
    "thermodynamic_completed_kernel.npz",
)
