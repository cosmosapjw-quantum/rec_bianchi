# Full Bianchi-HyRec C3B2B0 v0.29

This bundle locks the physical Ly-alpha cross-section convention and
audits the angular grids proposed for the next COM-KHW regeneration.

## Physical normalization

- integrated oscillator-strength cross section:
  1.104589773129e-06 m^2 Hz
- line-centre cross section at 3000 K:
  1.075770516663e-17 m^2
- line-centre cross section:
  1.075770516663e-13 cm^2
- example line-centre rate at n_H=250 cm^-3:
  8.062697185855e-01 s^-1

## Angular result

For the kappa=8 non-polynomial zonal preflight:

- 38 points: 1.240695e-02
- 50 points: 1.384360e-03
- 86 points: 5.850828e-06
- 146 points: 1.174199e-08
- 194 points: 1.513698e-11

Thus 38/50 are useful diagnostics but are not accepted as the final
angular reference before the actual COM-KHW kernel is recomputed.

## Status

- normalization source lock: PASS
- Lebedev registry: PASS
- physical rate-kernel regeneration: OPEN
- common-measure FP regression: OPEN
- monolithic HYREC/Bianchi substitution: NOT APPROVED
