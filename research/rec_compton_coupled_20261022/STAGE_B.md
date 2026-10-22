# Stage B: native full63 implementation and preflight

Runtime identity: `c89f576e2c7f15a0a1d0d3f96ce72de516245cbb83b5d4fbaeede342a76e86ac`.

The frozen adapter changes only the logT source/Jacobian row at a common state,
precomputes UV moments once, and uses a compact exact Hubble gradient.
The coupled BDF still evolves all63 coordinates. The source-only affine
relaxation oracle is not substituted for the complete solver.

Actual author tests:9/9. Independent driver helper tests:4 demonstrated
failures preserved, then the identical6 tests passed after minimal fixes.
Independent complete63x63 Jacobians:4, maximum entry-scaled discrepancy
1.907738655175594e-8 against3e-6. Energy/source/ledger checks agree.

Evidence/PREFLIGHT_ADMISSION.json binds the current runtime and actual
review/test/source receipts (the directory is lowercase `evidence`).
The first new IVP and remaining7 are now admitted under the frozen finite
allocation. No new solved trajectory is claimed at this source snapshot.
