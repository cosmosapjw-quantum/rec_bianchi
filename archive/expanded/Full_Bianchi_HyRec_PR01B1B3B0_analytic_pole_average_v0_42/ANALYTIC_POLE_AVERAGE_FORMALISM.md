# PR-01B1-B3B0 analytic conditional 2p-pole average

## Reduction

For an unordered photon endpoint pair, define

\[
\mathbf Q=\frac{h}{c}(\nu_s\mathbf n_s-\nu_t\mathbf n_t),
\qquad
\Delta E=h(\nu_s-\nu_t).
\]

The nonrelativistic atom-energy delta fixes

\[
P_\parallel=\frac{M\Delta E}{Q}-\frac Q2.
\]

Choose \(\mathbf e_T\) in the scattering plane and perpendicular to
\(\mathbf Q\).  With

\[
P_T=\sqrt{Mk_BT}\,z,\qquad z\sim N(0,1),
\]

the COM absorption-first 2p denominator is exactly linear,

\[
\frac{D^-_{2p}}h=A+Bz-i\gamma.
\]

The coefficients used by the implementation are

\[
A=\nu_{2p}-\nu_s+\frac{\nu_sP_\parallel}{Mc}
(\hat Q\!\cdot\!n_s)+\frac{h\nu_s^2}{2Mc^2},
\]

\[
B=\frac{\nu_s}{Mc}\sqrt{Mk_BT}
(e_T\!\cdot\!n_s),
\qquad
\gamma=\frac{A_{21}}{4\pi}.
\]

For

\[
\mathcal M_{2p}^{\rm pole}= -\frac{f_{12}\nu_{2p}}{2}
\frac1{A+Bz-i\gamma},
\]

the remaining Gaussian integral is analytic:

\[
\boxed{
\left\langle|\mathcal M_{2p}^{\rm pole}|^2\right\rangle
=
\left(\frac{f_{12}\nu_{2p}}2\right)^2
\frac{\sqrt\pi}{\sqrt2|B|\gamma}
H\!\left(
\frac{\gamma}{\sqrt2|B|},
\frac{A}{\sqrt2B}
\right)
}
\]

when \(B\ne0\).  For collinear geometry \(B=0\), the limit is simply

\[
\left(\frac{f_{12}\nu_{2p}}2\right)^2/(A^2+\gamma^2).
\]

Here \(H(a,x)=\Re w(x+ia)\) is the Voigt/Faddeeva function.

## Pole map

The tangent-quadrature coordinates used by v0.14 are not independent
fit parameters.  They are

\[
t_\star=-\frac{A}{\sqrt2B},
\qquad
\Delta t=\frac{\gamma}{\sqrt2|B|}.
\]

Thus the former numerical pole quadrature can be replaced by an analytic
special-function call for the scalar 2p pole.

## Absolute area

With

\[
\mathcal C_A=A_{21}^{\rm adopted}/A_{21}(f_{12}),
\]

the fixed-atom Lorentzian satisfies exactly

\[
\int d\nu\,\sigma_{2p}^{\rm pole}(\nu)=\pi r_ecf_{12}.
\]

This is a source-derived normalization identity, not a fitted scale.

## Scope

This stage closes the conditional transverse integral for the absorption
pole.  It does not yet integrate both photon frequency-cell interiors,
the continuous angular endpoint structure, or the crossed/background
amplitude.  Those are the next bounded stage.
