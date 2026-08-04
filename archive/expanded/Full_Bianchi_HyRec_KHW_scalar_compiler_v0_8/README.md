# Full Bianchi–HyRec scalar KHW compiler v0.8

This bundle locks the scalar fixed-nucleus bound+continuum
oscillator-strength compiler and the algebraic extension to
center-of-mass-resolved denominators.

## Verified sum rules

- Bound f-sum: 0.565004150675
- Continuum f-sum: 0.434995849325
- Total TRK sum: 1.000000000000
- Static polarizability: 4.500000000000 bohr^3

## Ly-alpha pole/background coefficients

A0 = f12/2 = 0.208098358989991

Modern exact oscillator-strength reconstruction:

| coefficient | value | ratio to A0 |
|---|---:|---:|
| A1 | -0.188409718890 | -0.905387816630 |
| A2 | -2.551443706415 | -12.260758416348 |
| A3 | -10.955622682401 | -52.646367494557 |
| A4 | -50.815205355507 | -244.188400149523 |
| A5 | -252.141960468080 | -1211.647999973930 |

The first relative cross-section coefficient is

    -1.810775633259

rather than Lee's listed -1.7922.  The discrepancy is retained as an
open audit finding; this bundle does not label the older result an error.

## Compiler formula

For each discrete or continuum transition s,

    M = 1 - 1/2 Sum_s f_s Delta_s
                  [1/D_s^- + 1/D_s^+].

The 2p absorption pole is isolated.  The crossed 2p term, higher bound
states, continuum, and seagull term remain in the smooth background.

In the fixed-nucleus elastic limit the TRK sum converts this to the
usual dynamic-polarizability form.

## Files

- `scalar_COM_compiler.py`
- `verify_scalar_compiler.wl`
- `compiler_ledger.json`
- `coefficient_decomposition.csv`
- `near_resonance_spot_checks.csv`
- `MANIFEST_SHA256.txt`

## Primary literature anchors

- Rohrmann & Vera Rueda (2022), arXiv:2208.02111.
- Kokubo (2024), arXiv:2308.04959.
- Lee (2003), arXiv:astro-ph/0308083.
- Lee & Kim (2004), arXiv:astro-ph/0402023.
