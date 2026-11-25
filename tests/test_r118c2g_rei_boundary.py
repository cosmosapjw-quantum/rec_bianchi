from pathlib import Path
from full_bianchi_hyrec.trajectory.standalone import independent_history
from full_bianchi_hyrec.trajectory.independent_rei_boundary import shared_handoff
ROOT=Path(__file__).resolve().parents[1]
RATES=ROOT/'archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip'
def test_shared_handoff_uses_own_history(tmp_path):
    # Minimal exact scenario schema as in original AX01 lock.
    import json
    s=tmp_path/'scenario.json'
    s.write_text(json.dumps(dict(schema="rei.axbi.scenario_lock.v1",cosmology=dict(h0_km_s_mpc=67.4,omega_m=.315,omega_r=.000092,omega_b_formula="0.0224/(0.674^2)",helium_mass_fraction=.2454,tcmb0_k=2.7255),interval=dict(zbar_start=20.),gas_initial=dict(kind="DECLARED_APPROXIMATE_CONDITIONAL_IC_NOT_REC_DONOR",x_HII=.0002,x_HeII=0.,x_HeIII=0.,temperature_k_formula="2.7255*21^2/(150*(0.0224/0.023)^0.4)"))))
    h=shared_handoff(RATES,s,points=51,rtol=1e-9,atol=1e-11)
    assert h['schema']=='rec_bianchi.rei_initial_state/1'
    assert h['history']['external_history'] is False
    q=h['initial']
    assert q['z']==20 and 0<q['x_HII']<1 and q['T_m_K']>0
    assert q['x_HeII']==q['x_HeIII']==0
    assert q['n_H_m3']==h['history']['states'][-1]['n_H_m3']
    assert h['background']['f_He']==.2454/(4*(1-.2454))
