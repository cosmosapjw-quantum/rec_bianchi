# Mathematical specification of the candidate donor

## 1. Conventions

\[
 g_{ab}=(-,+,+,+),\qquad \epsilon_{123}=+1.
\]

The hydrogen-frame photon direction is `e_H^a`, with

\[
 e_H^ae^H_a=1.
\]

Observer-side outward sky directions, when used elsewhere, satisfy

\[
 n_{\rm sky}^a=-e_H^a.
\]

Ordinary frequency is `nu_H` in Hz. Physical time is `t` in seconds. When a
ray-length parameter is used,

\[
 s=ct,\qquad R_t=cR_s,\qquad V_t^a=cV_s^a.
\]

## 2. Continuous causal authority

The donor authority is a function or immutable evaluator

\[
 \mathcal D_H:(t,\nu_H,e_H)\mapsto f_H(t,\nu_H,e_H)\ge0,
\]

not a finite vector. On the unpolarized paired-source lane,

\[
 \left(\partial_t+R_H\nu_H\partial_{\nu_H}
 +V_H^A\nabla_A\right)f_H
 =\eta_t(1+f_H)-\kappa_t f_H
 =\eta_t-\chi_t f_H,
\]

\[
 \chi_t=\kappa_t-\eta_t,
 \qquad [\eta_t]=[\kappa_t]=[\chi_t]=T^{-1}.
\]

Along a characteristic,

\[
 f_H(t)=e^{-\int_{t_0}^t\chi_tdu}\,f_H(t_0)
 +\int_{t_0}^t e^{-\int_{t'}^t\chi_tdu}\eta_t(t')dt'.
\]

For constant paired rates over one step,

\[
 f_{n+1}=e^{-\chi\Delta t}f_n
 +\eta\Delta t\,\phi_1(-\chi\Delta t),
 \qquad \phi_1(z)=\frac{e^z-1}{z}.
\]

Because `eta>=0`, positivity is preserved even when the net affine coefficient
`chi` is negative.

## 3. Positive spectral–angular chart

Define

\[
 x=\frac{h_P\nu_H}{k_BT_*}.
\]

On the regular photon BE branch,

\[
 \Psi(x,e)=xB(e)-A(e)+\rho(x,e),
 \qquad f_H=\frac1{e^{\Psi}-1},
 \qquad \Psi>0.
\]

`A` uses the TEFF sign convention; in the common CMB notation
`f=[exp(x+mu_CMB)-1]^{-1}`, `A=-mu_CMB`.

\[
 B(e)=\sum_{\ell m}^{L_B}b_{\ell m}Y_{\ell m}(e),
 \qquad A(e)=\sum_{\ell m}^{L_A}a_{\ell m}Y_{\ell m}(e),
\]

\[
 \rho(x,e)=\sum_{k=0}^{K}\sum_{\ell m}^{L_\rho}
 r_{k\ell m}P_k(\xi(x))Y_{\ell m}(e).
\]

Angular refinement cannot counterfeit missing spectral shape, and multigroup
refinement cannot counterfeit an omitted angular shell.

## 4. Face traces and fluxes

\[
 f_q(t,e)=f_H[t,\nu_q(t,e),e],\qquad q\in\{r,b\}.
\]

For one sign convention,

\[
 \mathcal F_r=\int\frac{d\Omega}{4\pi}
 \max[-v_{x,r}(e),0]f_r(e),
\]

\[
 \mathcal F_b=\int\frac{d\Omega}{4\pi}
 \max[v_{x,b}(e),0]f_b(e).
\]

The exact sign is an interface contract. The positive-part operation creates a
derivative kink at the grazing curve `v_x=0`; the corresponding half-range
trace with an indicator is discontinuous. A low-rank smooth full-sphere state
therefore does not imply a low-rank face integrand.

## 5. Independent error axes

The admission logic keeps

\[
 \epsilon_{\rm spec}(K),\qquad
 \epsilon_{\rm ang}(L),\qquad
 \epsilon_{\rm face}(Q)
\]

separate, supplemented by an orientation diagnostic

\[
 \epsilon_{\rm rot}
 =\frac{\max_j\mathcal F_{R_jQ}-\min_j\mathcal F_{R_jQ}}
        {\max(|\mathcal F_{Q_{\rm ref}}|,F_{\rm floor})}.
\]

Node count is not an error certificate.

## 6. Angular polyalgorithm

- Smooth state lane: positive dual/natural chart with adaptive harmonic/PSTF rank.
- Face-flux lane: at least two independent quadrature families with p- and
  orientation refinement.
- Low-regularity lane: local angular finite elements or mixed half-range
  moments when grazing curves, beams or residuals defeat the smooth lane.
- Lebedev-26: level-0 predictor and low-rank regression grid only.

## 7. Source-channel firewall

- source-identical virtual-spike updates act on signed `Delta_f`;
- paired one-photon coefficients act on total occupation;
- two-photon/Raman packet rates remain packet rates per H per second until an
  admitted deposition map converts them to occupation rate.
