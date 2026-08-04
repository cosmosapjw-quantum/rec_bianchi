# Event-pair conductance formalism

## 1. Microscopic event

A scalar photon–hydrogen scattering event is

\[
e:\quad (P_i,k_b)\longrightarrow(P_f,k_a),
\]

with

\[
P_i+k_b=P_f+k_a.
\]

The combined parity–time-reversed event is

\[
\bar e:\quad (P_f,k_a)\longrightarrow(P_i,k_b).
\]

For parity- and time-reversal-invariant scalar scattering,

\[
|\mathcal M_e|^2=|\mathcal M_{\bar e}|^2
\]

after the corresponding polarization reversal in the polarized theory.

## 2. Equilibrium edge measure

Let

\[
dS_e =
\mathcal N\,|\mathcal M_e|^2\,
\delta^{(4)}(P_i+k_b-P_f-k_a)
e^{-\beta[E_H(P_i)+E_b]}\,d\Xi_e.
\]

Energy conservation gives

\[
E_H(P_i)+E_b=E_H(P_f)+E_a,
\]

hence

\[
dS_e=dS_{\bar e}.
\]

After integrating atoms and depositing photon endpoints into cells,

\[
S_{ab}=S_{ba}\ge0.
\]

This is event-level pairing, not posterior matrix symmetrization.

## 3. Linear dilute collision operator

With photon equilibrium cell weight

\[
\Pi_a=g_a e^{-\beta E_a},
\]

define

\[
K_{a\leftarrow b}=S_{ab}/\Pi_b.
\]

Then

\[
\dot N_a=\sum_b S_{ab}
\left(
\frac{N_b}{\Pi_b}-\frac{N_a}{\Pi_a}
\right),
\]

so

\[
\mathbf 1^T G=0,\qquad G\Pi=0.
\]

## 4. Bosonic edge flux

For occupation \(f_a=N_a/g_a\), define

\[
\Psi_a=\ln\frac{f_a}{1+f_a}+\beta E_a.
\]

The flux into \(a\) from \(b\) is

\[
J_{a\leftarrow b}
=
S_{ab}(1+f_a)(1+f_b)
\left(e^{\Psi_b}-e^{\Psi_a}\right).
\]

A common-\(\mu_\gamma\) Bose–Einstein distribution has constant
\(\Psi=+\beta\mu_\gamma\), so every edge vanishes individually.

The free-energy production from one unordered edge is

\[
(\Psi_a-\Psi_b)J_{a\leftarrow b}
=
-S_{ab}(1+f_a)(1+f_b)
(\Psi_a-\Psi_b)
(e^{\Psi_a}-e^{\Psi_b})
\le0.
\]

## 5. Four-force

For one edge,

\[
\Delta p_\gamma^a=p_a^a-p_b^a,\qquad
\Delta P_H^a=-\Delta p_\gamma^a.
\]

Using the same edge flux,

\[
Q_\gamma^a=\sum_{a<b}J_{a\leftarrow b}\Delta p_\gamma^a,
\qquad
Q_H^a=-Q_\gamma^a.
\]

No separate recoil-heating formula is added.
