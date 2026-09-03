# CRAG adversarial audit — REC/BASS dual representation

## Correctness

The exact source-product oracle distinguishes three objects that were previously at risk of being conflated:

1. output rank `L_out`;
2. source-rate rank `L_chi`;
3. numerical distribution work rank `L_work`.

For `L_out=L_chi=2`, the exact target source contains rank-three/rank-four distribution contributions. `L_work=4` reconstructs it exactly in the axisymmetric polynomial witness; `L_work=2` does not.

The anisotropic jump witness independently shows that an exponential transmission is not band-limited even when optical depth is. Thus the polynomial source buffer theorem cannot be reused for the virtual spike.

## Retrieval

The SciSpace literature survey found mature methods that combine harmonic source representations with discrete-ordinate streaming, including scalar and vector SHDOM. It also found positivity-preserving geodesic angular finite elements that are competitive where either discrete ordinates or filtered harmonics fail. These support the dual-representation architecture and low-regularity fallback, but none supplies the REC source coefficients or BASS conventions.

The two TEFF papers support diagnostic separation of radial/spectral and angular information loss. Their own scope statements exclude transport dynamics and solver claims, so they are not used as closure authority.

## Augmented checks

The R2 claim was attacked by the following alternatives:

- **same cutoff mutation:** set `L_work=L_out`; rejected by a nonzero exact residual;
- **source isotropy control:** set `L_chi=0`; the extra buffer disappears as expected;
- **jump finite-tail mutation:** assume finite-rank `tau` implies finite-rank `exp(-tau)`; rejected by nonzero coefficients through every tested rank and leading order `alpha^ell`;
- **entropy-closure mutation:** replace the full BASS state by the TEFF representative; rejected by the papers' spectral-shape remainder and non-substitutability theorems;
- **26-node authority mutation:** drop parent state/source identities; rejected by the R2 contract;
- **signed-opacity mutation:** discard `(eta,kappa)` and require `chi>=0`; rejected because a physical positive pair may have `chi<0`.

## Generation

The derived structure predicts four likely implementation failures:

1. low-output PSTF source tests may pass while silently missing `L_out+L_chi` work-rank couplings;
2. the virtual-spike PSTF path will converge more slowly than the smooth affine-source path as optical-depth anisotropy grows;
3. if TEFF spectral and angular tails are both small but grid/PSTF residual is large, the defect is likely in the adapter, quadrature, convention or time integration rather than unresolved physical information;
4. a grid/PSTF comparison against `grid_coupled.G_a` can be invalid if it is mistaken for the full spectral grid state.

## Plot attempt and evidence boundary

A Wolfram plot of the anisotropic-jump harmonic tail was requested after the exact coefficient calculation, but the rendering call returned an upstream 502. Local Python/container plotting was also unavailable. No visual claim is therefore made. The machine evidence retained here is the exact coefficient series and source-projection residual in `WOLFRAM_RECEIPT.json`.

## Final classification

```text
SURVIVING
  one REC source authority can feed both BASS evolution representations
  exact all-rank source projection commutes with the distribution-to-PSTF map
  polynomial-rate source projection needs a work-rank buffer
  anisotropic exponential jumps need adaptive tail control
  TEFF quantities are useful independent information diagnostics

NARROWED
  BASS supports both architectures, but the inspected numerical grid slices have bounded family/mass/polarization scope
  no-moment-truncation does not mean no grid/time/interpolation error

REJECTED
  REC should own a third continuous evolution state
  the output cutoff can always be used as the source work cutoff
  finite-rank optical depth gives a finite-rank exact jump
  TEFF matching identifies the full distribution
  26-direction values are physical state authority
```
