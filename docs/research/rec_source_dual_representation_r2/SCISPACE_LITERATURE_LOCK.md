# SciSpace literature lock — dual angular representations

This literature set supplies methodological comparison only. It does not choose project signs, Formula IDs, repository ownership, source bytes, or admission status.

## Hybrid direct-angular / harmonic methods

1. **K. Franklin Evans, “The Spherical Harmonics Discrete Ordinate Method for Three-Dimensional Atmospheric Radiative Transfer,” Journal of the Atmospheric Sciences 55 (1998), 429–446, DOI 10.1175/1520-0469(1998)055<0429:TSHDOM>2.0.CO;2.**
   
   Admitted role: demonstrates a mature algorithmic split in which the source function is represented in spherical harmonics while transport is integrated along discrete ordinates, with adaptive refinement. This supports treating direct-angle and harmonic forms as cooperating representations rather than competing physical theories.

2. **A. Doicu, D. Efremenko and T. Trautmann, “A multi-dimensional vector spherical harmonics discrete ordinate method for atmospheric radiative transfer,” Journal of Quantitative Spectroscopy and Radiative Transfer 118 (2013), 121–131, DOI 10.1016/J.JQSRT.2012.12.009.**
   
   Admitted role: vector/polarized extension combining generalized spherical harmonics with discrete ordinates. It supports a later polarized dual-representation adapter but does not establish the REC source terms or BASS screen convention.

3. **M. K. Bhattacharyya and D. Radice, “A finite element method for angular discretization of the radiation transport equation on spherical geodesic grids,” Journal of Computational Physics 492 (2023), 112365, arXiv:2212.01409, DOI 10.1016/j.jcp.2023.112365.**
   
   Admitted role: compares discrete ordinates, filtered spherical harmonics and a positivity-preserving spherical finite-element representation. It supports retaining a low-regularity angular fallback rather than forcing every state or face mask into one global harmonic cutoff.

4. **O. Palii, “On approximation methods and efficient iterative solvers for the Radiative Transfer Equation,” University of Twente dissertation (2022), DOI 10.3990/1.9789036553889.**
   
   Admitted role: documents complementary strengths of global spherical harmonics and local/discontinuous angular discretizations and warns that mixed methods can introduce consistency errors unless the split is analysed.

## Entropy and realizability references

5. **M. R. A. Abdelmalik, Z. Cai and T. Pichard, “Moment Methods for the 3D Radiative Transfer Equation Based on phi-Divergences,” arXiv:2304.01758; Computer Methods in Applied Mechanics and Engineering 418 (2024), 116454.**
   
   Admitted role: shows how divergence/entropy geometry can support symmetry, equilibrium and realizability properties of a moment model. In this project it is only a comparison: TEFF diagnostics must not be promoted into a closure for the BASS distribution.

6. **C. Liu, W. Li, P. Song and K. Xu, “An entropy preserving implicit unified gas-kinetic wave-particle method for radiative transport equation,” arXiv:2302.07945.**
   
   Admitted role: illustrates regime-adaptive representation while retaining nonequilibrium distribution dynamics rather than imposing one artificial closure. It motivates, but does not validate, the project’s dual-representation verification strategy.

## Project interpretation

The literature supports four limited conclusions:

- direct-angle and harmonic/PSTF representations can be combined in one solver architecture;
- the source/projection split needs an explicit consistency theorem and numerical residual;
- angular regularity can determine which representation is efficient, but not which physical equation is true;
- entropy and realizability are useful diagnostics or invariant-domain tools, but an entropy representative is not automatically the fine distribution.

None of the cited work establishes grid/PSTF numerical parity for BASS, a source-complete REC donor, a physical 26-direction face, or provider readiness.
