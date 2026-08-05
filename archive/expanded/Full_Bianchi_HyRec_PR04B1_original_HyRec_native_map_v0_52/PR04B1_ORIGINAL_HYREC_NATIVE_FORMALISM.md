# PR-04B1 original-HyRec native primitive map

## Scope and conventions

This bounded stage byte-locks the owner-supplied `HyRec_Oct2012.zip`, compiles
its unmodified C sources, and derives the original native Ly-alpha diffusion
block.  It does **not** yet identify that algebraic proxy block with the
physical `m^-3 s^-1 Hz^r` event measure of PR-04A.

The project conventions remain

\[
 g_{\mu\nu}=(-,+,+,+),\qquad \nu=E/h,
 \qquad \Delta\nu=\nu_{\rm target}-\nu_{\rm source},
\]
\[
 \Delta E_\gamma=h\Delta\nu,\qquad
 \Delta E_{\rm H}=-h\Delta\nu .
\]

Original HyRec uses cgs lengths and eV temperatures.  Its native matrix
coefficients are in `s^-1`.

## Native variable

The technical supplement and `hydrogen.c` identify the virtual proxy as

\[
 \Delta x_b=x_b-x_{1s}e^{-h\nu_b/T_r}=x_{1s}\Delta f_{\nu_b}.
\]

`x_b` is not an atomic population and is not a photon number per cell.  The
stored spectrum is `x_v/x_1s`, the average occupation distortion in a bin.
The physical spectral diagnostic printed by original HyRec is

\[
 {8\pi\nu^3\over c^3 n_H}\Delta f_\nu
\]

per logarithmic frequency interval per hydrogen atom.

## Primitive diffusion network

For the 80 virtual bins `b=100,...,179`, original HyRec constructs
`Aup[b]=A_{b,b+1}` and `Adn[b]=A_{b,b-1}`.  The unresolved 2p line centre is an
81st proxy state.  With the matrix-generator convention

\[
 \dot x_i=\sum_j Q_{ij}x_j,
\]

all off-diagonal `Q_ij` are nonnegative and every column sums to zero.  The
reversible proxy measure is

\[
 \pi_b=e^{-E_b/T_m},\qquad
 \pi_{2p}=3e^{-E_{21}/T_m}.
\]

It obeys `Q pi=0`.  The oriented proxy moment tensor is

\[
 C^{(r)}_{ij}=\pi_j Q_{ij}(\nu_i-\nu_j)^r,
 \qquad i\ne j,
\]

with units `Hz^r s^-1`, not `m^-3 s^-1 Hz^r`, and exact exchange parity

\[
 C^{(r)}_{ji}=(-1)^r C^{(r)}_{ij}.
\]

## Exact 2p Schur elimination

Writing original HyRec's positive-diagonal matrix as `T=-Q`, the line-centre
proxy can be eliminated in the steady system:

\[
 T_{\rm eff}=T_{vv}-T_{vp}T_{pp}^{-1}T_{pv},\qquad
 Q_{\rm eff}=-T_{\rm eff}.
\]

The reduced 80-state generator remains conservative and reversible and
creates the exact red-to-blue bridge mediated by the unresolved 2p proxy.

## Physical-measure firewall

For diagnostic log-frequency edges, a physical photon mode weight is

\[
 g_b={8\pi\over 3c^3}
 \left(\nu_{b,+}^3-\nu_{b,-}^3\right).
\]

The primitive native block conserves `sum_b x_b`, whereas a physical
finite-volume photon generator would require `g^T Q=0`.  The measured nonzero
weighted-left-null residual is therefore a positive firewall result: direct
`Aup/Adn` substitution into the PR-04A physical common measure is forbidden.
The remaining PR-04B2 task must derive the escape/redshift/bin map on one
physical measure; it may not fit a multiplicative scale.
