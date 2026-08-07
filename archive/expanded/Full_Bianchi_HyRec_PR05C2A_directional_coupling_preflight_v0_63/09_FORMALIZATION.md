# PR-05C2A directional coupling formalism

The COM finite-volume number action uses upwind face flux

```text
F_{k+1/2,a} = v_{k+1/2,a} g_{x,k+1/2} f_upwind
Ndot_{k,a} = F_{k-1/2,a} - F_{k+1/2,a}.
```

The native ledger is the exact negative of the summed COM action.  Exact interface energy uses `h nu_face`; cell-centroid mismatch and internal frequency drift are separate representation/redshift-work ledgers.  Pure representation crossing has zero atom source.

The v0.48 chart variable satisfies `d/dt = H d/dtau` while `d eta/dt = H`, so `tau` and `eta=ln(a)` differ only by an additive anchor.  Local source-H rescaling multiplies all physical geometric rates by the same positive factor and preserves every Hubble-normalized tensor.

The locked native history has angular rank one, while the COM boundary has one value per quadrature direction. Moreover the COM state is a finite-volume cell average and the archive provides no face reconstruction. The P0 upwind face trace used for the bounded pilot is therefore a new explicit closure, not a source-identical full coupling.

The v0.50 COM mode measure is frozen to the reference 3000 K Doppler grid. Re-evaluating the same dimensionless cells at the source temperatures changes the physical mode measure by up to about 9.5 percent. The bounded pilot therefore retains the frozen v0.50 measure and records the missing thermodynamic grid/kernel adapter as a blocker.

The ell=0 collision Jacobian has spectral radius about `0.655 s^-1`; a canonical macro interval lasts `DLNA/H ~ 1e9 s`, giving stiffness number above `8e8`.  A harmonic-block or equivalent preconditioner/asymptotic-preserving reduction is required before a production macro trajectory can be claimed.
