# C3B1 native HYREC sparse block

Let the two real-state variables be
\[
X_r=(x_{2s},x_{2p})^T
\]
and the 311 virtual photon variables be \(X_v\). HYREC solves
\[
\begin{pmatrix}T_{rr}&T_{rv}\\T_{vr}&T_{vv}\end{pmatrix}
\begin{pmatrix}X_r\\X_v\end{pmatrix}
=
\begin{pmatrix}s_r\\s_v\end{pmatrix}.
\]

Outside the Ly-alpha diffusion interval, \(T_{vv}\) is diagonal. In the
80-bin interval \(b=100,\ldots,179\), it is tridiagonal. The exact
structured elimination is
\[
T_{\rm eff}=T_{rr}-T_{rv}T_{vv}^{-1}T_{vr},
\qquad
s_{\rm eff}=s_r-T_{rv}T_{vv}^{-1}s_v,
\]
\[
X_r=T_{\rm eff}^{-1}s_{\rm eff},
\qquad
X_v=T_{vv}^{-1}(s_v-T_{vr}X_r).
\]

HYREC applies scalar division to the 231 diagonal virtual states, a
Thomas solve to the 80-bin diffusion interval, and then solves the
remaining \(2\times2\) Schur system.

## Detailed balance

For adjacent virtual bins,
\[
e^{-E_b/T}A_{b,b+1}=e^{-E_{b+1}/T}A_{b+1,b}.
\]
For the 2p state, whose unresolved degeneracy is three,
\[
e^{-E_b/T}A_{b,2p}=3e^{-E_{21}/T}A_{2p,b}.
\]

## Double-counting firewall

- HYREC FULL regression: native \(A_{1s}\) diffusion ON, COM-KHW OFF.
- Full Bianchi production: native \(A_{1s}\) diffusion OFF, COM-KHW ON.
- Native \(A_{2s},A_{3s3d},A_{4s4d}\) two-photon/Raman couplings remain.
