"""Two physics figures from the pinned original-source derived ratio grid."""
from pathlib import Path
import csv
import matplotlib.pyplot as plt

def main(root:Path):
    root=Path(root)
    with (root/'evidence/SIXLINE_1800_SOURCE_RATIO_CASES.csv').open(newline='') as f:
        rows=list(csv.DictReader(f))
    fig,ax=plt.subplots(figsize=(9,5))
    for T in (1000.,2000.,3000.,4000.):
        x=sorted((r for r in rows if float(r['Tgas_K'])==T and float(r['z'])==0 and r['ratio_name']=='R(9)/R(7)'),key=lambda r:float(r['nH2_cm3']))
        ax.plot([float(v['nH2_cm3']) for v in x],[100*float(v['relative_source_delta']) for v in x],marker='o',label=f'{int(T)} K')
    ax.set_xscale('log');ax.set_xlabel(r'H$_2$ collider density (cm$^{-3}$)');ax.set_ylabel('Alternative/standard HD R(9)/R(7) change (%)')
    ax.set_title('Original Neufeld 2026 high-J extrapolation sensitivity (z=0)');ax.legend(title='Gas temperature');ax.grid(True,alpha=.25)
    fig.tight_layout();fig.savefig(root/'figures/FIG_R9_R7_DENSITY_SOURCE_SENSITIVITY.png',dpi=175);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5))
    for pair in ['R(9)/R(7)','R(9)/R(4)']:
        s=sorted((r for r in rows if r['ratio_name']==pair and float(r['Tgas_K'])==1000 and float(r['nH2_cm3'])==1e6),key=lambda r:float(r['z']))
        ax.plot([float(x['z']) for x in s],[100*float(x['relative_source_delta']) for x in s],marker='o',label=pair)
    ax.set_xlabel('CMB redshift z');ax.set_ylabel('Alternative/standard source-ratio change (%)')
    ax.set_title('Source extrapolation effect vs CMB background (1000 K, nH2=1e6)');ax.grid(True,alpha=.25);ax.legend()
    fig.tight_layout();fig.savefig(root/'figures/FIG_TWO_LINE_RATIOS_REDSHIFT.png',dpi=175);plt.close(fig)

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--root',type=Path,required=True)
    main(a.parse_args().root)
