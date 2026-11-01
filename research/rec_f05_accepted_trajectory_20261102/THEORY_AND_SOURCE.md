# REC original F05 accepted 0→64→128→160 source-physical trajectory

Date 2026-11-02 KST. Exact selected research unit:
recover the two historical **already accepted** intermediate source states
(tick64, tick128) in the original 46,080-cell 26-event H/He/thermal
MPRK22(1)+Alexander SDIRK2 model, using unchanged original owner source,
and deliver cellwise *real* electron, Thomson, binding-energy and
translational thermal energy histories for the 0,64,128,160 accepted
endpoints. This does not request a new F05 tick161 candidate.

## Authority and existing evidence

- Source owner: REI #363 HEAD
  \`abf83d4d883d5f311426b7f02cb001e70138ceb4\`. It replays tick0→64
  and finds byte-exact original state \`aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425\`.
- Consumer immutable parent: REC #194 HEAD
  \`b1f3dd6516539fc6b98a131528f42d8076b41fa3\`.
- Original REI archived 26-event source TAR SHA256
  \`a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b\`.
- Original 26-event map SHA256
  \`579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644\`;
  original policy SHA256
  \`c648c0ae1e10bced3b159e96f92bdc5f2bd3c1031b9a13e6b947dbf102557aa9\`.
- Historical REC accepted160 consumer includes source initial NPZ SHA256
  \`7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d\`.
- Historical attempt receipt: index1 [0,64] ACCEPT,
  index2 [64,128] ACCEPT, index3 [128,192] REJECTED,
  **index4 [128,160] ACCEPT**. The mapping from attempt to accepted
  index is not interchangeable.
- Frozen intermediate tick128 PRIMARY state SHA256
  \`bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6\`.
  Terminal tick160 PRIMARY state SHA256
  \`74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6\`.

All source tree inputs are read-only and source hashes are exact BYTE_IDENTITY.
A replay-produced .state is a private computational witness, not a new
REI official accepted job or production state.

## Physical derivation and numerical contract

Metric (-,+,+,+), original source proper clock in seconds. A cell j has
conserved nuclei \`N_H,j = N_HI+N_HII\`,
\`N_He,j = N_HeI+N_HeII+N_HeIII\`, free electrons

    Ne,j = N_HII,j + N_HeII,j + 2 N_HeIII,j.

The original source defines fixed first-interval redshift z=5.95,
positive original comoving W_j and proper source volume

    V_j = W_j (Mpc in cm)^3 / (1+5.95)^3.

At each actual accepted endpoint t_k, define, in cgs,

    Gamma_T,j = c sigma_T Ne,j / V_j,                   [s^-1]
    B_j = eV*(chi_H N_HII+chi_HeI N_HeII
             +(chi_HeI+chi_HeII) N_HeIII),               [erg]
    U_j = 3 k_B (N_H+N_He+Ne) T_j/2.                  [erg]

Use original \`chi_H=13.598434599702 eV\`,
\`chi_HeI=24.587389011 eV\`,
\`chi_HeII=54.41776 eV\`.
Only translational gas energy is in U; ionization binding is in B,
so the two are not double counted.

Original interval states provide lower and upper species/logT boxes.
Because all weights, chi, k_B, T and nucleus counts are positive,
componentwise substitution gives algebraic lower and upper
bounds for Ne, B, U, Gamma. For consecutive accepted endpoints
with values \`A_k in [L_k,U_k]\`, a conservative outer difference is

    Delta A_(k,k+1) in [L_(k+1)-U_k, U_(k+1)-L_k].

This is a safe interval arithmetic *box* combination; it may be loose
because true correlations between endpoints are not retained. Binary64
evaluated sums are not certified MPFR outward-rounding intervals.
For electron gain/loss cells use only strict interval separation.

A finite secant \`Delta U/(Delta t)\` is NOT a bound on instantaneous
time derivative nor a source energy-equation audit. The local 14 ledger
checks concern the original numerical source kernel's own reactions.
No claim of full continuum or true Bianchi null transport.

## Source map implementation and acceptance tests

Call the actual unchanged original source map for [64,128] and
[128,160], with original left-parent REIADP1 boxes and original
source time normalization. For each, calculate one full source map,
two half maps, original public four-variable local-error differences,
original max width, 14 source ledgers, table events, and serialize with
the exact historical accepted receipt's metadata.

PASS conditions are *fixed original* local error < 2e-4, width < 2e-3,
all 14 ledgers include zero, zero table events, full/half1/half2
source-certified, and reconstructed state bytes match the original
historical SHA. Additionally compare actual tick160 reconstructed
bytes against source archived ORIGINAL PRIMARY state.

If these hold, compute the 46,080 × 4 original material endpoint
history plus 3 physical interval transitions. Compare first64
H/He/energy totals with REI #363 and terminal gamma with REC #193.
Classify errors as original-source, physics, implementation or runtime;
a fail must not be waived by changing tolerances. Record old
[160,161] historical logT FAIL separately (2.124505e-4 > 2e-4).

## Literature and physical interpretation

For non-equilibrium H/He photoionization and thermal coupling, see
Pawlik & Schaye, *Multi-frequency, thermally coupled radiative
transfer with TRAPHIC: Method and tests* (arXiv:1008.1071),
and Ali-Haïmoud & Hirata, *HyRec* (Phys Rev D 83, 043513 2011).
Neither paper establishes original REI source admission or exact
numerical gate for these particular discrete sources; the immutable
owner source/receipt is the authority for this reconstruction.

Scientific value is real source trajectory history for eventual
source-clock-matched Thomson/Sachs characteristic transport, not
another analytic proxy atlas or a claim of an observed CMB map.

DAG baseline REI canonical 28/88, working 33/88, Physical Fast 4/7,
REC H5 physical 0/313; numerical-science completion does not grant
central owner node. Production HOLD, no original REI worker edit,
no source-owner swap, no merge, no force-push, no tolerance change,
no automatic next tick.
