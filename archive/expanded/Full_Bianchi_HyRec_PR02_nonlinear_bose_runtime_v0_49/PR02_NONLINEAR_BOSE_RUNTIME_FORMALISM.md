# PR-02 nonlinear anisotropic Bose collision production integration

## Scope and conventions

Metric signature is \((-,+,+,+)\). Physical constants are not set to one;
`BackgroundSnapshot` rates are in s\(^{-1}\), and the Ly-alpha boundary
adapter retains \(c\), \(h\), and \(k_B\) in the surrounding physical
model. This PR closes the scalar collision substep only. It does not yet replace
the provisional scalar 2p pole+crossed amplitude; that is PR-03.

## Frequency-angle state and exact BE family

For frequency cell \(i\), hydrogen-frame angular node \(q\), mode measure
\(g_i>0\), and equilibrium measure \(\pi_i>0\), define

\[
 z_i=\frac{\pi_i}{g_i},\qquad
 \phi_{iq}=\frac{f_{iq}}{z_i(1+f_{iq})}.
\]

Every isotropic Bose-Einstein activity family

\[
 f_i^{\rm BE}=\frac{a z_i}{1-a z_i}
\]

has constant \(\phi=a\) and is an exact null of the discrete pair action.

## Activity-reference-subtracted edge flux

Let \(K_{ij}^{(\ell)}=K_{ji}^{(\ell)}\) be the inherited v0.47
conductance moments and let \(\mathcal K_{ij}\star\) denote their zonal
harmonic convolution. A common angular activity

\[
 a_\star=\frac{1}{N_\nu}
 \sum_i\sum_q w_q\phi_{iq}
\]

is subtracted before convolution. With

\[
 \Delta_i=(1+f_i)(\phi_i-a_\star),
\]

the pair contribution is evaluated as

\[
 C^N_i=(1+f_i)
 \left[\mathcal K_{ij}\star\Delta_j
 -(\phi_i-a_\star)
  \mathcal K_{ij}\star(1+f_j)\right],
\]

plus the symmetric \(j\)-equation. This is algebraically identical to the
stimulated gain-minus-loss form, but avoids subtracting two large nearly equal
terms near equilibrium. Pair symmetry closes the discrete photon-number left
null.

The boundary-only diagnostic retains exactly the interior-to-near/far pairs and
sets same-cell terms to zero. Exterior-to-exterior collisions remain in the
Liouville/boundary module, as locked in v0.47.

## Positive harmonic-exact angular grids

The runtime policies are fixed to

* \(L=12\): finite or mixed tilt, SciPy Lebedev order 29, 302 nodes;
* \(L=20\): nonlinear even shear, order 41, 590 nodes;
* \(L=24\): directional red/blue crossing, order 53, 974 nodes.

All weights are positive. The discrete analysis matrices satisfy
\(\|AS-I\|_\infty<5\times10^{-12}\) in the released evidence. The order
and point-count mapping follows the SciPy `lebedev_rule` registry.

## BackgroundSnapshot runtime adapter

The grid directions are hydrogen-frame directions \(e_H\). They are inverse
aberrated to \(e_n\), passed through the PR-01 normal-frame characteristic,
and mapped back with the exact finite-tilt adapter. Geometry determines
\(\mathcal D_H\), \(R_H=D_0\ln\nu_H\), direction flow, and red/blue
boundary speeds. It is not an argument of the local conductance/amplitude
operator. A common forced-grid field therefore produces bitwise-identical local
collision actions for Bianchi II, tilted VI_h, and exceptional VI_-1/9.

## Exact JVP

For a perturbation \(\delta f\),

\[
 \delta\phi_i=
 \frac{\delta f_i}{z_i(1+f_i)^2},
 \qquad
 \delta a_\star=
 \frac{1}{N_\nu}\sum_{iq}w_q\delta\phi_{iq},
\]

and the stable derivative of \(\Delta_i\) is

\[
 \boxed{
 \delta\Delta_i=
 \frac{\delta f_i}{z_i}
 -a_\star\delta f_i
 -(1+f_i)\delta a_\star
 }.
\]

The production JVP differentiates each harmonic convolution analytically. No
finite-difference Jacobian enters Newton-GMRES. Central differences are retained
only as regression evidence.

## Positivity-preserving implicit collision update

The backward-Euler residual is

\[
 \mathcal R(f^{n+1})=
 f^{n+1}-f^n-\Delta t\,C[f^{n+1}]=0.
\]

Newton variables are \(u=\ln f\), so every accepted iterate has
\(f=e^u>0\). The matrix-free action is

\[
 D_u\mathcal R[\delta u]
 =f\,\delta u
 -\Delta t\,DC[f][f\,\delta u].
\]

No clipping and no post-step number renormalization are used. The released
stress timestep is 1.02 times the first explicit-Euler positivity limit; explicit
Euler is negative in every lane while the converged implicit fields remain
strictly positive. Number conservation follows from the collision left null and
residual closure. Discrete free-energy decrease is tested for the released
states; it is not asserted here as a theorem for arbitrary timestep and field.

## Thermodynamic and four-force ledgers

The number and free-energy functionals are

\[
 N_\gamma=\sum_{iq}g_iw_q f_{iq},
\]

\[
 \mathcal F=\sum_{iq}g_iw_q
 \left[f\ln f-(1+f)\ln(1+f)-f\ln z_i\right].
\]

The reported `entropy_free_energy_production` is

\[
 \dot{\mathcal F}=\sum_{iq}w_q
 \left[\ln\frac{f}{1+f}-\ln z_i\right]C^N_{iq}
 \le 0.
\]

Photon and atom four-force contributions are accumulated from the same event
with opposite sign and then Lorentz-transformed independently from the hydrogen
tetrad to the normal tetrad. Their sum vanishes in both frames.

## Independent references and limitations

The high-precision receipt uses 80-digit `mpmath` checks for the stable activity
derivative, Lorentz inverse, and BE pair null because no Wolfram or Precise
Special Functions connector was exposed in this runtime. The full JVP is also
checked against central differences on every production lane.

Numerical design references used for context:

1. SciPy documentation for `scipy.integrate.lebedev_rule` and its order/node registry.
2. Markowich and Pareschi, *Fast conservative and entropic numerical methods for the Boson Boltzmann equation*, arXiv:1009.2748.
3. Hu, Li, and Pareschi, *Asymptotic-preserving exponential methods for the quantum Boltzmann equation with high-order accuracy*, arXiv:1310.7658.
4. Zhang, Shen, and Hu, *SAV-based entropy-dissipative schemes for a class of kinetic equations*, arXiv:2408.16105.

The released stress occupations are deterministic collision-substep regression
states built from actual BackgroundSnapshot characteristics. They are not
claimed to be solutions of the coupled Liouville plus recombination system.
