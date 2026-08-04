# Maxwellian COM–KHW event-pair reduction

For a photon transition \(b\to a\), define the atom momentum transfer

\[
\mathbf Q=\mathbf p_b-\mathbf p_a,
\qquad
\Delta E=E_b-E_a.
\]

For a nonrelativistic hydrogen atom,

\[
E_H(\mathbf P+\mathbf Q)-E_H(\mathbf P)
=
\frac{\mathbf P\cdot\mathbf Q}{M}
+\frac{Q^2}{2M}.
\]

The energy delta function fixes

\[
P_\parallel=
\frac{M\Delta E}{Q}-\frac Q2.
\]

Integrating a normalized Maxwell distribution over the two unconstrained
momenta gives

\[
S_{\rm MB}(Q,\Delta E)
=
\sqrt{\frac{\beta M}{2\pi}}\frac1Q
\exp\left[
-\frac{\beta M}{2Q^2}
\left(\Delta E-\frac{Q^2}{2M}\right)^2
\right].
\]

It obeys

\[
S_{\rm MB}(Q,-\Delta E)
=
e^{-\beta\Delta E}
S_{\rm MB}(Q,\Delta E).
\]

The KHW amplitude depends only on one remaining momentum in the
scattering plane.  Hence the full atom integral becomes

\[
S_{\rm MB}(Q,\Delta E)
\left\langle
|\mathcal M_{\rm COM}(P_\parallel,P_T)|^2
\right\rangle_{P_T}.
\]

Because the absorption pole is much narrower than a global Hermite rule
resolves, the \(P_T\) integral is split into broad intervals and a local
tangent map around the pole.

For an unordered photon edge,

\[
S_{ab}\propto
\nu_a\nu_b\,
e^{-\beta E_b}
S_{\rm MB}(Q,E_b-E_a)
\langle|\mathcal M_{a\leftarrow b}|^2\rangle.
\]

The dynamic-structure-factor relation and COM amplitude reciprocity give

\[
S_{ab}=S_{ba}
\]

before any matrix-level symmetrization.
