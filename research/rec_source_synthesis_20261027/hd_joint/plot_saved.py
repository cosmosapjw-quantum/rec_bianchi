"""Plot only saved diagnostics; no source parser/scientific recomputation."""
import json
from pathlib import Path


def plot_saved(result_path, output_dir):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    result = json.loads(Path(result_path).read_text())
    output_dir = Path(output_dir)
    fig, axes = plt.subplots(1, 3, figsize=(14.4, 4.7), layout='constrained')
    markers = ['o', 's', '^', 'v', 'D', 'P', 'X', '*']
    for line_id in range(1, 9):
        rows = [row for row in result['rows'] if row['line_id'] == line_id]
        label = f"L{line_id}: J={rows[0]['upper_J']}→{rows[0]['lower_J']}"
        for ax, key in zip(axes[:2], ['paired_flux_imbalance_I', 'source_planck_deviation_D']):
            ax.plot([row['temperature_K'] for row in rows], [row[key] for row in rows], marker=markers[line_id - 1], label=label)
    for ax, label in zip(axes[:2], ['Signed paired-flux imbalance I', 'Signed source/Planck deviation D']):
        ax.set_yscale('symlog', linthresh=1e-12)
        ax.axhline(0, color='0.5', lw=0.7)
        ax.set_xlabel('Source temperature T [K]')
        ax.set_ylabel(label + ' [dimensionless]')
        ax.set_xticks([50, 100, 200])
        ax.grid(True, alpha=0.2)
    gates = result['line_source_gates']
    axes[2].bar([g['line_id'] for g in gates], [float(g['absolute_gap_Hz']) for g in gates], color=['#238b45' if g['passed'] else '#b2182b' for g in gates])
    axes[2].axhline(35, color='black', linestyle='--', label='Original 35 Hz gate')
    axes[2].set_yscale('log')
    axes[2].set_xlabel('Original catalog line ID')
    axes[2].set_ylabel('Absolute level/photon frequency gap [Hz]')
    axes[2].set_xticks(range(1, 9))
    axes[2].set_title('Original source qualification: 7/8 FAIL')
    axes[2].legend(fontsize=8)
    axes[0].legend(fontsize=7, ncol=2)
    fig.suptitle('HD fixed-column thermal compatibility — diagnostics preserve the original source gate', fontsize=12)
    for suffix in ('png', 'pdf'):
        fig.savefig(output_dir / ('joint_thermal_diagnostics.' + suffix), dpi=160)
    plt.close(fig)
