# REC-H5-THERMO-BRIDGE01: source-locked electron response and common density/expansion scaling

Date 2026-10-28. Research status: **derived + numerically checked in a scoped represented-real model**. This is not the six-axis FULL source Jacobian and is not a physical H5/H6/H7 error certificate.

## Definitions and exact scope

Use the original HyRec FULL hydrogen source retained in REC-H5-ELECTRON-RESPONSE01. Work with the last-source-writer state at each of 132 saved points and the same source-prefix representation. The FULL/H_STEADY, He-neutral, `fsR=meR=1`, `eta=ln a` baseline has electron variable `xe` and hydrogen ionized fraction `xHII` as **independent ambient source coordinates**; physical pure-H variations have `dxe=dxHII` and are NOT computed here. Frozen inputs are incoming `u` (311 virtual + 2 Lyman), all source table/grid/point data, `xHII`, `TR`, `TM`, `nH` and `H` except along one explicitly declared common-scaling path. Units: `nH [cm^-3]`, `H [s^-1]`, source-rescaled temperatures `[eV]`. Source and output are a specified **exact-real affine lift of saved binary64 coefficient prefixes**. No differentiation of the binary64 rounding map is claimed. Default spacetime signature (-,+,+,+); physical fundamental constants are not set to unity by this unit.

Let `X=(x_{r,2s},x_{r,2p},x_{v,0},...,x_{v,310})^T` and

`M X = s_0 + G u`,  `F = d + q^T X = d xHII / d ln(a)`.

The 313x313 M and 313x313 G and q are independent of ambient `xe` for fixed `xHII` and thermodynamic background. Define `a_i=nH*alpha_i*xHII` (`i=0,1`) with alpha_i the saved original table-interpolated recombination rate, `b=(a_0,a_1,0,...,0)^T`. The source and direct ionization term have `∂xe s=b` and `∂xe d=-(a_0+a_1)/H`. This is read from the actual stored source code, not from assumed general Bianchi dynamics.

## Proposition A: ambient electron column

At each saved point for which M is nonsingular,

`Dxe F := (∂F/∂xe)_(xHII,TR,TM,nH,H,u,tables) = q^T M^-1 b - (a_0+a_1)/H.`

If `M^T lambda=q`, then `Dxe F = lambda^T b - (a_0+a_1)/H`.

Proof: Differentiate `M X = s` at fixed M to obtain `M ∂xe X = b`. Differentiate F including its direct term. The adjoint identity is a transpose of the exact finite-dimensional solve. No independent six-dimensional physical tangent or regularity enclosure is inferred.

## Proposition B: exact common nH/H finite rescaling in the represented model

Let `nH(t)=nH(0)e^t`, `H(t)=H(0)e^t`, holding `xe,xHII,TR,TM,u,grid,tables` fixed. In the real represented coefficient extension, all optical-depth ratios `nH/H`, line-escape ratios `H/nH`, M and G remain fixed. The real source changes as `s(t)=s(0)+(e^t-1)xe b`, while `q(t)=q(0)e^-t` and `d(t)=e^-t[d(0)-(e^t-1)xe (a_0+a_1)/H]`. Consequently,

`F(t)=e^-t [F(0)+(e^t-1)xe Dxe F]`, and

`(∂ln nH + ∂ln H)F = xe Dxe F - F`.

The sum means a **simultaneous** increment of both log variables, not a separately measured column. It is exact in the defined smooth real extension, not asserted for a freshly recomputed native binary64 prefix (division/multiplication rounding can change) and not for the actual coupled time evolution. In particular this says nothing separately about `∂ln nH F` or `∂ln H F`.

## Preconditions and non-transfers

1. No xHII variation: changing xHII changes the neutral fraction, optical depths, M, q, G and direct terms. **The ambient xe column is not the physical pure-H column.**
2. The PR135 full six-axis stable-source map is a *different* represented operator from the source-prefix matrix of PR147. Agreement of one numeric column at index131 is an external numerical comparison, **not** an equality/transfer of operator norms, derivatives or source identities.
3. The source-prefix M is pointwise solved at 132 fixed points. A pointwise small residual does not prove continuous nonsingularity, a Lipschitz constant or a whole-cell interval bound.
4. Missing other five primitive columns, history pullback/endpoint/query retiming, Bianchi frame/geodesic/direction and thermal ODE/source identities remain open. No H5 physical `epsilon`, `e0`, `tube`, global convergence, production approval or REI activation.
