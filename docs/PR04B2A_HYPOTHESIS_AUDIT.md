# PR-04B2A hypothesis and adversarial audit

## H1 — direct finite-volume identification

`x_v` or `x_v/x_1s` is the photon number in an inferred native frequency cell.

**REJECTED.** The v0.52 physical-weighted left-null residual is
`5.243277338650812e-3`. The canonical source uses the virtual population as an
algebraic representation of radiation intensity. Reintroducing this route
would revive a superseded normalization error.

## H2 — physical edge-flux identity

The native escape-compressed algebra maps exactly to physical photon flux across
a logarithmic-frequency spike through the incoming/outgoing occupation jump.

**VERIFIED.** With

```text
A_b   = 8 pi nu_b^3/(c^3 n_H),
tau_b = x_1s Gamma_b/(H A_b),
P_b   = (1-exp(-tau_b))/tau_b,
```

one has

```text
x_1s Gamma_b (f_eq-fbar_b)
  = x_1s Gamma_b P_b (f_eq-fplus_b)
  = H A_b (fminus_b-fplus_b).
```

The exact symbolic residual is zero, the 100-digit relative residual is
`2.214e-101`, and the cancellation-safe float64 structural residual is
`3.414e-15`.

## H3 — raw primitive-rate substitution

`Aup/Adn` can be multiplied by v0.51 mode weights and used as the physical
COM–KHW generator.

**REJECTED.** These rates belong to a real/virtual algebra with line-centre
states, escape compression, bin-integrated sources, and a proxy left measure.
No source-derived cell normalization supports direct substitution.

## H4 — full PR-04 closure from one snapshot

One successful edge-flux identity proves the entire 17-cell COM–KHW/native
projection and full FLRW parity.

**REJECTED AS OVERCLAIM.** The locked trajectory closes source-identical
normalization and primitive/direct/Schur edge parity. It does not define a
measure-preserving map from 80 native diffusion bins to 17 production cells,
sub-cell conditional jump moments, or an all-redshift coupled trajectory.

## H5 — bounded PR-04B2A closure

A durable intermediate release can close canonical provenance,
source-identical instrumentation, physical edge normalization, and
primitive/Schur spectral-source parity while leaving direct 17-cell production
parity open.

**VERIFIED AND SELECTED.** This is the smallest coherent stage consistent with
the coding and research harnesses. It preserves fail-closed claims and leaves
PR-04 in progress.

## H6 — centre-overlap parity

Two native centre frequencies inside `|x|<=4.25` are enough to compare the
native edge source directly with the v0.51 17-cell event tensor.

**REJECTED.** Centre inclusion does not specify source/target cell boundaries,
cell measure, or conditional jump moments. The compared aggregates also differ
in state dependence: native edge flux is an escape-compressed net trajectory
source, while v0.51 `C0` is an occupation-independent event mass.

## H7 — high-resolution source table as an automatic solution

The canonical `two_photon_tables_hires.dat` can be silently substituted for the
311-state production registry and thereby establish direct parity.

**REJECTED AS AN UNTESTED SHORTCUT.** The high-resolution table may be used in
PR-04B2B as an immutable *reference/refinement lane* only after its indexing,
normalization, and reduction to production `NVIRT=311` are audited. It must not
silently change the canonical production operator.
