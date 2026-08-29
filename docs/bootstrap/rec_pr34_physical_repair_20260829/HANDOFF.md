# rec PR34 physical-component continuation

Use the separately delivered entry prompt to materialize and verify this branch's payload, record its immutable commit/tree, and create a new isolated implementation worktree. The exact scientific baseline is aa825d90397c561f7f753c0893ad7e99ea386a7e / ebe1d5038d8f80014a626a89d4069f450d024f10. Do not clean, reset, stash, rebase, amend, or change any retained user worktree.

## Already implemented here

The new ContextBoundSplitDomainReplacement API delegates the existing native algebra and binds every dataclass/snapshot field plus actual energy constants to restart v2. It rejects legacy unbound records and changed Doppler width before restore. The legacy module is unchanged and is NOT admissible for new physical restart. Do not call the native eight-state slice a physical COM solution.

COMSourceDepositionPlan validates an explicitly supplied physical mode measure and nonnegative number/energy-conserving map. It computes occupation source, fixed-map JVP including density tangent, and independently contracted input/output photon four-moments. It does not select a physical map, provide unknown face reconstruction, prove thermal null, or manufacture atomic recoil.

Host evidence: 27 component tests and four source mutants. Canonical nine restart tests and full coupled source integration have not run here. Old PR34 evidence and the old R2 archive/manifest remain unchanged.

## First local execution

```bash
python3 -m pytest -q tests/trajectory/test_split_context_and_deposition.py
python3 -m pytest -q tests/trajectory/test_split_restart_context_canonical.py
python3 -m pytest -q tests/trajectory/test_split_domain_replacement.py -k restart
python3 tools/check_rec_pr34_component_mutations.py
```

The new canonical test imports the context-bound API. Keep the old tests and their numerical thresholds unchanged. Missing canonical data is not a reason to manufacture a replacement fixture. The supplied synthetic 35x26 component fixture is not a canonical COM calculation.

## Physical reference implementation

Read existing source owners original_hyrec_native.py, original_hyrec_physical_flux.py, frequency_liouville.py, nonlinear_bose_release.py, nonlinear_bose_runtime.py, source_derived_parent.py, full_coupled_adaptive.py and single_com_macro.py. Work in a new trajectory/physical_split_reference.py with focused tests.

The physical source-spike law is J_b=H A_b(Dfminus_b-Dfplus_b), A_b=8*pi*nu_b^3/(c^3*n_H); compare to x1s*Gamma*(Dfeq-Dfbar) with the inherited escape-branch policy. This is not a cross-interface diffusion jump. Do not replace it with Aup*x_left-Adn*x_right.

Use the actual source-conditioned 35-state network and 26-direction HarmonicGrid. Keep its occupation, physical mode measure, representative energies, angular weights, Doppler width and parent identity explicit. Run the existing thermodynamic-grid consistency check. If temperature changes the measure, use the existing source-conditioned recompilation/remap path, not relabeling.

First run a locked-snapshot isotropic reference using the existing v0.65 initial-data axiom. Scalar native history cannot identify a general anisotropic boundary; do not silently average one. Preserve the full anisotropic target as open.

Before implementing the coupled action, retain numerical RED with nonuniform physical measure, both cross edges, a nonthermal positive COM occupation and independent source moments. Preserve native indices136..143 and edges(135,136),(143,144). Never infer finite cells from native spikes.

If source does not identify a deposition/face closure, make a candidate an explicit versioned EXPLORATORY_NONAUTHORITATIVE numerical input and execute it. Do not pretend it is source authority, require uniqueness by provenance, or tune tolerances after seeing results. A source-compatible acceptance still requires thermal null, spectral/source response and refinement. The provided positive two-moment map counterexample demonstrates why conservation alone is insufficient.

The physical unknown must include true COM occupation rather than eight native proxies. Assemble its residual with existing COM collision/transport/JVP and dimensional source deposition. The supplied JVP fixes map/measure; add their derivatives if those inputs depend on unknowns. Assemble atomic and photon four-forces separately, with explicit contravariant hydrogen-tetrad convention (-,+,+,+); do not manufacture independent proof by setting one to minus the other.

Prove source flux parity, number/energy/four-force balance, single ownership, thermal and spectral convergence, independent directional JVP, and accepted/rejected restart/history transactions. Use the context-bound API and include new map/measure variables in its context. No full recombination history claim follows from one snapshot.

## Review and delivery

Change only new physical-reference/component/test owners and new evidence under artifacts/trajectory/pr05c2c1b2b1e1c_repair. Do not modify old artifacts/trajectory/pr05c2c1b2b1e1c. Source readers, tables, equations, thresholds and owner edges remain frozen unless a concrete newly reproduced defect requires an explicitly explained patch.

After an actual candidate run, one PHYS-MATH and one PHYS-MATH-CODE review, at most one reproduced repair and differential retest. No timing/GPU/Wolfram/full-suite reassurance. A unavailable local model is nonblocking HOST_CODEX_CONTINUE.

Ordinary push one stacked draft implementation PR against this delivery branch. A bounded success is PASS_REC_ISOTROPIC_PHYSICAL_REFERENCE_ONLY, not the full split-domain terminal unless all original requirements actually pass. Otherwise retain a measured BLOCKED_REC_PHYSICAL_INTERFACE_DEFECT. No merge, ready, dynamic macro, BASS changes or rec-to-rei export.

rei PR14 remains STOP_INVALID/BLOCKED_MINIMUM_STEP. Do not change its log_T tolerance or minimum step. Correlation-preserving discrete-map propagation is a separate authorization; zero returned ledgers from a rejected attempt do not certify an accepted interval.
