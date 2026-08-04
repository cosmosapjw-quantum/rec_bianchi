"""Same-event photon and hydrogen four-momentum transfer."""
from __future__ import annotations

import numpy as np

from .event import RecoilEvent


def event_transfer(
    event: RecoilEvent,
) -> tuple[np.ndarray, np.ndarray]:
    delta_photon = event.k_f - event.k_i
    # Define the atomic transfer from the same event ledger. This avoids
    # subtracting two nearly equal massive four-momenta.
    delta_atom = -delta_photon
    return delta_photon, delta_atom


def four_force(
    event_rate: float,
    event: RecoilEvent,
) -> tuple[np.ndarray, np.ndarray]:
    if not np.isfinite(event_rate) or event_rate < 0.0:
        raise ValueError("event_rate must be finite and nonnegative")
    delta_photon, delta_atom = event_transfer(event)
    return event_rate * delta_photon, event_rate * delta_atom
