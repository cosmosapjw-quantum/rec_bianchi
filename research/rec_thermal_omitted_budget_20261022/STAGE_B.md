# Stage B: source providers and retained-grid postprocessor

Runtime source identity:
`88edf8e7e5ccff94509e03ff2979b3b93e5e988641c5dbd4a5d64f4583bca02c`.

- Compton provider: actual-U hot term, separate Planck reference, inherited
  dilute UV moments, and the common direct log-temperature source function.
- Collisional provider: source-bound HG97 H/He CI and H I/He II CE, native
  isotope mapping, explicit unavailable masks, strict accuracy-domain default,
  and separately requested analytic continuation.
- Postprocessor: validates eight old receipt/source/trajectory identities,
  retains all872 evaluated states, and makes no ODE call. The kinetic/binding
  gradient and particle-source gates use independently computed ledgers.
- Actual focused checks:6 Compton and10 collision unittest methods passed.
  The retained command/output/hash receipts are in evidence; no unchanged
  old suite or completed IVP was repeated to produce these receipts.

The completed first postprocess execution and its immutable arrays belong to
Stage C. Plot layout repairs do not alter this runtime identity or its inputs.
