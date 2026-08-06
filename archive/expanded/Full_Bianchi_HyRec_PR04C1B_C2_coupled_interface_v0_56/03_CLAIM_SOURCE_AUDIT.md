# Phase 3 — Claim–Source Audit

| Claim | Evidence | Status | Scope/repair |
|---|---|---|---|
| Direct native-to-COM state equality is unnecessary | v0.54 no-go; flux-mortar literature | SUPPORTED | Only structural analogy to mortar is claimed |
| `FR00` and `FB02` are the exact outer owners | frozen v0.47 state registry/NPZ | SUPPORTED | Byte-locked labels and intervals |
| `n_H q/g` is the occupation increment | units plus quadrature normalization | SUPPORTED | Uniform scalar packet only |
| Exact transported energy equals `h nu_face q` | v0.55 packet invariant | SUPPORTED | Does not identify finite-cell internal energy |
| Cell centroid may replace face frequency | no source | UNSUPPORTED | Deleted; correction ledger required |
| Red v0.55 packet is a canonical COM state reconstruction | no source; conflicts with v0.54 | UNSUPPORTED | Recast as source-conditioned face-flux target |
| Matrix-free JVP is suitable | existing code + PETSc primary docs | SUPPORTED | Exact analytic JVP used; finite difference only audit |
| Log variables guarantee accepted occupation positivity | algebra and existing solver | SUPPORTED | Transfer multipliers are also log-positive when enabled |
| Endpoint signs suffice for Bianchi branch selection | counterexample in stored speed histories | UNSUPPORTED | Exact piecewise-linear roots mandatory |
| Binary executable hash is a physics invariant | compiler counterexample in PR #12/#14 | REJECTED | Numerical output hash remains unconditional |
