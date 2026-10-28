# Incoming-radiation adjoint of the source-point electron field

## Source construction

The pinned October2012 HyRec source `populateTS_2photon` forms a 2+311 block
system. Its two real entries correspond to 2s and 2p. The virtual unknowns
are x1 times radiation occupation departures. Radiation incoming values
appear only in sr[0], sr[1] and the separate sv[b] sources; they do not occur
in A, B, C or V at fixed thermodynamic point.

Use the precise represented-coefficient model in CONTRACT.md. Its sparse G
is read directly from hydrogen.c lines defining sr and sv; in particular
Ly0 enters the 2p row and Ly1 enters the 2s row with kBeta=1.664786871919931.
The source population operator has units s^-1, X and u are dimensionless,
and FH=dxHII/dln(a) is dimensionless. Hence q=Beta/H and J have no dimensions.

Write a for the incoming-independent real source vector and d for the
incoming-independent scalar. Assuming exact-real M invertible,

    X=M^-1(a+Gu),       F=d+q^T X.

Differentiation at fixed P yields dX=M^-1 G du. Define the single adjoint
solution by M^T lambda=q. Then

    dF=q^T M^-1 G du=lambda^T G du,
    J=G^T lambda.

Because M,a,G,q,d are constant in u, this relation holds for any finite signed
du within this algebraic model. No small-perturbation remainder appears.
The second derivative with respect to u is exactly zero in this model.
This identity alone supplies neither a floating-point error certificate nor
a nonsingularity certificate for a coefficient neighborhood.

## Structured solve and transpose

The adjoint theorem above needs invertible M. The particular factorization
below additionally requires invertible V and nonzero exact pivots for the
chosen tridiagonal elimination; invertibility of M alone does not imply them.

Let mathematical C=Cstored^T. Put Z=V^-T B^T and Q=A-B V^-1 C.
Block elimination of M^T lambda=q gives

    Q^T lambda_r=q_r,
    lambda_v=-Z lambda_r,
    Q^T=A^T-C^T Z.

For a general right-hand side (r_r,r_v), first solve
V^T y=r_v, then Q^T lambda_r=r_r-C^T y, and finally
lambda_v=y-Z lambda_r. The code solves only tridiagonal systems and a 2x2
Schur system. It does not form an inverse.

The original stored band convention is lower[b]=V[b,b-1] and
upper[b]=V[b,b+1]. Therefore transpose lower[b]=upper[b-1] and
transpose upper[b]=lower[b+1]. A same-index swap is a different matrix and
is an intentional negative control.

The leading-principal-minor recurrence depends on lower[i]*upper[i-1].
It is invariant under transpose, so exact nonzero elimination pivots of V
are also those of V^T. Original row diagonal dominance cannot simply be
ascribed to the transpose. This study observes numerical pivots without
promoting those observations to exact interval certificates.

## Source-to-saved difference identity

Superscripts b and c denote a saved baseline and control with identical
point coefficients. They are not the constant source a. Define

    r_b=M X_b-S_b,       r_c=M X_c-S_c,
    r_lambda=M^T lambda_hat-q,
    e_b=FH_b-(d+q^T X_b),
    e_c=FH_c-(d+q^T X_c),
    e_G=(S_c-S_b)-G(u_c-u_b).

Direct substitution, with DeltaX=X_c-X_b and du=u_c-u_b, gives

    FH_c-FH_b-(G^T lambda_hat)^T du
      = (e_c-e_b)
        + lambda_hat^T e_G
        + lambda_hat^T(r_c-r_b)
        - r_lambda^T DeltaX.

All four right-hand contributions are computed from saved data. The first
contains native scalar rounding, the second contains the explicitly defined
real reconstruction's source mismatch, the third contains native linear
solve residuals, and the fourth contains this study's adjoint solve residual.
The source-mismatch term is separately gated; the identity cannot hide an
arbitrary incorrect G by merely naming its discrepancy a remainder.

The nine saved native controls are zero, negative and doubled incoming at
three points. They span one incoming direction per point, and therefore do
not independently test all 313 columns of J. The full vector is supported by
the source-derived G, the independently assembled adjoint residual and primal
directional checks; the saved controls test its connection to three recorded
native directions.

The exact-real inequality

    |deltaF| <= sum_j |J_j| * ||du||_infinity

explains why the adjoint response matters to a later radiation coupling.
An actual error enclosure also needs certified coefficient bounds, physical
input errors and the full coupled state norm. Those are separate providers.

## Full thermodynamic differential: implementation contract for later work

Within a differentiable branch/cell, allow P to vary and require dxe=dp for
the He-neutral manifold xe=p. Implicit differentiation gives

    dF = dd+(dq)^T X
         +lambda^T[da+(dG)u-(dM)X]
         +J^T du.

In source scalar variables, with c_i=nH(s*x1*DAlpha_i+Alpha_i*Delta),

    dF = [-sum_i dc_i+xr^T dBeta]/H-F*dH/H
         +lambda^T[da+(dG)u-(dM)X+Gdu].

The table interpolation cell, feature choices and optical-depth branch must
be fixed for the ordinary derivative to apply. At their interfaces one must
state one-sided or piecewise derivatives. This unit computes only incoming
response; it does not silently set the other terms to zero in a coupled
time derivative.

## Literature relationship

The HyRec effective multilevel atom and virtual-state radiative-transfer
construction is inherited from Ali-Haimoud and Hirata, Phys. Rev. D 83,
043513 (2011), arXiv:1011.3758v2, and the pinned October2012 implementation.
The adjoint identity is standard finite-dimensional linear algebra. The
contribution here is its source-specific 313-input construction, reproducible
writer-bound numerical response and explicit saved-native discrepancy
accounting. No claim of a new general adjoint theorem or strong no-go is made.

Primary source: https://arxiv.org/abs/1011.3758v2
Pinned source: ../rec_h5_electron_field_20261028/inputs/original/HyRec/hydrogen.c
