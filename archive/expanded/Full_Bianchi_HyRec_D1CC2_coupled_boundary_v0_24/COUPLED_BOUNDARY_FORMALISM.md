# D1C-C2 coupled boundary regression

## Exact finite-tilt adapter

\[
\nu_H=\Gamma_H(1-\beta_H\cdot e_n)\nu_n.
\]

Along the characteristic,

\[
D_{\rm char}\ln\mathcal D_H
=
\Gamma_H^2\beta_H\cdot D_{\rm char}\beta_H
-
\frac{
D_{\rm char}\beta_H\cdot e_n
+\beta_H\cdot D_{\rm char}e_n
}{
1-\beta_H\cdot e_n
}.
\]

Hence

\[
\mathcal R_H=\mathcal R_n+D_{\rm char}\ln\mathcal D_H.
\]

## Branch localization

Every zero of \(\mathcal A_{\alpha q}\) splits the timestep. The upwind
trace is selected independently on each open subinterval. A branch
chosen at the old time or at one midpoint may not cross the root.

## True transition

\[
C^{\rm true}(x)=\eta(x)[1+f(x)]-\chi(x)f(x).
\]

At LTE,
\[
\eta^{\rm eq}(1+f_{\rm eq})=\chi^{\rm eq}f_{\rm eq}.
\]

The same endpoint partition is used for gain and loss.

## Coupled ledger

Liouville crossing and resonant scattering conserve photon number over
the combined interior/exterior state. A one-photon true transition
satisfies

\[
\Delta N_\gamma=n_HV\Delta x_{1s}.
\]

All photon and hydrogen four-force changes use the same edge or event
flux.
