"""Plot saved results only. Sparse J are discrete points, not interpolated curves."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'results/RESULT.json').read_text())['data']
x=[z['upper_J'] for z in data]
fig,ax=plt.subplots(2,1,figsize=(8.2,8.2),layout='constrained',sharex=True)
res=[float(z['signed_delta_hz'])/1e6 for z in data]
ax[0].scatter(x,res,s=45,label='Level gap minus line frequency')
ax[0].axhline(0,color='black',linewidth=.8)
ax[0].set_ylabel('Signed defect / MHz')
ax[0].set_title('HD: fixed LAMDA 2021-06-07 source, CDMS v2 attributed')
for T,marker in [(50,'o'),(100,'s'),(200,'^')]:
 y=[float(z['thermal'][str(T)]['Kirchhoff_ratio_minus_1'])*1e6 for z in data]
 ax[1].scatter(x,y,s=45,marker=marker,label=f'{T} K')
ax[1].axhline(0,color='black',linewidth=.8)
ax[1].set_xlabel('Upper rotational quantum number J')
ax[1].set_ylabel(r'$10^6\,(j_\nu/(\alpha_\nu B_\nu)-1)$')
ax[1].legend(frameon=False,ncols=3)
ax[1].set_xticks(range(1,9))
for a in ax:a.grid(alpha=.2)
out=ROOT/'figures/HD_SOURCE_CROSS_ENERGY.png'
fig.savefig(out,dpi=180,bbox_inches='tight');fig.savefig(out.with_suffix('.pdf'),bbox_inches='tight');print(out)
