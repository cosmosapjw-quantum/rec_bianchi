"""Two figures read only saved primary observations; no coefficient/solve imports."""
import os
for key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS']:
    os.environ[key] = '1'
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--input', default='results/primary001')
    parser.add_argument('--output', default='results/figures001'); args = parser.parse_args()
    source = ROOT/args.input; out = ROOT/args.output; out.mkdir(parents=True, exist_ok=False)
    summary = json.loads((source/'SUMMARY.json').read_text())
    with np.load(source/'RAW_RESPONSE.npz', allow_pickle=False) as saved:
        K = saved['Khat']; number = saved['number_hat']; selected = summary['selected_output_row']
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    image = ax.imshow(np.log10(np.maximum(np.abs(K), np.finfo(float).tiny)), aspect='auto', origin='lower', cmap='magma')
    ax.set(xlabel='Incoming query index (313)', ylabel='Outgoing index (314)',
           title='Native opaque source: full frozen occupation response')
    fig.colorbar(image, ax=ax, label='log10 absolute represented response')
    fig.savefig(out/'absolute_response.png', dpi=170); fig.savefig(out/'absolute_response.pdf'); plt.close(fig)
    fig, axs = plt.subplots(2, 1, figsize=(10, 7), constrained_layout=True)
    x = np.arange(313)
    axs[0].semilogy(x, np.maximum(np.abs(K[selected]), np.finfo(float).tiny), label=f'Largest nominal row: {selected}')
    axs[0].semilogy(x, np.maximum(np.abs(K[311]), np.finfo(float).tiny), label='Lyalpha row 311', alpha=.8)
    axs[0].set(ylabel='Absolute occupation coefficient', title='Per-query unit-box sensitivity weights'); axs[0].legend()
    axs[1].semilogy(x, np.maximum(np.abs(number), np.finfo(float).tiny), color='#8b2c35')
    axs[1].set(xlabel='Incoming query index', ylabel='Number coefficient (m^-3 s^-1)',
               title='Single-event number response; physical incoming error box absent')
    fig.savefig(out/'query_event_contributions.png', dpi=170); fig.savefig(out/'query_event_contributions.pdf'); plt.close(fig)
    files = [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir())]
    (out/'RENDER_RECEIPT.json').write_text(json.dumps({'read_only_saved_outputs': True, 'scientific_solves': 0,
        'input_sha256': hashlib.sha256((source/'RAW_RESPONSE.npz').read_bytes()).hexdigest(),
        'files': files, 'actual_visual_inspection': 'PENDING_ROOT_INSPECTION'}, indent=2)+'\n')


if __name__ == '__main__':
    main()
