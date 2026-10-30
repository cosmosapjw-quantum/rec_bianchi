"""Original physical plots of conditional CMB bath predictions, no fitted data."""
from pathlib import Path
import importlib.util
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
M=Path(__file__).with_name('hd_cmb_balance.py')
spec=importlib.util.spec_from_file_location('hd_cmb_balance',M)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=Path(__file__).resolve().parents[1]
s,_=m.load_sources(base/'input/LAMDA_HD_PR161_SOURCE_TRANSCRIPTION.json',base/'input/SUNG_HD_PR164_SOURCE.json')
for typ in ('twolevel','full9'):
    fig, ax=plt.subplots(figsize=(8.3,4.9))
    zs=list(range(0,56,1))
    for T in (50,100,200):
        ys=[]
        for z in zs:
            b=m.T0*(1+z)
            r=getattr(m,typ)(s,T,'10000','0.5',b)
            ys.append(float(r['net'])*1e29)
        ax.plot(zs,ys,label=f'Tgas = {T} K')
    ax.axhline(0,linewidth=.7)
    ax.set_xlabel('CMB redshift z (assumed blackbody bath)')
    ax.set_ylabel('Net radiation transfer (10^-29 W / HD molecule)')
    ax.set_title('HD J1 source-gated CMB net cooling' if typ=='twolevel' else 'HD nine-level exploratory diagnostic (35 Hz gate FAIL7/8)')
    ax.legend()
    fig.tight_layout()
    fig.savefig(base/'evidence'/f'FIG_{typ}_CMB_BALANCE.png',dpi=160)
    plt.close(fig)
    print(typ,'plot saved')
