# Research Basis — Angular Representation for the REC Physical Donor

## Research question

Is the existing ordered 26-direction discretization sufficient as the physical directional donor for anisotropic recombination, or should it be retained only as one projection of a grid-independent donor?

## Prior state

The repository already has a typed 26-point hydrogen-frame quadrature and a manufactured 52-ray red/blue geometry witness. Its own admission logic retains `physical_face_admitted=false` because directional source authority and external verification are absent.

## Seed inputs

- TEFF Paper I: angular and spectral information losses must be measured separately; the supplied benchmark is solver-free.
- TEFF Paper II: moment fibers, realizability, entropy contraction, and minimum-information reconstruction; it explicitly does not provide a transport closure or inversion algorithm.
- Direct transport literature: Lagrange discrete ordinates, filtered moments, entropy closures, rotated/artificial-scattering discrete ordinates, and adaptive spherical meshes.

## Competing hypotheses

- H0: fixed 26-point state representation.
- H1: nested higher-order Lebedev state sequence.
- H2: global spherical-harmonic/PSTF state.
- H3: positive adaptive spherical mesh/discrete ordinates.
- H4: low-order harmonic backbone plus positive adaptive residual.
- H5: entropy/minimum-information directional lift from moments.

## Decision rule

Reject a candidate as physical donor authority if it fails any of:

1. reconstructibility independent of one named quadrature;
2. causal source/characteristic provenance;
3. controlled rotation sensitivity;
4. half-range and narrow-beam convergence;
5. total-occupation realizability;
6. independent angular and spectral refinement;
7. exact projection and ordering receipts.
