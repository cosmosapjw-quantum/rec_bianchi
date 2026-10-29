import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
p=Path(__file__).resolve().parents[1]; d=json.loads((p/'evidence/RESULT.json').read_text())
r=d['rows']; js=[int(x['J_upper']) for x in r]
val=np.array([float(x['nu_E_minus_nu_P_Hz_decimal']) for x in r])
upper=np.array([float(x['recoil_2u_upper_Hz']) for x in r]);lower=np.array([float(x['recoil_3u_reference_Hz']) for x in r])
fig,axes=plt.subplots(1,2,figsize=(11.5,4.8),layout='constrained')
a,b=axes
a.semilogy(js,np.abs(val),'o-',label='|LAMDA printed − level gap|')
a.semilogy(js,upper,'s--',label='Recoil magnitude upper (M >= 2 u)')
a.semilogy(js,lower,'^:',label='Reference recoil (M = 3 u)')
a.axhline(35,linewidth=1,linestyle=':',label='Frozen 35 Hz gate')
a.set(xlabel='Upper J of J→J−1',ylabel='Frequency magnitude (Hz)',title='Source field mismatch vs recoil-only scale')
a.set_xticks(js); a.grid(alpha=.2);a.legend(fontsize=8,loc='best')
b.plot(js,val,'o-',label='ν_E−ν_P (source literal)')
b.fill_between(js,-upper,upper,alpha=.15,label='± recoil magnitude bound (M >= 2 u)')
b.axhline(0,linewidth=.8)
b.set(xlabel='Upper J of J→J−1',ylabel='Signed ordinary-frequency difference (Hz)',title='Sign and kinematic magnitude')
b.set_xticks(js);b.grid(alpha=.2);b.legend(fontsize=8,loc='upper left')
fig.suptitle('Conditional free-emission/absorption recoil diagnostic; NOT an error bar or CDMS source choice',fontsize=11)
out=p/'evidence/RECOIL_BOUND.png';fig.savefig(out,dpi=210)
print(out)
