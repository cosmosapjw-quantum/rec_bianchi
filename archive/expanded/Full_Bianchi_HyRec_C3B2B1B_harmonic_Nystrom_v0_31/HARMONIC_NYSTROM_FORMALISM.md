# C3B2B1-B continuous-mu harmonic/Nyström reference

## 1. Half-angle variables

Let

\[
\mu=1-2s^2,\qquad
c_\theta=\sqrt{1-s^2},
\]

and

\[
u=\frac{x+x'}{2},\qquad
v=\frac{x-x'}{2}.
\]

Then

\[
dx\,dx'=2\,du\,dv,
\]

and the Hummer-II kernel becomes

\[
R_{\rm II}\,dx\,dx'
=
\frac{
e^{-v^2/s^2}
}{
\pi s c_\theta
}
H\left(
\frac{a}{c_\theta},
\frac{u}{c_\theta}
\right)
du\,dv.
\]

For outgoing cell \(I_i\) and incoming cell \(I_j\),

\[
v_{\min}(u)
=
\max(a_i-u,u-b_j),
\]

\[
v_{\max}(u)
=
\min(b_i-u,u-a_j).
\]

The \(v\) integral is exact:

\[
\boxed{
\mathcal R_{ij}(s)
=
\frac{1}{2\sqrt\pi c_\theta}
\int du\,
H\left(
\frac{a}{c_\theta},
\frac{u}{c_\theta}
\right)
\left[
{\rm erf}\frac{v_{\max}}{s}
-
{\rm erf}\frac{v_{\min}}{s}
\right].
}
\]

For the centre-sampled incoming frequency used in the v0.30 angular
audit, the equivalent one-dimensional transform is

\[
\boxed{
\mathcal R_i(x',s)
=
\frac1{\pi c_\theta}
\int_{t_i^-}^{t_i^+}
e^{-t^2}
H\left(
\frac a{c_\theta},
\frac{x'+st}{c_\theta}
\right)dt.
}
\]

## 2. Coherent-forward limit

As \(\mu\to1\),

\[
R_{\rm II}(x,x',\mu)
\to
\phi_x(x')\delta(x-x').
\]

With \(t=\sqrt{1-\mu}\), the finite-cell singular contribution is

\[
\boxed{
\mathcal R_i^{\rm coh}
=
\phi_x(x')
\left[
\Phi\left(
\frac{x_i^+-x'}{t}
\right)
-
\Phi\left(
\frac{x_i^--x'}{t}
\right)
\right].
}
\]

This term is integrated analytically over the forward endpoint interval.

## 3. Legendre kernel

For scalar zonal scattering,

\[
\boxed{
K_\ell(i,j)
=
\frac12
\int_{-1}^{1}
d\mu\,
\Phi_R(\mu)
P_\ell(\mu)
\mathcal R_{ij}(\mu).
}
\]

The harmonic collision action is

\[
C_\ell
=
n_{1s}c
\frac{\pi r_ecf_{12}}{\Delta\nu_D}
K_\ell F_\ell
-
\Gamma_{\rm cap}F_\ell.
\]

The same loss is used for every \(\ell\), while the gain uses \(K_\ell\).

## 4. Numerical split

- \(\mu\in[-1,-0.99]\): backscatter variable
  \(c=\sqrt{(1+\mu)/2}\);
- \(\mu\in[-0.99,0.999]\): regular half-angle transform;
- \(\mu\in[0.999,1]\): analytic coherent-forward Gaussian cell
  probability.

This removes both endpoint boundary layers before angular quadrature.

## 5. Consequence

The harmonic representation preserves isotropy and each Legendre
subspace algebraically. Lebedev collocation is retained for the
Liouville characteristic, but the local scalar collision action can be
evaluated by the zonal harmonic kernel.
