# PR-01B1-B2 Lorentz-invariant photon–atom pair measure

## 1. Invariant collision kernel

For photon–atom elastic scattering,

\[
(P_i,k_s)\longrightarrow(P_f,k_t),
\]

the common relativistic event measure is

\[
\boxed{
d\mathcal W
=
|\mathcal T|^2
(2\pi)^4
\delta^{(4)}(P_i+k_s-P_f-k_t)
\frac{d^3P_i}{(2\pi)^3\,2P_i^0}
\frac{d^3P_f}{(2\pi)^3\,2P_f^0}
\frac{d^3k_s}{(2\pi)^3\,2k_s^0}
\frac{d^3k_t}{(2\pi)^3\,2k_t^0}.
}
\]

This measure is invariant under endpoint exchange and PT reversal.  The
finite-volume photon-number conductance receives one factor of
\(\nu_s\) and one factor of \(\nu_t\), because

\[
\frac{d^3k}{2k^0}
\propto
\nu\,d\nu\,d\Omega.
\]

## 2. Eliminate the final atom

Let

\[
Q^\mu=k_s^\mu-k_t^\mu,
\]

\[
\delta=
\frac{h(\nu_s-\nu_t)}{Mc^2},
\]

\[
q=
\frac{|\boldsymbol k_s-\boldsymbol k_t|}{Mc},
\]

\[
\chi=\sqrt{q^2-\delta^2}>0.
\]

The final mass shell gives

\[
\boxed{
2P_i\cdot Q+Q^2=0.
}
\]

In the Breit frame of the spacelike transfer,

\[
Q_{\rm B}^\mu=(0,0,0,\chi),
\]

so the delta function fixes

\[
p_{\parallel,{\rm B}}=-\frac{\chi}{2}.
\]

The Breit boost is

\[
\beta_{\rm B}=\frac{\delta}{q},
\qquad
\Gamma_{\rm B}=\frac{q}{\chi}.
\]

The least possible initial-atom Lorentz factor in the gas frame is

\[
\boxed{
\gamma_{\min}
=
\frac{q}{\chi}
\sqrt{1+\frac{\chi^2}{4}}
-\frac{\delta}{2}.
}
\]

## 3. Exact Maxwell–Jüttner structure factor

With

\[
z=\frac{Mc^2}{k_BT_m}
\]

and the normalization convention inherited from v0.12,

\[
\boxed{
S_{\rm MJ}(q,\delta)
=
\frac{
\exp[-z(\gamma_{\min}-1)]
}{
2q\,e^zK_2(z)
}.
}
\]

The reverse transfer changes \(\delta\to-\delta\), while \(q,\chi\)
remain fixed. Since

\[
\gamma_{\min}(-\delta)
=
\gamma_{\min}(\delta)+\delta,
\]

one obtains

\[
\boxed{
S_{\rm MJ}(q,-\delta)
=
e^{-z\delta}
S_{\rm MJ}(q,\delta).
}
\]

In the nonrelativistic limit,

\[
\boxed{
S_{\rm MJ}
\longrightarrow
S_{\rm MB}
=
\frac{1}{\sqrt{2\pi\theta}\,q}
\exp\left[
-\frac{(\delta-q^2/2)^2}{2\theta q^2}
\right],
}
\]

where

\[
\theta=\frac{k_BT_m}{Mc^2}.
\]

## 4. Equilibrium pair conductance

For a positive PT-invariant amplitude average
\(\langle|\mathcal T|^2\rangle\),

\[
\boxed{
\begin{aligned}
\log \mathcal S_{ts}
={}&
\log\nu_t+\log\nu_s
-\frac{h\nu_s}{k_BT_m}
\\
&+
\log S_{\rm MJ}(q,\delta)
+
\log\langle|\mathcal T|^2\rangle.
\end{aligned}
}
\]

Using the structure-factor identity,

\[
\boxed{
\mathcal S_{ts}=\mathcal S_{st}
}
\]

before any matrix is assembled.

## 5. KHW-to-invariant-amplitude adapter

The fixed-target scalar KHW convention is

\[
\frac{d\sigma^*}{d\Omega^*}
=
r_e^2
\frac{\nu_f^*}{\nu_i^*}
|\mathcal M_{\rm KHW}|^2.
\]

For finite-mass two-body phase space in the initial atom rest frame,

\[
\frac{d\sigma^*}{d\Omega^*}
=
\frac{|\mathcal T|^2}{64\pi^2M^2}
\left(\frac{\nu_f^*}{\nu_i^*}\right)^2.
\]

Therefore the scalar adapter is

\[
\boxed{
|\mathcal T|^2
=
64\pi^2M^2r_e^2
\frac{\nu_i^*}{\nu_f^*}
|\mathcal M_{\rm KHW}|^2.
}
\]

PR-01A already established that the corresponding rest-frame
frequencies and amplitude are unchanged under the PT event map.

## 6. Full-coordinate Jacobian audit

The event map was independently parameterized by

\[
(\nu_i,\boldsymbol\beta_i,
\theta_i,\phi_i,\mu^*,\varphi^*)
\]

and its PT-reversed endpoint variables.  The numerical eight-dimensional
Jacobian was compared with the equilibrium differential-measure ratio

\[
\nu^2\sin\theta\,
F_{\rm MJ}(\boldsymbol\beta)
(1-\boldsymbol\beta\cdot\boldsymbol n)
p_R(\mu^*)e^{-h\nu/(k_BT)}.
\]

The maximum relative discrepancy over 48 generic thermal events was
below \(8\times10^{-7}\).  This is a finite-difference coordinate audit,
not the production quadrature.

## 7. Consequence for v0.39

The no-recoil Hummer matrix has a nearly pure linear thermal-affinity
defect

\[
\frac{C_{ij}-C_{ji}}{\tfrac12(C_{ij}+C_{ji})}
\simeq
(\alpha_T-2b_D)(x_i-x_j),
\]

with

\[
\alpha_T=\frac{h\Delta\nu_D}{k_BT_m}.
\]

The exact-event QMC correction removes about 98% of that coherent slope.
The remaining pair residual is irregular rather than a smooth missing
Jacobian signature.  Higher-resolution selected-pair reruns do not
reject detailed balance beyond \(3\sigma\).

Hence the prior statement that v0.39 had demonstrated a missing
phase-space Jacobian is superseded.  The production route is still the
common invariant pair integral, because it eliminates independent-column
cancellation noise and makes reciprocity an integrand-level property.
