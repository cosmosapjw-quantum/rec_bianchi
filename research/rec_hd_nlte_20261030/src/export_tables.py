from pathlib import Path
import csv,json
p=Path(__file__).resolve().parents[1]
a=json.loads((p/'evidence/NONLTE_GRID.json').read_text());s=json.loads((p/'data/LAMDA_HD_SOURCE_TRANSCRIPTION.json').read_text())
for name,keys,key in [
('J1_TWOLEVEL_COOLING.csv',['T_K','nH2_cm3','ortho_fraction','q10_cm3_s','q01_cm3_s','population_J1','cool_photon_W_per_HD','cool_gap_energy_W_per_HD','n_half_cooling_cm3'],'two_level_rows'),
('HD9_CONDITIONAL_COOLING.csv',['T_K','nH2_cm3','ortho_fraction','total_printed_power_W_per_HD','total_internal_gap_power_W_per_HD','power_difference_W_per_HD','minimum_population','stationary_residual_s1','valid_numerical_solution'],'full9_rows')]:
 with (p/'evidence'/name).open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
  for x in a[key]:writer.writerow({k:x[k] for k in keys})
with (p/'evidence'/'LAMDA54_COLLISION_VALUES.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['partner_id','partner','upper_J','lower_J','T_K','rate_cm3_s'])
 for label,spin in [('para_H2',2),('ortho_H2',3)]:
  for row in s['collision_partner_'+label]['rates_cm3_s1']:
   for T,v in zip(s['temperature_nodes_K'],row['values']):w.writerow([spin,label,row['upper_J'],row['lower_J'],T,v])
with (p/'evidence'/'HD9_PERLINE_PHOTON_OUTPUT.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['T_K','nH2_cm3','ortho_fraction','upper_J','nuP_Hz','nuE_Hz','population_upper','power_printed_W_per_HD','power_internal_W_per_HD'])
 for row in a['full9_rows']:
  for e in row['lines']:
   w.writerow([row['T_K'],row['nH2_cm3'],row['ortho_fraction'],e['upper_J'],e['nuP_Hz'],e['nuE_Hz'],e['population_upper'],e['power_printed_W_per_HD'],e['power_internal_gap_W_per_HD']])
print('csv: 54 collision rows, 63 twolevel, 63 full9, 504 line emissions')