"""Scientific diagnostic figure from generated source-owned CSVs."""
import csv, argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def go(root):
 root=Path(root)
 with (root/'evidence/MIRI_SOURCE_NUISANCE_PROFILE_140.csv').open() as f:r=list(csv.DictReader(f))
 fig,ax=plt.subplots(figsize=(8,5.1))
 for T in (1000,2000,3000,4000):
  rows=sorted((x for x in r if float(x['T_alt_K'])==T and float(x['z'])==0.),key=lambda x:float(x['n_alt_cm3']))
  ax.plot([float(x['n_alt_cm3']) for x in rows],[float(x['T_and_density_profile_logspread']) for x in rows],marker='o',label=f'T={T} K')
 ax.set_xscale('log');ax.set_yscale('symlog',linthresh=1e-5)
 ax.set_xlabel(r'H$_2$ collider density $n_{H_2}$ [cm$^{-3}$]')
 ax.set_ylabel('log-ratio shape spread after T,density profiling')
 ax.set_title('Neufeld 2026 v2: MIRI-accessible HD six-line source contrast, z=0')
 ax.legend(frameon=False);ax.grid(alpha=.2)
 fig.tight_layout();fig.savefig(root/'figures/MIRI_SIXLINE_SOURCE_PROFILE.png',dpi=180);plt.close(fig)
 with (root/'evidence/MIRI_MRS_REDSHIFT_COVERAGE.csv').open() as f:cov=list(csv.DictReader(f))
 fig,ax=plt.subplots(figsize=(8,3.8))
 z=np.array([float(q['z']) for q in cov]);n=np.array([int(q['observable_line_count']) for q in cov])
 ax.step(z,n,where='post');ax.plot(z,n,'o');ax.set_ylim(-.2,6.5);ax.set_xlim(0,1.3)
 ax.set_xlabel('redshift z');ax.set_ylabel('geometrically accessible lines R(4)–R(9)')
 ax.set_title('JWST/MIRI MRS effective 4.9–27.9 µm, geometric only')
 ax.grid(alpha=.25);fig.tight_layout();fig.savefig(root/'figures/MIRI_SIXLINE_BANDPASS_GRID.png',dpi=180);plt.close(fig)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));go(p.parse_args().root)
