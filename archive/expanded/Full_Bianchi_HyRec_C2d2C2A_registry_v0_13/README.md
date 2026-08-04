# Full Bianchi-HyRec C2d2C2-A registry v0.13

This artifact locks the geometry and memory layout for the first
17 x 26 scalar full-angle finite-volume Ly-alpha event-pair slice.

## Verified geometry

- 17 absorption-anchored frequency cells
- 26-point Lebedev rule
- 442 photon states
- 97,461 complete unordered edges
- 93,925 recommended active edges
- 1,972 scalar physics orbits
- 3,009 quadrature-weighted conductance orbits

The Lebedev rule integrates all 120 Cartesian monomials of total
degree at most 7 exactly; the Wolfram exact residual count is zero.

The scalar microphysics depends only on frequency pair and scattering
cosine. Endpoint Lebedev weight classes are tracked separately for
finite-volume conductance assembly.

The 3,536 same-direction
cross-frequency edges require an atom speed essentially equal to c.
They remain in the complete registry but are disabled by the
recommended active mask.

## Files

- geometry_registry.npz
- lebedev26_nodes.csv
- frequency_cells.csv
- state_registry.csv
- angular_orbits.csv
- physics_orbits.csv
- weighted_orbits.csv
- MEMORY_LAYOUT.md
- verify_registry.py
- verify_lebedev26.wl
- registry_ledger.json
- MANIFEST_SHA256.txt
