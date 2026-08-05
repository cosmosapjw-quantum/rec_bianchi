# PR-04B2B native/common partition no-go

## Conventions and dimensions

We keep `g=(-,+,+,+)`, ordinary frequency `nu` in Hz,
`x=(nu-nu_Lya)/Delta_nu_D`, `Delta nu=nu_target-nu_source`,
`Delta E_gamma=h Delta nu`, and `Delta E_H=-h Delta nu`.  The coordinate `x`
is dimensionless; the positive native edge weights have units `s^-1` per H.
Raw moment `M_r=sum_b J_b x_b^r` therefore retains units `s^-1` per H.

## Canonical table representation

The production and high-resolution members have five columns: one energy
centre and four rates already integrated over a latent `Delta nu_b`.  The
runtime reads exactly those five values.  The canonical runtime archive has no
numerical edge column, no dedicated two-photon-table generator member, and no
source statement that opens either bundled table for writing.  Consequently
midpoint, Voronoi, maximum-entropy, or optimal-transport cells would be new
modelling closures rather than recovered canonical metadata.

The two centre grids are not nested: the number of exact production-centre
matches in the high-resolution table is `0`.
Only `2` production and
`2` high-resolution
diffusion centres lie in the v0.51 core `[-4.25,4.25]`.

## Theorem 1 — positive support obstruction

For every positive target measure supported on `[-a,a]`,

```text
M2/M0 = integral x^2 dmu / integral dmu <= a^2.
```

Here `a=4.25`, so the sharp target bound is `1.80625000000000000e+01`.  The locked
v0.53 native physical edge measure gives

```text
full 311-state M2/M0 = 1.34470774977335602e+08,
diffusion-80 M2/M0   = 2.18087287530050562e+04.
```

Both violate the bound.  Therefore no nonnegative map to the 17-cell core can
preserve even `M0` and `M2` of the full native measure.  This conclusion is
independent of interpolation order or optimizer.

Restricting to the two native centres inside the core does not repair
conservation: it retains only
`1.73617800454452546e-03` of the full native
edge mass and `6.55001298797270193e-03`
of the diffusion-80 mass.

## Theorem 2 — moment constraints do not identify 17 masses

For any fixed target-cell basis, moments `r=0,...,4` produce a matrix with five
rows and seventeen columns, hence rank at most five and nullity at least twelve.
For the explicit uniform-within-cell finite-volume basis, exact rational
arithmetic gives rank `5` and nullity `12`.
The artifact supplies two distinct strictly positive cell-mass vectors with
identical moments; the exact moment difference is zero.  Thus those five
moments cannot choose a unique map without additional physical closure.

As controls, the actual two-core-centre moment vector is infeasible under both
a cell-centre Dirac basis and a uniform-within-cell basis.  These failures do
not prove every conceivable sub-cell closure impossible; they prove that the
most common silent closures are not hidden canonical solutions.

## Decision

A direct native-to-17-cell equality is rejected.  PR-04B2B closes as an
informative no-go, while PR-04 remains open.  The next route is a split-domain
conservative exchange contract: native transport retains its full frequency
support; the COM--KHW core retains its positive event measure; only explicitly
source-derived boundary photon-number and energy fluxes are exchanged.  No
arbitrary member of a moment-equivalent family is promoted as canonical.
