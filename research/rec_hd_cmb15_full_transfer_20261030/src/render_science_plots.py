"""Independent scientific figures from exact source-derived CSV evidence."""
from pathlib import Path
import csv,argparse,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def rows(filename):
  with open(filename,encoding='utf8',newline='') as f:return list(csv.DictReader(f))

def render(root:Path):
  root=Path(root); ev=root/'evidence';dst=root/'figures';dst.mkdir(exist_ok=True)
  win=rows(ev/'J1_INVERSION_WINDOWS_SOURCE_BOUND.csv')
  curve=rows(ev/'J1_INVERSION_DENSITY_CURVES.csv')
  for z in (0.,100.):
    fig,ax=plt.subplots(figsize=(8,5))
    for name in ('std','alternate'):
      rs=[r for r in curve if r['source']==name and float(r['z'])==z]
      ax.semilogx([float(r['nH2_cm3']) for r in rs],
                  [float(r['J1_minus_g1p0']) for r in rs],label=name)
    ax.axhline(0,ls=':',lw=1)
    ax.set_xlim(1e2,1e5);ax.set_ylim(-0.25,0.08)
    ax.set(xlabel=r'$n_{\mathrm{H_2}}$ (cm$^{-3}$)',ylabel=r'$p_{J=1}-3p_{J=0}$',
       title=f'Neufeld2026 v2, HD J=1->0 inversion, Tgas=4000 K, z={z:g}')
    ax.legend();ax.grid(True,alpha=.25)
    fig.tight_layout();fig.savefig(dst/f'HD_J1_INVERSION_DENSITY_z{int(z)}.png',dpi=175);plt.close(fig)
  r0=rows(ev/'FULLLINE_SLAB_TRANSFER_ATLAS.csv')
  # Two physically distinct configurations, NO observed flux.
  for T,n,z,label in [(100.,100.,100.,'CMB_ABSORPTION'),(4000.,1e4,0.,'WARM_EXCESS')]:
    rs=[r for r in r0 if r['source']=='std' and float(r['Tgas_K'])==T
      and float(r['nH2_cm3'])==n and float(r['z'])==z
      and float(r['microturb_km_s'])==0 and float(r['N_HD_cm2'])==1e18]
    rs.sort(key=lambda r:int(r['upper_J']))
    fig,ax=plt.subplots(figsize=(8,5))
    data=[float(r['I_excess_formal_rest_W_m2_sr']) for r in rs]
    ax.plot([int(r['upper_J'])-1 for r in rs],data,marker='o')
    ax.set_yscale('symlog',linthresh=1e-28)
    ax.axhline(0,ls=':',lw=1)
    ax.set(xlabel='HD rotational line R(J)',ylabel=r'\Delta I_{\mathrm{line,rest}}$ (W m$^{-2}$ sr$^{-1}$)',
      title=f'Source-locked {label}, T={T:g} K, n={n:.0e} cm-3, z={z:g}, N(HD)=1e18 cm-2')
    ax.grid(True,alpha=.25)
    fig.tight_layout();fig.savefig(dst/f'HD_14LINE_{label}.png',dpi=175);plt.close(fig)
  tab=rows(ev/'FULLLINE_PER_TRANSITION_SUMMARY.csv')
  fig,ax=plt.subplots(figsize=(8,5))
  ax.plot([int(r['upper_J'])-1 for r in tab],
          [float(r['max_tau0']) for r in tab],marker='o',label='max optical depth over grid')
  ax.axhline(.1,linestyle='--',label='|tau0|=0.1 fixed-population screening')
  ax.set_yscale('log');ax.set(xlabel='HD rotational line R(J)',ylabel='Max positive line-center tau0',
      title='Original HD 15-level source, 1e14--1e20 cm-2: formal-slab screening')
  ax.legend();ax.grid(True,alpha=.25);fig.tight_layout()
  fig.savefig(dst/'HD_14LINE_OPACITY_SCREEN.png',dpi=175);plt.close(fig)
  return [str(x.name) for x in sorted(dst.glob('*.png'))]

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'))
 print('\n'.join(render(p.parse_args().root)))

# Deliberately invoked by the authoring script below, not an implicit new run.
def render_phase_windows(root):
  root=Path(root);rs=rows(root/'evidence/J1_INVERSION_T_Z_PHASE_WINDOWS.csv')
  selected=[r for r in rs if r['source']=='std' and r['has_J1_inversion']=='True']
  fig,ax=plt.subplots(figsize=(8,5))
  for z in (0.,50.,100.):
    group=[r for r in selected if float(r['z'])==z]
    if not group:continue
    # Plot only actual Neufeld source temperature knots, no temperature interpolant.
    x=[float(r['Tgas_K']) for r in group]
    ax.scatter(x,[float(r['n_inversion_on_cm3']) for r in group],label=f'onset z={z:g}')
    ax.scatter(x,[float(r['n_inversion_off_cm3']) for r in group],marker='x',label=f'offset z={z:g}')
  ax.set_yscale('log')
  ax.set(xlabel='Original rate-table Tgas knot (K)',ylabel=r'$n_{\mathrm{H_2}}$ (cm$^{-3}$)',
      title='Source-owned HD J1 inversion density windows; no interpolation between T knots')
  ax.legend(fontsize='small',ncol=2);ax.grid(True,alpha=.25)
  fig.tight_layout();fig.savefig(root/'figures/J1_INVERSION_T_Z_PHASE_WINDOWS.png',dpi=175);plt.close(fig)

if __name__=='__main__':
 # The general 14-line figures were created by render() above.
 import sys
 if '--root' in sys.argv:
    pos=sys.argv.index('--root'); root_arg=Path(sys.argv[pos+1])
 else:root_arg=Path('.')
 render_phase_windows(root_arg)
