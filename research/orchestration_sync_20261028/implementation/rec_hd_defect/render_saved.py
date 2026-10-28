"""Display saved signed source defects; no scientific execution replay."""
import json,pathlib
from fractions import Fraction as F
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=pathlib.Path(__file__).resolve().parent
d=json.loads((ROOT/'results.json').read_text());edges=d['edges'];x=[z['line_id'] for z in edges];hz=[float(F(z['signed_defect_Hz'])) for z in edges];energy=[float(F(z['signed_energy_defect_J_event-1']))*1e27 for z in edges]
plt.rcParams.update({'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False});fig,axs=plt.subplots(1,2,figsize=(12,5))
axs[0].bar(x,[z/1e6 for z in hz],color=['#216a88' if z>=0 else '#be694a' for z in hz]);axs[0].axhline(0,color='black',lw=.6);axs[0].set(xticks=x,xlabel='HD downward line j → j−1',ylabel='Signed frequency defect [MHz]',title='Literal photon minus level-gap frequency')
axs[1].bar(x,energy,color=['#216a88' if z>=0 else '#be694a' for z in energy]);axs[1].axhline(0,color='black',lw=.6);axs[1].set(xticks=x,xlabel='HD downward line j → j−1',ylabel='Signed energy mismatch [10⁻²⁷ J/event]',title='Energy ledger residual δᵢ = h dᵢ')
fig.suptitle('REC source-column defects • exact signed 8-line analysis',fontsize=14);fig.text(.5,.045,'Downward flux Rᵢ contributes δᵢRᵢ; upward flux reverses sign. This mismatch is not physical heating.',ha='center',fontsize=10);fig.text(.5,.01,'Printed-precision chain first becomes EMPTY at level 2. Original 35 Hz status and source columns remain unchanged.',ha='center',fontsize=9);fig.tight_layout(rect=(0,.09,1,.94));fig.savefig(ROOT/'DIAGNOSTIC.svg');fig.savefig(ROOT/'DIAGNOSTIC.png',dpi=130)
