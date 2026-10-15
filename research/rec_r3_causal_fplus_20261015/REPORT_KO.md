# REC R3: original HyRec FULL causal incoming photon-history and prescribed Bianchi I

2026-10-15 KST. Theory R3, coding C5–C8: source mapping, independent native-C parity, direction-dependent transport, vectorization and memory optimization. **This is not an independent FULL HyRec ionization history.**

## 1. Authority and isolation

Parent commit 130775798c97c3af9baa4098f6b293f1f402b451 (PR #91 H-only q=0 EMLA2s2p + Tm). New isolated worktree /home/cosmosapjw/rec_theory_runs/REC_R3_CAUSAL_20261015/checkout. Source: archived original October-2012 HyRec ZIP SHA256 48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27. Original hydrogen.c lines 633–651 (interp_Dfnu), 667–718 (fplus_from_fminus), 735–799 (algebraic atomic/virtual solve, outgoing memory writeback), hyrec_params.h (DLNA=8.49e-5, NSUBLYA=140, NSUBLYB=271, NVIRT=311). Exact 311 energy bins read from original two_photon_tables.dat; no synthetic energy table in the native parity receipts.

Existing dirty REC checkout, REI owner producer/state/AX08, and independent local Codex processes were not modified or invoked. No native subagents were available.

## 2. Source-defined history model

The original C function fplus_from_fminus reads 311 earlier accepted virtual outgoing histories and 3 Lyman outgoing histories, and produces 311 virtual + 2 incoming Lyman boundary values. Virtual and real atomic departures are algebraic quasi-steady variables in original solve_real_virt, not 311 additional differential ODE variables. The causal radiation memory is committed outgoing accepted-step history. Original C interpolates across exactly the nearest two earlier samples. q=0 assumes zero spectral distortion before the history start; q≠0 must not silently inherit this isotropic early-time radiation condition.

The implemented module computes incoming photon **source transport only**. No original populateTS_2photon matrix, solve_real_virt coupling, final Dfminus writeback, FULL integrated ionization, He dynamics, Thomson/polarization collisions, or reionization source is claimed.

## 3. Exact prescribed axisymmetric Bianchi I kinematics (derived)

Metric signature (-,+,+,+) and coordinate proper time t:

\[
ds^2=-c^2dt^2+a(t)^2[e^{-2b(t)}(dx^2+dy^2)+e^{4b(t)}dz^2].
\]

Translation Killing momenta p_i are conserved on photon geodesics. With eta=ln(a), source time eta_s, face eta_f, d=eta_f-eta_s>0, constant prescribed q=db/deta, and face polar cosine mu_f,

\[
B=b_s-b_f=-qd,\quad
R^2=e^{-2qd}(1-\mu_f^2)+e^{4qd}\mu_f^2,
\]
\[
\ln(E_s/E_f)=d+\ln R,\qquad
\mu_s=\mu_f e^{2qd}/R.
\]

Each original-C specified upstream virtual/line source energy E_src and face target E_target defines a retarded emission time by

\[
d+\ln R(d,\mu_f,q)=\ln(E_{\rm src}/E_{\rm target}).
\]

Physical directional expansion is H_perp/H=1-q and H_parallel/H=1+2q. The root is unique for all directions when -1/2<q<1, because its derivative lies between min(1-q,1+2q) and max(1-q,1+2q). Vector safeguarded Newton + bisection implements this inversion; emission direction is then obtained analytically. This is a prescribed constant-q background, NOT an Einstein–matter backreaction solution.

### Anisotropic causal history gate

The actual source energy grid gives

\[
\ell_{\min}=\min_k\ln(E_{{\rm src},k}/E_{{\rm target},k})
 =8.49527887747085\times10^{-5}.
\]

The original q=0 DLNA=8.49e-5 is just below this. Under nonzero q, the received frequency may have been emitted less than one accepted step earlier, requiring an uncommitted history read. A *sufficient*, not necessary, step rule is

\[
\Delta\eta_{\rm step}<\ell_{\min}/\max(1-q,1+2q).
\]

New safe_constant_shear_dlna uses the native upper bound and safety factor 0.975. At q=.018 it returns 7.995074233141002e-5 (94.17% of original step) and q=.03 gives 7.814053684466111e-5 (92.04%). Tests confirm native q=0 step fails for some q=.03 directional rays, while causal safe step is admitted. If the retarded time predates the source-owned history, nonzero-q input is rejected pending physically specified incoming boundary data. **This is not a proof of the FULL coupled atomic/thermal solver's stability.**

### Reference Planck anisotropy (derived and numerically checked)

Collisionless occupation f is conserved, but Delta f=f-n_P(x) is not invariant with respect to a newly chosen isotropic reference T_r proportional to a^-1. Therefore

\[
\Delta f_f=\Delta f_s(\eta_s,E_s,\mu_s)
+n_P(x_fR)-n_P(x_f), \quad x_f=E_f/(k_B T_r).
\]

To first order in |qd|,

\[
\Delta f_{\rm geom}=-qd(3\mu^2-1)\frac{x e^x}{(e^x-1)^2}
+O(q^2d^2).
\]

Thus the first-order angular monopole vanishes; quadrupole is O(q) and monopole correction is O(q^2). Independent 96-node Gauss–Legendre tests show these scaling laws; previously established independent REC C10 Killing phase-volume map agrees at q positive/negative. The spectral distortion itself may be negative without violating absolute occupation positivity. Wolfram evaluator verified the derivative identities, exact q=0 limit, and first-order Planck formula with zero symbolic residual.

## 4. Code and verification (implementation-verified, scoped)

- src/full_bianchi_hyrec/trajectory/causal_virtual_redshift.py: authoritative native bin map, causal time/angle, prescribed q root, safe history step, Planck correction, readonly results.
- scripts/c_harness/original_hyrec_causal_fplus_harness.c: C adapter calling unmodified original hydrogen.c.
- scripts/verify_causal_fplus_native.py: independently extract raw original ZIP and compile GCC source in a temporary dir, C-contiguous data passed to ctypes.
- tests/trajectory/test_causal_virtual_redshift.py: C parity, exact Killing ray-map, independent prior C10 phase map, signed q, manufactured source, geometric moments, malformed source, unaccepted future, undefined early-time Bianchi history.
- research/rec_r3_causal_fplus_20261015/NATIVE_C_PARITY.json: iz=2,40,200,640, 4×313=1252 comparisons, max scaled relative residual 6.828510269357105e-14, max absolute 1.5670109524204556e-20, acceptance gate 2e-11. This validates ONLY q=0 C incoming operator, not native FULL trajectory nor nonzero-q native C physics.

## 5. Measured vectorization/memory/parallel benchmarks

Benchmark input: 311 native energies, 640 accepted-history steps, 17 source angle nodes, constant q=.018 and valid causal step, NumPy binary64, Ubuntu host with REI still active. Median repeated source-only calls, no whole-solver claim.

| Face rays | Before direct-gather (ms) | After direct-gather (ms) | Speedup | After, one-ray-by-one-ray (ms) |
| ---: | ---: | ---: | ---: | ---: |
| 16 | 7.947 | 2.270 | 3.50× | 26.624 |
| 64 | 7.702 | 3.837 | 2.01× | 115.947 |
| 128 | 12.197 | 6.424 | 1.90× | 300.761 |

Previously concatenating two owner history blocks created and copied 27,330,560 bytes at each call. The new direct gather does not allocate that copy and obtains mathematically identical ray output (max absolute difference zero in scalar-versus-vector tests). The 128-ray new vector vs repeated scalar speedup is 46.82×, *not whole ODE acceleration*. ThreadPool with 2 and 4 threads cost 9.021 and 11.531 ms on the 128-ray input, slower than single vector 6.424 ms; retain single-worker default. Repeated wall measurements reflect concurrent load and are not hardware-portable performance guarantees. See BENCHMARK.json.

## 6. Decision and next physical step

SCOPED_PASS: native source incoming history owner q=0, exact code/source pair, causal guard, associated regression tests. DERIVED_NUMERICALLY_CHECKED: prescribed constant-q Killing/Planck correction and sufficient causal step. NOT_ADMITTED: full native source radiation/atom energy-number coupling, helium species, actual independent REC FULL xe(z), Tm(z), q!=0 backreacting recombination solution, native REI signed-q outputs, CMB observable prediction.

Next R3b: independently rebuild original populateTS_2photon rates/matrix and solve_real_virt with source-C pointwise parity (zero-width virtual states remain algebraic); then original atomic current and Dfminus writeback on a single accepted history owner, native FULL q0 integrated trajectory against reference original C xe and Tm. Only afterwards couple He (source-native electron thermal budgets) and promote to Bianchi nonzero q with explicit prehistory/angle-dependent collision model. Original q0 EMLA vs FULL 1.43% physics-model discrepancy remains unchanged in this R3 stage.

Reference: Y. Ali-Haïmoud and C. M. Hirata, *Phys. Rev. D* 83, 043513 (2011), https://arxiv.org/abs/1011.3758 ; original HyRec 2012 ZIP checksum above. No FULL SCIENCE claim has been promoted.


## 7. Final execution gates and cross-project reuse

Actual final targeted native-C-including test: **13 passed**, exit 0. Full REC Python: **462 passed, 39 slow skipped** (49.64 s), exit 0. Syntax compileall exit 0. Repository quick gate exit 0 but retained the explicit dynamic-atomic ownership no-go scope; this is not FULL physics admission.

Current other-repository checks: BASS_HE PR #64 has source-scoped 16/16 warm saved cells; bass_cr PR #71 has adaptive q-grid positive source-envelope refinement; WU088_HH PR #80 has screened two-centre envelope certificates; rei_bianchi owner checkout HEAD 0fcb2dddf5de6b583c2e00f150abff0b2afb6315 remained active with separate source-age/clock research. We reused the REC C10 exact ray phase-volume result as an **actual cross-module scientific regression**, and source-ownership/non-invented-state principles where transferable. Warm REI/BASS photon physics and WU088 spectator Hamiltonian were **not** substituted into primordial HyRec2012. Exact evidence/transfer exclusions are in CROSS_REPO_20261015.json.

Original/source and native-C comparisons are fully reproducible via commands in TEST_RECEIPT.json, with native C and benchmark numerical receipts in this directory. Remaining closure obligations are machine-readable in NEXT_LOOP.json.
