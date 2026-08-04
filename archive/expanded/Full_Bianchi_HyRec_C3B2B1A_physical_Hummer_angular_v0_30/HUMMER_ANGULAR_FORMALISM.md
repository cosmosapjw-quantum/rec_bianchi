# Physical Hummer-II angular reference

For coherent scattering in the atom frame, define

\[
s=\sqrt{\frac{1-\mu}{2}},\qquad c=\sqrt{\frac{1+\mu}{2}}.
\]

The angle-dependent type-II redistribution density is

\[
R_{II}(x,x',\mu)
=
\frac{1}{\pi\sqrt{1-\mu^2}}
\exp\left[-\frac{(x-x')^2}{2(1-\mu)}\right]
H\left(a\sqrt{\frac{2}{1+\mu}},
\frac{x+x'}{\sqrt{2(1+\mu)}}\right).
\]

It obeys

\[
\int_{-\infty}^{\infty}R_{II}(x,x',\mu)\,dx
=\phi_x(x')=\frac{H(a,x')}{\sqrt\pi}.
\]

For exact backscattering,

\[
R_{II}(x,x',-1)
=
\frac{a}{2\pi^{3/2}}
\frac{\exp[-(x-x')^2/4]}
{[(x+x')/2]^2+a^2}.
\]

The physical transition rate on the normalized sphere measure is

\[
d\Gamma
=
n_{1s}c\frac{\pi r_ecf_{12}}{\Delta\nu_D}
\Phi_R(\mu)R_{II}(x,x',\mu)\,dx\frac{d\Omega}{4\pi},
\]

\[
\Phi_R(\mu)=\frac34(1+\mu^2).
\]

The \(\mu\to1\) limit contains a coherent frequency delta function.
After frequency discretization this becomes a narrow angular boundary
layer. A raw Lebedev rule must resolve that layer as well as the smooth
Rayleigh phase, which explains the slow non-monotone convergence found
in this audit.
