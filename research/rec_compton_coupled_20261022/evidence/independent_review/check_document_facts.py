"""Final written-claim spot checks beyond the complete saved-result review.

Reads arrays and records only; no ODE, model evaluator or old-suite execution.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
from pathlib import Path
import hashlib
import json
import numpy as np
from scipy.integrate import simpson

U=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
    with np.load(p,allow_pickle=False) as d:return {k:d[k].copy() for k in d.files}

def main():
    facts=json.loads((U/'evidence/REPORT_FACTS.json').read_text())
    summary=json.loads((U/'results/analysis_v1/SUMMARY.json').read_text())
    for p,h in facts['inputs'].items():assert sha(U/p)==h
    checked={}
    for seed,wanted_species in (('s03_m03_r03',20),('s04_m04_r04',16)):
        label=seed+'_actual_hot_refined';folder=U/'results/compton8'/label
        a=load(folder/'trajectory.npz');b=load(U.parent/'rec_thermal_moments_20261022/results/thermal8'/(seed+'_mao2017_refined')/'trajectory.npz');dense=load(folder/'dense_1025.npz')
        c=facts['primary'][label];s=summary['cases'][label]
        delta=a['raw_state'][:,40:61]-b['raw_state'][:,40:61];ij=np.unravel_index(np.argmax(abs(delta)),delta.shape)
        assert ij[1]==wanted_species==c['ionic_detail']['species_index']
        assert float(delta[ij])==c['ionic_detail']['max_fraction_difference'] and float(a['z'][ij[0]])==c['ionic_detail']['at_z']
        dtau=float(a['raw_state'][-1,61]-b['raw_state'][-1,61]);cum=100*dtau/b['raw_state'][-1,61];inc=100*dtau/(b['raw_state'][-1,61]-b['raw_state'][0,61])
        assert np.isclose(cum,c['delta_tau_end_percent_of_cumulative'],rtol=5e-14)
        assert np.isclose(inc,c['delta_tau_end_percent_of_restart_increment'],rtol=5e-14)
        d={k:dense['diagnostics'][:,j] for j,k in enumerate(dense['diagnostic_names'])}
        K=6.6524587051e-29/(9.1093837139e-31*299792458.);kb=1.380649e-23;ev=1.602176634e-19
        # These bath moments are retained diagnostic inputs; the completed
        # results check independently reconstructed them from their owners.
        names=[k for k in d if 'compton' in k or 'energy_density' in k]
        # The same-path algebra can also be recovered without additional bath
        # evaluator calls: Qref = -A_ref*T + A_ref*Tr, with Tr=2.7255/a.
        T=dense['T_K'];Tr=2.7255/(np.exp(dense['x'])/21)
        Qr=d['compton_planck_reference_W_m3'];Qh=d['compton_actual_hot_W_m3']
        ref_recoil=Qr*Tr/(Tr-T);replacement=(Qr-ref_recoil)-Qh
        den=d['nb_m3']*d['H_s']*ev
        ints={'density_replacement':float(simpson(replacement/den,x=dense['x'])),'reference_recoil':float(simpson(ref_recoil/den,x=dense['x']))}
        for k,v in ints.items():assert np.isclose(v,c['source_owner_decomposition_eV_per_baryon'][k],rtol=5e-11,atol=1e-14)
        collision=s['collisions']['energy_eV_per_baryon']
        fractions={k:collision[k]['continuation_or_boundary_absolute_throughput']/collision[k]['absolute_throughput_trapezoid'] for k in ('ci_kinetic','ce_HI')}
        ratio=100*abs(c['energy_eV_per_baryon']['compton_selected'])/c['energy_eV_per_baryon']['photo_primary']
        assert ratio==c['compton_over_primary_heat_percent']
        checked[label]=dict(maximum_conditional_fraction_species_index=int(ij[1]),maximum_conditional_fraction_signed=float(delta[ij]),at_z=float(a['z'][ij[0]]),tau_end=float(a['raw_state'][-1,61]),tau_delta=dtau,percent_of_cumulative=float(cum),percent_of_restart_increment=float(inc),same_path_source_decomposition_eV=ints,collision_continuation_throughput_fraction=fractions,compton_percent_of_primary_heat=ratio)
    rs=[json.loads(p.read_text()) for p in sorted((U/'results/compton8').glob('s*/RESULT.json'))]
    timing={k:sum(r[k] for r in rs) for k in ('wall_seconds','integration_wall_seconds','diagnostics_and_persistence_wall_seconds')}
    mapping={'wall_seconds':'case_wall_sum_seconds','integration_wall_seconds':'integration_wall_sum_seconds','diagnostics_and_persistence_wall_seconds':'diagnostics_persistence_wall_sum_seconds'}
    for k,f in mapping.items():assert abs(timing[k]-facts['totals'][f])<1e-10
    assert sum(r['accepted_nodes'] for r in rs)==2994
    print(json.dumps(dict(status='PASS_DOCUMENT_FACT_SPOTCHECKS',documents={n:sha(U/n) for n in ('REPORT_KO.md','HANDOFF_KO.md','STAGE_C.md','LOOP_EVIDENCE_KO.md','NEXT_UNIT_CONTRACT.md')},facts_sha256=sha(U/'evidence/REPORT_FACTS.json'),additional_facts=checked,timing_sums=timing,new_ODE_runs=0,old_suite_reruns=0),indent=2))

if __name__=='__main__':main()
