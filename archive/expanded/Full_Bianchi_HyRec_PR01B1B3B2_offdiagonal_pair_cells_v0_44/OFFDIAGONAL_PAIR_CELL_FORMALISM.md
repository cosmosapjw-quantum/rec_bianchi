# PR-01B1-B3B2 off-diagonal two-sided pair-cell conductance

## 1. Scope

This stage integrates every unordered pair of **distinct** frequency
cells in the bounded \(|x|\le4.25\) core.  The same-cell
coherent-forward angular block is intentionally excluded because its
\(\mu\to1\) contribution is distributional before the frequency-cell
projection.

The provisional scalar atomic amplitude is the unresolved \(2p\)
absorption pole plus crossed time ordering.  Its conditional atomic
momentum average is the analytic Faddeeva result locked in v0.43.

## 2. Physical cell conductance

Let

\[
\nu_s=\nu_{\rm abs}+x_s\Delta\nu_D,
\qquad
\nu_t=\nu_{\rm abs}+x_t\Delta\nu_D.
\]

For an unordered pair of distinct cells \(I_s,I_t\),

\[
\boxed{
\begin{aligned}
\mathsf S_{ts}^{(\ell)}={}&
\frac{8\pi\Delta\nu_D}{c^3}
\frac{n_{1s}c\,\sigma_T\,\mathcal C_A
h\Delta\nu_D}{M_Hc^2}
\\
&\times
\int_{I_s}dx_s\int_{I_t}dx_t
\frac12\int_{-1}^{1}d\mu\,
\Phi_R(\mu)P_\ell(\mu)
\\
&\times
\nu_s\nu_t e^{-h\nu_s/(k_BT_m)}
S_{\rm MJ}(q,\delta)
\left\langle|\mathcal M_{2p}^{p+c}|^2\right\rangle .
\end{aligned}
}
\]

Here

\[
\Phi_R(\mu)=\frac34(1+\mu^2),
\]

and \(S_{\rm MJ}\) is the exact Maxwell--Jüttner structure factor from
v0.40.  Endpoint exchange changes \(\delta\to-\delta\), and the thermal
identity for \(S_{\rm MJ}\) together with PT invariance of the analytic
amplitude gives

\[
\boxed{\mathsf S_{ts}^{(\ell)}=\mathsf S_{st}^{(\ell)}}.
\]

One canonical unordered integral is stored.  Independent reversed
integrations are retained as a numerical audit; no matrix-level
symmetrization is applied.

## 3. Cell equilibrium weight and rate

\[
\Pi_s=
\frac{8\pi\Delta\nu_D}{c^3}
\int_{I_s}dx_s\,
\nu_s^2e^{-h\nu_s/(k_BT_m)},
\]

\[
K_{t\leftarrow s}^{(\ell)}=
\frac{\mathsf S_{ts}^{(\ell)}}{\Pi_s}.
\]

For \(\ell=0\), the closed interior frequency generator is formed from
off-diagonal rates and

\[
G_{ss}=-\sum_{t\ne s}K_{t\leftarrow s}.
\]

It follows algebraically that

\[
\mathbf1^TG=0,
\qquad
G\Pi=0.
\]

This closed-interior generator is an audit object.  Physical loss into
red/blue exterior states is added in the next boundary stage.

## 4. Numerical coordinates

For the frequency cells,

\[
u_t=u+v,
\qquad
x_s=u-v,
\qquad
dx_tdx_s=2\,du\,dv.
\]

The \(u\) interval is split at all cell-diamond breakpoints.  Whenever
it crosses the line resonance, a tangent coordinate is used around
\(u=0\).  The angular domain is split as

\[
\mu=-1+2c^2
\quad\text{(backscatter)},
\]

regular Gauss--Legendre \(\mu\), and

\[
\mu=1-t^2
\quad\text{(coherent-forward endpoint)}.
\]

For distinct frequency cells the forward endpoint is regular after
cell integration.  The same-cell block is not inferred from this
limit.

## 5. Hummer limit

Setting the recoil terms to zero, replacing the photon momenta in the
atomic Doppler geometry by the fixed line frequency, and retaining only
the absorption pole reproduces the physical Hummer-II density.  This is
used only as an independent normalization and coordinate audit.

## 6. Supersession and limitations

This artifact supersedes centre-sampled off-diagonal pair rates for the
provisional scalar \(2p\) amplitude.  It does **not** supersede:

- the same-frequency-cell angular scattering block;
- red/blue exterior event deposition and four-force;
- the higher-bound, continuum and seagull COM--KHW background (PR-03);
- fine structure, polarization or atomic alignment.
