"""Independent small source/derivative audit; does not integrate an ODE."""
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'
import numpy as np

ROOT = Path('/workspace/scratch/36ad4bc67b35/rec_bianchi/research/rec_rei_tangent_20261021')
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'code'))
from owner_model import make_model
from tangent_core import TangentOperator
from canonical_fv import CanonicalMomentumFV

spec = importlib.util.spec_from_file_location('published_c21n', OUT / 'C21N_mass_shell_derivatives.py')
c21n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c21n)


def scaled_error(got, expected):
    return float(np.max(np.abs(got - expected) / (1 + np.abs(expected))))


def fd5(fun, step):
    return (fun(-2*step) - 8*fun(-step) + 8*fun(step) - fun(2*step))/(12*step)


def source_obs(model, x, y):
    fields = model.fields(x, y)
    factor = math.sqrt(6) * (8*math.pi*6.67430e-11/299792458.0**2)/fields['H']**2
    out = np.array([math.sqrt(6)*fields['s']/fields['H'],
        factor*fields['Pi_matter_J_m3'],
        factor*(fields['Pi_gamma_J_m3']+fields['Pi_nu_J_m3']), 0.])
    out[3] = out[1]+out[2]
    return out


def shifted_A(model, da):
    shifted = copy.copy(model)
    p = model.momentum
    shifted.momentum = CanonicalMomentumFV(p.mass, p.amplitude+da, 24, 12, 3)
    return shifted


def main():
    fixture = np.load(ROOT / 'inputs/STORED_STATE_FIXTURE.npz', allow_pickle=False)
    digest_before = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                     for name in ('code/tangent_core.py','code/owner_model.py','CONTRACT_KO.md')}
    rng = np.random.default_rng(20261021)
    rows = []
    for case, epoch in ((0, 0), (13, 2), (31, 4)):
        axes = fixture['axes'][case]
        x, y = float(fixture['x'][case, epoch]), fixture['y'][case, epoch]
        model, seeds = make_model(*axes)
        prep = TangentOperator(model).prepare(x, y)
        direction = rng.normal(size=40)*.03
        direction[3] = 0.
        da = .2
        jvp = prep.jvp(direction, da)
        rhs_fd = fd5(lambda h: shifted_A(model, h*da).rhs(x, y+h*direction), 5e-5)
        obs_fd = fd5(lambda h: source_obs(shifted_A(model,h*da),x,y+h*direction),5e-5)
        covector = rng.normal(size=40)
        jy, ja = prep.vjp(covector)
        left, right = float(covector@jvp), float(jy@direction+ja*da)
        p0 = c21n.packet_derivatives(model.momentum, x, float(y[1]), 0.)
        p1 = c21n.packet_derivatives(model.momentum, x, float(y[1]), 1.)
        moment = prep.moment_data
        row = {
            'case_index':case,'epoch_index':epoch,'axes':axes.tolist(),'x':x,
            'case_id':str(fixture['case_ids'][case]),
            'rhs_source_scaled_error':scaled_error(prep.rhs,model.rhs(x,y)),
            'signed_observables_source_scaled_error':scaled_error(prep.observables_signed,source_obs(model,x,y)),
            'joint_state_amplitude_jvp_fd5_scaled_error':scaled_error(jvp,rhs_fd),
            'observable_joint_jvp_fd5_scaled_error':scaled_error(prep.observable_jvp(direction,da),obs_fd),
            'transpose_scaled_residual':abs(left-right)/(1+abs(left)+abs(right)),
            'rho_b_published_C21N_direction_difference':float(moment['rho_b']-(p1['rho_eta']-p0['rho_eta'])),
            'pi_b_published_C21N_direction_difference':float(moment['pi_b']-(p1['pi_s_eta']-p0['pi_s_eta'])),
            'pi_b':moment['pi_b'],
            'rho_reference_normalization_derivative':moment['reference_energy_norm_A'],
        }
        rows.append(row)
        assert row['rhs_source_scaled_error']<2e-13
        assert row['signed_observables_source_scaled_error']<2e-13
        assert row['joint_state_amplitude_jvp_fd5_scaled_error']<2e-8
        assert row['observable_joint_jvp_fd5_scaled_error']<2e-8
        assert row['transpose_scaled_residual']<512*np.finfo(float).eps
        assert row['pi_b']<=0
    initial_rows = []
    for point in ((.003,.0001,-.001),(0.,.0003,-.0003)):
        model, seeds = make_model(*point)
        direction = np.array([.03,1e-4,-2e-4])
        state_fd = fd5(lambda h:make_model(*(np.array(point)+h*direction))[0].initial_state(),1e-4)
        amp_fd = fd5(lambda h:make_model(*(np.array(point)+h*direction))[1].amplitude,1e-4)
        row = {'axes':list(point),
            'initial_state_fd5_scaled_error':scaled_error(seeds.initial_tangents@direction,state_fd),
            'amplitude_fd5_scaled_error':scaled_error(seeds.amplitude_gradient@direction,amp_fd),
            'zero_shear_signed_extension_probe':point[0]==0}
        assert row['initial_state_fd5_scaled_error']<2e-9
        assert row['amplitude_fd5_scaled_error']<2e-9
        initial_rows.append(row)
    digest_after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in digest_before}
    result = {'status':'PASS_SCOPED_LOCAL_DERIVATIVE', 'new_ODE':0,'benchmark':0,
        'independent_reviewer':'/root/next_theory_scope',
        'source_checks':'Original pinned model RHS/fields, 5-point joint state+amplitude finite differences; published C21N directional derivative subtraction; separately expanded transpose.',
        'files_before':digest_before,'files_after':digest_after,
        'files_stable_during_checks':digest_before==digest_after,
        'stored_state_point_checks':rows,'initial_map_checks':initial_rows,
        'source_rhs_calls':15,
        'scope':'Three stored states and two initial maps; independent spot audit, not the full 200-state validation and not trajectory convergence.'}
    (OUT/'C9_POINT_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
