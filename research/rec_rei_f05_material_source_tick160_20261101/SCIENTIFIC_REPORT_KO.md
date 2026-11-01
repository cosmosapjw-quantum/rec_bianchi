# REC→REI F05 tick160: original 26-event thermochemical material source bridge

2026-11-01. Scope: **source-authentic, non-IVP, not a new canonical completion**. This is REC-owned read-only consumption of REI-owned actual H/He source physics, not replacement of the REI 26-event MPRK22/SDIRK2 owner.

## Immutable evidence
- REI PR #320 parent HEAD `e5836fc4b8804d1bcdcdcbb97ab33f822703fa46`, authentic frozen original first interval, original blocked source tar SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`. The existing accepted state artifact #13064333012 has 46,080 original nodes, SHA256 `48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7` (12,591,114 bytes, local CRC PASS).
- REI PR #321 source HEAD `9afee1ab4a45a7b4b277e183e7e18c59a8d39f4d`, actual 26-event original source run #41266308694 SUCCESS, artifact #13066329719 SHA256 `b40a4fe081ab6d84ca5319548aeebf63988665940ef08804789392839aef6b9a` (30,687,257 bytes, local CRC PASS). Both artifacts downloaded and directly read. Per-lane decompressed source CSV bytes match exactly for the three original shape labels. **46,080 unique nodes**, 2 source times, no extra physical independent lane copies.
- The 46,080 source representatives at tick160 lie within the corresponding original accepted state intervals for HII, HeII, HeIII, T, electron fraction and thermal energy: 0 outliers.

## Theory and correct normalization
Signature (-,+,+,+). Keep c, ħ, k_B. Source uses y_He=N_He/N_H=.079, H and He ion fractions per their own nuclear totals, erg/H, s, K. NIST ionization energies in eV: (H,HeI,HeII)=(13.598434599702,24.587389011,54.4177655282); ε_eV=1.602176634e-12 erg/eV.
Write x_e=x_HII+y_He(x_HeII+2x_HeIII).
Ionization binding energy relative to neutral ground state:
E_ion=ε_eV {χ_H x_HII+y_He[χ_HeI(x_HeII+x_HeIII)+χ_HeII x_HeIII]}.
For original 26-event source-derived representative rate (g_H,g_2,g_3), P_ion=ε_eV[χ_H g_H+y_He(χ_HeI g_2+(χ_HeI+χ_HeII)g_3)].
For ideal monatomic material kinetic u_th=(3/2)k_B T(1+y_He+x_e), E_m=u_th+E_ion:
d ln T/dt=(P_m-P_ion)/u_th - (dx_e/dt)/(1+y_He+x_e).
The **P_m=0** chemical sensitivity isolates a physical component, **not the actual full OTS/Compton/expansion thermal RHS**.

## Newly computed physical data
- 46,080 new derived model rows, 21 physical columns, preserving original source nodal identity; original 92,160 source records reused, not rerun.
- Max original source rate charge identity residual |g_H+y_He(g_2+2g_3)-g_e| = **4.733165431326071e-30 s^-1**.
- tick160 median P_ion **-1.7428248493891418e-28 erg/H/s**, 91.080729% of original nodes negative. Median |P_ion|/P_photo (per-node ratios) **28.094454515689108**. This is not a heating-budget error: photon/escape/energy owners differ.
- True historical 0→160 accepted endpoints t=779495799866.9248 s: median (ΔE_m/Δt) **-1.196622899138019e-27 erg/H/s**; 46,080/46,080 representative endpoint secants negative.
- Two-endpoint 26-event rate trapezoid vs accepted electron-history secant: Pearson correlation **0.9956621285285064**, median |difference| **6.64884555512947e-21 s^-1**, maximum **1.8910059671622424e-15 s^-1**; no claim of an exact evolution/solver error.
- One old tick = 4,871,848,749.16828 s. Fixed-material-energy chemical first-order ΔlnT indicator median **1.997810423721486e-7**, p95 **1.42399868237341e-4**, maximum **4.642777727266952e-4**. **1,320/46,080** nodes exceed the numerical scale 2e-4 in this **indicator**. It is neither the original [160,161] full-vs-half error nor a new failure gate. Do not add to PR #324's different 252 parent-width scale cases.

## Execution / self-adversarial review
Python 17/17 normal, 17/17 -O; exact SHA/CRC for both original ZIPs; 3-lane source-byte identity; source-state bounds; deterministic clean replay 3/3; full 34-member source-inclusive ZIP, CRC PASS, 33/33 manifest SHA PASS and fresh restore 17/17. Initial finite-difference derivative test showed 3.27e-9 cancellation (limit 2e-9); fixed by using physically interior test points and a stable 1e-4 perturbation of the exactly affine map; original acceptance/tolerances unchanged.
**Main limitation:** original 26-event flux interval-midpoint fields do not encode a jointly correlated F_h and F_{h/2} map, so NO same-parent nonlinear Jacobian/remainder or F05 recovery is claimed. Original [160,161] logT error 2.1245050576368385e-4 exceeds frozen 2e-4. First F05 interval remains 160/131072 accepted ticks.
Full local science code, 46,080-row data, original ZIPs, tests/plots and stage records are in the separately backed source-inclusive ZIP, not this thin GitHub branch. No independent distinct-author referee was run.

**DAG:** REI canonical 28/88 reported; REI working 33/88; REC H5 physical 0/313; REI physical fast 4/7; **all canonical deltas ZERO**.
**Controls:** PRODUCTION=HOLD, NO_MERGE, NO_FORCE_PUSH, NO_OWNER_SWITCH, NO_TOLERANCE_RELAXATION, NO_NEW_IVP, AUTO_NEXT_NODE=false.
**NEXT REI SCIENCE:** with original source 46,080-node tick160 common parent, rigorously enclose nonlinear original MPRK22/SDIRK2 D_h=F_h−F_{h/2}∘F_{h/2} including 26-event source and four evaluation sites; retry only [160,161] under unchanged gates and existing authorization; then full F05 if physically accepted.

References: Zeng & Hirata (ApJ DOI 10.3847/1538-4357/abca38); Norman et al. (ApJS DOI 10.1088/0067-0049/216/1/16). Papers are contextual only; quantitative authority is pinned original REI artifacts.