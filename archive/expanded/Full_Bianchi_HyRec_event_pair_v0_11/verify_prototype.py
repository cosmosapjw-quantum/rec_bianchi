"""
Re-run the invariant checks stored in event_pair_prototype.npz.
"""

from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
data = np.load(HERE / "event_pair_prototype.npz")

S = data["conductance"]
G = data["generator"]
Pi = data["equilibrium_cell_weight"]
K = data["rate"]
Gamma = data["opacity"]
P = data["conditional"]

assert np.max(np.abs(S-S.T)) < 1.0e-14
assert np.max(np.abs(np.ones(G.shape[0]) @ G)) < 1.0e-12
assert np.max(np.abs(G @ Pi)) < 1.0e-12
assert np.max(np.abs(P.sum(axis=0)-1.0)) < 1.0e-12
assert np.max(np.abs(K-Gamma[None,:]*P)) < 1.0e-12
assert np.max(np.abs(data["BE_action"])) < 1.0e-12

Q = data["anisotropic_photon_four_force"]
assert np.all(np.isfinite(Q))

print("event-pair architecture prototype: PASS")
