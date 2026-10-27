# REC-HISTORY-02R: constant-shear characteristic and history boundary

## Result and scope

For a diagonal Bianchi I background with positive directional expansion rates
\(a_i=1+b_i>0\), a specified target propagation direction and source/target energy
ratio determine a unique retarded source event. The construction below maps that
event into a native-Wien departure, a fixed-cell directional derivative and a
conditional error allocation. The recovered HISTORY02 Stage A supplied the
retarded-map and reference-conversion construction; this continuation makes its
implementation and finite independent validation concrete.

The frame is the orthonormal frame of the homogeneous normal observers.
The metric signature is \((-+++)\), and \(\eta=\ln a\). Write
\[
ds^2=-c^2dt^2+a(t)^2\sum_i e^{2\beta_i(t)}(dx^i)^2,\qquad
\beta_i=b_i\eta+\beta_{i0},\qquad \sum_i b_i=0.
\]
Here \(n_i\) is the propagation direction. A sky direction pointing toward the
source has the opposite sign. The reference temperature is prescribed by
\(T_s/T_t=e^\Delta\); no gas-temperature evolution is inferred.

## 1. Retarded crossing from the conserved spatial momentum

Translation invariance gives constant covariant spatial momenta
\(P_i=a e^{\beta_i}(E/c)n_i\). Therefore
\[
E_s n_{si}=E_t n_{ti}e^{a_i\Delta},\qquad
\Delta=\eta_t-\eta_s,\qquad \Lambda=\ln(E_s/E_t)\ge0.
\]
Define \(g_i=n_{ti}e^{a_i\Delta}\), \(D=\|g\|_2\), and
\[
F(\Delta)=\ln D-\Lambda,\qquad n_s=g/D.
\]
Then \(F(0)=-\Lambda\) and
\[
F'(\Delta)=q_s=\sum_i a_i n_{si}^2\in[a_{\min},a_{\max}].
\]
The intermediate-value theorem and strict monotonicity give exactly one root in
\[
\Lambda/a_{\max}\le\Delta\le\Lambda/a_{\min}.
\]
This is an analytic existence/uniqueness result for the specified domain.
For FLRW, \(\Delta=\Lambda\); for an exact axis \(j\),
\(\Delta=\Lambda/a_j\). The local target factor
\(q_t=\sum_i a_i n_{ti}^2\) belongs to the line-boundary transport coefficient;
the source factor \(q_s\) belongs to the root derivative.

A numerical implementation evaluates the norm through shifted logarithms and
preserves zero components. A positive lower bound on \(a_{\min}\) controls the
inverse-root conditioning. A small \(a_{\min}\) is a meaningful conditioning
limit, not a reason to use the FLRW clock.

## 2. Differentiation without dividing by a direction component

Let \(n_t\cdot\delta n_t=0\), \(\sum_i\delta b_i=0\). Differentiating \(F=0\)
at the root gives
\[
\delta\Delta=
\frac{\delta\Lambda-
 \sum_i n_{si}e^{a_i\Delta-\ln D}\delta n_{ti}
 -\Delta\sum_i n_{si}^2\delta b_i}{q_s},
\qquad
\delta\eta_s=\delta\eta_t-\delta\Delta .
\]
For
\[
v_i=e^{a_i\Delta-\ln D}\delta n_{ti}
+n_{si}\left(\Delta\delta b_i+a_i\delta\Delta\right)
\]
the normalized source tangent is
\[
\delta n_s=v-n_s(n_s\cdot v),\qquad
\delta q_t=\sum_i n_{ti}^2\delta b_i+
2\sum_i a_i n_{ti}\delta n_{ti}.
\]
Exact-axis values may have nonzero off-axis derivatives. The implementation must
retain their amplification factors when representable and reject an
unrepresentable tangent explicitly. It must not return a zero derivative merely
because the value used an axis shortcut.

## 3. Native-Wien reference conversion

The inherited source stores \(d=f-W(x)\), \(W(x)=e^{-x}\), where
\(x=E/(k_B T)\). Along collisionless propagation \(f\) is unchanged. Since
\[
x_s=x_t e^{\Lambda-\Delta},
\]
an admitted source departure \(H(\eta_s,n_s)\) gives
\[
d_{\rm in}=H(\eta_s,n_s)+W(x_s)-W(x_t),\qquad
f_{\rm in}=H+W(x_s).
\]
The distinction between the absolute occupation and its signed departure
determines the positivity check. The conversion vanishes in FLRW because then
\(x_s=x_t\). Its differential is
\[
\delta d_{\rm in}=\delta H+x_tW_t\,\delta\ln x_t
-x_sW_s(\delta\ln x_t+\delta\Lambda-\delta\Delta).
\]
Computing a small difference of two nearby exponentials requires a signed
expm1 form. Transformed \(x_s\) is represented in the log domain; its infinite-x
limit has \(W_s=0\) and \(x_sW_s=0\). The \(x_t=0\) limit is treated explicitly.

This coordinate conversion uses the native Wien definition. The source
definition is fixed by the exact vendor code, rather than inferred from a
literature statement about a Planck distribution.

## 4. Retained history, angular representation and boundary composition

The finite represented field is
\[
H=c_0+v\cdot n+n^TQn,
\]
with ten time-linear coefficient histories: one scalar, three vector,
three diagonal and three off-diagonal entries of a symmetric \(Q\).
Its source tangent is
\[
\delta H=\delta H_{\rm data}+H_\eta\delta\eta_s+
(v+2Qn_s)\cdot\delta n_s.
\]
The new wrapper admits only a retained strict-past prefix:
\(iz\ge2\), \(\eta_s\ge\eta_0\),
\(\eta_s<\eta_0+h(iz-1)\). It checks these before invoking the unchanged legacy
interpolator. At a time knot a nonzero source-time tangent is nonsmooth; a zero
source-time tangent can retain the fixed-cell data derivative.

With \(s=x_{r,p}/(3x_{1s})\), \(T=e^{-\tau/q_t}\),
\(A=-\operatorname{expm1}(-\tau/q_t)\), the inherited boundary is
\[
d_{\rm out}=d_{\rm in}+(s-d_{\rm in})A.
\]
The composed tangent is
\[
\delta d_{\rm out}=T\delta d_{\rm in}+A\delta s+
(s-d_{\rm in})T
\left(\frac{\delta\tau}{q_t}
-\frac{\tau\,\delta q_t}{q_t^2}\right).
\]
The unchanged event rate is \(R=G_{\rm native}H_tq_t(d_{\rm out}-d_{\rm in})\).
Atomic and radiation energy entries are \(-E_{21}R\) and \(+E_{21}R\), with
\(E_{21}\) converted to joules. The outgoing stored occupation encodes the same
event. Propagation redshift work has its own geometric owner.

## 5. Conditional error theorem

Assume a valid residual uncertainty \(\epsilon_F\), field uncertainty
\(\epsilon_H\), Lipschitz constants \(K_\eta,K_n\), and arithmetic allowance
\(\epsilon_{\rm arith}\) over the entire actual query uncertainty tube.
The root mean-value estimate gives
\[
\epsilon_\Delta\le\epsilon_F/a_{\min}.
\]
At fixed target direction,
\[
\partial_\Delta n_{si}=(a_i-q_s)n_{si},\qquad
\|\partial_\Delta n_s\|_2^2=\operatorname{Var}_{n_s^2}(a).
\]
For any weights \(w_i\ge0,\sum w_i=1\), mean \(q=\sum w_i a_i\),
\[
(a_{\max}-q)(q-a_{\min})-\operatorname{Var}_w(a)
=\sum_i w_i(a_i-a_{\min})(a_{\max}-a_i)\ge0.
\]
Consequently \(\|\partial_\Delta n_s\|\le(a_{\max}-a_{\min})/2\).
Moreover \(|\partial_\Delta W_s|=x_s e^{-x_s}\le1/e\). Hence
\[
\epsilon_{\rm in}\le\epsilon_H+
\left(K_\eta+\tfrac12K_n(a_{\max}-a_{\min})+1/e\right)\epsilon_\Delta+
\epsilon_{\rm arith}.
\]
Holding the target boundary coefficients fixed,
\[
\epsilon_{\rm out}\le T\epsilon_{\rm in},\quad
\epsilon_R\le G_{\rm native}H_tq_tA\epsilon_{\rm in},\quad
\epsilon_E=E_{21}\epsilon_R.
\]
These bounds are constructive once their input witnesses are supplied.
Sampled same-h parity does not supply the missing witnesses. The actual h4
data retained here have no admitted independent endpoint/reference uncertainty;
therefore their physical history-error gate remains uncalibrated.

A floating residual combined with a selected arithmetic allowance is only the
finite stated numerical test. It does not establish an interval bound for every
library operation. The primary controls compare against independent high
precision and save the allowance regime.

## 6. Independent checks and literature relation

The fresh pre-code reviewer independently recovered the conserved-momentum,
implicit-function, normalized-vector, reference-conversion and error arguments.
The one new Wolfram call returned zero for both the composed
Wien-plus-boundary differential difference and the variance interval identity.
Source and actual response are preserved in provenance/WOLFRAM_NEW_SOURCE.wl
and WOLFRAM_NEW_RESULT.json. Its requested 5 s kernel limit is not a measured
CPU/wall value. The original Stage A's two symbolic checks are reused separately.

Fleury, Pitrou and Uzan, PRD91,043511 (2015), Sec.IV A Eqs.(4.1)-(4.5),
derive the conserved covariant spatial wave-vector and the Bianchi I redshift.
Their eta is conformal time and their observation direction is opposite to
propagation; the conventions above perform the required translation.
https://arxiv.org/abs/1410.8473
https://arxiv.org/pdf/1410.8473

Ali-Haimoud and Hirata, PRD83,043513 (2011), describes HyRec's simultaneous
radiation/population treatment. Lee and Ali-Haimoud, PRD102,083517 (2020),
Sec.II C and III D, explicitly retain history dependence of effective line
rates and discuss the coupling of time and frequency resolution in full
radiative transfer. Those studies motivate a separate history-error obligation;
their published accuracy is not a bound on this retained array or Bianchi
extension.
https://arxiv.org/abs/1011.3758
https://arxiv.org/pdf/2007.14114

SciSpace supplied ten discovery records, including duplicate preprint/journal
versions. Primary records corrected the discovery dates; no new-literature
priority or strong no-go claim is made. The added result is this finite
source-pinned adapter and its independently checked controls.


