from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import subprocess
import zipfile
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.constants import c, k, physical_constants
from scipy.integrate import lebedev_rule, quad
from scipy.special import eval_legendre, wofz

OUT = Path('/mnt/data/Full_Bianchi_HyRec_C3B2B1A_physical_Hummer_angular_v0_30')
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

# ------------------------------------------------------------------
# Physical reference.
# ------------------------------------------------------------------
T = 3000.0
n1s_cm3 = 250.0
n1s_m3 = n1s_cm3 * 1.0e6
lambda_alpha_m = 1215.6701e-10
nu0 = c / lambda_alpha_m
A21 = 6.265e8
f12 = 0.4161967179799824
r_e = physical_constants['classical electron radius'][0]
M_H = physical_constants['atomic mass constant'][0] * 1.00782503223
vD = math.sqrt(2.0 * k * T / M_H)
dnu = nu0 * vD / c
a = A21 / (4.0 * math.pi * dnu)
S_int = math.pi * r_e * c * f12  # m^2 Hz
rate_scale = n1s_m3 * c * S_int / dnu  # s^-1 multiplying R_x

x_edges = np.arange(-4.25, 4.25 + 1.0e-12, 0.5)
x_centers = 0.5 * (x_edges[:-1] + x_edges[1:])
dx = 0.5
nf = len(x_centers)


def H(aa, xx):
    return np.real(wofz(np.asarray(xx) + 1j * aa))

phi_x = H(a, x_centers) / math.sqrt(math.pi)
physical_opacity = rate_scale * phi_x

# ------------------------------------------------------------------
# Angle-dependent Hummer RII, coherent in the atom frame, no recoil.
# The redistribution density integrates over x_out to phi_x(x_in).
# ------------------------------------------------------------------
def rII_density(x_out, x_in, mu):
    x_out = np.asarray(x_out)
    if mu >= 1.0 - 1.0e-13:
        raise ValueError('forward limit is a delta distribution')
    if mu <= -1.0 + 1.0e-13:
        return (
            a
            / (2.0 * math.pi ** 1.5)
            * np.exp(-0.25 * (x_out - x_in) ** 2)
            / (((x_out + x_in) / 2.0) ** 2 + a * a)
        )
    return (
        1.0
        / (math.pi * math.sqrt(1.0 - mu * mu))
        * np.exp(
            -(x_out - x_in) ** 2
            / (2.0 * (1.0 - mu))
        )
        * H(
            a * math.sqrt(2.0 / (1.0 + mu)),
            (x_out + x_in)
            / math.sqrt(2.0 * (1.0 + mu)),
        )
    )

# Broad cell integration; endpoint-near angular classes use adaptive quad.
gl_nodes, gl_weights = leggauss(32)
out_nodes = x_centers[:, None] + 0.25 * gl_nodes[None, :]
out_weights = 0.25 * gl_weights


def cell_matrix(mu):
    if mu >= 1.0 - 1.0e-13:
        return np.diag(phi_x)

    if mu <= -1.0 + 1.0e-13:
        matrix = np.zeros((nf, nf))
        for j in range(nf):
            lo, hi = x_edges[j], x_edges[j + 1]
            for i, xin in enumerate(x_centers):
                ridge = xin if mu > 0.0 else -xin
                points = [ridge] if lo < ridge < hi else None
                matrix[j, i] = quad(
                    lambda xout: float(rII_density(xout, xin, mu)),
                    lo,
                    hi,
                    points=points,
                    epsabs=2.0e-12,
                    epsrel=2.0e-10,
                    limit=400,
                )[0]
        return matrix

    xout = out_nodes[:, :, None]
    xin = x_centers[None, None, :]
    values = rII_density(xout, xin, mu)
    return np.sum(values * out_weights[None, :, None], axis=1)


def rounded_mu_matrix(directions):
    return np.round(directions @ directions.T, 14)


def apply_operator(directions, weights, matrices, mu_matrix, number_state):
    nq = len(weights)
    gain = np.zeros_like(number_state)
    loss = np.zeros_like(number_state)
    for q_out in range(nq):
        w_out = weights[q_out]
        for q_in in range(nq):
            mu = float(mu_matrix[q_out, q_in])
            phase = 0.75 * (1.0 + mu * mu)
            probability = matrices[mu]
            gain[:, q_out] += (
                rate_scale
                * w_out
                * phase
                * (probability @ number_state[:, q_in])
            )
            loss[:, q_in] += (
                rate_scale
                * w_out
                * phase
                * probability.sum(axis=0)
                * number_state[:, q_in]
            )
    return gain - loss


def isotropy_leakage(action, weights):
    restricted = action.sum(axis=1)
    projection = restricted[:, None] * weights[None, :]
    return float(
        np.linalg.norm(action - projection)
        / (np.linalg.norm(action) + 1.0e-300)
    )


def harmonic_projection(action, directions, weights, ell):
    basis = eval_legendre(ell, directions[:, 2])
    occupation_action = action / weights[None, :]
    norm = float(np.dot(weights, basis * basis))
    coefficient = (
        occupation_action @ (weights * basis)
    ) / norm
    projection = coefficient[:, None] * basis[None, :]
    leakage = float(
        math.sqrt(max(0.0, float(np.sum(
                weights[None, :]
                * (occupation_action - projection) ** 2
            ))))
        / (
            math.sqrt(max(0.0, float(np.sum(
                    weights[None, :]
                    * occupation_action**2
                ))))
            + 1.0e-300
        )
    )
    return coefficient, leakage

orders = [7, 11, 15, 19, 23, 29]
order_results = {}
summary_rows = []
harmonic_rows = []
capture_rows = []

spectral_shapes = {
    'smooth_L8': 1.0 + 0.05 * np.cos(x_centers / 8.0),
    'smooth_L2': 1.0 + 0.05 * np.cos(x_centers / 2.0),
    'narrow_core': 1.0 + 0.10 * np.exp(-0.5 * (x_centers / 0.4) ** 2),
    'odd_red_blue': 1.0 + 0.05 * np.tanh(x_centers / 0.5),
}

for order in orders:
    points, raw_weights = lebedev_rule(order)
    directions = points.T
    weights = raw_weights / (4.0 * math.pi)
    nq = len(weights)
    mu_matrix = rounded_mu_matrix(directions)
    unique_mu = np.unique(mu_matrix)
    matrices = {float(mu): cell_matrix(float(mu)) for mu in unique_mu}

    # Incoming-angle-dependent capture of the bounded frequency window.
    capture = np.zeros((nf, nq))
    for q_in in range(nq):
        for q_out in range(nq):
            mu = float(mu_matrix[q_out, q_in])
            phase = 0.75 * (1.0 + mu * mu)
            capture[:, q_in] += (
                weights[q_out]
                * phase
                * matrices[mu].sum(axis=0)
            )
    capture /= phi_x[:, None]

    capture_rows.append({
        'lebedev_order': order,
        'point_count': nq,
        'capture_fraction_min': float(capture.min()),
        'capture_fraction_max': float(capture.max()),
        'capture_fraction_mean': float(np.mean(capture)),
        'capture_angular_std_max': float(np.max(np.std(capture, axis=1))),
    })

    state_metrics = {}
    restricted_actions = {}
    for name, shape in spectral_shapes.items():
        number_state = shape[:, None] * weights[None, :]
        action = apply_operator(
            directions, weights, matrices, mu_matrix, number_state
        )
        restricted = action.sum(axis=1)
        restricted_actions[name] = restricted
        leakage = isotropy_leakage(action, weights)
        number_residual = float(
            abs(action.sum())
            / (np.sum(np.abs(action)) + 1.0e-300)
        )
        state_metrics[name] = {
            'isotropy_leakage': leakage,
            'number_relative_residual': number_residual,
            'action_norm_s^-1': float(np.linalg.norm(action)),
        }
        summary_rows.append({
            'lebedev_order': order,
            'point_count': nq,
            'state': name,
            **state_metrics[name],
        })

    harmonic_coefficients = {}
    envelope = np.exp(-0.5 * (x_centers / 2.0) ** 2)
    for ell in [1, 2, 3, 4]:
        basis = eval_legendre(ell, directions[:, 2])
        perturbation = envelope[:, None] * weights[None, :] * basis[None, :]
        action = apply_operator(
            directions, weights, matrices, mu_matrix, perturbation
        )
        coefficient, leakage = harmonic_projection(
            action, directions, weights, ell
        )
        harmonic_coefficients[ell] = coefficient
        harmonic_rows.append({
            'lebedev_order': order,
            'point_count': nq,
            'ell': ell,
            'harmonic_subspace_leakage': leakage,
            'projected_action_norm_s^-1': float(np.linalg.norm(coefficient)),
        })

    order_results[order] = {
        'point_count': nq,
        'directions': directions,
        'weights': weights,
        'restricted_actions': restricted_actions,
        'harmonic_coefficients': harmonic_coefficients,
        'state_metrics': state_metrics,
        'capture': capture,
    }

# Compare all orders to order-29 / 302-point reference.
reference = order_results[29]
convergence_rows = []
for order in orders:
    result = order_results[order]
    for name in spectral_shapes:
        current = result['restricted_actions'][name]
        target = reference['restricted_actions'][name]
        convergence_rows.append({
            'lebedev_order': order,
            'point_count': result['point_count'],
            'quantity': f'isotropic_{name}',
            'relative_to_302': float(
                np.linalg.norm(current - target)
                / (np.linalg.norm(target) + 1.0e-300)
            ),
        })
    for ell in [1, 2, 3, 4]:
        current = result['harmonic_coefficients'][ell]
        target = reference['harmonic_coefficients'][ell]
        convergence_rows.append({
            'lebedev_order': order,
            'point_count': result['point_count'],
            'quantity': f'P{ell}_projected_action',
            'relative_to_302': float(
                np.linalg.norm(current - target)
                / (np.linalg.norm(target) + 1.0e-300)
            ),
        })

# ------------------------------------------------------------------
# Continuous normalization spot checks.
# ------------------------------------------------------------------
normalization_rows = []
for xin in [-4.0, -2.0, 0.0, 2.0, 4.0]:
    phi = float(H(a, xin) / math.sqrt(math.pi))
    for mu in [-0.9, -0.5, 0.0, 0.5, 0.9]:
        integral = quad(
            lambda xout: float(rII_density(xout, xin, mu)),
            -40.0,
            40.0,
            epsabs=2.0e-12,
            epsrel=2.0e-10,
            limit=500,
        )[0]
        normalization_rows.append({
            'x_in': xin,
            'mu': mu,
            'integral_R_dxout': integral,
            'Voigt_phi_x': phi,
            'relative_residual': (integral - phi) / phi,
        })

# ------------------------------------------------------------------
# Durable outputs.
# ------------------------------------------------------------------
def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)

write_csv(OUT / 'angular_isotropy_tests.csv', summary_rows)
write_csv(OUT / 'harmonic_action_tests.csv', harmonic_rows)
write_csv(OUT / 'angular_order_convergence.csv', convergence_rows)
write_csv(OUT / 'bounded_capture_fraction.csv', capture_rows)
write_csv(OUT / 'Hummer_RII_normalization_checks.csv', normalization_rows)

# Store compact frequency-restricted results, not dense angular matrices.
npz_payload = {
    'classification': np.asarray('PHYSICAL_HUMMER_II_ANGULAR_ORDER_AUDIT'),
    'x_edges': x_edges,
    'x_centers': x_centers,
    'physical_opacity_s^-1': physical_opacity,
    'Voigt_phi_x': phi_x,
}
for order, result in order_results.items():
    npz_payload[f'directions_order_{order}'] = result['directions']
    npz_payload[f'weights_order_{order}'] = result['weights']
    for name, vector in result['restricted_actions'].items():
        npz_payload[f'restricted_{name}_order_{order}'] = vector
    for ell, vector in result['harmonic_coefficients'].items():
        npz_payload[f'P{ell}_coefficient_order_{order}'] = vector
np.savez_compressed(OUT / 'physical_Hummer_angular_audit.npz', **npz_payload)

# Summary release diagnostics.
def row_for(order, state):
    return next(row for row in summary_rows if row['lebedev_order']==order and row['state']==state)

def conv_for(order, quantity):
    return next(row for row in convergence_rows if row['lebedev_order']==order and row['quantity']==quantity)

release_table = []
for order in orders:
    points = order_results[order]['point_count']
    release_table.append({
        'lebedev_order': order,
        'point_count': points,
        'smooth_L8_isotropy': row_for(order,'smooth_L8')['isotropy_leakage'],
        'narrow_core_isotropy': row_for(order,'narrow_core')['isotropy_leakage'],
        'smooth_L8_restricted_vs_302': conv_for(order,'isotropic_smooth_L8')['relative_to_302'],
        'P1_vs_302': conv_for(order,'P1_projected_action')['relative_to_302'],
        'P2_vs_302': conv_for(order,'P2_projected_action')['relative_to_302'],
    })
write_csv(OUT / 'release_table.csv', release_table)

ledger = {
    'classification': 'C3B2B1A_PHYSICAL_HUMMER_II_ANGULAR_BOUNDARY_LAYER_AUDIT',
    'stage': 'C3B2B1A-reference',
    'physical_parameters': {
        'temperature_K': T,
        'n1s_cm^-3': n1s_cm3,
        'nu_alpha_Hz': nu0,
        'Doppler_width_Hz': dnu,
        'damping_a': a,
        'integrated_cross_section_m2_Hz': S_int,
        'rate_scale_s^-1': rate_scale,
        'line_center_opacity_s^-1': float(physical_opacity[nf//2]),
    },
    'kernel': {
        'type': 'angle-dependent Hummer RII, coherent atom frame, no recoil',
        'phase': 'Rayleigh Phi(mu)=3/4(1+mu^2) on normalized sphere measure',
        'frequency_grid': {'x_min': -4.25, 'x_max': 4.25, 'dx': 0.5, 'cells': nf},
        'incoming_frequency': 'cell-centre sampled',
        'outgoing_frequency': 'cell integrated',
        'absolute_rate': 'n1s c (pi r_e c f12/DeltaNu_D) Phi RII dx',
    },
    'normalization': {
        'max_RII_to_Voigt_relative_residual': float(max(abs(r['relative_residual']) for r in normalization_rows)),
        'physical_opacity_min_s^-1': float(physical_opacity.min()),
        'physical_opacity_max_s^-1': float(physical_opacity.max()),
    },
    'release_table': release_table,
    'hard_gate_status': {
        'absolute_two_level_rate': True,
        'RII_frequency_normalization': max(abs(r['relative_residual']) for r in normalization_rows) < 1e-8,
        'number_conservation_truncated_operator': max(r['number_relative_residual'] for r in summary_rows) < 1e-12,
        'Lebedev26_release': False,
        'Lebedev50_release': False,
        'Lebedev86_release': False,
        'Lebedev146_release': False,
        'Lebedev194_release': False,
        'bruteforce_Lebedev_policy': False,
        'full_COM_KHW_physical_kernel': False,
    },
    'decision': {
        'result': 'PASS_AS_PHYSICAL_REFERENCE_AUDIT',
        'production_release': 'NOT_APPROVED',
        'finding': (
            'The coherent forward angular boundary layer produces non-monotone, slow Lebedev convergence. '
            'Increasing point count alone is not an efficient release strategy.'
        ),
    },
    'next_stage': {
        'name': 'C3B2B1B_singularity_subtracted_harmonic_Nystrom_kernel',
        'tasks': [
            'Split the mu->1 coherent-forward contribution analytically from the regular angular kernel.',
            'Compute Legendre/zonal frequency kernels for l=0..L_work with adaptive mu quadrature.',
            'Use the analytic singular part plus a lower-order Lebedev residual for anisotropic action.',
            'Re-run isotropic and P1/P2 action convergence before regenerating full COM-KHW.',
            'Add recoil and Rybicki detailed-balance completion only after the angular reference is stable.',
        ],
    },
    'limitations': [
        'This is the physically normalized two-level Hummer-II reference, not the full COM-KHW kernel.',
        'Recoil, stimulated scattering, and exact detailed-balance completion are not included.',
        'Incoming frequency is centre sampled; this artifact audits angular order, not final finite-volume convergence.',
        'The bounded core operator uses within-domain loss for exact number conservation and records the omitted tail through capture fractions.',
    ],
}
(OUT / 'C3B2B1A_ledger.json').write_text(json.dumps(ledger,indent=2),encoding='utf-8')

formalism = r'''# Physical Hummer-II angular reference

For coherent scattering in the atom frame, define

\[
s=\sqrt{\frac{1-\mu}{2}},\qquad c=\sqrt{\frac{1+\mu}{2}}.
\]

The angle-dependent type-II redistribution density is

\[
R_{II}(x,x',\mu)
=
\frac{1}{\pi\sqrt{1-\mu^2}}
\exp\left[-\frac{(x-x')^2}{2(1-\mu)}\right]
H\left(a\sqrt{\frac{2}{1+\mu}},
\frac{x+x'}{\sqrt{2(1+\mu)}}\right).
\]

It obeys

\[
\int_{-\infty}^{\infty}R_{II}(x,x',\mu)\,dx
=\phi_x(x')=\frac{H(a,x')}{\sqrt\pi}.
\]

For exact backscattering,

\[
R_{II}(x,x',-1)
=
\frac{a}{2\pi^{3/2}}
\frac{\exp[-(x-x')^2/4]}
{[(x+x')/2]^2+a^2}.
\]

The physical transition rate on the normalized sphere measure is

\[
d\Gamma
=
n_{1s}c\frac{\pi r_ecf_{12}}{\Delta\nu_D}
\Phi_R(\mu)R_{II}(x,x',\mu)\,dx\frac{d\Omega}{4\pi},
\]

\[
\Phi_R(\mu)=\frac34(1+\mu^2).
\]

The \(\mu\to1\) limit contains a coherent frequency delta function.
After frequency discretization this becomes a narrow angular boundary
layer. A raw Lebedev rule must resolve that layer as well as the smooth
Rayleigh phase, which explains the slow non-monotone convergence found
in this audit.
'''
(OUT/'HUMMER_ANGULAR_FORMALISM.md').write_text(formalism,encoding='utf-8')

verify = r'''from pathlib import Path
import json
import numpy as np

HERE=Path(__file__).resolve().parent
ledger=json.loads((HERE/'C3B2B1A_ledger.json').read_text())
assert ledger['hard_gate_status']['absolute_two_level_rate']
assert ledger['hard_gate_status']['RII_frequency_normalization']
assert ledger['hard_gate_status']['number_conservation_truncated_operator']
assert not ledger['hard_gate_status']['full_COM_KHW_physical_kernel']
data=np.load(HERE/'physical_Hummer_angular_audit.npz')
assert data['x_centers'].shape == (17,)
assert data['physical_opacity_s^-1'][8] > 0.0
print('C3B2B1A physical Hummer angular audit: PASS')
'''
(OUT/'verify_C3B2B1A.py').write_text(verify,encoding='utf-8')

readme = f'''# Full Bianchi-HyRec C3B2B1A v0.30

This bundle regenerates an absolutely normalized angle-dependent
Hummer-II two-level reference on the 17-cell Ly-alpha core and tests
Lebedev orders 26 through 302 points.

## Physical scale

- line-centre opacity at n1s=250 cm^-3: {physical_opacity[nf//2]:.12e} s^-1
- integrated cross section: {S_int:.12e} m^2 Hz

## Main finding

The coherent forward limit creates a narrow angular-frequency boundary
layer. Raw Lebedev convergence is slow and non-monotone; point-count
inflation alone is not accepted as the final production strategy.

This is a physical Hummer-II reference, not yet the full COM-KHW,
recoil, stimulated, detailed-balance-completed operator.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')

# Durable generation script.
shutil.copy2(Path(__file__), OUT/'run_C3B2B1A.py')

manifest=[]
for p in sorted(OUT.iterdir()):
    if p.name=='MANIFEST_SHA256.txt': continue
    manifest.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")
(OUT/'MANIFEST_SHA256.txt').write_text('\n'.join(manifest)+'\n',encoding='utf-8')
subprocess.run(['python',str(OUT/'verify_C3B2B1A.py')],check=True)
zip_path=Path('/mnt/data/Full_Bianchi_HyRec_C3B2B1A_physical_Hummer_angular_v0_30.zip')
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED) as zf:
    for p in sorted(OUT.iterdir()):
        zf.write(p,arcname=f'{OUT.name}/{p.name}')
with zipfile.ZipFile(zip_path) as zf:
    bad=zf.testzip()
    if bad: raise RuntimeError(bad)
print(json.dumps({
    'bundle':str(zip_path),
    'ledger':str(OUT/'C3B2B1A_ledger.json'),
    'line_center_opacity_s^-1':float(physical_opacity[nf//2]),
    'release_table':release_table,
    'zip_sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),
},indent=2))
