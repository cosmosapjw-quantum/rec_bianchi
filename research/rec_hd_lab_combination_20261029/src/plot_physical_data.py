"""Plot only actual published spectroscopy constraints and typed conditional calculations."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'evidence'

def main():
    lab=json.loads((E/'MEASUREMENT_RECONCILIATION.json').read_text())
    data=json.loads((E/'PHOTON_PHYSICAL_TABLE.json').read_text())
    pairs=lab['measured_combinations']
    labels=['v=0: J2 - J0','v=0: J3 - J1']
    values=[float(x['experiment_minus_source_photon_combo_Hz'])/1e6 for x in pairs]
    sigma=[x['reported_uncertainty_Hz']/1e6 for x in pairs]
    fig,ax=plt.subplots(figsize=(8.6,4.6))
    ax.bar(labels,values)
    ax.errorbar([0,1],values,yerr=sigma,fmt='none',capsize=5)
    ax.axhline(0,linewidth=.8)
    for i,v in enumerate(values):ax.annotate(f'{v:+.4f} MHz', (i,v), xytext=(0,-16),textcoords='offset points',ha='center',va='top',color='white' if abs(v)>4 else 'black')
    ax.set_ylabel('2022 lab minus frozen 2021/2011-source combo (MHz)')
    ax.set_title('Measured HD rotational level combinations, not the original 35 Hz gate')
    fig.text(.1,.01,'Error bars show only published lab uncertainty (26/30 kHz); historical catalog fit uncertainty unknown.',fontsize=9)
    fig.tight_layout(rect=(0,.06,1,1));fig.savefig(E/'HD_LAB_COMBINATION_RESIDUALS.png',dpi=180);plt.close(fig)
    ratio=data['measured_based_LTE_ratios'];temps=[int(x['T_K']) for x in ratio]
    fig,ax=plt.subplots(figsize=(8.1,4.7))
    for key,label in [('LTE_nJ2_over_nJ0_from_measured_E2-E0','n(J=2)/n(J=0)'),('LTE_nJ3_over_nJ1_from_measured_E3-E1','n(J=3)/n(J=1)')]:
        ax.plot(temps,[float(x[key]) for x in ratio],marker='o',label=label)
    ax.set_yscale('log');ax.set_xticks(temps)
    ax.set_xlabel('Assumed thermal LTE temperature (K)');ax.set_ylabel('Conditional Boltzmann population ratio')
    ax.set_title('Laboratory-energy-anchored LTE ratios (not measured cosmic gas populations)');ax.legend()
    fig.tight_layout();fig.savefig(E/'HD_LAB_LTE_RATIOS.png',dpi=180);plt.close(fig)
    photons=data['radiative_lines']
    fig,ax=plt.subplots(figsize=(8.1,4.7))
    ax.plot([int(x['upper_J']) for x in photons],[float(x['photon_power_per_one_excited_molecule_W']) for x in photons],marker='o')
    ax.set_yscale('log');ax.set_xticks(range(1,9))
    ax.set_xlabel('Historical LAMDA v2 line: upper J');ax.set_ylabel('A h nu_print (W per excited HD molecule)')
    ax.set_title('Source-only photon radiative power, no gas occupancy/heat model')
    fig.tight_layout();fig.savefig(E/'HD_PINNED_PHOTON_POWER.png',dpi=180);plt.close(fig)
    print('generated',[(p.name,p.stat().st_size) for p in sorted(E.glob('HD_*.png'))])
if __name__=='__main__':main()
