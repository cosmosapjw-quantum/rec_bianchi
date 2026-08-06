# Phase 6 — Validation and Dimensional Closure

The exact adapter is byte-derived rather than inferred: `FR00` is state 29 on
`[-21.25,-16.25]` and `FB02` is state 34 on `[16.25,21.25]`. For each packet,
`Delta f = sigma n_H Delta t Phi_N/g_cell`; normalized angular weights close
this identity to roundoff. Exact transported energy remains `h nu_face Delta N`.
The finite-cell centroid mismatch is retained as an unresolved representation
correction, never converted into atom recoil.

The three source-conditioned solves give maximum normwise backward error
`1.3200190226745005e-17` and maximum number residual `2.5609198306764287e-14`. The
ordinary net residual normalized only by the dilute occupation reaches a
float64 cancellation floor near `1.7e-10`; this is not relabelled as a strict
net-residual pass. Convergence requires both a gross-term backward error below
`1e-11` and independent number closure below `1e-11` after Newton stagnation.
