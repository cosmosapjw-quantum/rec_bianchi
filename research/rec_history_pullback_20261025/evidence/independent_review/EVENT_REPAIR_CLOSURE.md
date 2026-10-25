# PB01 event repair closure

Verdict: PASS_TARGETED_SAVED_DATA_EVENT_REPAIR.
Finding PB01-POSTRUN-001 is CLOSED for the admitted saved-data realization.
The complete unit's final figure criterion remains separately pending.

The continuing reviewer read code/event_pair.py, the exact
SHARED_EVENT_PAIRING.diff, repairs/event_pair001/run_saved_repair.py,
ACCEPTED_SUMMARY.json and the actual paired NPZ artifacts.

The helper copies a finite shape(5,) vector and changes only paired[4] to
-paired[3]. The future-primary hook retains all four independent event vectors
and their comparisons before using that helper. The 2e-12 comparison criterion
is unchanged. No coefficient, geometry, source H, volume or thermodynamic
derivative changes. The future full primary was NOT rerun.

Independent byte readback of all32 paired NPZs established:

- All independent five-component payloads equal the respective original
  first-primary event vector bytes.
- All canonical first-four components equal the original bytes.
- Each canonical atomic eight-byte value is the exact sign-bit reversal of the
  same canonical radiation eight-byte value.
- The original381 raw/execution hash manifest entries match before/after.
- The original summary remains FAILED_FROZEN_CRITERION and original returncode2.
- All8 repaired case records pass; their largest canonical explicit-tangent
  normalized error is4.68283718715128e-15 against unchanged2e-12.

The detailed result is POSTREPAIR_RAW_READBACK.json. This readback decoded NPY
bytes through the standard library; no source, helper or NumPy module was
imported, and no matvec/event-dot/primary action was run. Its observed process CPU
through readback was0.035253s, body wall0.02422965400000976s, maxRSS11776KiB.
Body wall excludes interpreter startup. CPU was hard-capped at1s.
An unavailable /usr/bin/time launcher failed before launching a readback child;
that non-scientific launcher failure is recorded in the readback evidence.

Fingerprints:

- actual first-primary source, preserved:
  bc63fd1868710548f27381a6bbaea8d6b445357436a5fdc009e8997c03a66b26
- corrected future primary:
  ac69a3578ff45c0363fcc194ef694135543217f342eb861c06712c5eb6590ebb
- shared-event helper:
  fc10d2819944f8d78e4cb6ede33cded91f6c05a8e5671a848cdff541703898a2
- current19-entry execution manifest:
  879c8543c679b296a155a6b3202aa900d68657731a423da0e51035756b1c0cd3

The admitted result combines the original primary's unchanged passing
non-event criteria with one actual32-vector saved-data shared-event repair.
It is not an uninterrupted original-primary PASS and not an executed
full patched-primary PASS.

The first figure cell_margins_query_gains.png was actually viewed and is
accepted. The first remainder_adjoint_consistency.png has a concrete layout
failure (collapsed narrow axes, clipped headings/labels and overlapping ticks);
root independently observed the same issue and authorized one second-figure-only
saved-data layout correction. This remaining figure finding is
PB01-FIGURE-001; no data, tolerance or primary action change is required.

