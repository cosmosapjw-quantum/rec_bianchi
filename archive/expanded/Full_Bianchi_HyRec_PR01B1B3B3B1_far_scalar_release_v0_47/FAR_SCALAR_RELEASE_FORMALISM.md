# Far flux and nonlinear harmonic Bose release

The dynamic frequency-state registry is

\[
I=[-4.25,4.25],\quad
O^{\rm near}_{R/B}:4.25<|x|\le10.25,\quad
O^{\rm far}_{R/B}:10.25<|x|\le21.25.
\]

Every disjoint frequency pair is represented by Legendre conductance moments

\[
S_\ell(a,b)=\frac12\int_{-1}^{1}S_{ab}(\mu)P_\ell(\mu)d\mu.
\]

For occupations \(f_a(\boldsymbol n)\), the nonlinear Bose number action of
one pair is evaluated without reconstructing or clipping a pointwise kernel:

\[
\begin{aligned}
C_a(\boldsymbol n)={}&\frac{1+f_a}{z_b}\,\mathcal S_{ab}[f_b]
-\frac{f_a}{z_a}\,\mathcal S_{ab}[1+f_b],\\
z_a={}&\Pi_a/g_a.
\end{aligned}
\]

The zonal convolution is diagonal in spherical harmonics, while the
pointwise products are evaluated on positive-weight harmonic-exact Lebedev
rules.  Same-frequency Bose factors cancel exactly, leaving the linear
regularized rates \(D_{\ell a}=K_{\ell,aa}-K_{0,aa}\).

The far-tail gate compares the explicit |x|<=21.25 operator with the
|x|<=16.25 truncation and bounds the continuation using the last two adaptive
outer cells.  No free tail normalization is fitted.
