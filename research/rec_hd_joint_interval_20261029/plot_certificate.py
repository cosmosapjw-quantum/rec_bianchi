"""Render saved exact certificate; floating values serve display only."""
from pathlib import Path
import json
from fractions import Fraction
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.fonttype']='none'
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm
p=Path(__file__).resolve().parent
c=json.loads((p/'results/JOINT_CERTIFICATE.json').read_text())
a=np.full((8,8),np.nan)
for r in c['all_segments']['segments']:
 a[r['p'],r['q']-1]=float(Fraction(r['required_scale']))
fig,ax=plt.subplots(figsize=(9,6.3))
im=ax.imshow(a,origin='lower',norm=LogNorm(vmin=.1,vmax=1e5),cmap='viridis',aspect='equal')
ax.set_xticks(range(8),range(1,9));ax.set_yticks(range(8),range(8));ax.set_xlabel('Last level q');ax.set_ylabel('First level p')
ax.set_title('HD common-level consistency: all 36 contiguous intervals',pad=13)
for i in range(8):
 for k in range(i,8):
  v=a[i,k];ax.text(k,i,f'{v:.2g}',ha='center',va='center',fontsize=8,color='white' if v<600 else 'black')
ax.scatter([5],[5],marker='s',s=720,facecolors='none',edgecolors='#ef5656',linewidths=2.5)
cb=fig.colorbar(im,ax=ax,pad=.04);cb.set_label('Required common enclosure scale (dimensionless)')
fig.text(.5,.075,'Maximum: (p,q) = (5,6),  scale = 52,247.340357...; nominal printing scale = 1',ha='center',fontsize=10)
fig.text(.5,.037,'Exact-rational source diagnostic. Original 35 Hz gate retained; physical source choice remains open.',ha='center',fontsize=9)
fig.subplots_adjust(bottom=.17,top=.89,left=.10,right=.87)
fig.savefig(p/'results/joint_enclosure_scale.png',dpi=170)
fig.savefig(p/'results/joint_enclosure_scale.svg')
plt.close(fig)
