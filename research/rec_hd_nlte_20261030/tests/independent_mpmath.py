"""Independent 80-digit generator & steady solution from source literals, no hd_nlte imports."""
import json, sys
from pathlib import Path
import mpmath as mp
root=Path(__file__).resolve().parents[1]
src=json.loads((root/'data/LAMDA_HD_SOURCE_TRANSCRIPTION.json').read_text())
data=json.loads((root/'evidence/NONLTE_GRID.json').read_text())
mp.mp.dps=80
h=mp.mpf('6.62607015e-34'); c=mp.mpf('299792458');kb=mp.mpf('1.380649e-23')
E=[mp.mpf(x['E_cm1'])*h*c*100 for x in src['levels']]
A=[mp.mpf(x['A_s1']) for x in src['radiative_lines']]
nu=[mp.mpf(x['nu_GHz'])*mp.mpf('1e9') for x in src['radiative_lines']]
rows=[]
for x in data['full9_rows']:
 T=mp.mpf(x['T_K']); n=mp.mpf(x['nH2_cm3']); f=mp.mpf(str(x['ortho_fraction']))
 M=mp.matrix(9,9)
 def add(u,l,rate):
  M[l,u]+=rate;M[u,u]-=rate
 for j,a in enumerate(A,start=1):add(j,j-1,a)
 for pair in zip(src['collision_partner_para_H2']['rates_cm3_s1'],src['collision_partner_ortho_H2']['rates_cm3_s1']):
  pp,oo=pair;u=pp['upper_J'];l=pp['lower_J'];index=src['temperature_nodes_K'].index(int(T))
  q=(1-f)*mp.mpf(pp['values'][index])+f*mp.mpf(oo['values'][index]); downward=n*q
  upward=downward*mp.mpf(2*u+1)/mp.mpf(2*l+1)*mp.exp(-(E[u]-E[l])/(kb*T))
  add(u,l,downward);add(l,u,upward)
 B=mp.matrix(M); bb=mp.matrix(9,1)
 for j in range(9):B[8,j]=1
 bb[8]=1
 P=mp.lu_solve(B,bb)
 power=sum(P[j]*A[j-1]*h*nu[j-1] for j in range(1,9))
 reported=mp.mpf(str(x['total_printed_power_W_per_HD']))
 if reported==0:
  rel=mp.mpf('0') if power==0 else mp.inf
 else:rel=abs((power-reported)/power)
 pop_diff=max(abs(P[j]-mp.mpf(str(x['populations'][j]))) for j in range(9))
 rows.append(dict(T=int(T),n=int(n),f=float(f),rel_cooling_error=float(rel),max_population_abs_error=float(pop_diff),mp_min_population=float(min(P)),mp_cooling=float(power)))
summary={"schema":"HD_NONLTE_INDEPENDENT_MPMATH_V1","precision_digits":mp.mp.dps,"compared_rows":len(rows),"max_relative_cooling_error":max(y['rel_cooling_error'] for y in rows),"max_population_absolute_error":max(y['max_population_abs_error'] for y in rows),"min_mpmath_population":min(y['mp_min_population'] for y in rows),"worst_relative_cooling_row":max(rows,key=lambda y:y['rel_cooling_error']),"worst_population_row":max(rows,key=lambda y:y['max_population_abs_error'])}
(root/'evidence/INDEPENDENT_MPMATH.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
assert len(rows)==63
assert summary['max_relative_cooling_error'] < 3e-9
assert summary['max_population_absolute_error'] < 3e-9
assert summary['min_mpmath_population']>=0