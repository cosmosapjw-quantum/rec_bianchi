# D1C-C1 boundary-state contract

## 1. Domain and sign convention

The hydrogen-frame line window is

\[
I=[x_{\rm R},x_{\rm B}]\times S^2,
\qquad
x=\frac{\nu_{\rm H}-\nu_{\rm abs}}{\Delta\nu_D}.
\]

The first exterior blocks are

\[
O_{\rm R}:x<x_{\rm R},
\qquad
O_{\rm B}:x>x_{\rm B}.
\]

Every interface flux in this contract is **positive when it leaves the
line-window interior**.

The exterior states are dynamic radiation states supplied by the
Liouville/true-transition module. They are not fixed Planck ghost cells.

## 2. Tilted Bianchi characteristic

Let

\[
\mathcal R_{\rm H}
=
D_{\rm char}\ln\nu_{\rm H}
\]

be the exact hydrogen-frame logarithmic frequency characteristic,
expressed in the common normal-time variable. If
\(\nu_{\rm H}=\mathcal D_{\rm H}\nu_n\), then

\[
\mathcal R_{\rm H}
=
\mathcal R_n+
D_{\rm char}\ln\mathcal D_{\rm H}.
\]

For

\[
x=\frac{\nu_{\rm H}-\nu_{\rm abs}}{\Delta\nu_D},
\]

the characteristic speed relative to a moving numerical boundary
\(x_\alpha(\tau)\) is

\[
\boxed{
\mathcal A_{\alpha q}
=
\frac{
\nu_{\rm H}\mathcal R_{\rm H}
-D_0\nu_{\rm abs}
}{
\Delta\nu_D
}
-
x_\alpha D_0\ln\Delta\nu_D
-
D_0x_\alpha.
}
\]

For fixed atomic constants and
\(\Delta\nu_D\propto T_m^{1/2}\),

\[
\mathcal A_{\alpha q}
=
\frac{\nu_{\rm H}}{\Delta\nu_D}\mathcal R_{\rm H}
-\frac{x_\alpha}{2}D_0\ln T_m-D_0x_\alpha.
\]

This moving-grid term is compulsory.

## 3. Liouville interface flux

Let \(\mathscr N_{\alpha q}\) denote the conservative photon-number
density per \(x\) and angular cell supplied by the Liouville solver.

At the red interface,

\[
\boxed{
\mathcal L_{{\rm R},q}^{\rm L}
=
(-\mathcal A_{{\rm R},q})_+
\mathscr N_{I,{\rm R},q}
-
(\mathcal A_{{\rm R},q})_+
\mathscr N_{O_{\rm R},q}.
}
\]

At the blue interface,

\[
\boxed{
\mathcal L_{{\rm B},q}^{\rm L}
=
(\mathcal A_{{\rm B},q})_+
\mathscr N_{I,{\rm B},q}
-
(-\mathcal A_{{\rm B},q})_+
\mathscr N_{O_{\rm B},q}.
}
\]

Thus large shear may make one angular direction red-outflowing and
another blue-outflowing at the same time.

The module number updates are

\[
D_0N_I|_{\rm L}
=
-\sum_q(
\mathcal L_{{\rm R},q}^{\rm L}
+
\mathcal L_{{\rm B},q}^{\rm L}),
\]

\[
D_0N_{O_{\rm R}}|_{\rm L}
=
+\sum_q\mathcal L_{{\rm R},q}^{\rm L},
\qquad
D_0N_{O_{\rm B}}|_{\rm L}
=
+\sum_q\mathcal L_{{\rm B},q}^{\rm L}.
\]

Liouville crossing gives no hydrogen collision four-force.

## 4. Scattering interface edges

For an unordered resonant-scattering edge
\(i\in I\), \(o\in O_\alpha\), define

\[
\Psi_a
=
\ln\frac{f_a}{1+f_a}
+\beta_m h_{\rm P}\nu_a
\]

and

\[
\boxed{
J_{o\leftarrow i}^{\rm sc}
=
S_{oi}(1+f_o)(1+f_i)
\left(e^{\Psi_i}-e^{\Psi_o}\right).
}
\]

Positive \(J\) means interior-to-exterior transfer.

Number updates:

\[
D_0N_I|_e=-J_e,
\qquad
D_0N_{O_\alpha}|_e=+J_e.
\]

Four-momentum updates from the same edge flux:

\[
\boxed{
D_0P_I^\mu|_e=-J_ep_i^\mu,
}
\]

\[
\boxed{
D_0P_{O_\alpha}^\mu|_e=+J_ep_o^\mu,
}
\]

\[
\boxed{
Q_{\rm H}^\mu|_e=J_e(p_i^\mu-p_o^\mu).
}
\]

Their sum is exactly zero.

## 5. True-transition partition

Every elementary true-transition photon kernel is partitioned with one
non-negative partition of unity,

\[
\chi_I+\chi_{\rm R}+\chi_{\rm B}=1,
\]

\[
\eta_r^\alpha=\chi_\alpha\eta_r.
\]

The same endpoint partition must be used for forward and reverse
kernels. A true event is a source/sink, not an interface flux.

For one-photon Ly-alpha true transitions,

\[
D_0N_\gamma^{\rm true}
=
n_{\rm H}V\,D_0x_{1s}^{\rm true}
\]

with the convention that emission is positive.

## 6. Combined photon-number ledger

Define positive outward scattering fluxes

\[
\mathcal L_\alpha^{\rm sc}
=
\sum_{i\in I,o\in O_\alpha}
J_{o\leftarrow i}^{\rm sc}.
\]

Then

\[
\boxed{
D_0N_I
=
-\mathcal L_{\rm R}^{\rm L}
-\mathcal L_{\rm B}^{\rm L}
-\mathcal L_{\rm R}^{\rm sc}
-\mathcal L_{\rm B}^{\rm sc}
+S_I^{\rm true}+\cdots
}
\]

and

\[
D_0N_{O_\alpha}
=
+\mathcal L_\alpha^{\rm L}
+\mathcal L_\alpha^{\rm sc}
+S_{O_\alpha}^{\rm true}
-\mathcal L_{\alpha,\rm far}+\cdots.
\]

Therefore

\[
\boxed{
D_0(N_I+N_{O_{\rm R}}+N_{O_{\rm B}})
=
S_{\rm all}^{\rm true}
-\mathcal L_{{\rm R},\rm far}
-\mathcal L_{{\rm B},\rm far}.
}
\]

## 7. Hybrid FP/full-kernel firewall

A zero Fokker-Planck diffusion flux may be imposed only at the boundary
of the FP **subdomain**, while cross-boundary scattering is supplied by
the full redistribution kernel.

It is forbidden to impose zero physical scattering flux at the outer
boundary of the entire line-transfer domain when the full kernel has
non-zero cross-boundary edges.

## 8. Branch-safe stepping

For every angular direction and both interfaces, localize any root of

\[
\mathcal A_{\alpha q}(\tau)=0.
\]

A timestep may not inherit the old inflow/outflow branch across such a
root. The boundary flux must be reevaluated at the crossing time.

Repeated red-to-blue-to-red passages are handled by the same dynamic
upwind rule; no global FLRW red-out/blue-in assumption is allowed.
