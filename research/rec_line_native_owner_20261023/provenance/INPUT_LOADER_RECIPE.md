# Exact source reuse and matrix shape

Load selected original AST nodes from the byte-preserved
`original_hyrec_physical_flux.py` (module SHA256
`37e00dd8224ddd4d5cec7b2b78c689893996e499b944f38302c5dcc104b61e9f`).
Exact node source ranges and segment hashes are in `AST_REUSE_RECIPE.json`.
The minimum production input loader needs `_readonly_array`,
`OriginalHyRecTrajectorySnapshot`, `parse_original_hyrec_snapshot_csv`, and
`dense_original_hyrec_matrix`. Preserve the original `from __future__ import
annotations` and AST bodies. Give the isolated module namespace `dataclass`,
`math`, `csv`, `Path`, `Iterable`, `np`, `NVIRT=311`,
`H_PLANCK_EV_S=h_SI/eV_SI`. Register the temporary module in `sys.modules`
before executing the selected AST so dataclass annotation lookup works.
No imported native solver or unrelated collision package is required.

The exact original `structured_schur_solution` is a reference candidate, not
invoked during this source-read phase. Its dense virtual solve is independent
of a new small-band factorization. Do not count a future invocation as a native
cosmological rerun: it is a frozen-snapshot linear algebra reference, and count
it separately from application queries of an already computed factorization.

## scipy band storage

Stored native arrays use `Tvv[0,b]=V[b,b]`,
`Tvv[1,b]=V[b,b-1]`, `Tvv[2,b]=V[b,b+1]`. For
`scipy.linalg.solve_banded((1,1), ab, rhs)` construct:

```python
ab = np.zeros((3, 311))
ab[0, 1:] = Tvv[2, :-1]
ab[1, :] = Tvv[0, :]
ab[2, :-1] = Tvv[1, 1:]
rhs = np.column_stack((Tvr.T, sv))  # (311,3)
```

The first and last unused band entries remain zero. `Tvr` is stored (2,311),
but its block in the full matrix is `Tvr.T` of shape (311,2). Therefore
`Z=V^-1 Tvr.T` is (311,2), `w=V^-1 sv` is (311,), and
`K=Trr-Trv@Z`, `b=sr-Trv@w` are (2,2) and (2,).
The direct Lyα native owner modifies only real index 1. All virtual bands,
Trv, Tvr, and sv remain fixed in this unit.

## Frozen source-variable derivative

For an exclusive affine replacement `h*=a*xr[1]-b*`,
`F*=M_off@z-s_off+e*h*`.
At fixed `M_off,s_off`, the source-variable JVP is
`M_off@v + e*(a*v[1] + da*xr[1] - db*)`.
If controls are `(C,d)` with `a=r*C`, `b*=3*x*r*C*d`,
then `da=r*dC` and `db*=3*x*r*(d*dC+C*dd)`.
This is the boundary/source-variable derivative; it is not the derivative of
all native temperature, population, opacity and history coefficients.

Original diagnostic CSV bytes, source decimals and source coefficient
`LYA_FACT=4.662899067555897e15` remain fixed. Original files are not edited.
