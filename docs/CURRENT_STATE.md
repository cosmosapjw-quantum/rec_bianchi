# Current scientific state

## Summary

The durable endpoint is **PR-04B1 / v0.52**. PR-01 through PR-03 are complete. PR-04A supplied the positive 17-cell physical common measure. PR-04B1 now byte-locks and audits the owner-supplied original-HyRec October-2012 candidate archive, compiles and executes the unmodified source bytes under GNU C, and closes exact native diffusion/full-matrix/Schur parity. PR-04 remains open because the native virtual-level proxy has not yet been mapped onto the physical finite-volume photon measure along a full FLRW trajectory.

## Input and provenance lock

The durable input is:

```text
archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip
size:   726954 bytes
SHA256: 48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27
entries: 29 (26 files, 3 directories)
```

ZIP integrity, path safety, duplicate-name and symlink gates pass. Internal source headers say May 2012 while ZIP metadata for `history.c` and `Makefile` is dated 2012-10-05. The owner-supplied bytes are therefore locked as an official-release candidate corresponding to the October-2012 distribution, but independent equality with a fresh official-server download is not claimed.

The shipped Makefile selects Intel `icc`, which was unavailable. The same source bytes compile under GNU C without edits. The portable baseline exits normally and emits 8001 history rows.

## Native-variable census

Original HyRec uses cgs lengths and eV temperatures/energies. Its local virtual radiation coordinate is a dimensionless population proxy

```text
x_b = x_1s f_nu_b
```

or the corresponding nonthermal departure. Native `T`/`Aup`/`Adn` coefficients have dimensions `s^-1`; the time relation is `d/dt = H d/d ln a`. In FULL mode there are two real states `(2s,2p)` and 311 virtual states. The Ly-alpha diffusion subblock occupies virtual indices 100 through 179, i.e. 80 resolved virtual bins, with an unresolved 2p line-centre state.

The project adapter continues to use ordinary frequency `nu` in Hz,

```text
Delta nu = nu_target - nu_source,
Delta E_gamma = h Delta nu,
Delta E_H = -h Delta nu,
```

with `c`, `h`, and `k_B` explicit.

## Closed in PR-04B1

- exact C/Python reconstruction of original `populate_Diffusion`;
- original C 313-state real/virtual matrix and solution dump;
- dense direct solve and structured Schur solve parity;
- 81-state reversible native proxy network (80 diffusion bins plus unresolved 2p);
- native moment exchange parity through order four;
- steady 2p Schur elimination with positive red/blue bridge rates;
- analytic JVP and conservative positive backward-Euler proxy update;
- explicit firewall showing that raw native rates do not conserve the inferred physical photon finite-volume measure.

Key residuals are:

| Gate | Result |
|---|---:|
| C/Python diffusion-rate relative residual | `1.216e-16` |
| Original C vs pinned C3B1 maximum residual | `4.335e-11` |
| Direct matrix residual | `9.992e-14` |
| Original C vs direct solution | `1.034e-14` |
| Schur vs direct solution | `2.286e-15` |
| Native column residual | `1.390e-16` |
| Native equilibrium residual | `1.063e-15` |
| Maximum native moment exchange-parity residual | `2.432e-15` |
| Schur column residual | `1.217e-16` |
| Schur equilibrium residual | `7.581e-16` |
| Analytic JVP residual | `9.951e-17` |
| Implicit minimum proxy state | `3.593e-18` |
| Implicit proxy-number relative change | `0` |
| Direct physical-number-map residual | `5.243e-3` |

The last quantity is an intentional **failure of the forbidden identification**, not a failed PR-04B1 gate: native proxy conservation has left measure one, whereas physical photon cells carry frequency-dependent mode weights. It proves that direct `Aup/Adn -> physical finite-volume generator` substitution is not legitimate.

## Explicit scope boundary

PR-04B1 does not close physical common-measure parity, a full FLRW recombination snapshot, or the PR-04 production interface. It does not fit a scale to make native and direct COM–KHW moments agree. The full scalar release still excludes Raman production, fine structure, J-state interference, polarization and atomic alignment.

Wolfram and Precise Special Functions were not exposed in this runtime. The independent checks used original C execution, NumPy dense/Schur linear algebra and central-difference JVP regression; no unavailable plugin is claimed to have run.

## Immediate next stage

**PR-04B2 physical native-measure and full-trajectory FLRW closure** must:

1. instrument a source-identical original-HyRec trajectory at a locked hydrogen-recombination redshift;
2. dump the native radiation proxy, diffusion/escape coefficients, real/virtual blocks and local thermodynamic state;
3. derive the physical `photons per H per d ln nu` redshift-flux and escape map with explicit dimensions and signs;
4. compare direct v0.51 COM–KHW, native primitive and Schur-reduced actions on one physical measure without free normalization;
5. close normalization, detailed balance, photon-plus-atom recoil energy, analytic/JVP, positivity and one FLRW snapshot parity gate.

## Remote synchronization

The owner performs GitHub synchronization locally. This runtime provides a full Git bundle and binary-safe incremental/cumulative patches but does not claim a remote push or PR.
