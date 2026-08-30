# REC-LOCAL-01 admission and REC-LOCAL-02 execution plan

## Gate 0 — preserve and inventory

- Treat the original `REC-LOCAL-01` worktree as read-only evidence.
- Record branch, HEAD, tree, `git status --porcelain=v1`, all six reported
  evidence/receipt paths, sizes, mtimes and SHA-256 digests.
- Preserve the 37 tracked cache changes. Do not infer that they are scientific
  evidence and do not import them into the implementation branch.
- Create a separate worktree from the immutable recovery payload identified by
  this branch's `REMOTE_PUBLICATION.json`.

## Gate 1 — package and source-object admission

- Fetch the historical bootstrap branch and the recovery branch by explicit
  ref; do not fetch an unqualified moving default.
- Run `FETCH_AND_VALIDATE.sh` in the clean recovery worktree.
- Require the exact `47e19df...` commit/tree/subtree/manifest identities, the
  exact three historical mismatches and the seven-entry sidecar rebind.
- Require the repaired PR #39 followthrough manifest and its existing
  `verify_payload.py` to pass.

## Gate 2 — local receipt admission

- Copy, never move, the local receipt and five sibling mutation-evidence files
  into a new evidence directory.
- Verify every copied byte against a pre-copy inventory.
- Inspect the actual receipt schema; do not derive evidence solely from
  `REC_LOCAL_01_USER_REPORT.json`.
- Fill a new admission record from `REC_LOCAL_01_ADMISSION_TEMPLATE.json`,
  replace every placeholder, bind the source receipt SHA-256 and preserved
  worktree identity, and run `validate_local01_admission.py` before source
  mutation. This is administrative admission of an already executed run; it
  is not a rerun of `REC-LOCAL-01`.
- Only this gate may change the local state from user-reported to
  `PASS_REC_LOCAL01_EVIDENCE_ADMITTED_NOT_PHYSICAL_SPLIT`.

## Gate 3 — REC-LOCAL-02 physical reference

- Freeze and record these tracked authority inputs before calculation:

  | Input | Tracked path | SHA-256 |
  | --- | --- | --- |
  | z~1100 boundary snapshot | `archive/expanded/Full_Bianchi_HyRec_PR04C0C1A_split_domain_boundary_v0_55/pr04c_z1100.csv` | `147ba6e6cfdae9c06530a0983161e769198b3bb5ad56c0c4d820b0a3f5d3e7b5` |
  | Original HyRec | `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip` | `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27` |
  | 35-state network | `data/z1100_direct_network_node.npz` | `e6a28194d183658a87f0974afe3f46323106382970a85338f9ce94c20c7b5736` |
  | 26-direction grid | `data/pr01c_background_snapshots_v048.npz` | `df136bca7c120054cc45cf2b4fc2bd52acc3d60e6159b0f63c2622de03f2f03c` |
  | Accepted scalar history | `data/pr05b2_source_history_v060.npz` | `d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1` |
  | 35x26 source parent | `data/pr05c2c1b2b1e0_source_derived_parent_v073.npz` | `c74a2a0e69d6d34c338d19af2f123d1eb32130ac103a68e4494a2c9542eaa958` |
  | Existing 35x26 COM root | `data/pr05c2c1b2b1e1a_single_com_macro_v074.npz` | `b05e227e7ff8ffd64639e4a432a5789fff08cc89b8bbd63adbcec5fc2da3903c` |
  | Two-photon/Raman evidence | `data/pr05c2c1b2a_two_photon_raman_source_v068.npz` | `536154894ce3779cc877a04b490a6e2b4501826d98efd9a12a4a6568dd0eabad` |

- Use the source-owned occupation/flux inputs and the actual 35-frequency by
  26-direction COM measure at the locked isotropic z~1100 snapshot.
- Preserve native indices `136..143` and crossing edges `(135,136)` and
  `(143,144)`. Do not infer cells from point spikes or fit normalization.
- Establish positive moment feasibility before selecting a deposition map.
  On failure, retain a reproducible infeasibility certificate instead of
  clipping or silently changing the target.
- The coupled directional derivative must include `dM`, source-target moment
  changes, prior changes, Doppler-width/frame derivatives and moving-measure
  terms whenever those quantities depend on state.
- Assemble photon and atomic number, energy and four-force contributions
  independently using metric signature `(-,+,+,+)`, an explicit hydrogen
  frame and explicit SI units.

The principal source owners are
`recoil/original_hyrec_physical_flux.py`, `recoil/frequency_liouville.py`,
`trajectory/hyrec_source_adapter.py`, `trajectory/hyrec_two_photon_raman.py`,
`trajectory/source_derived_parent.py` and
`trajectory/full_coupled_adaptive.py`. Do not replace them with the additive
`physical_inputs.py` helper or with `COMSourceDepositionPlan`.

Treat the following as pre-registered blocking tests, not implementation
details to smooth over:

- the tracked native history has angular rank one while the COM face has 26
  angular values; no source-defined face reconstruction is currently sealed;
- the source-derived parent uses an explicit isotropic initial-data axiom and
  is not a coupled endpoint;
- the existing single-COM macro holds outer occupations fixed;
- the direct thermodynamic network accepts exact nodes rather than a general
  interpolated network;
- the boundary and modern-network Doppler widths differ at roughly `1.2e-5`
  relative scale (about `5.7907148e10 Hz` versus `5.7907835e10 Hz`). Bind the
  selected definition and its constants explicitly; never choose silently.

An adjacent-energy positive barycentric map may be used only as
`EXPLORATORY_NONAUTHORITATIVE` feasibility evidence. It is not source
authority, a face closure, a thermal-preservation proof or a physical PASS.

## Gate 4 — tests and adversarial checks

- Prove source-flux parity, positive/physical-domain behavior, number and
  energy balance, four-force balance, thermal/spectral response, independent
  directional-JVP agreement and accepted/rejected restart/history
  transactions.
- Mutate at least the map/measure, Doppler width, frame, source provenance,
  energy constants, topology, prior and payload bytes. Each mutant must reach
  and fail the intended numerical or contract assertion without collection
  errors.
- Run one PHYS-MATH and one PHYS-MATH-CODE review after real execution. Repair
  at most one reproduced P0/P1 defect, then rereview only its dependency cone.

## Terminal states

- `PASS_REC_ISOTROPIC_PHYSICAL_REFERENCE_ONLY`: allowed only if the bounded
  35x26 reference, full moving-map JVP and its ledgers pass.
- `BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT`: retain measured evidence when any
  physical map, feasibility, derivative, ledger or restart condition fails.
- `NO_PASS_REC_PHYSICAL_SPLIT`: remains the repository-wide claim until every
  original split-domain physical requirement closes.

No merge, ready transition, rec-to-rei numerical export, dynamic macro,
performance campaign, GPU/Wolfram work or unrelated full-suite reassurance is
authorized by this package.
