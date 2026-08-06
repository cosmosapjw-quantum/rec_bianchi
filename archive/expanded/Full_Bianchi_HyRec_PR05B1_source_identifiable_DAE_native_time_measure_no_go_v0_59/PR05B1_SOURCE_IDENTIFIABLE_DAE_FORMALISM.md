# PR-05B1/v0.59 source-identifiable original-HyRec DAE and native-time-measure no-go

## Result

The canonical local system in independent variable `eta=ln(a)` has one differential row and 313 algebraic rows:

```text
U_local = (x_e, Delta x_2s, Delta x_2p, Delta x_v[0:311])
M_local = diag(1,0,...,0).
```

The radiation history arrays `Dfminus_hist`, `Dfminus_Ly_hist`, and `Dfnu_hist` are accepted-step causal memory, not local differential rows. Their total one-slice size is `625` values.

## Source residual and shifted Jacobian

The electron row is

```text
R_e = d x_e/d eta - F_e(x_e, Delta x_2s, Delta x_2p).
```

The 313 native rows are the canonical algebraic constraint `T_native x_native-s_native=0`. PETSc's shifted Jacobian is `dR/dU + shift*dR/dUdot`; the maximum three-lane centered-difference residual is `3.85954811782200288e-15`.

## Constructive no-go

For a finite virtual-spike transient equation, the photon time-derivative mass is proportional to a finite `Delta ln(nu)` support (and to `1/x_1s` for the source variable `Delta x_b=x_1s Delta f_b` on a frozen background). The canonical archive supplies centre frequencies and integrated rates but no finite support widths, edge array, or spike shape.

Two positive nonoverlapping top-hat support choices, `0.2` and `0.4` times each centre's nearest log-frequency gap, give candidate masses in ratio `2.00000000000000000e+00`. Both converge to zero in the source's zero-width limit. Therefore no finite local native-radiation mass is source-identifiable; neither candidate is promoted.

## Causal replacement path

The source-identifiable time dependence is the characteristic history path: use accepted outgoing radiation at earlier redshift/higher frequency to construct incoming `Dfplus`, solve the real/virtual algebraic block, compute `dxHIIdlna`, then append `Dfminus` and `Dfnu` only after the step is accepted. PR-05B2 implements this typed accepted-step state and its analytic JVP.

## Claim boundary

PR-05B1 is a bounded no-go, not a solver failure. It closes the source-role/mass-matrix audit and a positive bounded electron/algebraic DAE reference. It does not remove Sobolev escape, `A1s` diffusion, completed/Schur `Tvv`, or scalar history feedback; PR-05B remains open.
