# Completed R6 mathematical review

This reproduces the completed derivations, findings, and original tiny-check command/output. **No computation was rerun, no files were changed, and the new `time_convergence.py` was not reviewed.**

## Verdict

**The inspected U6 recurrence and derivative-memory rollover match the source. The method is second order under smooth, consistently initialized conditions, with strict negative-real scalar stability interval \((-2,0)\). The saved U6 \(h/2\) result cannot establish R3I global three-grid convergence.**

The mathematical requirements for the saved-history diagnostic are to preserve checkpoint provenance, propagate uncertainty with absolute interpolation weights, and distinguish complete-domain comparisons from boundary and order-resolution masks.

## 1. Local defect and stability: second order; exclude the \(-2\) endpoint

Let \(t=\ln a\), and define the defect as **exact increment minus numerical increment**, using exact derivative samples:

\[
\begin{aligned}
d_{n+1}
&=y(t+h)-y(t)
-h\left[\frac54y'(t)-\frac14y'(t-2h)\right]\\
&=\frac23h^3y'''(t)-\frac7{24}h^4y^{(4)}(t)+O(h^5).
\end{aligned}
\]

Thus the one-step defect is \(O(h^3)\), and the normalized local truncation error \(d_{n+1}/h\) is \(O(h^2)\). The zero-step characteristic polynomial is

\[
\rho(\xi)=\xi^2(\xi-1),
\]

which satisfies the root condition: the root \(1\) is simple and the double root \(0\) lies inside the unit disk. With suitable starting data and smoothness, this yields global order two.

This agrees with Appendix C, Eq. C1, and with the updates and rollover in [`primordial_2012_owned_u6.py`](sandbox:/workspace/scratch/afe554957b2e/rec_work/src/full_bianchi_hyrec/trajectory/primordial_2012_owned_u6.py), particularly lines 79, 80, 98 and 99. genui{"citation":{"ref":"turn3view1"}}

### Independent scalar stability derivation

For \(y'=\lambda y\), put \(\mu=\lambda h\). The amplification polynomial is

\[
P_\mu(\xi)=\xi^3-\left(1+\frac54\mu\right)\xi^2+\frac14\mu.
\]

Use \(s=-\mu>0\) and the Cayley transformation

\[
\xi=\frac{1+w}{1-w}.
\]

Multiplication by \((1-w)^3\) gives

\[
(2-s)w^3+2(2-s)w^2+2(1+s)w+s.
\]

For \(0<s<2\), all coefficients are positive, and the cubic Hurwitz determinant is

\[
a_2a_1-a_3a_0=(2-s)(4+3s)>0.
\]

Hence all transformed roots satisfy \(\operatorname{Re}w<0\), and all amplification roots satisfy \(|\xi|<1\).

At the endpoint,

\[
P_{-2}(\xi)=(\xi+1)^2\left(\xi-\frac12\right),
\]

so the double root \(-1\) permits \(n(-1)^n\) growth. For \(\mu<-2\), \(P_\mu(-1)>0\), while \(P_\mu(\xi)\to-\infty\) as \(\xi\to-\infty\); therefore a real root lies below \(-1\).

**Impact / minimum correction:** use

\[
\boxed{-2<\lambda h<0}
\]

for strict scalar decay stability. The point \(\mu=0\) satisfies the bounded root condition, giving \((-2,0]\) under that convention. Neither this scalar result nor the local defect proves stability or second-order convergence of the entire coupled, retarded, switching calculation.

## 2. Restart errors can lower order; a common checkpoint bias can disappear from Richardson differences

Suppose the restart state is unchanged, but the stored derivatives have errors \(\delta_{-2}\) and \(\delta_{-1}\). Comparing two scalar numerical continuations gives

\[
e_1=-\frac h4\delta_{-2},
\qquad
e_2=\left(1+\frac54\mu\right)e_1-\frac h4\delta_{-1}.
\]

After these two updates, the directly contaminated memory has rolled out, **but the injected state error remains**. For a fixed number of restarts and uniformly stable propagation, its contribution is \(O(h\delta)\):

- Fixed \(O(1)\) derivative errors can introduce an \(O(h)\) global term.
- \(O(h)\) derivative errors can still permit second-order global accuracy, while changing the leading error coefficient.
- \(O(h^2)\) derivative errors preserve \(O(h^3)\) startup defects.
- Differencing independently uncertain stored states can produce derivative uncertainty \(O(\epsilon/h)\), hence an \(O(\epsilon)\) injected state error.

The original C seeds are centered differences at the intended memory times: see `rec_build_history` in [`history.c`](sandbox:/workspace/scratch/afe554957b2e/rec_raw/evidence_full_001/full5210_stored/source_extract/HyRec/history.c), beginning at lines 525, 546 and 575.

The inspected U6 path correctly carries the already coupled RHS values at inputs 53177 and 53178. Its loader checks those values and their indices in [`primordial_2012_refined_u6_rt_boundary.py`](sandbox:/workspace/scratch/afe554957b2e/rec_work/src/full_bianchi_hyrec/trajectory/primordial_2012_refined_u6_rt_boundary.py). **I found no reseeding error in that inspected continuation path.**

### Shared-checkpoint cancellation

A separate problem survives even perfect memory rollover. Suppose a common inaccurate checkpoint produces

\[
P_h(t)=y(t)+B(t)+C(t)h^2+o(h^2).
\]

Then

\[
D_{01}=P_h-P_{h/2}
=\frac34Ch^2+o(h^2),
\]

\[
D_{12}=P_{h/2}-P_{h/4}
=\frac3{16}Ch^2+o(h^2).
\]

Consequently,

\[
\frac{D_{01}}{D_{12}}\longrightarrow4,
\qquad
p_{\rm observed}\longrightarrow2,
\]

while Richardson extrapolation approaches **\(y+B\)**. The common leading bias is invisible to the differences.

Here the checkpoint includes photon prehistory as well as \(x_e,T_m\), derivative memory and stage state. [`owned_flrw_history.py`](sandbox:/workspace/scratch/afe554957b2e/rec_work/src/full_bianchi_hyrec/trajectory/owned_flrw_history.py) protects ownership and accepted-past access; its finite-prefix checks do not establish the prefix’s accuracy.

**Impact / minimum correction:** require each resolution’s independently evolved checkpoint, RHS memory and photon history, traceable back to the contracted \(z=8000\) start. Same-grid continuation may reuse its own checkpoint. A restart exclusion window does not remove inherited bias from downstream results.

## 3. Four-point interpolation requires absolute-weight uncertainty propagation

The original [`hyrectools.c`](sandbox:/workspace/scratch/afe554957b2e/rec_raw/evidence_full_001/full5210_stored/source_extract/HyRec/hyrectools.c), `rec_interp1d`, uses

\[
r=\frac{t-t_0}{h},\qquad
i=\min(\max(\lfloor r\rfloor,1),N-3),\qquad
\theta=r-i
\]

and the stencil \(y_{i-1},y_i,y_{i+1},y_{i+2}\), with weights

\[
w=\left(
-\frac{\theta(1-\theta)(2-\theta)}6,\,
\frac{(1+\theta)(1-\theta)(2-\theta)}2,\,
\frac{(1+\theta)\theta(2-\theta)}2,\,
-\frac{(1+\theta)\theta(1-\theta)}6
\right).
\]

**Clamp the index, not the fraction.** The first/last stencils legitimately allow \(\theta\in[-1,0]\) or \([1,2]\).

The inspected [`source_interp1d`](sandbox:/workspace/scratch/afe554957b2e/rec_work/src/full_bianchi_hyrec/trajectory/primordial_2012_low_z_to_end.py) preserves this rule, but its constants and required array length are specific to the coarse grid.

### Nonnegative uncertainty bounds

For nonnegative **absolute-unit** parity bounds \(E_{\ell j}\) and quantization half-units \(Q_{\ell j}\), the appropriate propagated bounds are

\[
\bar E_\ell=\sum_j|w_{\ell j}|E_{\ell j},
\qquad
\bar Q_\ell=\sum_j|w_{\ell j}|Q_{\ell j}.
\]

A pairwise difference therefore has bounds \(\bar E_a+\bar E_b\) and \(\bar Q_a+\bar Q_b\). Preserve the original floor by taking

\[
F_{ab}=\max\!\left\{
F_{ab}^{\rm existing},
32u\max(|P_a|,|P_b|,s_0),
10(\bar E_a+\bar E_b),
10(\bar Q_a+\bar Q_b)
\right\},
\]

where \(u=2^{-53}\), and \(s_0\) is the applicable field floor.

The failure mechanism is concrete. At \(\theta=1/2\),

\[
w=(-1,9,9,-1)/16.
\]

For bounds \((9\epsilon,\epsilon,0,0)\), signed interpolation gives **zero**, whereas the correct absolute-weight bound is

\[
\frac98\epsilon.
\]

Even uniform bounds are amplified by \(\sum|w|=5/4\); endpoint stencils can amplify more.

**Minimum correction:** use each level’s actual \((t_0,h,N)\) and global indices, preserve the original value-evaluation association, and propagate uncertainty separately with \(|w|\). Do not use signed interpolation followed by clipping or absolute value, assume root-sum-square independence, or treat missing uncertainty metadata as zero.

Compute

\[
p=\log_2\left|\frac{D_{01}}{D_{12}}\right|
\]

only after both signed differences exceed their respective floors and have the same sign, as required by [`R3I-CONVERGENCE-v1`](sandbox:/workspace/scratch/afe554957b2e/rec_work/research/rec_r3i_time_refinement_20261016/CONTRACT.json). Keep order resolution separate from sensitivity/contraction results.

## 4. U6 coverage and the required masks

The saved [`verification.json`](sandbox:/workspace/scratch/afe554957b2e/rec_work/research/rec_r3m_u6_full_owner_20261019/receipts/full5210_stored/verification.json) reports 5,210 steps ending at index 58389,

\[
z=669.959490187319,
\]

with status `RT_BOUNDARY_REACHED_NO_EMLA_EVALUATION`. Its [`U6 contract`](sandbox:/workspace/scratch/afe554957b2e/rec_work/research/rec_r3i_time_refinement_20261016/h2_u6_rt_boundary_001/CONTRACT.json) starts at index 53179,

\[
z=836.0411750186029,
\]

on \(h/2\).

This supplies one resolution over one segment. It does not supply the complete three-level comparison or full-domain coverage. Same-\(h\) C parity cannot supply the missing Python levels. The saved [`EVIDENCE.json`](sandbox:/workspace/scratch/afe554957b2e/rec_work/research/rec_r3m_u6_full_owner_20261019/EVIDENCE.json) already states that scope correctly.

### Boundary and validity masks

| Mask or classification | Required treatment |
|---|---|
| **Coverage and stencil availability** | Require all three independent Python levels and all four native stencil nodes at each comparison point. Preserve the original endpoint padding needed for \(z=0\). A truncated U6 segment must not acquire artificial endpoint clamps. |
| **Contract transition regions** | Include \(z\in[1553,1573]\), \(z\in[826,846]\), and the union of every level’s stage neighborhoods \(t_{\rm event}\pm4h_{\rm coarse}\). |
| **Stage and restart boundaries** | Tag HeIII exit, He post-Saha exit, FULL onset, He cutoff, H post-Saha exit, thermal coupling, FULL→EMLA, EMLA→Peebles, and restart seams. Identify stencils crossing them and retain input-versus-output event semantics. |
| **Endpoint/clamped stencils** | Report separately from ordinary interior stencils; they remain valid output values when their original support is present. |
| **Order resolution** | Require finite data, the signed-difference condition and both frozen uncertainty floors. Zero or unresolved differences must not produce an order claim. |

Locate events from the **2012 source guards**. For example, the active [`hyrec_params.h`](sandbox:/workspace/scratch/afe554957b2e/rec_raw/evidence_full_001/full5210_stored/source_extract/HyRec/hyrec_params.h) uses

\[
\texttt{DXHII\_MAX}=3\times10^{-4},\quad
\texttt{DLNT\_MAX}=5\times10^{-4},\quad
\texttt{PION\_MAX}=10^{-2};
\]

`history.c` determines the RT index and low-temperature table exits. The paper’s earlier switch thresholds are source context; they do not replace these rules.

**Minimum correction:** use boundary masks to qualify interior order estimates, while retaining boundary points in complete global sensitivity/contraction norms and reporting their contributions separately. Preserve the \(h/4\)-based scales,

\[
S_{x_e}=\max(|x_{e,h/4}|,10^{-4}),
\qquad
S_{T_m}=\max(|T_{m,h/4}|,1\ {\rm K}),
\]

the contracted global and per-regime sensitivity/contraction tests, and report points \(1563,836,1100,20,0\).

Empty or missing regions cannot count as passing regions. For the supplied U6-only result, global convergence remains `NOT_ESTABLISHED`; the three-grid order test remains unperformed. No global \(p=2\) claim follows.

## Exact original independent check

This was the only numerical calculation command. **The command and output below are copied from the completed check; they were not rerun.** In the root-check loop, `z` denotes \(\lambda h\).

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python3 - <<'PY'
from fractions import Fraction as F
from math import factorial, floor, log
import numpy as np

# Coefficient of h**k * y**(k) in exact-minus-numerical increment.
print('defect k=1..5:', [str(F(1,factorial(k)) - (F(5,4) if k==1 else 0) + F(1,4)*F((-2)**(k-1),factorial(k-1))) for k in range(1,6)])
print('boundary factor coefficients:', np.polymul([1,2,1],[1,-.5]).tolist())
for z in (-1.9, -2.0, -2.1):
    r=np.roots([1, -(1+1.25*z), 0, .25*z])
    print(f'z={z:.1f}, roots={np.sort_complex(r)}, rho={max(abs(r)):.12f}')

def weights(f):
    return (-f*(1-f)*(2-f)/6, (1+f)*(1-f)*(2-f)/2,
            (1+f)*f*(2-f)/2, -(1+f)*f*(1-f)/6)
for f in (F(-1,2), F(1,2), F(3,2)):
    w=weights(f)
    print('f=',str(f),'weights=',list(map(str,w)),'sum=',str(sum(w)),'abs_sum=',str(sum(map(abs,w))))
w=weights(F(1,2)); e=(9,1,0,0)
print('nonnegative e=(9,1,0,0): signed=',str(sum(a*b for a,b in zip(w,e))), 'bound=',str(sum(abs(a)*b for a,b in zip(w,e))))
for div in (1,2,4):
    h=8.49e-5/div; raw=log(8001.)/h; n=floor(2+raw)
    ix=min(max(floor(raw),1),n-3); f=raw-ix
    print(f'h/{div}: N={n}, z0_stencil={list(range(ix-1,ix+3))}, f={f:.12f}, abs_sum={sum(map(abs,weights(f))):.12f}')
PY
```

**Original exit code: 0. Original stdout:**

```text
defect k=1..5: ['0', '0', '2/3', '-7/24', '7/40']
boundary factor coefficients: [1.0, 1.5, 0.0, -0.5]
z=-1.9, roots=[-0.93896478-0.25062207j -0.93896478+0.25062207j  0.50292955+0.j        ], rho=0.971836545622
z=-2.0, roots=[-1.00000001+0.j -0.99999999+0.j  0.5       +0.j], rho=1.000000014281
z=-2.1, roots=[-1.32674918+0.j -0.79561007+0.j  0.49735925+0.j], rho=1.326749178430
f= -1/2 weights= ['5/16', '15/16', '-5/16', '1/16'] sum= 1 abs_sum= 13/8
f= 1/2 weights= ['-1/16', '9/16', '9/16', '-1/16'] sum= 1 abs_sum= 5/4
f= 3/2 weights= ['1/16', '-5/16', '15/16', '5/16'] sum= 1 abs_sum= 13/8
nonnegative e=(9,1,0,0): signed= 0 bound= 9/8
h/1: N=105859, z0_stencil=[105855, 105856, 105857, 105858], f=1.736311544460, abs_sum=1.531273640912
h/2: N=211717, z0_stencil=[211713, 211714, 211715, 211716], f=1.472623088921, abs_sum=1.616302552945
h/4: N=423432, z0_stencil=[423428, 423429, 423430, 423431], f=1.945246177842, abs_sum=1.152433693231
```

The numerical splitting near the double root at \(-2\) is roundoff; the exact factorization determines its instability. The \(z=0\) results confirm that all three grids require an unclipped fraction greater than one and that their uncertainty amplification factors differ.

## Evidence and preserved status

The saved-run facts above were read from JSON receipts. No production integration or raw-CSV parity recomputation was performed. The mathematical conclusions derive from the inspected source text, independent algebra, and the reproduced tiny check.

**Preserved without reset:** U5 `HOLD_9_FAIL` / `HOLD_8_FAIL`, historical cost `CLOSED_HOLD_NOT_RESET`, and `REI=false`.
