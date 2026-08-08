# PR-05C2C1B2A canonical two-photon/Raman source formalism

## Conventions and scope

The metric signature is `(-,+,+,+)`.  Frequency is ordinary frequency in Hz,
while the canonical October-2012 HyRec table uses photon energy and radiation
temperature in eV.  `c`, `h`, and `k_B` remain explicit.  The stage is scalar,
unpolarized and homogeneous.

## Canonical table and process registry

The canonical five-column table stores `E_b`, `A1s`, `A2s`, `A3s3d`, and
`A4s4d`.  The integrated-bin rates have units `s^-1`.  HyRec renormalizes the
sub-Ly-alpha `A2s` sum to `8.2206 s^-1`.  The process interpretation is
threshold-dependent: below the relevant transition energy the table is a
two-photon spectrum; above it the stored coefficient is a Raman rate.  The
`4s4d` production grid ends below its threshold.

## Source-identical real--virtual coefficients

For virtual-bin energy `E_b` and radiation temperature `T_r` in eV, HyRec's
source coefficients are

\[
R_{2s\to b}=\alpha_{\rm fs}^{8}m_e\,
\frac{A_{2s,b}}{|\exp[(E_b-E_{21})/T_r]-1|},
\]

\[
R_{b\to2s}=R_{2s\to b}\exp[(E_b-E_{21})/T_r],
\]

and

\[
R_{2p\to b}=\frac{\alpha_{\rm fs}^{8}m_e}{3}
\left[
\frac{e^{-E_{32}/T_r}A_{3s3d,b}}{|e^{(E_b-E_{31})/T_r}-1|}
+
\frac{e^{-E_{42}/T_r}A_{4s4d,b}}{|e^{(E_b-E_{41})/T_r}-1|}
\right],
\]

\[
R_{b\to2p}=3e^{(E_b-E_{21})/T_r}R_{2p\to b}.
\]

All rates are nonnegative.  The off-diagonal matrix entries are their negatives,
while the real-state diagonal receives the sum of outgoing rates.  Analytic
log-temperature derivatives are evaluated with stable `expm1` arithmetic.

## Positive physical paired action

A distinct theory-contract object acts on an angle-resolved tracked photon bin.
For two-photon emission/absorption,

\[
\dot N_\gamma = \Lambda
\left[x_u(1+f_c)(1+f_t)-g\,x_{1s}f_cf_t\right].
\]

For Raman scattering,

\[
\dot N_\gamma = \Lambda
\left[x_u f_c(1+f_t)-g\,x_{1s}(1+f_c)f_t\right].
\]

Here `c` is the companion photon and `t` the tracked photon.  Both forward and
reverse terms are nonnegative.  At LTE atomic populations and Planck photon
occupations the two terms are equal.  This paired action is not relabelled as a
separately stored original-HyRec coefficient.

## Claim boundary

This stage closes the canonical table census, source-identical real--virtual
matrix coefficients, detailed balance and the scalar physical two-photon/Raman
paired action.  It does not select a scalable preconditioner and does not run a
four-or-more-macro trajectory.
