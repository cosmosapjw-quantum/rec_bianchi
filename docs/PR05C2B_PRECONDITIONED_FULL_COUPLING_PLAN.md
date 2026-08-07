# PR-05C2B — angle-resolved thermodynamic full-coupling plan

## Entry evidence

PR-05C2A/v0.63 establishes a conservative direction-resolved pilot on the frozen v0.50 COM grid, but proves that a fully source-identical anisotropic native/COM coupling is not currently identified. Four independent blockers are load-bearing:

1. original-HyRec native boundary history has angular rank one, whereas number plus spatial momentum requires at least four independent angular moments and the locked collocation has 26 directional values;
2. the COM state stores cell averages and provides no source-defined face trace, so P0 upwind is an explicit numerical closure;
3. the source-temperature physical mode measure differs from the frozen v0.50 grid by up to about 9.5 percent;
4. the canonical macro collision stiffness number is `8.5e8`--`1.55e9`, so the one-second pilot does not justify an unpreconditioned macro solve.

## B1. Angle-resolved native exterior state

Introduce a new, explicitly downgraded Bianchi extension rather than relabelling scalar original HyRec as angle resolved.

```text
AngleResolvedNativeHistory
NativeAngularClosureRegistry
NativeMomentLedger
NativeAngularRestartState
```

Primary closure candidate:

- isotropic atomic source in the local hydrogen frame;
- directional free streaming from actual `BackgroundSnapshot` characteristics;
- positive filtered spherical-harmonic or positive collocation representation;
- exact recovery of the original-HyRec scalar monopole in the FLRW/isotropic limit;
- explicit uncertainty envelope comparing isotropic lifting, minimum-flux positive lifting and filtered-P_N evolution.

Hard gates: positivity, monopole parity, photon number, redshift work, restart, angular refinement and fixed-local-state geometry firewall. No unique momentum claim is allowed until the closure is fixed and its uncertainty reported.

## B2. Source-temperature COM network family

Compile or reconstruct the COM--KHW network on a controlled temperature grid spanning the three source windows.

```text
T ≈ 2458 K, 3003 K, 3549 K
plus midpoint/refinement nodes
```

For every node lock:

- physical frequency faces and mode measures;
- equilibrium weights and momentum scale;
- pair and same-cell conductances;
- detailed balance, number, entropy and four-force gates;
- source hashes and interpolation convention.

A dynamic adapter may interpolate only positive conductances or their logarithms and must reproduce directly compiled validation nodes. A simple Doppler-width rescaling of the v0.50 network is forbidden unless derived term by term.

## B3. Face-reconstruction hierarchy

Treat face reconstruction as a declared numerical model.

1. P0 upwind baseline;
2. positivity-limited piecewise-linear reconstruction;
3. nested frequency-grid refinement with directly recompiled cell kernels;
4. face-flux, number, exact face-energy and entropy convergence.

P0 remains the robust fallback; a higher-order method becomes production only if refinement is monotone and positivity preserving.

## B4. Harmonic-block/AP preconditioner

Build a collision-dominant preconditioner in the harmonic basis.

```text
analysis  -> per-(ell,m) 35x35 collision block
null mode -> explicit photon-number constraint/deflation
transport -> diagonal or low-rank correction
synthesis -> directional grid
```

Compare:

- diagonal loss preconditioner;
- harmonic block factorization;
- micro-macro/asymptotic-preserving reduction.

Hard gates at canonical macro `dt=DLNA/H`:

- Newton and Krylov convergence without fitted relaxation;
- JVP below `1e-8`;
- backward error below `1e-11`;
- exact number and face-energy ledgers;
- strict positivity and nonpositive collision free-energy production;
- iteration counts stable under angular/frequency refinement.

## B5. Coupled adaptive macro windows

Only after B1--B4 pass, run at least four canonical macro intervals around each of `z~1300,1100,900` for FLRW, Bianchi II, class-B `VI_h` and exceptional `VI_-1/9`.

The accepted-history transaction remains unchanged: arbitrary microsteps do not mutate the canonical history, and each successful macro endpoint commits exactly one slice. All boundary-speed and branch events are localized from actual `BackgroundSnapshot` data.

## Completion decision

PR-05C2B may close in one of three ways:

- `PASS_FULL_COUPLING`: all source-temperature, angular-closure, face, preconditioner and conservation gates pass;
- `PASS_EXPLICIT_CLOSURE_WITH_UNCERTAINTY`: a noncanonical angular/face closure is adopted with quantified convergence and uncertainty;
- `PASS_BOUNDED_NO_GO`: one of the required measures remains underidentified or no stable macro solver is found without an unjustified fit.
