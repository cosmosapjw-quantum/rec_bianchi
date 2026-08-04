# PR-01B1-B0 line-centre Maxwell–Jüttner deposition

## Scope

This bounded integrated slice treats the central incoming Ly-alpha
frequency cell. It combines exact recoil kinematics, the scalar
\(2p\)-pole+crossed response, a Maxwell–Jüttner atom distribution, the
moving-target incident flux and positive red/interior/blue deposition.

It is not the complete \(17\times17\) full-angle kernel.

## Rate measure

\[
\nu_i^*=\Gamma(1-\boldsymbol\beta\cdot\boldsymbol n_i)\nu_i,
\]

\[
\boxed{
d\Gamma
=
n_{1s}F_{\rm MJ}(\boldsymbol p)
c(1-\boldsymbol\beta\cdot\boldsymbol n_i)
\,d^3p\,d\sigma^*.
}
\]

The outgoing rest-frame direction is importance sampled from

\[
p(\mu)=\frac38(1+\mu^2).
\]

## Oscillator-area correction

\[
A_{21}(f_{12})
=
\frac{8\pi^2r_ef_{12}\nu_\alpha^2}{3c},
\qquad
\boxed{
\mathcal C_A=
\frac{A_{21}^{\rm adopted}}{A_{21}(f_{12})}.
}
\]

This correction preserves the oscillator-strength area while retaining
the adopted natural width. It is source-derived, not fitted.

## Resonance importance sampling

The longitudinal velocity uses a Gaussian/Cauchy mixture centred on the
Doppler resonance root. The exact Maxwell–Jüttner density divided by the
proposal density is the importance weight.

## Control variate

The known no-recoil finite-volume Hummer column is evaluated with the
same Sobol point:

\[
\boxed{
K^{\rm exact}
=
K^{\rm Hummer}
+
\langle K_e^{\rm exact}-K_e^0\rangle_{\rm QMC}.
}
\]

## Positive deposition

\[
D_R(e)+\sum_iD_i(e)+D_B(e)=1,
\qquad D_\alpha(e)\ge0.
\]

The same event gives

\[
\Delta p_\gamma^\mu=k_f^\mu-k_i^\mu,
\qquad
\Delta P_H^\mu=-\Delta p_\gamma^\mu.
\]

## Shared conductance

After the independent PT audit of PR-01B1-A,

\[
S_{ic}=K_{i\leftarrow c}\Pi_c,
\qquad
K_{c\leftarrow i}=S_{ic}/\Pi_i.
\]

This is microscopic event pairing, not posterior matrix
symmetrization.
