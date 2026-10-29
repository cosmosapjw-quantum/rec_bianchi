from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'evidence/CROSSWALK.json').read_text())
rows=r['source_lines']
fig,ax=plt.subplots(figsize=(7.4,3.4))
xs=[j['J_upper'] for j in rows]
y=[float(j['egy_gap_minus_photon_Hz'])/1000 for j in rows]
ax.bar(xs,y)
ax.axhline(0,linewidth=.7)
ax.set_xlabel('HD ground-state transition, upper J')
ax.set_ylabel('2011 CDMS .egy gap − 2021 photon (kHz)')
ax.set_title('Historical printed-level crosswalk (not fit uncertainty)')
fig.tight_layout();fig.savefig(ROOT/'evidence/PRINTED_GAP_RESIDUALS.png',dpi=160);plt.close(fig)

fig,ax=plt.subplots(figsize=(7.4,3.4))
o=[float(j['photon_cumulative_level_minus_egy_cm1'])*1e6 for j in rows]
ax.plot(xs,o,'o-')
ax.axhline(.5,linestyle='--');ax.axhline(-.5,linestyle='--')
ax.axhline(0,linewidth=.7)
ax.set_xlabel('J, cumulative source-photon level from E0=0')
ax.set_ylabel('E* − printed 2011 CDMS .egy (10⁻⁶ cm⁻¹)')
ax.set_title('ONE 9-level vector fits all CDMS print cells, 8/8')
fig.tight_layout();fig.savefig(ROOT/'evidence/GLOBAL_PRINT_CELL_COMPATIBILITY.png',dpi=160);plt.close(fig)