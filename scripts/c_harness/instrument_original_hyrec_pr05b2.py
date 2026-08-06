#!/usr/bin/env python3
"""Guarded PR-05B2 instrumentation of canonical October-2012 HyRec.

The canonical archive remains immutable.  The transformation first applies the
already-audited PR-04C source diagnostics and renames their guard to
``PR05B2_DIAGNOSTICS``.  It then adds one raw, source-order dump of the accepted
causal radiation history at the z~900 diagnostic call.  Building without the
macro must therefore remain source-identical to the canonical executable and
numerical history.
"""
from __future__ import annotations

import argparse
import difflib
import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent
PR04C_PATH = HERE / "instrument_original_hyrec_pr04c.py"
_spec = importlib.util.spec_from_file_location("_pr04c_instrumenter", PR04C_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError("cannot load PR-04C source instrumenter")
_pr04c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pr04c)


_HISTORY_DUMP = r'''
            if (pr05b2_target_z == 900.) {
               char pr05b2_hist_path[4096];
               FILE *pr05b2_hist_fp;
               unsigned pr05b2_row;
               const unsigned pr05b2_count = iz + 1;

               snprintf(pr05b2_hist_path, sizeof(pr05b2_hist_path), "%s/pr05b2_history_meta.csv", pr05b2_dir);
               pr05b2_hist_fp = fopen(pr05b2_hist_path, "w");
               if (pr05b2_hist_fp == NULL) { fprintf(stderr, "PR05B2 history meta open failed\n"); exit(90); }
               fprintf(pr05b2_hist_fp, "schema,PR05B2_SOURCE_HISTORY_RAW_V1\n");
               fprintf(pr05b2_hist_fp, "z,%.17g\n", z);
               fprintf(pr05b2_hist_fp, "zstart,%.17g\n", zstart);
               fprintf(pr05b2_hist_fp, "iz_current,%u\n", iz);
               fprintf(pr05b2_hist_fp, "accepted_count,%u\n", pr05b2_count);
               fprintf(pr05b2_hist_fp, "dlna,%.17g\n", DLNA);
               fprintf(pr05b2_hist_fp, "nvirt,%u\n", (unsigned) NVIRT);
               fprintf(pr05b2_hist_fp, "nlyman,3\n");
               fclose(pr05b2_hist_fp);

               snprintf(pr05b2_hist_path, sizeof(pr05b2_hist_path), "%s/pr05b2_energy_eV.f64", pr05b2_dir);
               pr05b2_hist_fp = fopen(pr05b2_hist_path, "wb");
               if (pr05b2_hist_fp == NULL) { fprintf(stderr, "PR05B2 energy dump open failed\n"); exit(91); }
               if (fwrite(twog->Eb_tab, sizeof(double), NVIRT, pr05b2_hist_fp) != NVIRT) { fprintf(stderr, "PR05B2 energy dump failed\n"); exit(92); }
               fclose(pr05b2_hist_fp);

               snprintf(pr05b2_hist_path, sizeof(pr05b2_hist_path), "%s/pr05b2_Dfminus_hist.f64", pr05b2_dir);
               pr05b2_hist_fp = fopen(pr05b2_hist_path, "wb");
               if (pr05b2_hist_fp == NULL) { fprintf(stderr, "PR05B2 Dfminus dump open failed\n"); exit(93); }
               for (pr05b2_row=0; pr05b2_row<NVIRT; pr05b2_row++) {
                  if (fwrite(Dfminus_hist[pr05b2_row], sizeof(double), pr05b2_count, pr05b2_hist_fp) != pr05b2_count) { fprintf(stderr, "PR05B2 Dfminus dump failed\n"); exit(94); }
               }
               fclose(pr05b2_hist_fp);

               snprintf(pr05b2_hist_path, sizeof(pr05b2_hist_path), "%s/pr05b2_Dfminus_Ly_hist.f64", pr05b2_dir);
               pr05b2_hist_fp = fopen(pr05b2_hist_path, "wb");
               if (pr05b2_hist_fp == NULL) { fprintf(stderr, "PR05B2 Lyman dump open failed\n"); exit(95); }
               for (pr05b2_row=0; pr05b2_row<3; pr05b2_row++) {
                  if (fwrite(Dfminus_Ly_hist[pr05b2_row], sizeof(double), pr05b2_count, pr05b2_hist_fp) != pr05b2_count) { fprintf(stderr, "PR05B2 Lyman dump failed\n"); exit(96); }
               }
               fclose(pr05b2_hist_fp);

               snprintf(pr05b2_hist_path, sizeof(pr05b2_hist_path), "%s/pr05b2_Dfnu_hist.f64", pr05b2_dir);
               pr05b2_hist_fp = fopen(pr05b2_hist_path, "wb");
               if (pr05b2_hist_fp == NULL) { fprintf(stderr, "PR05B2 Dfnu dump open failed\n"); exit(97); }
               for (pr05b2_row=0; pr05b2_row<NVIRT; pr05b2_row++) {
                  if (fwrite(Dfnu_hist[pr05b2_row], sizeof(double), pr05b2_count, pr05b2_hist_fp) != pr05b2_count) { fprintf(stderr, "PR05B2 Dfnu dump failed\n"); exit(98); }
               }
               fclose(pr05b2_hist_fp);
            }
'''


def instrument_hydrogen_source(text: str) -> str:
    result = _pr04c.instrument_hydrogen_source(text)
    result = result.replace("PR04C_DIAGNOSTICS", "PR05B2_DIAGNOSTICS")
    result = result.replace("PR04C", "PR05B2").replace("pr04c", "pr05b2")
    anchor = "            fclose(pr05b2_fp);\n            pr05b2_dumped[pr05b2_itarget] = 1;"
    if result.count(anchor) != 1:
        raise ValueError("cannot uniquely locate PR-05B2 history-dump anchor")
    return result.replace(
        anchor,
        _HISTORY_DUMP + "\n" + anchor,
        1,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--diff", type=Path)
    args = parser.parse_args()
    original = args.source.read_text(encoding="utf-8")
    instrumented = instrument_hydrogen_source(original)
    args.source.write_text(instrumented, encoding="utf-8", newline="")
    if args.diff is not None:
        args.diff.write_text(
            "".join(
                difflib.unified_diff(
                    original.splitlines(keepends=True),
                    instrumented.splitlines(keepends=True),
                    fromfile="canonical/hydrogen.c",
                    tofile="instrumented/hydrogen.c",
                )
            ),
            encoding="utf-8",
            newline="\n",
        )


if __name__ == "__main__":
    main()
