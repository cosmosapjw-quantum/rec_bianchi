# PR-01B1-B3A exact Maxwell–Jüttner orbit reweighting

## 1. Scope

This bounded stage isolates one question: how much does replacing the
nonrelativistic Maxwell–Boltzmann atom measure by the exact relativistic
Maxwell–Jüttner measure change the already deterministic, PT-audited
centre-sampled COM–KHW orbit cache?

The input is the v0.14 scalar cache:

- 17 frequency-cell centres;
- Lebedev-26 directions;
- 1,836 physical \((i,j,\mu)\) orbits;
- 93,925 active unordered state edges;
- resonance-adapted COM–KHW amplitude averages.

This stage does **not** redo the amplitude integral or integrate the two
frequency-cell interiors. It is therefore a measure-isolation pilot, not
the final PR-01B1-B3 production kernel.

## 2. Dimensionless transfer variables

For photon endpoints \((\nu_s,\boldsymbol n_s)\) and
\((\nu_t,\boldsymbol n_t)\), define

\[
q=\frac{h}{M_Hc^2}
\sqrt{\nu_s^2+\nu_t^2-2\nu_s\nu_t\mu},
\]

\[
\delta=\frac{h(\nu_s-\nu_t)}{M_Hc^2},
\qquad
\mu=\boldsymbol n_s\cdot\boldsymbol n_t.
\]

The transfer is spacelike when \(q^2>\delta^2\).

## 3. Exact relativistic and nonrelativistic structure factors

Let

\[
z=\frac{M_Hc^2}{k_BT_m},
\qquad
\chi=\sqrt{q^2-\delta^2},
\]

\[
\gamma_{\min}
=
\frac{q}{\chi}\sqrt{1+\frac{\chi^2}{4}}
-\frac{\delta}{2}.
\]

The Maxwell–Jüttner factor is

\[
\boxed{
S_{\rm MJ}(q,\delta)
=
\frac{
\exp[-z(\gamma_{\min}-1)]
}{
2q\,e^zK_2(z)
}.
}
\]

The nonrelativistic Maxwell–Boltzmann limit is

\[
\boxed{
S_{\rm MB}(q,\delta)
=
\frac{1}{\sqrt{2\pi\theta}\,q}
\exp\left[
-\frac{(\delta-q^2/2)^2}{2\theta q^2}
\right],
}
\]

with

\[
\theta=\frac{k_BT_m}{M_Hc^2}.
\]

Both obey the same endpoint-exchange affinity,

\[
S(q,-\delta)=e^{-z\delta}S(q,\delta).
\]

Therefore

\[
\boxed{
R_{\rm rel}(q,\delta)
=
\frac{S_{\rm MJ}(q,\delta)}{S_{\rm MB}(q,\delta)}
}
\]

is positive and even under \(\delta\to-\delta\).

## 4. Conductance reweighting

The v0.14 unordered edge conductance already contains the MB structure
factor and the deterministic COM–KHW amplitude average. This stage sets

\[
\boxed{
\mathsf S_{ab}^{\rm MJ}
=
\mathsf S_{ab}^{\rm MB}
R_{\rm rel}(q_{ab},\delta_{ab}).
}
\]

No matrix symmetrization is applied. Since both factors are symmetric on
an unordered orbit,

\[
\mathsf S^{\rm MJ}=\mathsf S^{{\rm MJ}\,T}
\]

follows algebraically.

With equilibrium state weight \(\Pi_b\), the generator is

\[
K_{a\leftarrow b}=\frac{\mathsf S_{ab}^{\rm MJ}}{\Pi_b},
\]

\[
G_{a b}=K_{a\leftarrow b}\quad(a\ne b),
\qquad
G_{bb}=-\sum_{a\ne b}K_{a\leftarrow b}.
\]

Hence

\[
\boldsymbol1^TG=0,
\qquad
G\Pi=0.
\]

## 5. Numerical result

At \(T_m=3000\,\mathrm K\), the exact relativistic correction spans

\[
0.999987438345
\le
R_{\rm rel}
\le
0.999999999484.
\]

The largest correction occurs for the widely separated
\(x=-4\leftrightarrow+4\) orbit at the most forward available
Lebedev-26 angular class. It has very small conductance weight.
Consequently the full harmonic kernels through \(\ell=6\) change by at
most

\[
6.53\times10^{-10},
\]

and the tested collision actions change by at most

\[
1.18\times10^{-9}.
\]

## 6. Interpretation

The relativistic Maxwell–Jüttner correction is numerically negligible
for recombination-era hydrogen **after** the deterministic COM–KHW
amplitude cache is fixed. This validates Maxwell–Boltzmann conditional
momentum quadrature as a production approximation, while retaining the
Maxwell–Jüttner pair measure as the exact reciprocity reference.

It does not remove the remaining B3 tasks:

1. two-sided frequency-cell integration;
2. resonance-adapted transverse amplitude integration on the invariant
   pair measure;
3. absolute heavy-atom/Hummer normalization;
4. full \(17\times17\), \(\ell\le6\) physical conductance;
5. later extension to adaptive \(\ell_{\max}=12,20,24\).
