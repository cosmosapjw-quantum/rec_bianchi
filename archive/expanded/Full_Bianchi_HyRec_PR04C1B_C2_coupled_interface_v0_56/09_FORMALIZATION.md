# Phase 9 — Formalization

The production state is `(u,v)` with `f=exp(u)>0` and packet multiplier
`rho=exp(v)>0`. For each interface side `s`, `q_s=Delta t Phi_s rho_s` and
`R_rho,s=rho_s-1`. The occupation residual is

`R_f = f-f_old-Delta t C[f]-sum_s Delta f_s(rho_s)`.

The analytic JVP is

`D R_f[du,dv] = f du-Delta t D C[f](f du)-sum_s rho_s dv_s Delta f_s(1)`,
`D R_rho[dv]=rho dv`.

The exact transfer ledger uses opposite signs in native and COM number/energy
entries. Interface atom energy is identically zero. The resolved-cell energy
proxy plus the unresolved correction reconstructs the exact face energy.
