# C8 — precision, reproducibility and measured resources

## Precision at the claimed scale

The source delta is formed exactly before binary64 conversion. The independent80-digit reference checks the small I and D directly; their largest observed relative errors are3.011593202799463e-16 and2.999772662453845e-16 against the fixed2.842170943040401e-14 limit. The margin reflects implementation roundoff agreement and is not an estimate of laboratory/source-data error.

The independent C9 audit additionally evaluated two delicate line1 cases at100 Decimal digits using positive fluxes and (exp(xnu)-exp(xE))/(exp(xE)-1), importing neither production module nor the80-digit reference. The smallest D at200K is4.1745971013940654e-12. Its production relative error is1.610389687317524e-16. The maximum relative-D-error case at100K has D=5.470240070099096e-12. The saved80-digit values agree with the separate100-digit results at roughly1e-68 relative.

For history, exact rational equality is the acceptance criterion; there is no tolerance widening or estimated floating residual. Display floats are checked against saved exact records. The reviewer reconstructed all313 native-real query values independently from original endpoint witnesses and audited all1240 retiming identities,313 chord identities and5127 clock records. A synthetic cancellation case verifies zero signed error with positive bound6. The actual selected chord cases happen to have no strict cancellation; that observation is not generalized to all histories.

## What is reproducible

The source, parser, history and context identities are frozen. Receipts record exact commands, code identities, Python/library environment, threading and limits. Saved JSON carries exact rational numerators/denominators; CSV and figures provide display forms. The plots read saved results, and all primary history result bytes remain unchanged in the plot receipt. The independent audit found22 current frozen paths unchanged. Both actual PNGs were inspected by parent and reviewer.

The C5 Git commit8ef3abe1f3a463e63d2e4897800f738455cee834 contains code, raw results and all four PNG/PDF artifacts; its1,449,327-byte full-stage ZIP is backed up to both providers. The separate binary blob publication acknowledgements are in the C5 delivery receipt. Source hashes and exact payload manifests support restoration. We did not repeat a primary solely to claim a second identical execution, and do not claim that timestamps or PDF metadata are universally byte-deterministic.

No mesh-refinement study, global ODE convergence campaign, performance speedup comparison or physical stability calculation was run. Exact finite-representation identities and the fixed-precision HD diagnostic are the numerical claims being verified.

## Measured resource use

| Phase | Controlled CPU s | Wall measurement | Peak child/process RSS |
|---|---:|---|---:|
| HD primary, controls, figure and measured wrapper |4.301855738|child4.376630457s|82148KiB|
| History primary and measured supervisor |6.109471|6.151483030s|69660KiB|
| History saved-output figure and measured supervisor |3.260151|3.302582492s|85992KiB|
| Independent saved-result audit |0.442506|0.397330989s after imports|59172KiB|
| **Measured local controlled total** |**14.113983738**|different scopes, not summed as elapsed duration| |

All local children obeyed the frozen per-process caps and exited0. The HD/history unit debits are4.301855738/360 and9.369622/360 CPU seconds. The reviewer audit debits the separate180-second integration allocation. The successful R7 Wolfram check is reused; its remote CPU/memory were not exposed. Its20-second planning reservation is not a measured CPU debit. Preparation/source/publication metadata and unmeasured tails remain UNKNOWN_NOT_ZERO. Detailed current and historical preservation rules are in BUDGET_LEDGER.json.

Unused allowance does not authorize another unit or a replay. Original REC caps/debits, failed attempts, GEO01 results and foreign REI limits remain preserved.

