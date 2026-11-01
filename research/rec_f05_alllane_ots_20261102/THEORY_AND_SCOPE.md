# REC-F05 source-owned all-lane accepted predecessor and kinetic–chemical–OTS source

Date 2026-11-02, original user objective: REI Bianchi IGM scientific progress, not speedups or surrogate optical sky.

## R1–R4: owner, source, research question

Immutable REC owner predecessor: PR #195, HEAD `0f1f6dbd33a654a3dd49bc2d9dbe8854b572d235` (PRIMARY original 0→64→128→160 exact states).
Original REI scientific source owner: PR #365, HEAD `fab9429140038974a98f3ad3212036b0227e600e` (all three original [0,64] lanes).
Original F05 26-event source TAR `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`;
unchanged original map `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`;
original acceptance local criterion `2e-4`, width `2e-3`.
One original physical realization, three shape-audit lanes. Original official F05 tick160/131072, tick161 unaccepted.

Task: (i) close remaining two original-lane [64,128] and [128,160] historical SHA predecessor links *without original REI source/worker modification*; (ii) extract true original 26-event source-stage and final event `H/He` chemical, OTS and photon-to-thermal source terms, grounded in 46,080 native cells and accepted parent clocks; (iii) discriminate binding/heat energy from the previously observed finite accepted energy secants. Avoid recasting the same three shape lanes as three independent cosmologies or inventing observed sky.

Primary physical context: Pawlik & Schaye (2011), *Multi-frequency, thermally coupled radiative transfer with TRAPHIC: Method and tests*, DOI:10.1111/j.1365-2966.2010.18032.x. The specific source kernel and conventions are determined by the byte-locked original REI 26-event code, not a public reference donor.

## R5: microscopic source derivation and thermal identity

Species order `X=(N_HI,N_HII,N_HeI,N_HeII,N_HeIII)`. Electric charge numbers `q=(0,1,0,1,2)`; ionization reservoir weights in eV:
`b=(0,chi_H,0,chi_HeI,chi_HeI+chi_HeII)`, with source-approved chi_H=13.598434599702 eV, chi_HeI=24.587389011 eV, chi_HeII=54.41776 eV.

The original event flux is `F_{destination,source} [events/s]`, with positive rates.
At any ORIGINAL source event evaluation time, exact finite-dimensional stoichiometry gives

    dot Ne = Sum_{d,s}(q_d-q_s) F_{d,s}                   [electrons/s]
    dot B  = (eV in erg) Sum_{d,s}(b_d-b_s) F_{d,s}   [erg/s].

For intra-H and intra-He transitions separately, conserved nuclear inventories have identically zero source derivative. Wolfram exact sparse 6-edge example checked that the two equations reduce to the expected H/He ionization contributions (two symbolic residuals {0,0}). This is an algebraic identity, not an original map error certificate.

Original F05 OTS source's local `EventBox` separately reports
`E_OTSresolved, E_OTSescape, E_OTSchemical, E_OTSunresolved` with its own defining ledger

    E_OTSresolved + E_OTSescape + E_OTSchemical
      + E_OTSunresolved = 0                              [erg/s].

The chemically stored binding derivative `dot B` from *all 26 event channels* is NOT the same variable as the OTS-only `E_OTSchemical`. The net primary `photo_heat = primary_heat + E_OTSresolved`; never add E_OTSresolved a second time. Source external 4-group ionizing photons and optional isotropic-CMB bath of REC #194 are disjoint.

For each original endpoint state with temperature `T` and exact source nucleus totals,
`U=(3/2)k_B(N_H+N_He+Ne)T`. Its correct derivative is

    dot U = (3/2) k_B (N_H+N_He+Ne) dot T
          + (3/2) k_B T dot Ne.                         [erg/s]

The original `thermal_root` solves `ecoef*T - U0 - dt*(const + weight*thermal_rhs) = 0`, with `ecoef=(3/2)k_B*Npart`. **Thus `thermal_rhs=Pheat-Cool-Pexpansion` already denotes the full translational energy source `dot U` in this original solver.** The composition work `C=(3/2)k_B*T*dot Ne` belongs within the decomposition `dot U_T=thermal_rhs-C`; **adding C to thermal_rhs would double count** and is rejected by inspection of the original root equation. These are instantaneous source-equation identities, not a new integrated IVP error theorem.

Every source field comes as [lower,upper]. For a signed linear coefficient c, use [c Flo,c Fhi] if c≥0 and [c Fhi,c Flo] otherwise. For sums, add interval endpoints. Nonlinear products must use four-corner interval arithmetic, not naive lower×lower for signed factors. Implemented f64 intervals inherit original model's source enclosure but aggregate roundoff is not claimed to be formal MPFR-outward proof.

## R6–R7: falsifiable checks

Use all three source-native byte-locked tick64 parent REIADP1 states from REI #365, and full/half1/half2 `run_step` on original [64,128] and [128,160] in two missing audit lanes. No new original ionization IVP beyond **replay of historically accepted ranges**; no REI source, main or history mutation.

Replay candidate tick128 and tick160 REIADP1 files must match *each lane's own historical receipt SHA256*, with original 14/14 ledgers including 0 and local/width gates unchanged. Same physical floating-body numerical identity across lanes is required. Extract original event-box flux, heat, OTS chemical/unresolved/escape at *actual solver-internal stage and final evaluation sites*. Verify all-row charge/energy stoichiometry independently and no double-count OTS. Source time t must be derived from original forcing and accepted tick clock.

Test both directional electron source and chemical reservoir source rates against charged species coefficients, chemical/OTS sign, f64 source closure scaled to actual energy inventory, zero H/He nuclei derivative. For an endpoint source-gas equation, report thermal RHS and particle-number correction separately; DO NOT call stage-derived rates the exact integrated [0,64]/[64,128]/[128,160] secular rates. Preserve historical failed [160,161] V1 logT, even if previous endpoint and new stage rates pass.

## R8–R10: admission and next science

If exact historical byte-state and source-stoichiometry checks pass, admit a NEW REC source-conditional *event-level physics record* plus one all-lane historical predecessor witness, not three cosmological histories, not direct CMB/LoS tau. If exact gate fails, preserve source material and precise failure; do not widen thresholds. After this source-connected unit, stop and return to owner versioned [160,161] decision and source/clock-matched photon geometry.

DAG on selection and every phase: REI canonical **28/88**, working **33/88**, Physical Fast **4/7**, REC H5 physical **0/313**. All deltas 0 unless the original REI scientific owner actually admits a new canonical node. Source owner REI read-only, REC only additive branch; NO_MERGE/NO_FORCE_PUSH/NO_OWNER_SWAP/NO_TOLERANCE_RELAXATION/AUTO_NEXT=false. Native subagent NOT_RUN (no advertised host delegation); same-context hostile referee required once, different-author reviewer NOT_RUN.

Pragmatic scope: ONE genuinely new event-level source physics outcome and exact lane-bridge, rather than twenty empty checklists. Theory checkpoint then actual code/data/test checkpoint then source-inclusive cold backup and remote Draft PR readback; each phase reports REI 28/88 and REC H5 0/313.
