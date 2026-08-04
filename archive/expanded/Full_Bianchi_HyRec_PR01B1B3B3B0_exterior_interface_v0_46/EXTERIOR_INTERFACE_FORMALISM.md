# Near-exterior scattering interface

The compact line core is

\[
I=[-4.25,4.25].
\]

The first dynamic near-exterior states use the validated adaptive wing grid

\[
O_R^{\rm near}=[-10.25,-4.25],\qquad
O_B^{\rm near}=[4.25,10.25].
\]

Each interior/exterior frequency-cell pair is represented by one unordered
Maxwell--Juttner equilibrium conductance

\[
S_{ei}^{(\ell)}=S_{ie}^{(\ell)}.
\]

Rates are

\[
K_{e\leftarrow i}^{(\ell)}=\frac{S_{ei}^{(\ell)}}{\Pi_i},\qquad
K_{i\leftarrow e}^{(\ell)}=\frac{S_{ei}^{(\ell)}}{\Pi_e}.
\]

For every harmonic block, loss uses the scalar outflow

\[
\Gamma_i^{I\leftrightarrow O}=\sum_e\frac{S_{ei}^{(0)}}{\Pi_i}.
\]

For one nonlinear edge flux \(J_{e\leftarrow i}\), the same endpoint event
produces

\[
\Delta p_\gamma^\mu=p_e^\mu-p_i^\mu,\qquad
\Delta P_H^\mu=-\Delta p_\gamma^\mu.
\]

The present artifact closes the near interface only.  Direct jumps beyond
\(|x|=10.25\) are an explicit far-boundary ledger, not silently discarded.
