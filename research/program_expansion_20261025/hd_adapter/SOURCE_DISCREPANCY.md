# Exact source discrepancy retained under the original 35 Hz gate

For the pinned source, the independent Fraction calculation and the adapter's
80-digit Decimal calculation agree exactly on

`abs(299792458*100*(E_u_cm_inverse-E_l_cm_inverse) - 1e9*nu_GHz)`.

| Source line | Transition | Absolute discrepancy (Hz) | Fixed 35 Hz criterion |
|---|---|---:|---|
| 1 | J=1→0 | 8.241016200 | PASS |
| 2 | J=2→1 | 947678.840324000 | FAIL |
| 3 | J=3→2 | 1084318.742916400 | FAIL |
| 4 | J=4→3 | 47627.409091400 | FAIL |
| 5 | J=5→4 | 1245461.910729000 | FAIL |
| 6 | J=6→5 | 1827572.560757200 | FAIL |
| 7 | J=7→6 | 1411205.450255200 | FAIL |
| 8 | J=8→7 | 6864.989622800 | FAIL |

The gate's rounding allowance remains
`2*(0.5e-9 cm^-1)*c*100 + 5 Hz = 34.9792458 Hz`, rounded outward to 35 Hz.
The observed seven differences exceed that allowance. Their physical/source
mechanism has not been identified. No source column is corrected, no frequency
is substituted and no tolerance is enlarged in this unit.

The previously recorded J=1→0 scalar reference is consistent with its own line.
That single-line result cannot establish the seven other line relations. Literal
parsing can preserve both columns; a consumer requiring a common internal and
photon transition energy uses the explicit per-line refusal gate.

`raw/attempt1/unittest.stderr.txt` retains the first failed criterion, and
`raw/source_diagnostic/diagnostics.json` records all eight actual differences.
The first chat notification mistakenly called the failure line 1 before the full
row map was printed; it was corrected immediately to line 2. Files and all final
records use the actual row identities above.

The separate 54 detailed-balance and 24 thermal Kirchhoff checks satisfy their
unchanged 128-epsilon roundoff criterion. Their distinct energy conventions are
stated in README.md. This is a bounded source-data discrepancy, not a no-go theorem
or a physical rejection of HD spectroscopy.
