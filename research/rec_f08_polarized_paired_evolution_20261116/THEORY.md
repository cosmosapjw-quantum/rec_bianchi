# Original F08 paired evolution with persistent polarized Thomson collisions

## Scope, source identity, and status

This note derives the collision and screen-transport operations used by the
source-matched F08 receiver.  The inherited source is the original REI F08
`paired_runtime`, imported through REC PR199 and the physical-tetrad correction
in REC PR200.  PR200 was inspected at commit
`c995fb84a5523202ab429003a78d7d590b51ace9`; its degree-four positive quadrature
and explicit `q_midpoint_continuum` interpretation are reused.  The source pair
SHA256 is
`0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8`.

The actual original anisotropic model has

\[
 (H_x,H_y,H_z)=(1.01,0.99,1.00)\times10^{-14}\ {\rm s}^{-1},
 \qquad a_i(t)=\exp(H_i t).
\]

It is diagonal, homogeneous, non-tilted **triaxial Bianchi I**.  Its unequal
transverse expansion rates must be retained.  An axisymmetric simplification
of polarization-basis transport does not apply to these source values.
The signature is \((-+++ )\), proper time is measured in seconds, and the
original source uses \(\Delta t=625000000\ {m s}\) per recorded macro step.
The photon mass unit remains photons/H; physical spectral energy is measured
in the source's eV convention.  The inherited gas density, cross sections,
helium abundance, boundary treatment, and source normalization remain source
inputs.  F05 normalization and clocks are not inputs to this receiver.

The derived frozen-tetrad Thomson semigroup is exact for the stated finite
quadrature.  The complete receiver additionally uses a native/physical
collocation adapter, prescribed gas/transport splitting, and finite time
steps.  These approximations have separate error diagnostics.  In particular:

* The original fixed-hat support FAIL remains an inherited source failure.
* The original q-frame photon-number-quadrupole comparison at tick 142 remains
  FAIL: relative method disagreement `0.04152277708926094` exceeds `0.03`.
  The threshold and historical output are retained.  A new physical-tetrad
  comparison also uses its original `0.03` threshold; changing the target or
  representation does not retrospectively pass the old test.
* Resetting photon intervals to the post-collision point is a conditional
  point-state continuation.  It permits a local native trial with that point
  as input; it does not propagate the previous interval enclosure and gives
  no cumulative interval certification of the coupled trajectory.
* Kernel verification and a conditional coupled trajectory do not constitute
  original-owner admission or canonical DAG advancement.

## 1. Physical screen and the frozen-tetrad collision equation

Let \(n_i\in S^2\) be physical propagation directions in the instantaneous
comoving orthonormal tetrad and let

\[
 P_i=\mathbf 1-n_i n_i^{\mathsf T},\qquad w_i>0,\qquad\sum_iw_i=1.
\]

The angular rule uses a normalized sphere average, rather than weights that
sum to \(4\pi\).  The state \(S_i\) is a Hermitian transverse **coherency mass**:

\[
 S_i=P_iS_iP_i,\qquad S_i\succeq0,\qquad
 N_i=\operatorname{tr}S_i,\qquad M=\sum_iS_i.
\]

For a screen basis \((e_\theta,e_\phi)\), the local two-dimensional coherency is

\[
 C_i=\frac12\begin{pmatrix}I_i+Q_i&U_i+iV_i\\U_i-iV_i&I_i-Q_i\end{pmatrix},
 \qquad S_i=E_iC_iE_i^{\mathsf T},\quad E_i=(e_\theta,e_\phi).
\]

Thus \(Q=I_\theta-I_\phi\), \(U=2\operatorname{Re}C_{\theta\phi}\), and
\(V=2\operatorname{Im}C_{\theta\phi}\).  The sign of \(V\) is explicit because
both signs occur in the literature.  Positivity is equivalent to
\(I\ge0\) and \(Q^2+U^2+V^2\le I^2\) on each screen.

For cold stationary electrons in the comoving frame, in the elastic Thomson
limit, the collision equation at each fixed **physical photon energy** is

\[
 \frac{dS_i}{d\tau}=({\cal K}S)_i-S_i,
 \qquad ({\cal K}S)_i=\frac32w_iP_iMP_i,
 \qquad d\tau=c\,\sigma_Tn_e(t)\,dt.                 \tag{1}
\]

Here \(c\) is retained and \(n_e\) is the proper electron density from the same
gas state and clock as the photon state.  The product \(c\sigma_Tn_e dt\) is
dimensionless when the source's consistent length and time units are used.
Recoil, electron thermal redistribution, bulk-velocity corrections, and
frequency-changing Compton effects are outside equation (1).

For unpolarized input \(S_j=m_jP_j/2\), taking the trace of the gain gives

\[
 \operatorname{tr}({\cal K}S)_i
 =\sum_j\frac34w_i[1+(n_i\cdot n_j)^2]m_j.          \tag{2}
\]

This is precisely the PR200 unpolarized angular kernel.  Equation (1) also
uses the incoming \(Q,U,V\), so polarization persists and feeds later
scattering events.

## 2. Conservation, positivity, and the closed moment equation

The required second and fourth moments are

\[
 \sum_iw_i n_{ia}n_{ib}=\frac{\delta_{ab}}3,
\]
\[
 \sum_iw_i n_{ia}n_{ib}n_{ic}n_{id}
 =\frac{\delta_{ab}\delta_{cd}+\delta_{ac}\delta_{bd}
              +\delta_{ad}\delta_{bc}}{15}.        \tag{3}
\]

Second-moment exactness alone gives

\[
 \sum_i\operatorname{tr}({\cal K}S)_i
 =\frac32\operatorname{tr}\left(M\sum_iw_iP_i\right)
 =\operatorname{tr}M.                              \tag{4}
\]

Photon number is therefore conserved by the collision.  At fixed physical
energy \(E_g\), multiplying (4) by \(E_g\) proves elastic energy conservation
in that group, and summing groups gives the corresponding total energy
statement.  It does not justify mixing distinct direction-dependent physical
energies into one scattering group.

Since \(w_i>0\) and \(P_iMP_i\succeq0\), \({\cal K}\) is a positive map.
The collision evolution has the convergent uniformization representation

\[
 e^{\tau({\cal K}-1)}
   =e^{-\tau}\sum_{r=0}^{\infty}\frac{\tau^r}{r!}{\cal K}^r,
 \qquad\tau\ge0,                                  \tag{5}
\]

which proves positivity and trace conservation of its exact finite-time map.
No clipping, cone projection, or final trace normalization is needed by this
operator.  Every gain remains screen projected, so transversality is also
preserved.

For a general Hermitian \(M\), define

\[
 M_0=\frac{\operatorname{tr}M}{3}\mathbf1,\quad
 M_2=\frac{M+M^{\mathsf T}}2-M_0,\quad
 M_A=\frac{M-M^{\mathsf T}}2.                       \tag{6}
\]

Here \(M_2\) is real symmetric trace free and \(M_A\) is imaginary
antisymmetric.  Expanding \(PMP\) and applying (3) gives

\[
 \sum_i\frac32w_iP_iMP_i
 =\frac7{10}\frac{M+M^{\mathsf T}}2
   +\frac1{10}\operatorname{tr}M\,\mathbf1
   +\frac12\frac{M-M^{\mathsf T}}2.                \tag{7}
\]

Consequently,

\[
 M(\tau)=M_0+e^{-3\tau/10}M_2+e^{-\tau/2}M_A.      \tag{8}
\]

The zero, \(3/10\), and \(1/2\) decay rates belong to the scalar, real STF,
and imaginary antisymmetric total coherency moments.  They are not a claim
that every angular multipole has one of these three rates: the remaining
kernel-null angular modes decay at unit rate.

## 3. Exact collision advance and stable incremental form

Substitute (8) into the variation-of-constants solution of (1):

\[
 S_i(\tau)=e^{-\tau}S_i(0)
  +\frac32w_iP_i\bigl[a(\tau)M_0+b(\tau)M_2+d(\tau)M_A\bigr]P_i, \tag{9}
\]

\[
 a=1-e^{-\tau},\qquad
 b=\frac{e^{-3\tau/10}-e^{-\tau}}{7/10},\qquad
 d=2(e^{-\tau/2}-e^{-\tau}).                        \tag{10}
\]

The moments on the right of (9) are those of the initial state of the
collision substep.  The large-depth limit is the unpolarized isotropic mass

\[
 S_{i,\mathrm{eq}}=\frac12w_iN P_i,
 \qquad N=\operatorname{tr}\sum_iS_i(0).             \tag{11}
\]

For small optical depth, evaluate coefficients with `expm1`:

```python
a = -expm1(-tau)
b = exp(-0.3*tau) * (-expm1(-0.7*tau)) / 0.7
d = 2*exp(-0.5*tau) * (-expm1(-0.5*tau))
```

A stable increment is

\[
 \Delta S_i=-a(S_i-S_{i,\mathrm{eq}})
       +\frac32w_iP_i(bM_2+dM_A)P_i.               \tag{12}
\]

For an extremely weak newly produced polarization, extract \(\Delta Q\),
\(\Delta U\), and \(\Delta V\) from (12), then add them to separately stored
Stokes components.  Subtracting large nearly equal Cartesian coherency
diagonals after the full update can erase a small polarization signal.
This numerical measure does not change the collision model.

## 4. Triaxial geodesic and polarization-basis transport

The conserved Killing-ray label \(q\) and the physical tetrad direction obey

\[
 n(t)=\frac{A(t)q}{g(t)},\quad
 A(t)=\operatorname{diag}(e^{-H_xt},e^{-H_yt},e^{-H_zt}),\quad
 g(t)=|A(t)q|,
\]
\[
 J(t)=\frac{\det A(t)}{g(t)^3}
 =\frac{d\Omega_n}{d\Omega_q}.                     \tag{13}
\]

In particular, a native equal-q-cell continuum mass represents a physical
angular intensity proportional to \(N_q/J\); applying \(J\) a second time
would be a measure error.  Equation (13) is inherited from PR200.

For \(H=\operatorname{diag}(H_x,H_y,H_z)\),

\[
 \dot n=(H_n\mathbf1-H)n,\qquad H_n=n^{\mathsf T}Hn.\tag{14}
\]

The screen-gauge form of parallel transport of a unit polarization vector is

\[
 \dot e=-n(e\cdot\dot n)=n(n^{\mathsf T}He).        \tag{15}
\]

It preserves \(e\cdot n=0\) and \(e\cdot e=1\).  In the spherical screen
basis, set \(e=a_\theta e_\theta+a_\phi e_\phi\).  Since
\(e_\theta\cdot\dot e_\phi=-\cos\theta\,\dot\phi\),

\[
 \dot\phi=(H_x-H_y)\frac{n_xn_y}{n_x^2+n_y^2},\qquad
 \dot\Omega=n_z(H_x-H_y)\frac{n_xn_y}{n_x^2+n_y^2}, \tag{16}
\]
\[
 \binom{a_\theta}{a_\phi}_{t_1}
 =\begin{pmatrix}\cos\Omega&\sin\Omega\\-\sin\Omega&\cos\Omega\end{pmatrix}
  \binom{a_\theta}{a_\phi}_{t_0},\qquad
 \Omega=\int_{t_0}^{t_1}\dot\Omega\,dt.
\]

Thus the persistent Stokes components transform as

\[
 (Q+iU)_{t_1}=e^{-2i\Omega}(Q+iU)_{t_0},\qquad
 I_{t_1}=I_{t_0},\quad V_{t_1}=V_{t_0}               \tag{17}
\]

for this basis operation alone.  Physical intensity/energy changes are
handled by the native transport factors and are not included in (17).
The original q128 grid has no exact polar directions.  A general-purpose
implementation must handle the screen-chart singularity separately if poles
are introduced.  Triaxial paths are not generally great circles, so an
endpoint-only minimal rotation is not a replacement for (16).

## 5. Positive native/physical adapter and its conditional generator

The native source stores equal-q-cell continuum coherency masses \(T_i\).
The moment-exact physical collision rule stores masses on \(w_i\).  The
source-matched adapter uses

\[
 A_i=\frac{w_i}{J_i},\qquad B_i=A_i^{-1}=\frac{J_i}{w_i}.
\]

For one physical-energy group with native total
\(N=\operatorname{tr}\sum_iT_i\), mapping forward, applying (9), mapping
back, and restoring the original group total is equivalently

\[
 F_\tau(T)=
 N\,\frac{B\,e^{\tau L_w}AT}
 {\operatorname{tr}\sum_i[B\,e^{\tau L_w}AT]_i}.      \tag{18}
\]

The forward common normalization cancels from this composite formula.
For zero optical depth it is identity.  Positive \(A_i,B_i\) preserve the
coherency cone.  At fixed geometry, (18) is a normalized conjugation of the
finite semigroup and itself has the semigroup property.  The native
representation of unpolarized isotropic physical intensity,
\(T_i\propto J_iP_i\), is stationary.  Empty energy groups require an
explicit zero-state branch rather than division by their zero trace.

Equation (18) is **nonlinear in the radiation state**.  Its modified generator
can be stated exactly.  Define

\[
 G_i(T)=\frac32J_iP_i
       \left[\sum_j\frac{w_j}{J_j}T_j\right]P_i-T_i,
 \qquad\kappa(T)=\frac{\operatorname{tr}\sum_iG_i(T)}{N}.
\]

Then

\[
 \frac{dT_i}{d\tau}=G_i(T)-\kappa(T)T_i.             \tag{19}
\]

The final term is a state-dependent common extinction correction induced by
the native-total normalization.  Therefore the exact finite-quadrature claim
for (9) does not turn (18) into an exact linear continuum Thomson operator.
Its status is a **conditional collocation discretization**.  Diagnostics are
the raw inverse-projection trace drift, the inferred normalization factor or
\(\kappa\), method disagreement between the retained degree-four and
degree-six rules, and the superposition defect
\(F_\tau(T+U)-F_\tau(T)-F_\tau(U)\).  These quantify this approximation
without changing the old 3% gate.

## 6. Physical-energy elasticity and feedback to the native gas solver

Each collision group must refer to a common physical photon energy or to a
documented common physical-energy spectral basis across directions.  A
conserved-q radial label generally maps to different physical energies on
different rays through \(g(t)\).  Passing such a label unchanged to a new
direction is not elastic Thomson scattering; it requires an explicit
physical-energy remap.  Number and energy ledgers must include that remap if
the native spectral representation needs it.

For isotropic comoving targets, an instantaneous photoionization rate has
the form

\[
 \Gamma_a=c\int dE\,\sigma_a(E)
                 \int d\Omega\,n_\gamma(E,\Omega). \tag{20}
\]

Pure elastic angular redistribution that preserves each physical-energy
group total leaves (20) and the corresponding instantaneous heating
integral unchanged.  Later direction-dependent redshift and threshold
crossing can change them.  This is a useful discriminating check: a change
of the frozen-frame immediate gas rate would point to spectral grouping,
normalization, or ledger inconsistency.

The new receiver retains the original `paired_trial` as the scalar
gas/transport stage, including its two inherited half-step endpoints.  The
updated photon intensity is fed back to the next `paired_trial`; polarization
is a persistent state, not a fresh source-only diagnostic.  Existing
polarized photons receive the audited native `point_factors` and the screen
phase (17).  Newly emitted unpolarized photons enter with \(Q=U=V=0\).
The factors must apply to the corresponding pre-existing photon component;
unpolarized injection is not a reason to regenerate or rescale polarization
without its transport/absorption factor.

The receiver then applies a post-step collision at the endpoint gas density,

\[
 \Delta\tau_k=c\,\sigma_Tn_{e,k+1}\,\Delta t,
 \qquad\Delta t=625000000\ {\rm s}                 \tag{21}
\]

for the original run, with the same macro time interval as the just-completed
native step.  The source's gas fractions and proper density determine
\(n_{e,k+1}\); it is not imported from another scenario or clock.  When the
usual fraction definitions are used,
\(n_e=n_H[x_{\rm HII}+f_{\rm He}(x_{\rm HeII}+2x_{\rm HeIII})]\), with
every factor inherited from this source.

This ordering is a **Lie split**, native gas/transport followed by collision.
Endpoint opacity is also a time quadrature approximation.  The exactness of
the frozen collision solution and any symmetric substructure within
`paired_trial` do not make the complete composition second order.
Refinement at the same final proper time, using \(\Delta t/2\) and
\(\Delta t/4\) with the same physical inputs, measures its temporal error.

After collision, replacing the photon lower/upper interval endpoints by the
point result explicitly forgets the previous enclosure.  A subsequent
native interval trial is conditional on that point input.  Native local
checks, point trajectory comparisons, source support failures, and a
cumulative certified coupled enclosure are distinct claims; the latter is
not established by this receiver.

## 7. Quadrupole conventions and retained method comparison

For an axisymmetric analytic check only, define

\[
 I_\ell=\frac12\int_{-1}^{1}I(\mu)P_\ell(\mu)\,d\mu,
 \qquad Q_\ell=\frac12\int_{-1}^{1}Q(\mu)P_\ell(\mu)\,d\mu.
\]

With the stated \(Q\) convention,

\[
 \Pi=I_2-Q_0+Q_2,\qquad
 I'=-I+I_0+\frac12\Pi P_2,\qquad
 Q'=-Q-\frac34\Pi(1-\mu^2),\qquad
 \Pi'=-\frac3{10}\Pi.                              \tag{22}
\]

The normalized Cartesian intensity quadrupole

\[
 {\cal Q}_{ab}=\frac{\langle I(n)(n_an_b-\delta_{ab}/3)\rangle}
                    {\langle I\rangle}
\]

satisfies \({\cal Q}_{zz}=2I_2/(3I_0)\) and
\({\cal Q}_{xx}={\cal Q}_{yy}=-I_2/(3I_0)\) in that analytic axisymmetric
case.  The actual triaxial source requires its full tensor, with directions,
measure, normalization, and tensor basis matched before comparing estimators.
For a very small quadrupole, record the absolute difference and signal
amplitude alongside relative disagreement.  These diagnostics do not alter
the historical threshold or its FAIL.

## 8. Independent derivation checks performed before repository integration

These checks concern the mathematical kernel and screen-transport formula.
They are separate from producer-authored repository tests and from the
actual F08 coupled replay.

1. **Wolfram symbolic integration.**  With
   \(n=(\sqrt{1-\mu^2}\cos\phi,\sqrt{1-\mu^2}\sin\phi,\mu)\),
   integrate \((3/2)PMP\) over \(d\phi\,d\mu/(4\pi)\) for a symbolic
   real symmetric 3 by 3 matrix.  The result was exactly
   \((7M+\operatorname{tr}M\,\mathbf1)/10\), and subtracting that expression
   returned the exact zero matrix.  Antisymmetric contraction in (7) follows
   independently because \(n^{\mathsf T}M_An=0\).
2. **Python/NumPy independent uniformization.**  Use the original 8 midpoint
   polar rings and 16 azimuths with PR200's rational degree-four weights,
   random complex positive screen coherencies (seed `70414`), and normalize
   total trace to one.  Compare (9) at \(\tau=0.7\) with the independent
   Poisson series (5), repeatedly applying the projected gain.  Seventeen
   nonzero terms reduced the term below `1e-19`.  Maximum absolute difference
   was `3.469451597035155e-18`.  The closed moment identity error was
   `2.7755575966177844e-16`; composition at `0.2 + 0.5` differed from `0.7`
   by `1.7347261048464754e-18`; total trace residual was zero.  The minimum
   eigenvalue was `-1.7190798362322042e-18` at roundoff, transversality residual
   was `6.594944350062752e-19`, and the `tau=500` equilibrium error was
   `1.301046168446706e-18`.
3. **Independent screen-vector ODE.**  With scaled rates
   `(1.01, 0.99, 1.0)`, normalized initial direction proportional to
   `(0.43, 0.51, 0.744983221)`, and initial screen components `(0.8, 0.6)`,
   integrate (15) on scaled time `[0,2]` using SciPy `solve_ivp`
   (`rtol=1e-12`, `atol=1e-14`).  Independently integrate (16) with `quad`
   (`epsabs=1e-14`).  The phase was `0.014620246644247239`, and the final
   screen components differed by `2.886579864025407e-15`.  This verifies the
   sign in (17) without using the receiver's basis implementation.
4. **Independent read-only implementation review.**  Inspect `collision.py`
   with SHA256
   `8ee1e6faefc2a681e9d3d8c592546b77f83d13d3a2bd792a85a368974c4ff969`.
   Construct a different degree-four-exact grid: the 12 normalized
   icosahedron vertices `(0,+/-1,+/-phi)`, `(+/-1,+/-phi,0)`, and
   `(+/-phi,0,+/-1)`, with equal weights and the golden ratio `phi`.
   Independently form all 2 by 2 Jones screen overlaps, write their real
   Mueller 4 by 4 blocks explicitly, and assemble the 48 by 48 generator.
   Compare SciPy `scipy.linalg.expm(tau*L)` against the module's
   `exact_collision_stokes` on random physical Stokes masses (seed `96217`).
   Maximum absolute differences were `8.881784197001252e-16` at `tau=1e-8`,
   `1.5543122344752192e-15` at `tau=0.7`, and
   `6.972200594645983e-14` at `tau=30`.  Total intensity residual was at most
   `7.105427357601002e-15`, the Stokes-cone slack remained positive, and the
   independently assembled generator had decay eigenvalues
   `{-1, -0.5, -0.3, 0}`.  No significant kernel defect was identified.
   This ephemeral review used a different grid and a dense matrix
   exponential, and was not added as another producer-authored test.

## Primary literature and convention mapping

* Cyril Pitrou, *The radiative transfer at second order: a full treatment of
  the Boltzmann equation with polarization*,
  <https://arxiv.org/abs/0809.3036>, original PDF
  <https://arxiv.org/pdf/0809.3036>.  Section 1 defines the screen-projected
  Hermitian distribution; equation (6.17) gives the rest-frame Thomson
  intensity, linear-polarization, and circular-polarization terms.  The
  screen convention is directly compatible with `(-,+,+,+)` after retaining
  the physical constants used here.
* Anthony Challinor, *Microwave background polarization in cosmological
  models*, Physical Review D **62**, 043004 (2000),
  <https://doi.org/10.1103/PhysRevD.62.043004>,
  <https://arxiv.org/abs/astro-ph/9911481>, original PDF
  <https://arxiv.org/pdf/astro-ph/9911481>.  Equation (3.7) is the exact
  electron-rest-frame Thomson scattering tensor; equations (3.13)--(3.14)
  identify basis transport and optical depth in its line-of-sight solution.
  That paper uses `(+,-,-,-)` and `c=1`, so screen signs and factors of `c`
  must be converted before comparing component expressions.

Both primary PDFs and the indicated equations were read on 2026-11-16.
Exa, SciSpace, and Parallel were used for discovery; a failed Parallel fetch
of Pitrou's author-hosted PDF was resolved by reading the arXiv PDF.  The
finite-quadrature moment decomposition, exact semigroup, and normalized
adapter generator above are direct derivations here, rather than claims
that these implementation formulas were quoted from those papers.
