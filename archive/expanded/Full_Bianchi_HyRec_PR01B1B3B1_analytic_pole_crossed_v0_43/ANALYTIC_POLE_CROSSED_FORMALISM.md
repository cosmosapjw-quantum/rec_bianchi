# PR-01B1-B3B1 analytic scalar 2p pole+crossed average

## 1. Linear denominators

After the atomic energy delta fixes the momentum parallel to the photon
transfer, write the remaining scattering-plane momentum as

\[
P_T=\sqrt{Mk_BT}\,z,\qquad z\sim N(0,1).
\]

The unresolved scalar 2p time orderings are

\[
\mathcal M(z)=a\left[
\frac1{A+Bz-i\gamma}
+\frac1{C+Dz+i\gamma}
\right],
\qquad a=-\frac{f_{12}\nu_{2p}}2.
\]

The coefficients are

\[
A=\nu_{2p}-\nu_s+
\frac{\nu_sP_\parallel}{Mc}(\hat Q\cdot n_s)
+\frac{h\nu_s^2}{2Mc^2},
\]

\[
B=\frac{\nu_s\sqrt{Mk_BT}}{Mc}(e_T\cdot n_s),
\]

\[
C=\nu_{2p}+\nu_t-
\frac{\nu_tP_\parallel}{Mc}(\hat Q\cdot n_t)
+\frac{h\nu_t^2}{2Mc^2},
\]

\[
D=-\frac{\nu_t\sqrt{Mk_BT}}{Mc}(e_T\cdot n_t).
\]

Since \(e_T\cdot Q=0\),

\[
\nu_s(e_T\cdot n_s)=\nu_t(e_T\cdot n_t),
\]

and therefore

\[
\boxed{D=-B.}
\]

## 2. Gaussian resolvent

For \(Z\sim N(0,1)\), define

\[
\mathscr R(\zeta)=\left\langle\frac1{Z-\zeta}\right\rangle.
\]

Using the Faddeeva integral,

\[
\mathscr R(\zeta)=
\begin{cases}
 i\sqrt{\pi/2}\,w(\zeta/\sqrt2),&\Im\zeta>0,\\
-i\sqrt{\pi/2}\,w(-\zeta/\sqrt2),&\Im\zeta<0.
\end{cases}
\]

The two Lorentzian terms are the Voigt averages already locked in
v0.42.  For the interference define

\[
\alpha=A-i\gamma,\qquad \beta=C-i\gamma,
\]

\[
\zeta_1=-\alpha/B,\qquad \zeta_2=-\beta/D.
\]

Partial fractions give

\[
\boxed{
J_{pc}=\left\langle
\frac1{(A+BZ-i\gamma)(C+DZ-i\gamma)}
\right\rangle
=
\frac{\mathscr R(\zeta_1)-\mathscr R(\zeta_2)}
{B\beta-D\alpha}.
}
\]

Hence

\[
\boxed{
\langle|\mathcal M|^2\rangle
=a^2\left(I_p+I_c+2\Re J_{pc}\right),
}
\]

where

\[
I_p=\left\langle[(A+BZ)^2+\gamma^2]^{-1}\right\rangle,
\quad
I_c=\left\langle[(C+DZ)^2+\gamma^2]^{-1}\right\rangle.
\]

Collinear cases \(B=D=0\) reduce to constant rational functions.

## 3. Interpretation

This closes the provisional unresolved 2p pole+crossed amplitude without
any momentum quadrature.  The v0.14 `full_mean_amp2` additionally contains
seagull and smooth higher-bound/continuum background.  Therefore its
difference from the present result is expected and is not a failed gate.
