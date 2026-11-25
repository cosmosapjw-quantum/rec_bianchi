# REC_BIANCHI independent-runtime architecture

User requirement (2026-11-25): REC_BIANCHI must be executable independently of HyRec. Fundamental atomic constants and reaction-rate tables may be inherited unchanged unless a physical modification is necessary.

- Production ownership: REC evolves populations, thermal state, and radiation using its own operators, IC/BC and explicitly supplied geometry. A Bianchi background provider can be supplied as a scientific input, not an upstream recombination trajectory.
- Inherited data: canonical atomic rates, constants and their source interpolation conventions remain immutable, hash-identified inputs. Their archive container can contain only the required data members. Inheritance of rates does not imply equivalence of the cosmological evolution or validity for arbitrary distorted radiation.
- External HyRec executables, C/FFI reference solves, and sampled x_e/T_m histories are optional validation tools. Matched-reference lanes retain their existing meaning and may not be presented as independent production evolution.
- Avoid duplicate ownership: original virtual-state Aup/Adn, diffusion, Sobolev and COM-KHW line terms require explicit non-overlapping replacement before active coupling. Existing v0.75 failure/ownership receipt remains unchanged.
- This first independently runnable lane is H-only EMLA2s2p+Tm with neutral helium (Python/SciPy) plus source-calibrated scalar line tracer (native REC Rust), and a separate unanchored native reduced TLA/W integrator on FLRW/prescribed LRS Bianchi I. Neither implies full all-Bianchi multilevel transfer, self-consistent Einstein feedback, or full He chronology.

Example (REC root, no HyRec executable required):

```sh
cargo build --release --locked --manifest-path rust/rec_microphysics/Cargo.toml --bin rec_live_line --bin rec_owned_history
PYTHONPATH=src python -m full_bianchi_hyrec.trajectory.standalone --rates archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip --out NEW_HISTORY.json --z-end 900
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m full_bianchi_hyrec.standalone_line --rates archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip --binary rust/rec_microphysics/target/release/rec_live_line --out NEW_LINE --subcells 4 --duration 100 --steps 4 --initial radiation --exterior
rust/rec_microphysics/target/release/rec_owned_history 1600 900 1024 0.01 > NEW_TLA_LRS.tsv
```

The standalone line command builds its own HMLA state and compiles the scalar source directly at that bath; it never consumes a precomputed recombination history. Material bath is held fixed over the local line experiment. Exterior reservoirs are finite local dynamic cells, not the original HyRec virtual state solution. See research/r118c2f_standalone/ for reproducible scope receipts.

Next: unify calibrated nonseparable angular redistribution and local radiation transport with REC's explicit atomic ownership, then remove reference dependence from remaining full population/thermal trajectories, including early He stages and long causal radiation histories. Test live replacement before deactivating any legacy term; compare to HyRec only as an external reference.
