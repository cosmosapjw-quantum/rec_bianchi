# PR-05C2C0 / v0.65 — mathematical and physical closure contract

## 0. Result and claim boundary

This stage closes the remaining **load-bearing scalar equations and theorems**
needed before direct source-temperature network compilation and multi-macro
trajectory integration.  It does not claim that those numerical implementations
have already been completed.

The closure is exact under the following declared scope:

1. metric signature `(-,+,+,+)`;
2. ordinary frequency `nu` in Hz, with `c`, `h`, and `k_B` explicit;
3. homogeneous Bianchi background, tetrad plus 1+3 variables;
4. all eleven Bianchi types through the chart-independent `BackgroundSnapshot`
   interface, with finite tilt and nonlinear large shear;
5. scalar, unpolarized atomic populations without atomic alignment;
6. the current scalar-elastic COM--KHW collision sector.  Raman production,
   fine structure, polarization, and atomic alignment remain outside this
   scalar completion target.

The two v0.64 non-identifiability results are **not erased**:

- an instantaneous scalar original-HyRec history datum does not determine an
  angular distribution;
- an explicit positive thermodynamic conductance rescaling is not a direct
  source-temperature COM--KHW network.

They are resolved at theory level by (i) a well-posed initial-boundary-value
problem that generates angular structure by exact Bianchi characteristics from
an explicitly isotropic hydrogen-frame source, and (ii) a structure-preserving
contract for direct positive event-kernel compilation and interpolation.  These
are new, explicitly stated extension axioms, not relabelled source data.

---

## 1. Phase-space and frame conventions

Let `n^a` be the normal congruence and let `e^a` be a normal-frame unit spatial
photon direction,

\[
 n_a e^a=0,\qquad e_a e^a=1.
\]

For ordinary frequency `nu_N` in the normal tetrad,

\[
 p^a=\frac{h\nu_N}{c}\left(n^a+e^a\right).
\]

The finite hydrogen-frame tilt is `beta^alpha`, with

\[
 \beta^2<1,\qquad \gamma=(1-\beta^2)^{-1/2},\qquad
 D=\gamma\left(1-\boldsymbol\beta\!\cdot\!\mathbf e\right)>0.
\]

The hydrogen-frame frequency is

\[
 \nu_H=D\nu_N.
\]

The strict positivity of `D` follows from
`1-beta.e >= 1-|beta| > 0`; hence the finite boost cannot change the sign of
frequency.  Photon occupation is the scalar phase-space distribution and is
therefore evaluated at the boosted frequency and aberrated direction rather
than multiplied by an intensity Jacobian.

### 1.1 Exact normal-frame characteristic

With physical rates in `s^-1`,

\[
 \frac{d\ln\nu_N}{dt}
 =R_N
 =-H-\sigma_{\alpha\beta}e^\alpha e^\beta .
\]

Define `P^alpha_beta=delta^alpha_beta-e^alpha e_beta` and

\[
 s^\alpha
 =A^\alpha-(A_\mu e^\mu)e^\alpha
   +\left[\mathbf e\times(N\mathbf e)\right]^\alpha .
\]

The exact direction flow used by the locked background adapter is

\[
 \frac{de^\alpha}{dt}
 =-P^\alpha{}_{\beta}\sigma^\beta{}_{\gamma}e^\gamma
  +(\boldsymbol\Omega\times\mathbf e)^\alpha
  -P^\alpha{}_{\beta}s^\beta .
\]

No expansion in `sigma/H`, `A/H`, `N/H`, or tilt is made.

### 1.2 Exact finite-tilt hydrogen-frame characteristic

Let a dot denote the same physical characteristic derivative.  Then

\[
 R_H\equiv\frac{d\ln\nu_H}{dt}=R_N+\frac{d\ln D}{dt},
\]

with

\[
 \frac{d\ln D}{dt}
 =\gamma^2\boldsymbol\beta\!\cdot\!\dot{\boldsymbol\beta}
 -\frac{\dot{\boldsymbol\beta}\!\cdot\!\mathbf e
       +\boldsymbol\beta\!\cdot\!\dot{\mathbf e}}
       {1-\boldsymbol\beta\!\cdot\!\mathbf e}.
\]

The aberrated hydrogen-frame direction is

\[
 \mathbf e_H=
 \frac{\mathbf e+
 \left[\frac{(\gamma-1)(\boldsymbol\beta\cdot\mathbf e)}{\beta^2}
       -\gamma\right]\boldsymbol\beta}
 {\gamma(1-\boldsymbol\beta\cdot\mathbf e)} ,
\]

with the continuous zero-tilt limit.  The derivative is projected onto the
screen tangent plane, so `e_H.dot(e_H)=1` is preserved.

### 1.3 FLRW limit

For

\[
 \sigma_{\alpha\beta}=0,\quad A_\alpha=0,\quad N_{\alpha\beta}=0,
 \quad\Omega_\alpha=0,\quad\beta_\alpha=0,
\]

one obtains

\[
 \dot{\mathbf e}=0,\qquad \dot\nu=-H\nu.
\]

Thus isotropic initial and local source data stay isotropic, and the angular
extension reduces exactly to the scalar FLRW history.

---

## 2. Geometry-exact source-isotropy angular lift

### Definition 2.1 — extension axiom

The scalar original-HyRec history is interpreted as the hydrogen-frame
monopole of an **unpolarized, scalar atomic source**.  At each local atomic
emission/absorption event the primitive source and opacity are isotropic in the
hydrogen rest frame.  Anisotropic elastic redistribution and recoil are owned
by the COM--KHW collision operator, not duplicated in this source term.

This is the explicit extension axiom:

\[
 j_H=j_H(t,\nu_H),\qquad \chi_H=\chi_H(t,\nu_H),
\]

with no direction label.  It is exact within the scalar, unaligned-atom scope
and is not a claim that the original FLRW code supplied missing angular data.

### Definition 2.2 — characteristic transfer problem

Let the exact Bianchi/tilt characteristic through
`(t,nu_H,e_H)` be denoted by

\[
 s\mapsto\bigl(\nu_H(s),\mathbf e_H(s)\bigr).
\]

Between explicit collision events the occupation satisfies

\[
 \frac{df}{ds}=j_H\bigl(s,\nu_H(s)\bigr)
                -\chi_H\bigl(s,\nu_H(s)\bigr)f .
\]

For initial or inflow value `f_0`, define

\[
 \tau(s,t)=\int_s^t\chi_H(u,\nu_H(u))\,du .
\]

The formal solution is

\[
 \boxed{
 f(t,\nu_H,\mathbf e_H)=
 e^{-\tau(t_0,t)}f_0
 +\int_{t_0}^{t}e^{-\tau(s,t)}
 j_H(s,\nu_H(s))\,ds .}
\]

For pure free streaming, `j_H=chi_H=0` and occupation is constant along the
Bianchi photon characteristic.

### Theorem 2.3 — existence, uniqueness, positivity, and angular generation

Assume:

1. each `BackgroundSnapshot` branch is piecewise `C^1` in physical time;
2. `|beta|<1`;
3. branch, face, and grazing events are localized and the trajectory is
   restarted there;
4. `j_H>=0`, `chi_H>=0`, and `f_0>=0`;
5. the characteristic vector field is locally Lipschitz between events.

Then the phase-space characteristic and the formal transfer solution are unique
between events, and

\[
 f(t,\nu_H,\mathbf e_H)\ge0.
\]

Direction dependence at the target is generated because different target
directions backtrace to different source times and frequencies.  Consequently,
one scalar value at a fixed event still has angular rank one, but the complete
scalar source **history plus the exact characteristic flow** defines a unique
angle-resolved initial-boundary-value problem.

This reconciles the v0.63 rank no-go without inventing an instantaneous inverse
map.

### Moment ownership

- local source monopole: original-HyRec scalar primitive;
- geometric angular advection and redshift: exact Bianchi characteristic;
- collision-generated dipole and higher moments: direct COM--KHW kernel;
- any reduced moment closure used instead of discrete characteristics: an
  explicit approximation with its own realizability and uncertainty ledger.

Minimum-entropy closures may be used as reduced models, but they are not the
primary reconstruction theorem and cannot be called canonical original-HyRec
angular data.

---

## 3. Direct thermodynamic COM--KHW event network

Let a composite discrete phase-space index be

\[
 A=(i,a),
\]

where `i` is a frequency cell and `a` a positive-weight angular node.  Define

\[
 m_A=g_iw_a,\qquad [m_A]={\rm m}^{-3},
\]

where `sum_a w_a=1`, and

\[
 N_A=m_A f_A,\qquad [N_A]={\rm m}^{-3}.
\]

Let

\[
 z_A=z_i=\frac{\Pi_i}{g_i}>0
\]

be the dimensionless equilibrium activity weight.

### Definition 3.1 — direct positive event conductance

The locked scalar COM--KHW amplitude, atomic velocity measure, recoil
mass-shell, and positive angular quadrature define an unordered event
conductance

\[
 \mathcal K_{AB}(\vartheta)=\mathcal K_{BA}(\vartheta)\ge0,
 \qquad [\mathcal K_{AB}]={\rm m}^{-3}{\rm s}^{-1},
\]

at thermodynamic state `vartheta`.  The primary compiled object is the
**nonnegative nodal kernel**.  Harmonic coefficients are derived from it after
positivity is checked; arbitrary harmonic coefficients are not independently
interpolated because a nonnegative monopole alone does not imply a nonnegative
pointwise kernel.

### Definition 3.2 — stimulated Bose edge flux

The number flux into endpoint `A` from `B` is

\[
 J_{A\leftarrow B}
 =\mathcal K_{AB}
 \left[\frac{f_B(1+f_A)}{z_B}
       -\frac{f_A(1+f_B)}{z_A}\right].
\]

Define

\[
 \phi_A=\frac{f_A}{z_A(1+f_A)},\qquad
 \psi_A=\ln\phi_A.
\]

Then

\[
 \boxed{
 J_{A\leftarrow B}
 =\mathcal K_{AB}(1+f_A)(1+f_B)(\phi_B-\phi_A).}
\]

### Theorem 3.3 — structural closure of the edge network

For every symmetric nonnegative conductance graph:

1. **pair antisymmetry**
   \[
   J_{B\leftarrow A}=-J_{A\leftarrow B};
   \]
2. **photon-number conservation**
   \[
   \frac{d}{dt}\sum_A N_A=0;
   \]
3. **Bose--Einstein activity family**
   \[
   f_A^{\star}(q)=\frac{qz_A}{1-qz_A},\qquad 0\le qz_A<1,
   \]
   is an exact edgewise null state;
4. **quasi-positivity**: if `f_A=0` and all other occupations are nonnegative,
   then
   \[
   \dot N_A=\sum_B\mathcal K_{AB}\frac{f_B}{z_B}\ge0;
   \]
5. **relative free-energy dissipation** for
   \[
   \mathcal F[f]=\sum_A m_A\left[
   f_A\ln f_A-(1+f_A)\ln(1+f_A)-f_A\ln z_A\right]
   \]
   is
   \[
   \boxed{
   \dot{\mathcal F}
   =-\sum_{A<B}\mathcal K_{AB}(1+f_A)(1+f_B)
   (\phi_A-\phi_B)(\ln\phi_A-\ln\phi_B)\le0.}
   \]

Equivalently, with the positive logarithmic mean

\[
 \Lambda(x,y)=\frac{x-y}{\ln x-\ln y},
\]

one has

\[
 \dot{\mathcal F}
 =-\sum_{A<B}\mathcal K_{AB}(1+f_A)(1+f_B)
 \frac{(\phi_A-\phi_B)^2}{\Lambda(\phi_A,\phi_B)}.
\]

The proof is edge-local and therefore remains valid for a direct thermodynamic
network of arbitrary size.

### Same-cell angular redistribution

For equal-frequency endpoints, Bose stimulation cancels algebraically:

\[
 f_b(1+f_a)-f_a(1+f_b)=f_b-f_a.
\]

A symmetric nonnegative same-cell angular graph therefore has generator

\[
 \dot N_{ia}=\sum_b S_{i,ab}(f_{ib}-f_{ia}),
 \qquad S_{i,ab}=S_{i,ba}\ge0,
\]

which conserves the cell photon number and dissipates every convex angular
entropy.  The direct compiler must construct this graph from positive event
weights before harmonic projection.

---

## 4. Thermodynamic interpolation theorem

Let `theta` denote a thermodynamic path coordinate; for the source history it
may be chosen as `theta=ln T_m`, or as the branch-local accepted `eta=ln a`.
Compile the direct nodal event kernel at ordered nodes `theta_r`.

### Fixed-topology cell

On an interpolation cell, each event edge is either:

- identically zero at all vertices; or
- strictly positive at all vertices.

A zero/nonzero topology change is a discrete compiler event.  The
thermodynamic cell must be split there; no numerical floor is allowed to hide
it.

For a positive edge in a one-dimensional cell,

\[
 \ln\mathcal K_{AB}(\theta)
 =(1-\lambda)\ln\mathcal K_{AB}^{(0)}
 +\lambda\ln\mathcal K_{AB}^{(1)},
 \qquad
 \lambda=\frac{\theta-\theta_0}{\theta_1-\theta_0}.
\]

Thus

\[
 \mathcal K_{AB}(\theta)>0,
\]

and the analytic derivative is

\[
 \frac{\partial\mathcal K_{AB}}{\partial\theta}
 =\mathcal K_{AB}
 \frac{\ln\mathcal K_{AB}^{(1)}-\ln\mathcal K_{AB}^{(0)}}
      {\theta_1-\theta_0}.
\]

The same construction extends to nonnegative barycentric weights on a simplex.
Because symmetry is imposed on the unordered edge before interpolation, exact
reciprocity survives bitwise.  Because the target `g_i(theta)` and `z_i(theta)`
are rebuilt from the target thermodynamic state, Theorem 3.3 survives
interpolation **exactly**.  Withheld-node error affects accuracy, not
conservation, positivity, the BE null, or entropy sign.

No fitted global normalization appears anywhere in this contract.

---

## 5. Entropy-metric linearization and stiffness-independent preconditioner

At a connected Bose--Einstein state `f_A^star(q)`, perturb the entropy variable

\[
 \xi_A=\delta\psi_A,
 \qquad
 \delta f_A=f_A^\star(1+f_A^\star)\xi_A.
\]

The positive time metric is

\[
 W_A=m_A f_A^\star(1+f_A^\star)>0,
 \qquad [W_A]={\rm m}^{-3}.
\]

The edge linearization is

\[
 \delta J_{A\leftarrow B}
 =\omega_{AB}(\xi_B-\xi_A),
\]

where

\[
 \omega_{AB}
 =q\mathcal K_{AB}(1+f_A^\star)(1+f_B^\star)
 =\omega_{BA}\ge0.
\]

Therefore

\[
 W\dot\xi=-L_\omega\xi,
\]

where `L_omega` is a weighted graph Laplacian.  It is symmetric positive
semidefinite and

\[
 L_\omega\mathbf1=0,
\]

with only the constant activity mode in the nullspace when the event graph is
connected.

### W-orthogonal micro--macro split

Define

\[
 P x=\mathbf1\frac{\mathbf1^TWx}{\mathbf1^TW\mathbf1},
 \qquad Q=I-P.
\]

`P` owns the conserved chemical-activity/number mode and `Q` the relaxing
kinetic modes.

### Theorem 5.1 — AP spectral-equivalence contract

Consider the shifted collision block

\[
 A_\varepsilon=aW+\varepsilon^{-1}L_\omega,
 \qquad a>0,
\]

and an approximate graph `L_tilde` with the same nullspace.  Assume that on the
`Q` subspace

\[
 c_1 x^TL_\omega x
 \le x^T\widetilde Lx
 \le c_2 x^TL_\omega x,
 \qquad 0<c_1\le c_2<\infty.
\]

Then

\[
 \widetilde A_\varepsilon=aW+\varepsilon^{-1}\widetilde L
\]

is positive definite and, for every nonzero vector,

\[
 \boxed{
 \min\!\left(1,\frac1{c_2}\right)
 \le
 \frac{x^T A_\varepsilon x}{x^T\widetilde A_\varepsilon x}
 \le
 \max\!\left(1,\frac1{c_1}\right).}
\]

Consequently

\[
 \kappa\!\left(\widetilde A_\varepsilon^{-1}A_\varepsilon\right)
 \le
 \frac{\max(1,c_1^{-1})}{\min(1,c_2^{-1})},
\]

which is independent of collision stiffness `epsilon^{-1}`.

The proof decomposes `x=Px+Qx`; `P` and `Q` are `W`-orthogonal, and both graph
operators vanish on `P`.  On `Q`, the assumed inequalities imply
`c_1 L_omega <= L_tilde <= c_2 L_omega` as quadratic forms.  The generalized
Rayleigh quotient is therefore a positive weighted average of the common
`aW` ratio `1` and a graph ratio in `[1/c_2,1/c_1]`.

### Full coupled block

For native/atomic, collision, interface, and thermatter variables, write

\[
 J=\begin{pmatrix}
 A_C & B\\ C & D
 \end{pmatrix},
 \qquad
 S=D-CA_C^{-1}B.
\]

The production preconditioner contract is:

1. transform `A_C` to entropy variables;
2. attach the constant activity nullspace explicitly;
3. approximate only the `Q` graph with a measured spectrally equivalent
   operator;
4. keep the `P` number mode in the slow/native/interface Schur block;
5. compare unpreconditioned residual, Newton iterations, Krylov iterations,
   setup/reuse cost, wall time, and peak RSS before selection.

A harmonic block that does not respect the entropy metric and conserved
nullspace has no theorem-level stiffness-independent guarantee.  This explains
why the v0.64 tested harmonic block could be slower without contradicting the
AP contract.

For the PETSc DAE interface, the supplied shifted Jacobian is

\[
 \frac{\partial F}{\partial U}
 +a\frac{\partial F}{\partial\dot U},
\]

and the known nullspaces must be attached to the operator/preconditioner
matrices.

---

## 6. Exact native face trace and conservative COM reconstruction

### 6.1 Native trace

The native-side trace at a red or blue interface is the characteristic formal
solution of Section 2 evaluated at the **exact face frequency and direction**.
It is not inferred from a broad cell average.  This removes the v0.63 native
face ambiguity at theory level.

### 6.2 COM finite-volume traces

Use log-frequency coordinate `y=ln nu`.  Let `bar f_i>0` be a cell average,
`y_i` the midpoint, and `y_{i+/-1/2}` the faces.  First compute a minmod slope
`s_i`.  Let

\[
 d_i^\pm=s_i(y_{i\pm1/2}-y_i).
\]

Choose one common multiplier `0<=theta_i<=1` so that

\[
 \epsilon\le \bar f_i+\theta_i d_i^\pm\le M_i,
\]

where

\[
 M_i=\max(\bar f_{i-1},\bar f_i,\bar f_{i+1})
\]

and the lower bound is the corresponding local minimum, not below the positive
floor `epsilon`.  The traces are

\[
 f_{i,L}=\bar f_i+\theta_i d_i^-,\qquad
 f_{i,R}=\bar f_i+\theta_i d_i^+.
\]

Because the same multiplier scales one linear polynomial and `y_i` is the cell
midpoint,

\[
 \frac1{\Delta y_i}\int_{I_i}f_i^{\rm rec}(y)\,dy=\bar f_i.
\]

Thus positivity and the local maximum principle do not alter the cell average.

### 6.3 Upwind numerical flux

For face speed `v_{i+1/2,a}`,

\[
 \mathcal F_{i+1/2,a}
 =v^+_{i+1/2,a}f^-_{i+1/2,a}
 +v^-_{i+1/2,a}f^+_{i+1/2,a},
\]

where `v^+=max(v,0)` and `v^-=min(v,0)`.  The same face flux enters adjacent
cells with opposite signs; therefore the interior sum telescopes exactly.
Only external red/blue flux remains in the global number ledger.

The transported face energy is always

\[
 h\nu_{i+1/2}\mathcal F_{N,i+1/2},
\]

not a broad-cell centroid substitute.

On a fixed limiter and upwind branch, the trace and flux have analytic JVPs.
Limiter ties and `v=0` are semismooth/discrete branch events.  The current
trajectory policy localizes the event and restarts; no derivative is taken
through a changed active branch.  P0 is the fail-safe fallback.

Backward Euler applied to the upwind transport generator has an M-matrix
system: off-diagonal inflow coefficients are nonpositive in the residual,
diagonal coefficients are positive, and column conservation holds.  Hence the
linear transport solve is positivity preserving without an explicit CFL bound.
The nonlinear coupled solve retains log variables for strict positivity.

---

## 7. Complete scalar coupled equation and owner registry

The phase-space equation is

\[
 \boxed{
 \mathcal L_{\rm Bianchi}f
 =C_{\rm atom,iso}[x_r,f]
  +C_{\rm COM-KHW}[f,x_r]
  +C_{\rm interface}[f].}
\]

Here

\[
 \mathcal L_{\rm Bianchi}
 =\partial_t
 +R_H\nu_H\partial_{\nu_H}
 +\dot e_H^\alpha\nabla^{S^2}_\alpha .
\]

The rank-one original-HyRec DAE and causal history remain

\[
 M(U)\dot U=F(U,f;B),\qquad C(U,f;B)=0,
\]

with `x_e` the single local differential atomic row and 313 real/virtual
algebraic rows.  Accepted scalar history is committed only on canonical macro
surfaces.

Owner rules:

| Term | Sole owner |
|---|---|
| normal/hydrogen frame redshift and direction flow | `BackgroundSnapshot` characteristic |
| scalar unpolarized local atomic source/opacity | primitive original-HyRec block |
| scalar causal `Dfplus/Dfplus_Ly` history | typed characteristic-history owner |
| anisotropic elastic redistribution and recoil | direct COM--KHW event kernel |
| cross-representation number and exact face energy | interface owner |
| atom/photon collision four-force | physical collision owner |
| pure representation crossing atom source | exactly zero |

No compressed owner is removed until its replacement residual, JVP,
conservation ledger, and restart state coexist in the same stage.

### Theorem 7.1 — local well-posedness of the scalar coupled branch

Split the finite-dimensional state into differential variables `X` (electron
fraction, positive COM occupations, interface accumulators and any retained
thermal variables) and algebraic real/virtual populations `Y`.  On one fixed
background, topology, limiter and upwind branch, write

\[
 \dot X=G(X,Y;B),\qquad 0=C(X,Y;B).
\]

Assume:

1. `G` and `C` are continuously differentiable in the positive interior;
2. the original-HyRec algebraic Jacobian `C_Y` is nonsingular on the branch;
3. the characteristic coefficients are locally Lipschitz;
4. all discrete branch changes are localized as events;
5. initial data satisfy the algebraic constraints and all positive-state
   inequalities.

Then the implicit-function theorem gives a unique local algebraic map
`Y=Y(X;B)`.  Substitution produces the locally Lipschitz ODE

\[
 \dot X=G\bigl(X,Y(X;B);B\bigr),
\]

so Picard--Lindelof gives a unique local scalar solution up to the first event
or loss of the algebraic regularity condition.  Quasi-positivity of the event
network, the positive formal transfer solution, and log variables for strictly
positive unknowns make the physical nonnegative cone forward invariant on the
fixed branch.  At a localized branch event, the accepted parent state is
retained and the initial-value problem is restarted with the new owner/branch
registry.

This is a local discrete well-posedness theorem.  It does not replace the
multi-macro convergence, global continuation, or PR-06 FLRW history-parity
gates.

### Conservation and source ledger

The coupled equation does **not** assert conservation of photon number under
atomic emission or absorption.  Instead, ownership is componentwise:

- elastic COM--KHW edges conserve photon number and exchange equal-and-opposite
  photon/atom four-force;
- finite-volume transport telescopes internally, leaving only external face
  flux and cosmological redshift work;
- a representation crossing applies equal-and-opposite photon number and exact
  face energy to its two representations and has zero atom source;
- primitive atomic emission/absorption owns photon creation/destruction and the
  corresponding atomic/nuclear/electron and energy ledgers.

Thus no term is silently forced into a false global photon-number invariant.

---

## 8. Dimensional checks

| Quantity | Dimension |
|---|---|
| `f`, `z`, `phi`, `psi`, angular weights | dimensionless |
| ordinary frequency `nu` | `s^-1 = Hz` |
| `H`, `sigma`, `A`, `N`, `Omega`, `R` | `s^-1` |
| cell/angle mode measure `m_A` | `m^-3` |
| photon number state `N_A=m_A f_A` | `m^-3` |
| event conductance `K_AB` | `m^-3 s^-1` |
| number action | `m^-3 s^-1` |
| exact face photon-energy action | `J m^-3 s^-1 = W m^-3` |
| entropy metric `W_A=m_A f*(1+f*)` | `m^-3` |
| graph Laplacian `L_omega` | `m^-3 s^-1` |
| DAE shift `a` | `s^-1` |
| shifted entropy block `aW+L` | `m^-3 s^-1` |

If `eta=ln a` is used as independent variable in an expanding branch,
`d/deta=H^{-1}d/dt`.  Near a recollapse or any `H=0` surface, physical time or
a D-normalized branch chart must be used; division by `H` is forbidden.

---

## 9. Limits and red-team cases

The contract explicitly survives:

- zero tilt;
- finite tilt with `|beta|<1`;
- FLRW isotropy;
- nonlinear large shear;
- disconnected event graphs, provided one conserved activity mode is retained
  per connected component;
- exact zero conductances, provided topology-change surfaces split interpolation
  cells;
- limiter/upwind branch switches, provided they are event-localized;
- collision stiffness tending to infinity, provided the preconditioner shares
  the exact nullspace and satisfies the stated spectral-equivalence bound.

It explicitly does **not** claim:

- reconstruction of angular information from one scalar instantaneous datum;
- source-identical Raman/polarization/alignment physics;
- positivity from unconstrained harmonic-coefficient interpolation;
- differentiability through a changed limiter, upwind, or conductance-topology
  branch;
- direct-network numerical convergence before the withheld-node and refinement
  gates are run.

---

## 10. Closure decision

The remaining scalar mathematical/physical ambiguity is closed at the theorem
and owner-contract level:

1. the angular field is a unique characteristic initial-boundary-value problem
   under an explicit hydrogen-frame source-isotropy axiom;
2. direct thermodynamic kernels are compiled and interpolated as positive
   reciprocal nodal event graphs;
3. number, BE null, positivity, entropy, and linearized nullspace properties are
   exact structural consequences;
4. exact native face traces and conservative limited COM traces are defined;
5. the stiff collision preconditioner has a stiffness-independent theorem under
   explicit spectral-equivalence assumptions;
6. the fixed-branch scalar DAE/transport/collision problem is locally
   well-posed whenever the 313-row algebraic Jacobian is nonsingular, with
   event-localized restart at branch changes.

The next stage is implementation and numerical evidence, not the invention of
additional equations:

- direct thermodynamic node compiler and withheld-node refinement;
- characteristic angular solver and exact native face evaluation;
- entropy-metric/nullspace preconditioner measurement;
- four-or-more canonical macro intervals in every locked redshift/background
  lane;
- PR-06 full FLRW recombination-history parity.
