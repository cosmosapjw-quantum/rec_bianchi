# REC-HD-26CHANNEL-CYCLE-SPACE01 | Exact source-obstruction cycle rank

## Scope / primary and inherited sources

A source-locked, *conditional* graph result for the original **neutral 1H2H HD** nine J-labelled levels and 26 marked transitions of pinned **LAMDA 2021-06-07** (`SHA256 0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`, 2,289 bytes). Radiative 8, p-H2 collisions 9, o-H2 collisions 9; p/o-H2 remain **separate channels**. Original source has 9 J labels and an unspecified vibrational assignment; no source correction, new rate, molecular network or real thermo-chemical evolution is implemented.

The original HD adapter's 35 Hz printed energy-frequency compatibility gate remains **7 FAIL / 1 PASS** (J=2..8 fail); original December 2011 CDMS version 2 catalogue/fit bytes are missing. Prior REC #150 24-Kirchhoff source diagnostics and #151 26-channel six 9×9 synthetic stationary results are treated as immutable source evidence; we **do not** rerun either prior campaign or solve any new stationary or time evolution.

## Theorem: complete graph cycle obstruction for the declared two-energy model

Fix orientation for every marked edge `e=(i,j)` with `i<j` (from lower J to upper J). Let the 9×26 integral incidence matrix be `B_ve = +1` for the destination upper `j`, `−1` for the lower `i`, and zero otherwise. The 8 nearest-neighbour p-H2 collision channels furnish a spanning tree, and the remaining 18 marked edges are chords. For each chord `e=(i,j)`, the fundamental cycle has coefficient `+1` on `e` and `−1` on every p-H2 chain edge `(k−1,k)` for `k=i+1,…,j`. This defines the explicit integral matrix `C∈Z^(26×18)` satisfying `B C=0`.

Because the nine-state marked multigraph is connected, `rank(B)=9−1=8`. The chord columns of `C` are linearly independent as each carries a unique non-tree pivot; hence `rank(C)=26−8=18`. This counts **independent marked cycles** and is not a count of physically distinct HD molecules or collisional channels.

At positive common temperature `T`, retain source energies `E_i=hc100 w_i` (w in cm⁻¹) and photon energies `ε_j=h 10^9 ν_j` for the 8 adjacent radiative transitions (ν in GHz). Fix `β=(k_B T)^−1`. For each marked channel, write upward and downward source-defined positive rates `k^+_e,k^-_e` and degeneracies `g_i=2i+1`. Define its *degeneracy-reduced affinity cochain*

`u_e = ln(k^+_e/k^-_e) − ln(g_j/g_i)`.

For each p/o-H2 collision `u_e=−β(E_j−E_i)`. For each radiative adjacent channel `u_e=−βε_j`. Let `φ_i=−βE_i`, and define the *fixed-source mismatch vector* `a_j=β[(E_j−E_(j−1))−ε_j]`. Define `D∈Z^(26×8)` with `D_(photon_j,j)=1` and zero elsewhere. Then **exactly**

`u = B^T φ + D a`, `C^T u = (C^T D) a`.

The 18×8 map `M=C^T D` for the p-H2 spanning tree is `M = [I_8 ; 0_(10×8)]`. Thus `rank(M)=8` and the **source-defect-independent null subspace** of the 18-cycle space has dimension `18−8=10`. More invariantly, the restriction of the photon-coordinate projection to `ker(B)` has rank eight and a ten-dimensional kernel. Other spanning trees (including the radiative chain) give cycle coordinates in which every basis vector can carry nonzero affinity for the particular pinned mismatch, but **rank 8 / universal null dimension 10 remain invariant**. The wording '10 zero cycles' always means ten-dimensional subspace with zero affinity for *every possible* source-mismatch vector, not that ten arbitrarily selected physical loops independently vanish.

In the orientation chosen here `a_j = −A_j` where `A_j` was PR #151's pair-loop affinity (photon downward, collision upward); the 0→1 photon up, 1→2 photon up, 2→0 collision down triangle carries `a_1+a_2`. Sign is fixed by the incidence convention; no photon source energy is moved into collision rates. Both collisions are conditionally Maxwellian at **exact T=50,100,200 K only**; partner density drops out of affinities, but not of currents/entropy, which are *not* recomputed here.

A common zero-energy offset changes no energy gap. A redefinition of `φ` by a constant changes neither `B^Tφ` nor `C^T u`. This is gauge invariance in the **energy-origin** sense only, not an Einstein–Boltzmann gravitational gauge assertion.

## Verification and scientific meaning

Wolfram exact integer check on a 9×26 source-shaped graph returned `{rank B, rank C, rank(C^T D), ||BC||∞} = {8,18,8,0}`. The locally executed SymPy integer matrix and an independently built `networkx.MultiGraph` with a **different (radiative) spanning tree** reverified rank and basis-span invariance. Direct source-locked 100-digit mpmath logarithms from positive actual collision and radiation rates at T={50,100,200} and n_p=n_o={1e3,1e6} cm⁻³ give `C^T u = M a` with maximum numerical error `1.56e−100`, and cochain decomposition maximum `4.57e−100`. Saved PR #151 affinity comparison maximum `3.46336e−61` reflects reuse of its finite printed result strings. All 13 targeted regression tests PASS. Failed first attempts due to input degeneracy parsing (`1.0`), JSON SymPy integer serialization and a *reviewer mistaken count* of photon-tree nonzero chords are preserved in raw logs; only changes to parsing/serialization/count were made, never to physics or tolerances.

**Scope gate:** This is a *finite marked-graph / common-T synthetic source consistency* result. The exact integer ranks are not a novel general graph theorem, no independently measured HD spectroscopy is inferred, and the original CDMS 2011 version2 files `.cat/.egy/.par/.fit` and source-to-LAMDA conversion recipe remain unacquired. The archive directory index at `https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/` was located, but neither `Exa`, `Parallel Search`, Web nor current runtime obtained the raw bytes; the catalog filename `c003501.cat` has index mtime **2019-02-25**, which forbids equating its directory placement with exact original 2011 file identity. Do not import the August 2026 CDMS version3 fit into version2. The archive index is a new **source locator**, not a corrected physical rate, spectroscopic uncertainty, temperature interpolation, collisional cross section, full H5 residual, production solver or a physical entropy production certificate.

## Source literature, scoped

- Original primary LAMDA HD data and metadata: https://home.strw.leidenuniv.nl/~moldata/HD.html
- Original CDMS version2 archive listing: https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/
- CDMS catalog format and measured-vs-predicted tag: https://cdms.astro.uni-koeln.de/classic/predictions/description.html
- J. Schnakenberg (1976), Rev. Mod. Phys. 48, 571, DOI 10.1103/RevModPhys.48.571, background on graph-cycle affinities. No novelty claim for graph rank-nullity.
- REC scoped PR #150 and #151 for source identities and saved numerical model; owner contracts and source-specific statements take precedence over generic literature.
