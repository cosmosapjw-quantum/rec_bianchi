# Bounded REC source intake after REFINE01

## Actual source cutoff and delta

One provider census on 2026-10-24 observed 151 branches in actual pages 100+51 and 133 all-state PRs in actual pages 100+33. Compared with the prior 150/132 census, the only new branch is `research/rec-history-refinement-envelope-delivery-20261024` at `c5394eccf6ff45f134e396c549844af91988aeb7`, and the only new PR is draft open #133 for completed REFINE01. Previously enumerated branch heads have zero changes and zero deletions. `metadata/DELTA.json`, raw full branch and PR pages, and `PR_METADATA_DELTA.json` retain the comparison. The recursive current tree has 6377 entries and `truncated=false`.

The actual root `AGENTS.md` at this REC commit returns 404; this is preserved in `metadata/agents.json`. The provided prior CENTRAL_AGENTS policy was read. No claim is made to have read every file on every branch. Unchanged branch identities reuse the prior census; new content is completed REFINE01. No new independent matching-target reference/endpoint/whole-cell curvature/stability/parameter-transfer uncertainty supplier was identified by this bounded delta, current-tree path scan, and all-state PR metadata scan. Existing h2 U4, h4 U4A/U4B, and h2 U5 data remain actual available candidates; this is not a claim of missing finer data.

## Restored original-target operator inputs

All paths below are preserved under `fetched/`, with original response/base64 under `responses/`. `FETCHED_IDENTITIES.json` records exact commit, repository path, Git blob, SHA256, and byte count; reconstructed Git identities match for every restored payload.

| Input | Repository path | Git blob | SHA256 |
|---|---|---|---|
| Native snapshot, 141089 bytes | research/rec_history_characteristic_resume_20261024/inputs/target_native_snapshot.csv | 6399b59ca3c97d6c5b1162f83f50a6677fad06ff | 3a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7 |
| Prepared blocks, 32453 bytes | research/rec_line_native_owner_20261023/results/attempt001/PREPARED_BLOCKS.npz | e96d15dfc0432429f2fcb680159f4820c02ce591 | 014ce6c467639b28086cfc1d6a70a09818544896b5d21e88508523bec111b9de |
| H01 frozen map | research/rec_history_boundary_20261023/code/history_boundary.py | 1aa7f134c332bc4596372df18c7c47306260ecfc | see manifest |
| Native hydrogen source, 37471 bytes | research/rec_line_native_owner_20261023/vendor/hydrogen.c | 2df4561f1b1ef80991ca3b7645666a630eea19b7 | 421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b |

NPZ header inspection only (`PREPARED_BLOCKS_HEADER.json`) gives M[313,313], source[313], W[311,2], u[311], K[2,2], j[2], X0[313], w[313], all binary64. Existing K is a 2x2 Schur block, not the proposed 314x313 response.

Snapshot META values: z=1099.9986525171403, xe=xHII=0.1449299966903522, x1s=0.85507000330964777, nH_cm3=250.18675437302318, H_sInv=4.9696512229238343e-14, TM_eV_rescaled=0.25882127610727856, TR_eV_rescaled=0.25882399309326415, fsR=meR=1. This is the original T0=2.728/nH0=0.18745798773143102 target, not candidate T0=2.7255/nH0=0.18971712352134673.

## Existing work and proposed response scope

H01 `FrozenHistoryMap` lines218–326 already exposes Mstar, source_increment, source_at, outgoing, and outgoing_jvp. Its original-target frozen coefficients and source arithmetic can be reused. Source_increment is B times incoming313; outgoing is T times state313 plus P times incoming313. H01 run_history_checks.py lines305–406 already tested three manufactured dense RHS directions and a positive comparison witness with conditional envelopes for two RHS directions. Do not describe the next unit as the first comparison-envelope construction.

The current-tree response-name scan and all133PR metadata scan identified no published full 314x313 incoming-to-outgoing response. Existing `research/rec_line_native_owner_20261023/results/attempt001/AFFINE_RESPONSE.csv` (blob876156c0380e4d73254004c444cedff334c50c92) is a two-scalar r_ratio/b_ratio scan with aggregate virtual_response_inf, not that full operator. Therefore root can decide whether a bounded complete response plus validated stored-operator box envelope is a new executable unit. This intake does not compute or admit it.

## Exact313 retarded owners and outgoing314

Native hydrogen.c function fplus_from_fminus, lines667–718, and H01 native_links lines131–146 define the query owners. Incoming313 consists of virtual0..310, Ly-alpha at311, Ly-beta at312. Stored outgoing314 consists of virtual0..310, Ly-alpha311, Ly-beta312, Ly-gamma313. Most incoming virtual b uses outgoing virtual b+1; exceptions are incoming139<-outgoing311, incoming270<-outgoing312, incoming310<-outgoing313. Incoming311<-outgoing140 and incoming312<-outgoing271. The lowest outgoing virtual channel has no downstream incoming owner in this one-step mapping.

H01 incoming_history lines149–181 uses source-owned ainv=(1+z_face)*E_source/E_target, query=-log(ainv), the selected outgoing row, and actual committed prefix iz. Keep strict upper exclusion. The original target retarded source range remains z1100.092189396162...1133.87330719964,313queries. Source errors/endpoint uncertainty/curvature error sidecars must supply these incoming313 owners before a physical output allocation can be claimed. Manufactured errors and operator amplification alone do not supply physical uncertainty.

## Thermodynamic/source coefficient ownership, open scope

`src/full_bianchi_hyrec/trajectory/full_2012_atomic_source.py` (blobffeda51ddbde4d631088fd4787822e3a94e49785), populate_original_full_atomic(source:HMLAFlrwSource,*,z,xHII,xe,Tm_K,incoming_virtual[311],incoming_lyman[2]), already builds actual Trr/Trv/Tvr/Tvv,sr/sv,tau from the original rates, coupling and diffusion. complete_original_full_atomic solves the Schur system and returns real/virtual departures, all314 outgoing, and dxHII/dln_a. This file has no complete thermodynamic JVP.

`primitive_rates.py` (blob3ae7cda8c91456025a019f81ca13f638f717079b) already supplies PrimitiveRateSnapshot.derivative_log_Tr_vector_si and derivative_Tm_over_Tr_vector_si. `hyrec_two_photon_raman.py` (blob911a2cdc76c5812d32d7fe6f584f1b8d52dabcd0) supplies CanonicalTwoPhotonRamanCoupling.jvp for logTr/logfsR/logmeR. `original_hyrec_native.py` supplies populate_original_hyrec_diffusion and `original_hyrec_physical_flux.py` supplies parsing, source escape factors, equilibrium/outgoing and fixed-snapshot edge_flux_jvp. `HMLAFlrwSource` requires explicit cosmology fields, so original-target cosmology must be bound rather than silently borrowing the refined candidate constructor.

The full atomic builder sets x1s=1-xHII, uses source.cosmology(z) for H and nH, rate-table Tr and Tm/Tr derivatives, Tr-dependent Raman coupling, Tm-dependent diffusion, Ly-alpha rate proportional H/(nH*x1s), Gamma from coupling+diffusion, and tau proportional Gamma*x1s*nH/H. The retained native snapshot owns numeric values at the target; it does not by itself own derivatives of those coefficients. H01's local boundary_jvp already accepts incoming,xr_p,x1s,tau,q tangents with fixed reference; the frozen full matrix map does not constitute the full thermodynamic Jacobian. G_N/expansion/frame/geodesic/normalization derivative ownership remains outside the frozen response claim.

## Execution and claim boundary

This intake performed provider GETs, exact byte reconstruction/hashing, text reads, metadata comparison, and NPZ header inspection only. Scientific solve/primary replay/IVP/native/denseRHS/array-value comparison/provider mutation=0. One local NPZ header-reader API mismatch was corrected by using the public versioned header reader; no scientific execution occurred. Physical HOLD, REC_U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, global_convergence NOT_RUN, production NOT_APPROVED, REI_activation=false, parent REC-HISTORY PARTIAL and H5 INPUT_DEPENDENT_UNCALIBRATED remain unchanged. Root owns the next framing, frozen contract, budget and admission decision.
