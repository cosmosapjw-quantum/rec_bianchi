#!/usr/bin/env python3
"""Only stored rows. No physical inference from interpolated T or density."""
import json, argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p=argparse.ArgumentParser();p.add_argument('--result',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
a=json.loads(args.result.read_text());rows=a['rows'];d=min(r['pH2_and_oH2_density_each_cm3'] for r in rows)
fig,ax=plt.subplots(2,1,figsize=(8,8),layout='constrained')
for T in (50,100,200):
 r=next(r for r in rows if r['T_K']==T and r['pH2_and_oH2_density_each_cm3']==d)
 x=[p['line'] for p in r['pairs']];y=[float(p['A_rad_down_col_up'])*1e6 for p in r['pairs']]
 ax[0].scatter(x,y,s=42,label=f'{T} K')
ax[0].axhline(0,lw=.8)
ax[0].set_xticks(range(1,9));ax[0].set_xlabel('Upper rotational quantum number J')
ax[0].set_ylabel(r'$10^6\,\mathcal{A}_{\mathrm{rad}\downarrow,\mathrm{col}\uparrow}$')
ax[0].set_title('HD: source-locked channel cycle affinities');ax[0].legend(ncols=3)
for den in (1000,1000000):
 subset=[r for r in rows if r['pH2_and_oH2_density_each_cm3']==den]
 x=[r['T_K'] for r in subset];y=[float(r['original_source_sigma_formal_per_s']) for r in subset]
 ax[1].scatter(x,y,s=55,label=rf'$n_{{p}}=n_{{o}}=10^{{{3 if den==1000 else 6}}}$ cm$^{{-3}}$')
ax[1].set_xticks([50,100,200]);ax[1].set_yscale('log')
ax[1].set_xlabel('Fixed tabulated temperature (K)')
ax[1].set_ylabel(r'Formal $\sigma/k_B$ per molecule (s$^{-1}$)')
ax[1].set_title('Synthetic same-T two-bath Markov stationary diagnostic')
ax[1].legend()
for b in ax:b.grid(alpha=.22)
args.out.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(args.out,dpi=170,bbox_inches='tight')
fig.savefig(args.out.with_suffix('.pdf'),bbox_inches='tight')
print(json.dumps({'png':str(args.out),'pdf':str(args.out.with_suffix('.pdf')),'source':'RESULT.json only','data_connected':False}))
