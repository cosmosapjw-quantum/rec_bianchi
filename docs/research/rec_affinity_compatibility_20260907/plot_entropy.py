"""Plot exact manufactured curves and separately identified API observations."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--result', required=True, type=Path)
parser.add_argument('--out', required=True, type=Path)
args = parser.parse_args()
data = json.loads(args.result.read_text())
if data['classification'] != 'PASS_BOUNDED_AFFINITY_DISCRIMINATOR':
    raise ValueError('Expected accepted discriminator data')
args.out.mkdir(parents=True, exist_ok=True)

eta = np.linspace(-.25, .25, 401)
xg = (9/16)/(1+np.exp(eta)/8)
xu = xg*np.exp(eta)/8
gamma_chi = (8*xu-xg)/3
gamma_log = 2*xu*(1+1/np.sqrt(15))-xg/np.sqrt(15)
eta0 = np.log(4/(1+np.sqrt(15)))
plt.rcParams.update({'font.size': 8, 'axes.labelsize': 9, 'legend.fontsize': 8,
                     'xtick.labelsize': 8, 'ytick.labelsize': 8, 'svg.fonttype': 'none'})
fig, ax = plt.subplots(figsize=(3.54, 2.95), layout='constrained')
ax.axvspan(eta0, 0, color='#C76B64', alpha=.13, zorder=0)
ax.axhline(0, color='.35', linewidth=.7)
ax.axvline(eta0, color='#AD5048', linestyle=':', linewidth=1)
ax.plot(eta, 1e3*eta*gamma_chi, color='#007C83', label=r'Matched $\chi$ read')
ax.plot(eta, 1e3*eta*gamma_log, color='#AA3D41', linestyle='--', label=r'Log-$f$ control')
for kind, color, marker in [('chi', '#007C83', 'o'), ('log_control', '#AA3D41', 's')]:
    rows = [r for r in data['observations']['cases'] if r['read_kind'] == kind]
    ax.scatter([r['eta'] for r in rows], [1e3*r['entropy_rate'] for r in rows],
               color=color, marker=marker, s=19, edgecolors='white', linewidth=.35, zorder=4)
ax.set(xlim=(-.26, .26), xlabel=r'$\eta=\ln(8x_u/x_g)$',
       ylabel=r'$10^3\,\mathrm{d}[S/(N_H k_B)]/\mathrm{d}t\quad[\mathrm{s}^{-1}]$')
ax.legend(loc='upper left', frameon=False)
ax.spines[['top', 'right']].set_visible(False)
fig.savefig(args.out/'entropy_compatibility.png', dpi=240)
svg = args.out/'entropy_compatibility.svg'
fig.savefig(svg)
# SVG path whitespace is lexical separation; retain newlines, trim line tails.
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
plt.close(fig)
