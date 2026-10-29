"""Pure, deterministic synthetic policy-sensitivity figure and evidence writer."""
from __future__ import annotations
from decimal import Decimal, getcontext
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from source_policy_firewall import exact_fixed_phi_policy_ratios, covariance_free_gap_sd_bounds

ROOT=Path(__file__).resolve().parent
getcontext().prec=80
nu=Fraction(5331561951400,1)  # Frozen PR156 J=2->1 printed ordinary frequency, Hz
out=[]
for eps in [-1000000,-100000,-10000,0,10000,100000,1000000]:
 ratios=exact_fixed_phi_policy_ratios(nu,eps)
 out.append({'delta_Hz':eps, 'ratios': {k:f'{x.numerator}/{x.denominator}' for k,x in ratios.items()},
             'relative_ppm':{k:str(Decimal(1000000)*(Decimal(v.numerator)/Decimal(v.denominator)-1)) for k,v in ratios.items()}})
unit=[str(x) for x in covariance_free_gap_sd_bounds('0.000001','0.000002')]
result={
 'schema':'REC_HD_PINNED_ADAPTER_SOURCE_POLICY_FIREWALL_V1',
 'date_kst':'2026-10-29',
 'repo_parent':'cosmosapjw-quantum/rec_bianchi',
 'parent_commit':'8806a4f757d916b6cf040625be931a66e2f0f6fe',
 'parent_tree':'7254269c5f8bcb198638f542d2d4545ecd647d20',
 'newly_added_actual_consumer':{'path':'research/program_expansion_20261025/hd_adapter/lamda_hd.py',
       'git_blob':'632a8a094e7eedd24a1ec3132fec20765d6e39da',
       'classification':'RESEARCH_SCOPED_PINNED_LAMDA_HD_ADAPTER_WITH_DISCONNECTED_DIRECT_BRIDGE',
       'mapping':'einstein_B, line_coefficients, thermal_line use printed nu_P; require_energy_frequency_bridge separate',
       'physical_promotion':False},
 'source_provenance':{'LAMDA_hd_sha256':'0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb',
                     'LAMDA_bytes':2289,'CDMS_v2_raw':'NOT_ACQUIRED','CDMS_v3_auto_substitution':False},
 'frozen_gate':{'hz':35,'pass_line_ids':[1],'fail_line_ids':[2,3,4,5,6,7,8], 'original':'FAIL_7_OF_8'},
 'math':{
    'fixed_A_populations_phi_per_Hz':{'B_ratio':'r^-3','emission_ratio':'r','opacity_ratio':'r^-2','source_function_ratio':'r^3','r':'(nu+delta)/nu'},
    'covariance_free_sd_interval_Hz':'[100c*abs(sigma_u-sigma_l),100c*(sigma_u+sigma_l)]',
    'SD_example_marginal_cm1':['0.000001','0.000002'], 'SD_bounds_example_Hz':unit,
    'uncertainty_interpretation':'Conditional covariance-free bounds assuming correlated joint Gaussian-like finite-second-moment fit errors; not actual .egy/CDMS source error or CI.'},
 'synthetic_policy_sweep':{'J_upper':2,'J_lower':1,'nu_P_Hz':str(nu),'records':out},
 'tests':{'mock_guard':'17/17 PASS', 'actual_private_adapter_invocation':'NOT_RUN: original private raw source and pinned module bytes not present locally'},
 'production':'HOLD','REI_activation':False,'H5_epsilon':None,
 'canonical_DAG':'28/88 (+0)','REC_physical_DAG':'0/313 (+0)',
 'native_distinct_author_review':'NOT_RUN',
 'no_prior_full_suite_or_IVP_reruns':True,
}
(ROOT/'evidence'/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(6.8,3.8))
    xx=[x['delta_Hz']/1e6 for x in out]
    for name in ('B_ul','j_nu','alpha_nu','source_function'):
        yy=[float(x['relative_ppm'][name]) for x in out]
        ax.plot(xx,yy,marker='.',label=name)
    ax.axhline(0,linewidth=0.6)
    ax.set_xlabel('Synthetic shift of printed HD J=2→1 line frequency (MHz)')
    ax.set_ylabel('Fixed-profile coefficient response (ppm)')
    ax.set_title('Conditional policy sensitivity; not a physical correction')
    ax.legend(ncol=2,fontsize=8)
    fig.tight_layout()
    fig.savefig(ROOT/'evidence'/'FIXED_PHI_POLICY_SWEEP.png',dpi=155)
    plt.close(fig)
except ImportError:
    pass
print(json.dumps({'rows':len(out),'max_ppm_response':max(abs(float(x['relative_ppm']['source_function'])) for x in out),'bounds_Hz':unit}))
