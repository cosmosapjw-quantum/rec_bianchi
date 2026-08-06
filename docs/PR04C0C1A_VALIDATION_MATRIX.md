# PR-04C0/C1A validation matrix

| Lane | Targets | Expected |
|---|---|---|
| source guard OFF | canonical compile/run | binary and history hashes exact |
| source guard ON | z~1300,1100,900 | history hash exact; two interface rows each |
| Python reconstruction | all six packets | max relative residual `<3e-13` |
| current-endpoint case | at least one packet | right index equals current solved index, never exceeds it |
| packet validation | all six | positive total; exact component additivity; atom source zero |
| ownership registry | all declared processes | no duplicates/missing/extra |
| ledger | all six | evaluation 1, native application 1, COM application 1, exact cancellation |
| Bianchi firewall | II, V, `VI_-1/9` | identical packet SHA-256 |
| Wolfram | symbolic scalar identities | positivity and exact cancellations |
| PSF/mpmath | `zeta(3)`, `Gamma(3)` | 100-digit independent parity |
| replacement switch OFF | arbitrary finite states | exact copied states and zero ledger |
