# Local angular Sobolev escape: constructive derivation and implementation contract

Date: 2026-10-22 UTC. Scope: supplied isotropic line emissivity, local Sobolev operator, positive expansion in every ray direction. Signature \((-+++)\). No cosmological IVP was executed for this derivation.

## A. Geometry, dimensions, and the supplied operator

Let \(H>0\) and \(\sigma_{ab}\) be the expansion scalar divided by three and the real symmetric tracefree shear in the comoving orthonormal tetrad. Both have units s\(^{-1}\). Let \(n^an_a=1\). For a geodesic, non-tilted observer congruence,
\[
-\frac{d\ln\nu}{dt_{\rm p}}=H_{\boldsymbol n}
=H+\sigma_{ab}n^an^b.
\]
Here \(t_{\rm p}\) is proper cosmic time in seconds. An explicit Bianchi-I check uses
\[
ds^2=-c^2dt_{\rm p}^2+\sum_i a_i^2dx_i^2,\quad
E=c\sqrt{\sum_i k_i^2/a_i^2},\quad
n_i=\frac{k_i/a_i}{\sqrt{\sum_jk_j^2/a_j^2}}.
\]
The conserved covariant spatial momenta \(k_i\) give
\[
\frac{\dot E}{E}=-\sum_iH_i n_i^2,\quad
H=\tfrac13\sum_iH_i,\quad
\sigma_{ij}=\operatorname{diag}(H_i-H),\quad
\dot n_i=(H_{\boldsymbol n}-H_i)n_i.
\]
The local redshift identity does not assert that directions remain fixed over a finite ray. Other Bianchi types require their own direction transport/connection; the local expansion contraction remains the relevant geodesic redshift coefficient.

For a non-inverted isolated line \(u\to l\), one standard supplied positive Sobolev coefficient is
\[
C_S=\frac{A_{ul}\lambda_{ul}^3}{8\pi}
\left(\frac{g_u}{g_l}n_l-n_u\right)>0,
\qquad
\tau_{\boldsymbol n}=\frac{C_S}{H_{\boldsymbol n}}.
\]
\(n_l,n_u\) are physical number densities in reciprocal-volume units consistent with \(\lambda^3\); \(A\) and \(C_S\) are s\(^{-1}\). This follows by integrating the isolated line opacity through a local monotone redshift with the Einstein coefficient relations. Using this expression requires the populations, degeneracies, profile, and stimulated term to be source-bound. In the usual small-upper-population hydrogen \(2p\to1s\) limit, \(g_{2p}/g_{1s}=3\), so
\[
A_\alpha\frac{H}{C_S}\simeq
\frac{8\pi H}{3n_Hx_{1s}\lambda_\alpha^3},
\]
matching HyRec-2 Eq. (10). No numerical atomic coefficient was newly supplied or fitted in this unit.

The analysis below only assumes a supplied direction-independent \(C_S>0\). Its probability
\[
\beta(\tau)=\frac{1-e^{-\tau}}{\tau}
\]
is the local complete-redistribution Sobolev probability, not a solution of the full cosmological line-transfer problem. The source reference is Chluba–Sunyaev 2009 §3.2, Eq. (35b), https://arxiv.org/abs/0810.1045. The physical assumptions and their primordial-recombination limitations are described explicitly by Hirata–Forbes 2009, https://arxiv.org/abs/0903.4925.

Define dimensionless
\[
S_{ab}=\sigma_{ab}/H,\quad \mathrm{tr}S=0,\quad
q=1+S_{ab}n^an^b,\quad
\tau_0=C_S/H.
\]
Let \(q_{\min}=1+\lambda_{\min}(S)>0\), \(q_{\max}=1+\lambda_{\max}(S)\); \(\langle f\rangle=(4\pi)^{-1}\int f\,d\Omega\). Then \(\langle q\rangle=1\), and
\[
b(q)=\beta(\tau_0/q)=\frac{q}{\tau_0}(1-e^{-\tau_0/q}).
\]
The target observables are
\[
B=\langle b(q)\rangle,\qquad
Q_{ab}=\langle A_{ab}(\boldsymbol n)b(q)\rangle,\quad
A_{ab}=n_an_b-\delta_{ab}/3.
\]
These are probability moments. \(Q\) is not a photon stress tensor without an emissivity/energy/transport map.

## B. Exact Jensen inequality and a variance bound

Differentiate at fixed \(\tau_0>0\):
\[
b'(q)=\frac{1-(1+\tau_0/q)e^{-\tau_0/q}}{\tau_0}>0,
\quad
b''(q)=-\frac{\tau_0e^{-\tau_0/q}}{q^3}<0.
\]
Strict concavity and \(\langle q\rangle=1\) yield
\[
\boxed{B\le b(1)=\beta(\tau_0)}.
\]
For finite positive \(\tau_0\), equality requires \(q\) constant almost everywhere; symmetric tracefree \(S\) then forces \(S=0\). This statement compares the same \(C_S,H\) and isotropic angular measure. It is not a claim about self-consistently changed populations or histories.

A quantitative bound follows from Taylor's theorem about \(q=1\), after averaging the zero linear term:
\[
0\le \beta(\tau_0)-B\le
\frac12 M\langle(q-1)^2\rangle
=\frac{M}{15}\operatorname{tr}(S^2),
\]
where
\[
M=\max_{q\in[q_{\min},q_{\max}]}
\frac{\tau_0e^{-\tau_0/q}}{q^3}.
\]
This maximum is explicit: with
\[
q_*=\min\{q_{\max},\max\{q_{\min},\tau_0/3\}\},
\qquad M=\tau_0e^{-\tau_0/q_*}/q_*^3,
\]
the bound holds because the logarithmic derivative of the maximand is
\((\tau_0-3q)/q^2\). The formula provides a bound, not an asymptotic fit.

## C. Thick-limit mean and tensor, with explicit errors

Since \(q>0\),
\[
\frac1{\tau_0}-B
=\frac1{\tau_0}\langle q e^{-\tau_0/q}\rangle.
\]
For every ray, \(e^{-\tau_0/q}\le e^{-\tau_0/q_{\max}}\), and \(\langle q\rangle=1\). Therefore
\[
\boxed{0\le \frac1{\tau_0}-B
\le\frac{e^{-\tau_{\min}}}{\tau_0}},
\qquad \tau_{\min}=\tau_0/q_{\max}.
\]
Only the strongest-expanding direction controls the uniform thick certificate. Requiring merely a large mean optical depth is insufficient.

The isotropic angular moments are
\[
\langle n_an_b\rangle=\delta_{ab}/3,\quad
\langle n_an_bn_cn_d\rangle=
(\delta_{ab}\delta_{cd}+\delta_{ac}\delta_{bd}+\delta_{ad}\delta_{bc})/15.
\]
Consequently,
\[
\langle A_{ab}q\rangle=2S_{ab}/15,
\quad
Q^{\rm thick}_{ab}=\frac{2S_{ab}}{15\tau_0}
=\frac{2\sigma_{ab}}{15C_S}.
\]
For every unit direction, \(\|A(\boldsymbol n)\|_F=\sqrt{2/3}\). The triangle inequality yields
\[
\left\|Q-Q^{\rm thick}\right\|_F
=\frac1{\tau_0}\left\|
\left\langle A q e^{-\tau_0/q}\right\rangle\right\|_F
\le \frac{\sqrt{2/3}}{\tau_0}
\langle q e^{-\tau_0/q}\rangle
\le
\boxed{\sqrt{\frac23}\frac{e^{-\tau_{\min}}}{\tau_0}}.
\]
Thus \(B^{\rm thick}=1/\tau_0\) has no explicit tracefree shear contribution, while the escaping angular distribution retains its quadrupole. These are compatible outcomes.

The quoted errors bound replacing \(b(q)\) by \(q/\tau_0\) in the supplied local model. They do not bound complete-versus-partial redistribution, nonlocal history, recoil/diffusion, line overlap, feedback, or changes in the emitter/absorber populations.

## D. Finite-optical-depth small-shear expansion

The same fourth moment gives
\[
\langle(S_{ab}n^an^b)^2\rangle=\frac{2}{15}\operatorname{tr}(S^2).
\]
Taylor expansion with the domain bounded away from \(q=0\) yields
\[
\boxed{B=\beta(\tau_0)
-\frac{\tau_0e^{-\tau_0}}{15}\operatorname{tr}(S^2)
+O(\|S\|^3)}.
\]
The probability quadrupole begins at first order:
\[
\boxed{Q=\frac{2}{15\tau_0}
[1-(1+\tau_0)e^{-\tau_0}]S+O(\|S\|^2)}.
\]
As \(\tau_0\to0^+\), \(\beta\to1\) and the quadrupole tends to zero. The quadratic scalar coefficient has the Jensen sign and vanishes exponentially in the uniform thick limit.

For LRS,
\[
S=\operatorname{diag}(-s/2,-s/2,s),\quad
q(\mu)=1+sP_2(\mu),\quad P_2=(3\mu^2-1)/2.
\]
The exact directional positivity interval is \(-1<s<2\). Then
\[
B=\frac12\int_{-1}^1b(1+sP_2)\,d\mu,\quad
\operatorname{tr}S^2=\frac32s^2,
\]
\[
B=\beta(\tau_0)-\frac{s^2\tau_0e^{-\tau_0}}{10}+O(s^3),
\quad
\langle P_2 b\rangle_{\rm thick}=\frac{s}{5\tau_0}.
\]
If the normalized angular escape density is \(p=b/B\) with \(\langle p\rangle=1\), its leading LRS Legendre amplitude is \(5\langle P_2p\rangle=s\). This normalization must not be confused with \(Q_{zz}=2s/(15\tau_0)\).

## E. Exact failure of the unweighted cancellation outside its source class

Suppose instead that a prescribed nonnegative emissivity weight is
\[
w(\boldsymbol n)=1+E_{ab}n^an^b,\qquad \operatorname{tr}E=0,
\quad\langle w\rangle=1.
\]
The thick mean becomes
\[
\langle w b_{\rm thick}\rangle
=\frac1{\tau_0}\left[1+\frac{2}{15}\operatorname{tr}(ES)\right].
\]
Thus an anisotropic emissivity quadrupole can couple to shear even in the thick limit. This constructive counterexample prevents extending the isotropic-source scalar cancellation to arbitrary incoming radiation or emissivity. Additional magnetic-sublevel alignment/polarization and frequency-dependent source structures require their own operator.

If a direction contracts or turns, the adopted \(q>0\) domain is left. A local depth defined with \(|H_{\boldsymbol n}|\) may be useful in a different directional transport problem, but it no longer has \(\langle|q|\rangle=1\); the present tracefree average proof does not apply. Keep the existing donor's zero/sign-change handling.

## F. Numerical contract for the parent implementation

Inputs: \(H,C_S\) or \(\tau_0\); an explicitly normalized \(S\); a supplied isotropic-source declaration; requested scalar/tensor tolerance; donor/source identities. Validate finite real data, symmetry, tracefree condition within an explicitly justified input criterion, \(\tau_0>0\), \(q_{\min}>0\).

Use \(-\mathrm{expm1}(-\tau)\!/\tau\) for a ray probability, with the continuous \(\tau=0\) limit if that limit is explicitly exposed. Small-\(\tau\) stable series may be used with a separate truncation estimate.

The frozen ANGULAR01 controller uses the actual mean probability as the normalizer. With
\[
r=e^{-\tau_{\min}},\qquad B\ge(1-r)/\tau_0,
\]
the bounds imply
\[
\frac{|B^{\rm thick}-B|}{B}\le\frac{r}{1-r},\qquad
\frac{\|Q^{\rm thick}-Q\|_F}{B}\le\sqrt{2/3}\,\frac{r}{1-r}.
\]
For the frozen target \(\epsilon=10^{-8}\), a sufficient common gate is
\[
r\le\frac{\epsilon}{1+\epsilon}
\quad\Longleftrightarrow\quad
\boxed{\tau_{\min}\ge\log(1+1/\epsilon)}.
\]
Compute the threshold as `log1p(1/epsilon)` (about 18.4206807539524 for the frozen target), and decide the branch using log quantities. The tensor bound is normalized by \(B\), not by \(\|Q\|_F\), so it remains meaningful at zero shear.

Retain the finite logarithmic relative bound
\[
\log\left[\frac{r}{1-r}\right]
=-\tau_{\min}-\log(1-e^{-\tau_{\min}}),
\]
and add \(\tfrac12\log(2/3)\) for the tensor/mean bound. If conversion to a floating number underflows, record that representation explicitly and keep the log bound; never describe an underflowed zero as an exact zero error.

Return \(B=1/\tau_0\), \(Q=2S/(15\tau_0)\) only under that gate, together with the analytic bounds. Record overflow/underflow deliberately; underflow of the exponential may conservatively yield a positive representable bound or use a log-bound. Do not claim a bound is machine-exact without addressing floating-point input/eigensolver arithmetic.

Outside the gate, use the exact supplied angular integrand. The frozen finite validation uses N=64 versus N=128 with normalized tolerance 1e-8. Compare these finite quadrature resolutions and structural identities as finite validation. A quadrature error estimate or N-versus-2N difference alone is not a rigorous interval certificate. The analytically certified thick reduction and the numerically evaluated finite-\(\tau\) branch should be distinguished in the result type.

Meaningful checks: isotropic closed form; Jensen inequality; scalar and tensor thick bounds; rotation covariance; tracefree tensor; small-shear coefficients; thin limit; equality of individual ray \(\tau\)/jump maps with the preserved PR114 donor; qmin positivity rejection and original sign-event boundary. New cosmological IVPs are unnecessary for these checks.

The chosen unit is ANGULAR01. Its proof and CAS construction are not a fresh-context independent review. The finite unit does not change the project holds, does not run global convergence, and does not re-use the REC126/REI129 execution counts as its own evidence.

