# C3B2B1-D0 thermodynamic completion

## 1. Scope

This stage is the finite-volume analogue of the Rybicki
detailed-balance correction. It is not yet the exact COM event-recoil
kernel.

The input \(B_\ell(i,j)\) is the symmetric no-recoil Hummer-II proposal
from v0.32.

## 2. Cell measures

For an isotropic photon occupation, the mode density in frequency cell
\(i\) is

\[
g_i=
\frac{8\pi}{c^3}
\int_{\nu_i^-}^{\nu_i^+}\nu^2\,d\nu.
\]

The dilute thermal weight is

\[
\Pi_i=
\frac{8\pi}{c^3}
\int_{\nu_i^-}^{\nu_i^+}
\nu^2e^{-h\nu/(k_BT_m)}\,d\nu.
\]

Define

\[
z_i=\Pi_i/g_i,
\qquad
E_i^{\rm th}=-k_BT_m\ln z_i.
\]

The exact discrete Bose family is

\[
f_i^{\rm BE}(q)=
\frac{qz_i}{1-qz_i}.
\]

## 3. Square-root detailed-balance completion

For every Legendre block,

\[
\boxed{
W_\ell(i\leftarrow j)
=
B_\ell(i,j)
\sqrt{\frac{\Pi_i}{\Pi_j}}.
}
\]

For \(\ell=0\),

\[
\boxed{
W_0(i\leftarrow j)\Pi_j
=
W_0(j\leftarrow i)\Pi_i.
}
\]

The occupation-space gain is

\[
\widetilde W_\ell(i,j)
=
\frac{g_j}{g_i}W_\ell(i,j),
\]

and the per-photon loss is

\[
\Gamma_j=\sum_iW_0(i\leftarrow j).
\]

## 4. Bose edge flux

For one unordered frequency edge,

\[
J_{i\leftarrow j}
=
W_{ij}g_jf_j(1+f_i)
-
W_{ji}g_if_i(1+f_j).
\]

With

\[
\Psi_i=
\ln\frac{f_i}{1+f_i}-\ln z_i,
\]

the same flux is

\[
J_{i\leftarrow j}
=
S_{ij}(1+f_i)(1+f_j)
\left(e^{\Psi_j}-e^{\Psi_i}\right),
\]

where

\[
S_{ij}=W_{ij}\Pi_j=S_{ji}.
\]

Thus every Bose-Einstein edge vanishes separately and

\[
\sum_{i<j}
(\Psi_i-\Psi_j)J_{i\leftarrow j}\le0.
\]

## 5. Recoil and phase-space slope

Let

\[
b_D=\Delta\nu_D/\nu_\alpha,
\qquad
g=\frac{h\nu_\alpha}{M_Hc^2b_D}.
\]

Since \(\Delta\nu_D/\nu_\alpha=\sqrt{2k_BT_m/(M_Hc^2)}\),

\[
\boxed{
\frac{h\Delta\nu_D}{k_BT_m}=2g.
}
\]

At line centre,

\[
\frac12\frac{d\ln\Pi}{dx}
=
b_D-g.
\]

For a symmetric small-jump proposal,

\[
\Delta A_1
=
\frac12
\frac{d\ln\Pi}{dx}A_2
+O(\Delta x^3).
\]

The term \(-gA_2\) is the recoil drift and \(+b_DA_2\) is the exact
frequency phase-space correction.

## 6. Firewall

The completion enforces thermodynamic microreversibility and the
Rybicki Fokker-Planck drift. It does not replace the exact recoil event
map

\[
\nu_{\rm out}^*
=
\frac{\nu_{\rm in}^*}
{1+\frac{h\nu_{\rm in}^*}{M_Hc^2}(1-\mu^*)}.
\]

That event-level kernel and its spatial four-force remain the next
stage.
