"""Conditional box API: absent physical epsilon yields null, never an estimate."""
import os
for key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS']:
    os.environ[key] = '1'
import argparse
import json
from pathlib import Path
import numpy as np
from interval import box_weights


def response(raw_path, epsilon=None):
    with np.load(raw_path, allow_pickle=False) as raw:
        outgoing = box_weights((raw['Klo'], raw['Khi']), epsilon)
        number = box_weights((raw['number_lo'][None, :], raw['number_hi'][None, :]), epsilon)
        radiation = box_weights((raw['radiation_lo'][None, :], raw['radiation_hi'][None, :]), epsilon)
    return {'outgoing': outgoing, 'number_event': number, 'radiation_energy': radiation,
            'atomic_energy_magnitude': radiation, 'exact_paired_energy_sum': 0,
            'physical_epsilon_provider': None if epsilon is None else 'CALLER_RESPONSIBILITY'}


def main():
    p = argparse.ArgumentParser(); p.add_argument('raw_npz'); p.add_argument('--epsilon-json')
    args = p.parse_args(); epsilon = None if args.epsilon_json is None else json.loads(Path(args.epsilon_json).read_text())
    print(json.dumps(response(args.raw_npz, epsilon), indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
