# PR-04B2A physical native edge-flux formalism

## Conventions

Metric signature is `(-,+,+,+)`. The local frame is the hydrogen orthonormal
tetrad. Ordinary frequency `nu` is measured in Hz, `y=ln(nu)`, and cosmological
time is `eta=ln(a)`, so `d/dt=H d/deta`. The jump sign remains
`Delta nu=nu_target-nu_source`; `Delta E_gamma=h Delta nu` and
`Delta E_H=-h Delta nu`. Constants `c`, `h`, and `k_B` are explicit.

The canonical original-HyRec source uses cgs lengths and eV energies. Its
source-consistent `hc` constant is `1.239841874331000e-04 eV cm`.

## Physical measure and transport equation

For occupation distortion `Delta f_nu`, define photons per hydrogen atom per
logarithmic-frequency interval,

```text
N_y = 8 pi nu^3 Delta f_nu / (c^3 n_H) = A(nu) Delta f_nu.
```

Since `n_H` scales as `a^-3`, the homogeneous free-streaming operator obeys

```text
partial_eta N_y - partial_y N_y = A(nu) C[f]/H.
```

The redshift flux is `F_y=-N_y`. Across native virtual spike `b`,

```text
P_b       = (1-exp(-tau_b))/tau_b,
fbar_b    = P_b fplus_b + (1-P_b) feq_b,
fminus_b  = fplus_b + (1-exp(-tau_b))(feq_b-fplus_b),
tau_b     = x_1s Gamma_b/(H A_b).
```

Therefore

```text
x_1s Gamma_b (feq_b-fbar_b)
  = x_1s Gamma_b P_b (feq_b-fplus_b)
  = H A_b (fminus_b-fplus_b).
```

Both sides have units `s^-1` per H. Multiplication by `h nu_b` gives W per H;
the same event assigns the exact opposite energy to the atom.

## Closed and open claims

The source solution, an independent dense 313-state solve, and the structured
Schur solve reproduce the same physical edge flux and signed source moments
through order four. These are *spectral source moments* `sum_b J_b nu_b^r`,
with units `Hz^r s^-1` per H; they are not COM--KHW jump moments.

Only two native virtual centres lie inside the v0.51 `|x|<=4.25` production
core. Native spikes and 17 finite-volume COM--KHW cells do not yet share a
measure-preserving partition. Raw v0.51 event mass divided by `n_H` and native
trajectory flux are therefore recorded only as a negative overlap diagnostic;
no ratio is fitted and no direct parity is claimed. PR-04B2B remains open.
