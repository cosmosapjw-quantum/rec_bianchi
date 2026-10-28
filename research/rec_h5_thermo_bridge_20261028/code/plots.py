#!/usr/bin/env python3
"""Saved-data-only plot; no science computation or input mutation."""
import argparse,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--points',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();rows=sorted([json.loads(l) for l in a.points.read_text().splitlines()],key=lambda x:float(x['z']))
    z=np.array([float(r['z']) for r in rows]);
    dx=np.array([float(r['dF_dxe_fixed_xHII']) for r in rows]);
    ds=np.array([float(r['dF_dln_nH_plus_dln_H']) for r in rows]);
    err=np.array([float(r['adjoint_vs_primal_error']) for r in rows]);
    err2=np.array([float(r['common_scaling_exact_identity_error']) for r in rows]);
    fig,ax=plt.subplots(2,1,figsize=(7.0,7.5),sharex=True,layout='constrained')
    ax[0].plot(z,dx,linestyle='None',marker='.',markersize=3.4,label=r'$\partial_{x_e} F|_{x_{\mathrm{HII}},P_\perp,u}$')
    ax[0].plot(z,ds,linestyle='None',marker='.',markersize=3.4,label=r'$(\partial_{\ln n_H}+\partial_{\ln H})F$')
    ax[0].set_ylabel(r'Dimensionless $F$ derivative');ax[0].legend(loc='best',fontsize=9);ax[0].grid(alpha=.25)
    ax[1].plot(z,err,linestyle='None',marker='.',markersize=3.3,label='adjoint vs primal, absolute')
    ax[1].plot(z,err2,linestyle='None',marker='.',markersize=3.3,label='common-scaling identity, absolute')
    ax[1].axhline(1e-60,linestyle='--',color='black',lw=1,label='frozen scoped gate')
    ax[1].set_yscale('log');ax[1].set_ylabel('Absolute discrepancy');ax[1].set_xlabel('Stored redshift z');ax[1].grid(alpha=.25);ax[1].legend(loc='best',fontsize=9)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(a.out,dpi=220);fig.savefig(a.out.with_suffix('.pdf'));plt.close(fig)
    print(str(a.out))
if __name__=='__main__':main()
