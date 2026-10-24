"""Render the two prescribed figures exclusively from retained results."""
import argparse
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    src, out = ROOT/args.results, ROOT/args.out
    out.mkdir(parents=True, exist_ok=False)
    with np.load(src/'RAW_COMPARISON.npz', allow_pickle=False) as a:
        b = a['B']
        nodal = np.maximum(np.abs(a['E0']), np.abs(a['E1']))
        detail = np.abs(a['delta'])
        channel = a['channel_index']
        cell = a['cell_index']
        fig, axes = plt.subplots(2, 1, figsize=(11, 7), gridspec_kw={'height_ratios': [2, 1]}, constrained_layout=True)
        for arr, label, color in [(b, 'Stored discrepancy B', '#143d74'), (nodal, 'Common-node contribution', '#ab4e16'), (detail, 'Fine midpoint detail', '#248465')]:
            axes[0].plot(channel, np.max(arr, axis=1), label=label, color=color, linewidth=1.25)
        axes[0].set_yscale('symlog', linthresh=1e-18)
        axes[0].axvspan(310.5, 313.5, color='#e8dff2', alpha=.6)
        axes[0].set(xlabel='Outgoing channel (0–310 virtual; 311–313 Lyman)', ylabel='Absolute occupation departure', title='Channel discrepancy and its two contributions')
        axes[0].legend(fontsize=9)
        scale = np.maximum(np.max(np.abs(a['coarse']), axis=1), np.max(np.abs(a['fine']), axis=1))
        normalized = np.divide(np.max(b, axis=1), scale, out=np.zeros(314), where=scale != 0)
        axes[1].plot(channel, normalized, color='#143d74', linewidth=1.2)
        axes[1].set(xlabel='Outgoing channel', ylabel='B / history scale', title='Descriptive normalization; zero scale explicitly maps to zero')
        fig.suptitle('REC-HISTORY-REFINE01 · retained tables on the common early-time domain', fontsize=13)
        for ext in ['png', 'pdf']:
            fig.savefig(out/('channel_envelopes.'+ext), dpi=170)
        plt.close(fig)
        fig, axes = plt.subplots(2, 1, figsize=(11, 7), gridspec_kw={'height_ratios': [2, 1]}, constrained_layout=True)
        for arr, label, color in [(b, 'B across channels', '#143d74'), (nodal, 'Nodal across channels', '#ab4e16'), (detail, 'Detail across channels', '#248465')]:
            axes[0].plot(cell, np.max(arr, axis=0), label=label, color=color, linewidth=1.1)
        axes[0].axvspan(-.5, 7.5, color='#f3cfa7', alpha=.7, label='Startup-origin cells 0–7')
        axes[0].axvspan(757.5, 758.5, color='#e8b9c9', alpha=.9, label='Event cell 758')
        axes[0].set_yscale('symlog', linthresh=1e-18)
        axes[0].set(xlim=(-.5, 758.5), xlabel='Coarse cell m', ylabel='Absolute departure discrepancy', title='Time envelope; propagated startup effects remain after cell 7')
        axes[0].legend(fontsize=8, loc='best')
        k = int(np.argmax(b[:, 758]))
        u = np.linspace(0, 1, 101)
        e0, e1, delta = (float(a[name][k, 758]) for name in ['E0', 'E1', 'delta'])
        linear = (1-u)*e0+u*e1
        triangular = 2*np.minimum(u, 1-u)*delta
        axes[1].plot(u, linear+triangular, color='#143d74', label='Difference D(u)')
        axes[1].plot(u, linear, color='#ab4e16', linestyle='--', label='Nodal linear term')
        axes[1].plot(u, triangular, color='#248465', linestyle=':', label='Fine detail term')
        axes[1].scatter([0, .5, 1], [e0, float(a['Dmid'][k, 758]), e1], color='#143d74', s=20)
        axes[1].axvline(.5, color='#9a5271', linewidth=.7)
        axes[1].set(xlabel='Last-cell coordinate u (endpoint is a closure witness)', ylabel='Signed departure difference', title=f'Event cell 758 · largest-B channel {k}; fine midpoint is first H_ONLY input')
        axes[1].legend(fontsize=8)
        fig.suptitle('Stored interpolant comparison · physical reference uncertainty unavailable', fontsize=13)
        for ext in ['png', 'pdf']:
            fig.savefig(out/('time_event_envelopes.'+ext), dpi=170)
        plt.close(fig)
    (out/'RENDER_RECEIPT.json').write_text(json.dumps({'data_source': str(src.relative_to(ROOT)/'RAW_COMPARISON.npz'), 'new_scientific_comparisons': 0,
                                                    'saved_figures': ['channel_envelopes.png', 'channel_envelopes.pdf', 'time_event_envelopes.png', 'time_event_envelopes.pdf'],
                                                    'first_pngs_preserved': True, 'visual_inspection': 'PENDING_ACTUAL_VIEW'}, indent=2)+'\n')


if __name__ == '__main__':
    main()
