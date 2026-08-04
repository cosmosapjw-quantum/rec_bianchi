# C3A physical true kernel and all-11 Bianchi registry

## 1. Channel-resolved true kernel

In the hydrogen frame, using photon number spectral density
\(N_\nu=2\nu^2 n_\nu/c^2\),

\[
\frac1c D_0N_\nu\big|_{\rm true}
=
\sum_i\frac{\phi_i(\nu)}{4\pi\Delta\nu_D}
\left[
 p_{\rm em}R_{2p}^{i,+}
-p_d^i h\nu_\alpha B_{12}N_{1s}
 f_{\rm th}(\nu)N_\nu
\right].
\]

The exact stimulated thermodynamic factor is

\[
f_{\rm th}^{\rm exact}(\nu)
=
\left(\frac{\nu_\alpha}{\nu}\right)^2
\exp\!\left[\frac{h(\nu-\nu_\alpha)}{k_BT}\right]
\frac{1+n_{\rm Pl}(\nu_\alpha)}{1+n_{\rm Pl}(\nu)}.
\]

It obeys

\[
f_{\rm th}^{\rm exact}(\nu)N_\nu^{\rm Pl}
=N_{\nu_\alpha}^{\rm Pl}.
\]

The usual Chluba-Sunyaev factor is its Wien-limit reduction.

## 2. Bosonic completion

Writing the channel equation as

\[
D_0N_\nu=A_i-B_iN_\nu,
\]

and \(N_\nu=g_\nu n_\nu\), define

\[
\eta_i=A_i/g_\nu,
\qquad
\chi_i=\eta_i+B_i.
\]

Then

\[
D_0n_\nu
=
\eta_i(1+n_\nu)-\chi_i n_\nu
=
\eta_i-B_i n_\nu.
\]

Thus \(\eta_i,\chi_i\ge0\) give a positivity-preserving gain-loss
operator without changing the standard affine recombination equation.

## 3. Bianchi registry

The spatial commutators are

\[
[e_\beta,e_\gamma]
=C^\alpha{}_{\beta\gamma}e_\alpha,
\]

\[
C^\alpha{}_{\beta\gamma}
=\epsilon_{\beta\gamma\delta}n^{\delta\alpha}
+\delta^\alpha_\gamma a_\beta
-\delta^\alpha_\beta a_\gamma.
\]

The Jacobi constraint is

\[
n^{\alpha\beta}a_\beta=0.
\]

For an orthonormal left-invariant spatial frame, the Koszul connection is

\[
{}^{(3)}\Gamma_{\gamma\beta\alpha}
=\frac12\left(
 C_{\gamma\alpha\beta}
-C_{\alpha\beta\gamma}
+C_{\beta\gamma\alpha}
\right).
\]

The Lie part of the photon direction characteristic is

\[
V_{\rm Lie}^\gamma
=-{}^{(3)}\Gamma^\gamma{}_{\beta\alpha}
 e^\alpha e^\beta,
\qquad
e_\gamma V_{\rm Lie}^\gamma=0.
\]

The pre-existing Stage-2 kinematical characteristic is combined with
this registry output; collision microphysics is not rederived per type.
