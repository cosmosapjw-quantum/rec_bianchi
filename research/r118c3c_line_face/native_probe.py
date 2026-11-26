import json
from pathlib import Path
import numpy as np
from full_bianchi_hyrec.trajectory.full_2012_atomic_source import _canonical_twophoton_table
from full_bianchi_hyrec.recoil.original_hyrec_native import populate_original_hyrec_diffusion,build_native_diffusion_network,schur_reduce_line_centre,inferred_log_cell_edges_eV,inferred_photon_mode_measure_m3,physical_number_map_residual
D=Path(__file__).resolve().parent;R=Path('archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip');p=D.parent/'r118c2w_causal/FULL_128.npz';a=np.load(p);tab=_canonical_twophoton_table(R);rows=[]
for k in (96,104,112):
 rates=populate_original_hyrec_diffusion(np.column_stack((tab.energy_eV,tab.integrated_rates_s_inv.T)),float(a['T'][k]));net=build_native_diffusion_network(rates);reduced=schur_reduce_line_centre(net)
 g=inferred_photon_mode_measure_m3(inferred_log_cell_edges_eV(tab.energy_eV))
 z=np.exp(-(tab.energy_eV[140]-10.198714553953742)/rates.temperature_eV)
 rows.append(dict(k=k,Adn=float(rates.Adn_s_inv[140]),A2p=float(rates.A2p_up_s_inv),detailed_balance_relative=float(abs(rates.Adn_s_inv[140]*z/3/rates.A2p_up_s_inv-1)),physical_null_defect=float(physical_number_map_residual(reduced,g))))
print(rows);(D/'PROBE.json').write_text(json.dumps(rows,indent=2)+'\n')
