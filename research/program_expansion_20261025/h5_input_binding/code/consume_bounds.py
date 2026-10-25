"""Consume a source-bound H5 packet; missing actual inputs remain explicit."""
import argparse
import json
from pathlib import Path
from h5_bounds import BoundInputError, evaluate_files


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--context", type=Path, required=True)
    p.add_argument("--packet", type=Path, required=True)
    p.add_argument("--proof-root", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise ValueError("OUTPUT_EXISTS_USE_NEW_ATTEMPT_PATH")
    try:
        result = evaluate_files(args.context, args.packet, proof_root=args.proof_root)
        code = 0
    except BoundInputError as exc:
        result = {"status": "REFUSED_BOUND_INPUT", "reason": str(exc),
                  "physical_epsilon": None, "physical_outgoing_bound": None}
        code = 2
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
