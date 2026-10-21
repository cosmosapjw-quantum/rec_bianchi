"""Independent scalar audit of saved trajectory reduction; no solver import."""
from __future__ import annotations
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np


BASE = Path('/workspace/scratch/36ad4bc67b35/rec_bianchi/research/rec_rei_trajectory_reuse_20261021')
OUT = Path('/workspace/scratch/36ad4bc67b35/agent_theory')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    result = BASE/'results_verified'
    meta = json.loads((result/'INPUT_PROJECTION.json').read_text())
    summary = json.loads((result/'SUMMARY.json').read_text())
    root = Path(meta['source_root_at_ingest'])
    with np.load(result/'TRAJECTORY_ANALYSIS.npz', allow_pickle=False) as d:
        data = {k: d[k].copy() for k in d.files}
    axes, actual, predicted = (data[k] for k in ('axes','actual','predicted'))
    expected_axes = list(itertools.product((0.,.0003,.001,.003,.01,.03,.1),
        (-.0003,-.0001,0.,.0001,.0003),(-.001,-.0003,0.,.0003,.001)))
    assert list(map(tuple, axes)) == expected_axes
    assert actual.shape == predicted.shape == (175,153,3)
    keys = list(map(tuple, axes))
    support = np.array([m == 0. or r == 0. for _,m,r in keys])
    assert np.array_equal(support, data['support'])
    assert int(support.sum()) == 63
    index = {key:i for i,key in enumerate(keys)}
    scalar_prediction_max_error = 0.
    for i,(s,m,r) in enumerate(keys):
        for t in range(153):
            for k in range(3):
                if support[i]:
                    expected = float(actual[i,t,k])
                else:
                    expected = (float(actual[index[(s,m,0.)],t,k])
                        + float(actual[index[(s,0.,r)],t,k])
                        - float(actual[index[(s,0.,0.)],t,k]))
                scalar_prediction_max_error = max(scalar_prediction_max_error,
                    abs(expected - float(predicted[i,t,k])))
    assert scalar_prediction_max_error == 0.
    assert np.array_equal(actual[support], predicted[support])

    # Re-read all source arrays and calculate the signed shear independently.
    # The reducer module is intentionally not imported by this audit.
    max_saved_shear_norm_difference = 0.
    max_source_projection_difference = 0.
    raw_finite = True
    for i,record in enumerate(meta['cases']):
        assert record['nominal'] == axes[i].tolist()
        assert record['case_id'] == str(data['case_ids'][i])
        folder = root/'z2_extension/results/cases'/record['case_id']
        assert sha(folder/'raw.npz') == record['raw_sha256']
        with np.load(folder/'raw.npz',allow_pickle=False) as source:
            for name in ('x','a','H','s','elapsed_proper_s','P_m','P_r','P_total',
                         'Pi_matter_J_m3','Pi_gamma_J_m3','Pi_nu_J_m3','Sigma_F','raw_y'):
                raw_finite &= not np.iscomplexobj(source[name]) and bool(np.isfinite(source[name]).all())
            assert np.array_equal(source['x'],data['x'])
            assert np.array_equal(1/source['a']-1,data['z'])
            assert np.array_equal(source['elapsed_proper_s'],data['elapsed_proper_s'][i])
            signed = math.sqrt(6)*source['s']/source['H']
            max_saved_shear_norm_difference = max(max_saved_shear_norm_difference,
                float(abs(abs(signed)-source['Sigma_F']).max()))
            projected = np.column_stack([signed,source['P_m'],source['P_r']])
            max_source_projection_difference = max(max_source_projection_difference,
                float(abs(projected-actual[i]).max()))
    assert raw_finite
    assert max_source_projection_difference == 0.

    metric_names = ('S_F_signed','P_m_F_signed','P_r_F_signed',
                    'P_total_F_signed','Pi_total_F_norm')
    independently_measured = {}
    for component,name in enumerate(metric_names):
        points=[]
        peak=0.
        endpoint_peak=0.
        for i in np.flatnonzero(~support):
            for t in range(153):
                if component < 3:
                    observed,estimate = float(actual[i,t,component]),float(predicted[i,t,component])
                else:
                    observed = float(actual[i,t,1])+float(actual[i,t,2])
                    estimate = float(predicted[i,t,1])+float(predicted[i,t,2])
                    if component == 4:
                        observed,estimate = abs(observed),abs(estimate)
                difference = abs(observed-estimate)
                peak=max(peak,abs(observed))
                if t == 152: endpoint_peak=max(endpoint_peak,difference)
                points.append((difference,int(i),t))
        worst=max(points,key=lambda p:p[0])
        reported=summary['metrics'][name]
        assert worst[0] == reported['max_abs_difference']
        assert keys[worst[1]] == tuple(reported['max_at_nominal'])
        assert worst[2] == reported['max_at_epoch']
        assert endpoint_peak == reported['endpoint_max_abs_difference']
        assert peak == reported['signal_peak_abs']
        independently_measured[name] = {'max_abs_difference':worst[0],
            'max_at_nominal':axes[worst[1]].tolist(),'max_at_epoch':worst[2],
            'endpoint_max_abs_difference':endpoint_peak}
    total=actual[:,:,1]+actual[:,:,2]
    ptotal=predicted[:,:,1]+predicted[:,:,2]
    reverse_triangle_slack=abs(total-ptotal)-abs(abs(total)-abs(ptotal))
    assert float(reverse_triangle_slack.min()) == 0.

    with np.load(BASE/'results/TRAJECTORY_ANALYSIS.npz',allow_pickle=False) as old:
        arrays_identical = all(np.array_equal(old[k],v) for k,v in data.items())
    assert arrays_identical
    old_summary=json.loads((BASE/'results/SUMMARY.json').read_text())
    assert old_summary == summary
    record={
        'schema':'rec.independent_trajectory_result_audit.v1',
        'status':'PASS_SCOPED_SAVED_ARRAY_COMPARISON',
        'method':'independent scalar reconstruction and source projection; reducer not imported',
        'result_array_sha256':sha(result/'TRAJECTORY_ANALYSIS.npz'),
        'auditor_source_sha256':sha(Path(__file__)),
        'cases':175,'support_cases':63,'mixed_cases':112,'epochs':153,
        'all_source_fields_real_finite':raw_finite,
        'max_source_projection_difference':max_source_projection_difference,
        'max_scalar_prediction_difference':scalar_prediction_max_error,
        'support_reused_exactly':True,
        'max_saved_shear_norm_difference':max_saved_shear_norm_difference,
        'metrics':independently_measured,
        'min_reverse_triangle_slack':float(reverse_triangle_slack.min()),
        'old_and_guarded_result_arrays_equal':arrays_identical,
        'old_and_guarded_summaries_equal':True,
        'physical_integrations':0,'performance_comparison':'NOT_RUN',
        'physical':'HOLD','global_convergence':'NOT_RUN','production':'NOT_APPROVED'}
    (OUT/'C9_ACTUAL_RESULTS_AUDIT.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(json.dumps(record,indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
