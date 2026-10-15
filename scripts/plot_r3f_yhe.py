"""Read-only publication-style local diagnostic figures from source-native run."""
import argparse
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def run(data_dir:Path):
    path=data_dir/'SOURCE_DERIVATIVES_Z20_1600.csv'
    rows=list(csv.DictReader(path.open()))
    if len(rows)!=1581: raise ValueError('unverified full source derivative grid')
    z=[float(v['zbar']) for v in rows]
    x=[float(v['source_dln_ne_dYhe']) for v in rows]
    deriv=[float(v['dTm_K_dYhe_Richardson']) for v in rows]
    fig,ax=plt.subplots(figsize=(7,4.3))
    ax.plot(z,x,lw=1.7,label=r'Original HyRec 2012 FULL: $\partial_{Y_{\rm He}}\ln n_e$')
    ax.axhline(0,lw=0.8,linestyle=':')
    ax.set_xlabel('Mean FLRW redshift $z$')
    ax.set_ylabel(r'$\partial\ln n_e/\partial Y_{\rm He}$ (fixed $\omega_b$)')
    ax.set_xlim(min(z),max(z))
    ax.legend(frameon=False,fontsize=8)
    fig.tight_layout()
    fig.savefig(data_dir/'SOURCE_NE_YHE_SENSITIVITY.png',dpi=155)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4.3))
    ax.plot(z,deriv,lw=1.7,label=r'Original HyRec2012 FULL: $\partial_{Y_{\rm He}}T_m$')
    ax.axhline(0,lw=0.8,linestyle=':')
    ax.set_xlabel('Mean FLRW redshift $z$')
    ax.set_ylabel(r'$\partial T_m/\partial Y_{\rm He}$ [K]')
    ax.set_xlim(min(z),max(z))
    ax.legend(frameon=False,fontsize=8)
    fig.tight_layout()
    fig.savefig(data_dir/'SOURCE_TM_YHE_SENSITIVITY.png',dpi=155)
    plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path,required=True)
    run(p.parse_args().data_dir)
