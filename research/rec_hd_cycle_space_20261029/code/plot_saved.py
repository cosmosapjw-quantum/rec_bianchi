from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1]
a=json.loads((root/'results/RESULT.json').read_text())
point={p['T_K']:p for p in a['sample_cases'] if p['n_pH2_each_cm3']==1000}
fig,axes=plt.subplots(2,1,figsize=(8,7),layout='constrained')
for T,p in point.items():
    vals=[float(x)*1e6 for x in p['source_defect_affinity_up_orientation']]
    axes[0].scatter(list(range(1,9)),vals,label=f'{T} K')
axes[0].axhline(0,linewidth=.8,color='black');axes[0].legend(frameon=False,ncols=3)
axes[0].set_xlabel('Upper rotational quantum number J')
axes[0].set_ylabel(r'$10^6\,\beta(\Delta E-h\nu)$')
axes[0].set_title('Eight source-column defects, sampled at original LAMDA T nodes')
axes[0].set_xticks(range(1,9));axes[0].grid(alpha=.2)
axes[1].bar(['Marked channels','Cycle space','Driven rank','All-source-null'],[26,18,8,10])
axes[1].set_ylim(0,28);axes[1].set_ylabel('Exact integer dimension / count')
axes[1].set_title('Graph structure (not physical species or rate coverage)')
for y,rect in zip([26,18,8,10],axes[1].patches):
    axes[1].annotate(str(y),(rect.get_x()+rect.get_width()/2,y),xytext=(0,4),textcoords='offset points',ha='center')
axes[1].grid(axis='y',alpha=.2)
out=root/'results/CYCLE_SPACE_SOURCE_DEFECT.png'
fig.savefig(out,dpi=155)
print(out)
