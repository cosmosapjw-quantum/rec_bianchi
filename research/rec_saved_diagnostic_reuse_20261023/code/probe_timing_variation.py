"""One targeted order probe after the C2 baseline's observed timing fluctuation.

This is not a candidate benchmark. It preserves the original profile and changes
only the order in which two already selected, exact saved-state corpora are read.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import time
import traceback

import profile_saved_diagnostics as p


def main():
    root = p.UNIT/"evidence/profile/attempt_001"
    out = p.UNIT/"evidence/timing_order_probe"
    finished = json.loads((root/"FINISHED.json").read_text())
    if finished["status"] != "PASS_C2_BASELINE_PROFILE":
        raise ValueError("BASELINE_NOT_COMPLETE")
    p.LIMIT_SECONDS = 600-finished["active_wall_seconds"]
    out.mkdir(parents=True, exist_ok=False)
    schedule = ["refined", "nominal", "nominal", "refined", "refined", "nominal"]
    p.save_json(out/"STARTED.json", dict(command=sys.argv, script=p.binding(__file__),
                  profile_harness=p.binding(p.__file__), baseline_receipt=p.binding(root/"FINISHED.json"),
                  reason="The final baseline case had large unprofiled timing fluctuations; distinguish a repeatable case-cost ordering from order/time variation without rerunning all cases.",
                  schedule=schedule, selected_seed="s04_m04_r04", selected_branch="planck_reference",
                  prior_active_wall_seconds=finished["active_wall_seconds"], total_budget_seconds=600,
                  new_IVPs=0, candidate_implementation=False, expected_point_arrays="exact saved-state equality"))
    status = "FAILED_PRESERVED"
    try:
        manifest = json.loads((root/"INPUT_MANIFEST.json").read_text())
        corpus = json.loads((root/"CORPUS_MANIFEST.json").read_text())
        runtime_id, sources = p.runner.source_identity()
        if runtime_id != p.RUNTIME_ID or sources != manifest["source_files"]:
            raise ValueError("PROBE_SOURCE_CHANGED")
        cases, preparation = {}, {}
        for resolution in ("nominal", "refined"):
            label = "s04_m04_r04_planck_reference_"+resolution
            def prepare():
                folder = p.PARENT/"results/compton8"/label
                rec = json.loads((folder/"RESULT.json").read_text())
                source = folder/"dense_1025.npz"
                if p.digest(source) != rec["outputs"][source.name]["sha256"]:
                    raise ValueError("PROBE_INPUT_CHANGED")
                a = p.load_npz(source)
                indices = p.np.array(corpus[label]["selected_indices"], dtype=p.np.int64)
                selected = p.subset(a, indices)
                model = p.ComptonFull63(rec["specification"]["config"], branch="planck_reference")
                collision = p.CollisionalBudget(model.atomic)
                d = {str(name): selected["diagnostics"][:, k] for k, name in enumerate(selected["diagnostic_names"])}
                cref = p.PARENT/"results/analysis_v1"/label/"collisions/collisions_dense_1025.npz"
                bound = next(row for row in manifest["files"] if row["path"] == p.relative(cref))
                if p.digest(cref) != bound["sha256"]:
                    raise ValueError("PROBE_COLLISION_REFERENCE_CHANGED")
                expected_collisions = p.subset(p.load_npz(cref), indices)
                return model, collision, selected, d, expected_collisions
            cases[resolution], preparation[resolution] = p.measured(prepare)
        def execute(resolution):
            model, collision, selected, d, expected_collisions = cases[resolution]
            g, gt = p.measured(lambda: p.runner.gather_set(model, selected["x"], selected["raw_state"], selected["initial_Y"], p.deadline))
            c, ct = p.measured(lambda: p.collision_analysis._evaluate_grid(selected, d, model.atomic, collision))
            ga, ca = g[0], c[0]
            gc = p.exact_comparison(ga, selected, p.GATHER_POINT_FIELDS)
            fields = tuple(name for name, a in ca.items() if a.ndim and a.shape[0] == 64 and "cumulative" not in name)
            cc = p.exact_comparison(ca, expected_collisions, fields)
            if not gc["pass_exact"] or not cc["pass_exact"]:
                raise ValueError("PROBE_POINT_MISMATCH")
            return dict(resolution=resolution, states=64, gather=gt, collision=ct,
                        gather_exact=True, collision_exact=True)
        warmup = [execute(resolution) for resolution in ("nominal", "refined")]
        rows = [dict(order=i, **execute(resolution)) for i, resolution in enumerate(schedule, 1)]
        if p.ODE_ATTEMPTS:
            raise RuntimeError("PROBE_IVP_ATTEMPT")
        status = "PASS_TARGETED_ORDER_PROBE"
        p.save_json(out/"RESULT.json", dict(status=status, preparation=preparation, warmup=warmup, measured=rows,
                    source_identity=runtime_id, source_files=sources, new_IVPs=0, IVP_attempts=p.ODE_ATTEMPTS,
                    interpretation_limit="Timing ordering is diagnostic only; this probe does not identify a system-level cause or establish a candidate speedup."))
        print(json.dumps(dict(status=status, rows=rows)), flush=True)
    except Exception as exc:
        p.save_json(out/"FAILED.json", dict(error=repr(exc), traceback=traceback.format_exc()))
        raise
    finally:
        p.save_json(out/"FINISHED.json", dict(status=status,
                    active_wall_seconds=time.perf_counter()-p.PROCESS_START,
                    active_cpu_seconds=time.process_time()-p.CPU_START,
                    prior_active_wall_seconds=finished["active_wall_seconds"],
                    total_budget_seconds=600, new_IVPs=0, IVP_attempts=p.ODE_ATTEMPTS))


if __name__ == "__main__":
    main()
