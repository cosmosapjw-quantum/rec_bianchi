
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
d=np.load(HERE/"orbit_cache_and_conductance.npz")
S=d["full_conductance"]; G=d["full_generator"]; Pi=d["equilibrium_cell_weight"]
K=S/Pi[None,:]; Gamma=d["full_opacity"]; P=d["full_conditional"]

assert d["active_physics_orbit_id"].size == 1836
assert np.max(d["orbit_integrated_reciprocity"]) < 1e-12
assert np.max(d["orbit_pointwise_reciprocity"]) < 1e-12
assert np.max(d["orbit_quad_change_full"]) < 1e-12
assert np.max(np.abs(S-S.T)) < 1e-14
assert np.max(np.abs(np.ones(G.shape[0])@G)) < 1e-12
assert np.max(np.abs(G@Pi)) < 1e-12
assert np.max(np.abs(P.sum(axis=0)-1)) < 1e-12
assert np.max(np.abs(K-Gamma[None,:]*P)) < 1e-12
print("C2d2C2-B orbit cache: PASS")
