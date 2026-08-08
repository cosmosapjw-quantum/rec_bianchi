# PR-05C2C — direct thermodynamic network family and native angular evolution

## Entry result

PR-05C2B/v0.64 runs one canonical macro interval for all nine locked
redshift/background lanes after replacing the dominant Python pair loops and
using a hybrid diagonal-GMRES / batched-dense reference solver.  It closes only
as an explicit noncanonical angular/face/thermodynamic closure: selected direct
COM–KHW pair ratios differ from the positive symmetric thermodynamic closure by
up to about 31 percent, and scalar original-HyRec boundary data do not identify
an angular distribution.

## C1. Direct source-temperature network family

Compile every pair and same-cell block directly at locked thermodynamic nodes
covering the z~900, 1100 and 1300 windows.  Add midpoint and refinement nodes.
Interpolate only positive reciprocal conductances (prefer log conductance) and
validate withheld nodes.  Required gates:

- photon-number left null and BE right null;
- reciprocity and nonnegative scalar conductance;
- entropy production and same-event four-force;
- interpolation analytic JVP;
- refinement and withheld-node relative error;
- exact v0.50 parity at the 3000 K reference.

No fitted global normalization is allowed.

## C2. Angle-resolved native boundary evolution

Do not infer 26 directional values from one scalar datum.  Evolve a declared
positive angular representation from the isotropic FLRW limit using actual
Bianchi photon characteristics.  Lock monopole, dipole and higher-moment
ownership separately.  If a closure is still needed, publish its moment order,
positivity domain and uncertainty; never call it canonical original HyRec.

## C3. Production face trace

Promote positivity-limited MUSCL or a low-order DG trace only after:

- frozen-limiter or semismooth JVP parity;
- no new extrema and strict positivity;
- photon number and exact face-energy conservation;
- event localization when the active limiter branch changes;
- nested frequency-grid refinement.

P0 remains the fail-safe fallback.

## C4. Multi-macro adaptive trajectory

Run at least four canonical macro intervals per independent z~900, 1100 and
1300 window for Bianchi II, class-B VI_h and exceptional VI_-1/9.  Every
successful macro commits one history slice; rejected trials and event rollback
must preserve parent bytes exactly.

## C5. Completion gates

- full analytic JVP < 1e-8;
- gross backward and algebraic residuals < 1e-11;
- photon number, exact face energy, redshift work and collision four-force;
- strict positivity without clipping;
- nonpositive collision free-energy production;
- event-time and tolerance refinement;
- direct thermodynamic withheld-node convergence;
- deterministic restart and fixed-local-state geometry firewall.

If direct network-family generation remains too expensive, optimize the
scientific quadrature itself with cacheable state-independent factors and
parallel independent pair blocks, while preserving the exact reference lane.
## C6. Performance and lightweight execution contract

Direct network generation must not repeat state-independent symbolic and radial
factors for every thermodynamic node.  Factor the compiler into cacheable
atomic pieces, pair-local thermodynamic pieces and final positive conductance
assembly.  Independent pair/same-cell blocks may run in separate processes,
with deterministic ordered reduction and per-block SHA-256 receipts.

The runtime solver must retain three tiers:

1. an exact scalar-pair audit oracle;
2. a vectorized matrix-free production action/JVP;
3. a bounded batched-dense reference only for small cancellation-dominated
   lanes.

Profile and gate wall time, peak resident memory, Newton iterations and GMRES
iterations.  Reuse immutable network/background/angular caches across
redshift/geometry lanes, avoid dense identities, and stream large diagnostic
arrays rather than retaining all trial states.  No optimization may alter the
number null, BE null, reciprocity, positivity, entropy or four-force gates.
