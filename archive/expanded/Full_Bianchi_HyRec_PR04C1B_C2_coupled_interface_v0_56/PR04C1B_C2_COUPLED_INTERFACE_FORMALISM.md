# PR-04C1B/C2 coupled-interface formalism

## Conventions and scope

Metric `(-,+,+,+)`; ordinary frequency `nu` in Hz; `c`, `h`, and `k_B`
remain explicit. This release is homogeneous and scalar. Original HyRec and the
35-state COM--KHW representation remain distinct. No fitted normalization or
global native-to-COM remap is introduced.

## Boundary conversion

For integrated packet number `q_s=Delta t Phi_N^s`, the exact scalar resolved
update is

`Delta f_(i_s,a) = sigma_s n_H q_s / g_(i_s)`

with `sigma_red=-1`, `sigma_blue=+1`, normalized angular weights and exact
outer states `FR00`/`FB02`. The exact transported energy is `h nu_face q_s`.
The finite-cell centroid proxy is diagnostic; its difference from the face
energy is retained in the unresolved correction ledger. Interface atom source
is zero.

## Positive monolithic residual

`f=exp(u)>0`, `rho_s=exp(v_s)>0`, and

`R_f=f-f_old-Delta t C[f]-sum_s rho_s Delta f_s`,
`R_rho,s=rho_s-1`.

The analytic JVP follows directly by differentiating these expressions and the
existing Bose collision action. Newton--GMRES acts matrix-free. A strict net
residual is used while it decreases. If float64 cancellation prevents further
net-residual decrease, acceptance requires a normwise gross-term backward error
below `1e-11` **and** independent photon-number closure below `1e-11`; neither
condition alone can declare convergence.

## Results

Three source-conditioned lanes at z~1300,1100,900 pass. Maximum backward error
is `1.3200190226745005e-17`, maximum number residual is
`2.5609198306764287e-14`, and maximum JVP relative error is
`1.279553711820355e-09`. Total free energy may change because the interface is an
external transfer; the collision entropy-production diagnostic remains
nonpositive. PR-04C3 remains open.
