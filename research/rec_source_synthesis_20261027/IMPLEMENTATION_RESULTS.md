# C5 — complete implementation and observed primary results

Both delegated features ran through actual fixed input, calculation, independent/control checks, saved machine-readable output and scientific plots. Parent C4 GO followed Git commit1ba7efb5d99b4dcc75be313a63d81b1a31e7c0a3 and actual dual-provider ACK. Neither primary was rerun.

## HD path

`hd_joint/joint_diagnostic.py::joint_thermal` exposes the exact-source/stable-float diagnostic. `decimal_reference.py` independently evaluates positive fluxes and the original exponential source ratio at80 digits. The existing parser is reused without altering its qualification gate or collider data. The bounded runner produced24 actual rows,21 passing controls, JSON/CSV, raw stdout/stderr and PNG/PDF.

Observed maximum absolute I is8.770964953285911e-7; maximum absolute D is1.7541951787469943e-6. Maximum relative errors versus Decimal80 are3.011593202799463e-16 for I and2.999772662453845e-16 for D, below the frozen2.842170943040401e-14 threshold. The source/Planck ratio ranges from0.9999986454572667 to1.0000017541951787. The old35Hz source gate still fails7/8 lines.

The process exited0, stderr empty, child CPU4.286188s, wall4.376630457s, peakRSS82148KiB. Including measured wrapper CPU, HD debit is4.301855738s against360s. Metadata tails remain unknown rather than zero.

## Native-real represented-history path

`history_remainder/remainder.py::PiecewiseLinear` implements exact values, directional slopes, jumps, finite-retiming identities and Peano chords. The actual runner confirmed313 exact native-grid cell/source/sample/anchor bindings. It evaluated626 within-cell moves with exactly zero remainder,313 left crossings,301 right crossings,313 chords and30 passing controls. It recorded12 unavailable right crossings as SKIP_CAUSAL_PREFIX. All614 actual crossings are nonzero and detect omission of their jump term.

The maximum retiming remainder is1.8566648889656617e-19 and maximum chord remainder1.6749900771700771e-19, in dimensionless occupation departure. Direct and finite-sum expressions agree exactly as rationals and obey their absolute-jump bounds. Exact numerators and denominators are saved, alongside display values.

Maximum native-real versus stored-grid coordinate difference is4.71736365248443e-16 in eta. The maximum new nominal anchor radius is1.8495299543650757e-29; the preserved old geometric anchor is2.806325270875912e-28. These different reconstruction objects remain distinguished.

Primary and saved-output plot each exited0. Their combined measured controlled CPU is9.369622s against360s; peak child RSS is85992KiB. Plotting read saved scientific results, whose bytes remain unchanged.

## Actual output locations and review status

- HD: `hd_joint/raw/primary001/`, including DIAGNOSTICS, TARGETED_CONTROLS, SUMMARY, PREEXEC, EXECUTION and raw logs.
- History: `history_remainder/results/primary001/`, including retimings, chords, bindings, clock differences, skips, controls and summary; receipts/raw logs in `evidence/`.
- Figures: HD raw directory's `joint_thermal_diagnostics.png/.pdf`; history `figures/history_remainders.png/.pdf`.

Parent visually inspected both PNGs: HD signed diagnostic panels distinguish the35Hz source gate; history shows within-cell zero, actual crossed-knot errors and the absolute-jump envelope, and labels physical coverage0/313. Independent C9 admission is pending. A new reviewer thread request was rejected by the host thread limit; the existing Astra review agent, which did not implement the code, is reused under the current AGENTS capacity-recovery rule. Its prior R6 context is disclosed.

These successful implementations supply numerical diagnostics and exact represented-function identities. They do not establish physical H5 epsilon, change production qualification, start an IVP or complete a new canonical DAG node. Working32/88, shared27/88, physicalepsilon null, coverage0/313 are retained.

