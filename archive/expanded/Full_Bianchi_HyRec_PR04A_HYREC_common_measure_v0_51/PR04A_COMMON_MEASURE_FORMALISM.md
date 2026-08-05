# PR-04A HYREC common-measure projection formalism

## Scope and conventions

This bounded release uses metric signature `(-,+,+,+)`, the local hydrogen
orthonormal tetrad, ordinary frequency `nu` in Hz, and explicit `c`, `h`, and
`k_B`.  The oriented jump is

\[
\Delta\nu=\nu_{\rm target}-\nu_{\rm source},
\qquad
\Delta E_\gamma=h\Delta\nu,
\qquad
\Delta E_{\rm H}=-h\Delta\nu.
\]

The stage covers the 17 interior Ly-alpha cells, `-4.25 <= x <= 4.25`.
Exterior transport and the native HYREC virtual-state/escape map are not
silently folded into this bounded core projection.

## Positive common measure

For an oriented source cell `j` and target cell `i`, define

\[
 S^{(r)}_{ij}=\int_{I_j\rightarrow I_i}
        (\nu_i-\nu_j)^r\,d\mathcal S,
 \qquad r=0,\ldots,4.
\]

The positive event measure `dS` is the v0.50 scalar elastic COM--KHW event
measure.  Its dimensions are

\[
 [S^{(r)}]={\rm m}^{-3}{\rm s}^{-1}{\rm Hz}^{r}.
\]

Exchange of source and target gives the exact parity

\[
 S^{(r)}_{ji}=(-1)^r S^{(r)}_{ij}.
\]

The lower-cost moment quadrature computes conditional ratios.  Its zeroth
mass is projected to the already accepted v0.50 production conductance,

\[
 S^{(r)}_{ij}\leftarrow S^{(0),v0.50}_{ij}
   {S^{(r),raw}_{ij}\over S^{(0),raw}_{ij}}.
\]

This is a conservative same-event projection, not a fitted normalization:
no HYREC output or adjustable scale enters it.  Active same-cell jumps are
integrated separately; the exact coherent `Delta nu=0` identity is excluded
because it cancels from the collision action and all positive-order moments.

For the equilibrium source measure `Pi_j`,

\[
 \Gamma_j={1\over\Pi_j}\sum_i S^{(0)}_{ij},\qquad
 M_r(j)={1\over\Pi_j}\sum_i S^{(r)}_{ij}.
\]

Thus `[Gamma]=s^-1` and `[M_r]=Hz^r s^-1`.  The per-source atomic recoil power
is `-h M1`.

## Nonlinear Bose edge and entropy

Let `g_i` be the cell mode density, `z_i=Pi_i/g_i`, and

\[
 \phi_i={f_i\over z_i(1+f_i)}.
\]

For every unordered pair, the number flux into `i` is

\[
 J_{i\leftarrow j}=S^{(0)}_{ij}(1+f_i)(1+f_j)(\phi_j-\phi_i).
\]

The discrete BE family

\[
 f_i={qz_i\over1-qz_i}
\]

has constant `phi_i=q` and is therefore an exact null.  Pairwise antisymmetry
closes photon number.  With

\[
 \psi_i=\ln{f_i\over1+f_i}-\ln z_i=\ln\phi_i,
\]

`sum_i psi_i dot N_i <= 0`.  Photon and atom energy are accumulated from the
same first moment with opposite signs.

The backward-Euler update is solved in `u=ln f`, so every Newton iterate is
strictly positive.  The dense 17-state Jacobian is assembled from the exact
analytic JVP; finite differences are regression evidence only.

## Native HYREC firewall

The exact durable HYREC-2 source lock is commit
`09e8243d0e08edd3603a94dfbc445ae06cafe139`.  FULL mode has
`(2s,2p) + 311` virtual photon states; the 80-bin Ly-alpha diffusion block is
zero-based `100..179`.  Native energies are in eV and convert by `nu=E/h`.

The primitive `Aup/Adn` arrays are retained as diagnostics.  They populate an
escape-compressed real/virtual Schur system and are not directly equal to the
per-source COM--KHW `Gamma,M_r`.  A free scale match or direct replacement of
the completed native `Tvv` block is forbidden.

## Claim boundary

The official HyRec page confirms that original HyRec performs numerical
time-dependent radiative transfer, whereas default HYREC-2 uses correction
functions.  The October-2012 original archive bytes were not retrievable in
this runtime.  Therefore this artifact closes PR-04A source/convention and
17-cell common-measure gates but leaves original-archive/native primitive
parity open for PR-04B.  It does not claim the full PR-04 or PR-05 operator
integration.
