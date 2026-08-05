# PR-04C literature basis — conservative coupling without a global remap

## Scope

This note records the external numerical-analysis basis for the PR-04C design.
It is not used as evidence for the v0.54 no-go, which follows from the locked
HyRec tables and exact moment/support calculations.  It constrains the next
implementation route after that no-go.

## 1. Positive quadrature existence does not supply the missing canonical map

Tchakaloff-type results establish the existence of a finite positive quadrature
of prescribed degree for a positive compactly supported measure.  That theorem
does not assert that an arbitrarily fixed 17-cell support can represent a
source measure whose normalized second moment lies outside the target support
bound, and it does not choose a unique rule when a fixed moment system has a
nontrivial null space.  Thus it is compatible with both v0.54 results:

```text
support obstruction: M2/M0(source) > 4.25^2,
identifiability:      rank/nullity = 5/12 for 17 target masses.
```

Reference:

- R. E. Curto and L. A. Fialkow, *A duality proof of Tchakaloff's theorem*,
  arXiv:math/0207065.

## 2. Conservative positive remapping requires an explicit source/target
##    relation

Conservative positivity-preserving transfer methods are constructive only after
source and target cells, their intersections/evolution, and the conserved
measure have been specified.  The original-HyRec runtime tables provide centre
values and width-integrated coefficients but no numerical source-cell edge
array or canonical table-generation map.  A midpoint, Voronoi, maximum-entropy,
or optimal-transport remap would therefore add a new closure rather than recover
an existing one.

Reference:

- M. Zhang, W. Huang, and J. Qiu, *High-order conservative
  positivity-preserving DG-interpolation for deforming meshes and application
  to moving mesh DG simulation of radiative transfer*, SIAM J. Sci. Comput. 42
  (2020), DOI 10.1137/19M1297907; arXiv:1910.11931.

## 3. Nonmatching representations can be coupled through an interface flux

Mortar and flux-mortar formulations provide a relevant architectural analogue:
subdomains retain nonmatching discretizations, while an interface trace or flux
variable enforces the desired conservation/continuity condition weakly.  PR-04C
adopts only this structural principle, not the elliptic PDE formulation itself.
The proposed spectral interface variable is a same-event photon-number and
photon/atom-energy flux packet, evaluated once and entered with opposite signs
in the native and COM--KHW ledgers.

References:

- T. Arbogast, L. C. Cowsar, M. F. Wheeler, and I. Yotov, *Mixed finite element
  methods on nonmatching multiblock grids*, SIAM J. Numer. Anal. 37 (2000), DOI
  10.1137/S0036142996308447.
- W. M. Boon, D. Gläser, R. Helmig, and I. Yotov, *Flux-Mortar Mixed Finite
  Element Methods on NonMatching Grids*, SIAM J. Numer. Anal. 60 (2022), DOI
  10.1137/20M1361407; arXiv:2008.09372.

## 4. HyRec representation boundary

Original HyRec evolves the radiation field together with level populations and
the free-electron fraction, including Ly-alpha frequency diffusion in a full
radiative-transfer calculation.  Therefore the native transport representation
must remain a first-class dynamical subsystem; it should not be replaced by a
17-cell moment fit.  PR-04C instead couples it conservatively to the independently
verified COM--KHW collision subsystem.

Reference:

- Y. Ali-Haïmoud and C. M. Hirata, *HyRec: A fast and highly accurate primordial
  hydrogen and helium recombination code*, Phys. Rev. D 83, 043513 (2011),
  arXiv:1011.3758.

## Design consequence

The bounded PR-04C implementation shall therefore:

1. retain each representation on its native support;
2. declare one owner for every local collision, redshift, escape and interface
   contribution;
3. exchange only source-derived number and energy flux packets;
4. avoid any fitted normalization or silently selected moment-equivalent map;
5. prove discrete cancellation, positivity and JVP parity at the interface.
