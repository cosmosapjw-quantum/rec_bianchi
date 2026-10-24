"""Native source-owned coefficient representation and inverse-residual enclosure."""
import csv
import math
from pathlib import Path
import sys
import numpy as np
import interval as iv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor'))
import history_boundary as native


def load():
    return native.load_frozen(ROOT/'inputs/target_native_snapshot.csv', ROOT/'inputs/PREPARED_BLOCKS.npz')


def coefficients(f):
    M = f._M.copy(); B = np.zeros((313, 313))
    T = np.zeros((314, 313)); P = np.zeros((314, 313))
    B[0, 312] = 3*f.r0*f.x1s*1.664786871919931
    B[1, 311] = 3*f.r0*f.x1s
    B[np.arange(311)+2, np.arange(311)] = f._tvv[0]*f.x1s*(1-f._one_minus_P)
    owners = []
    for b in range(311):
        if f._tau[b] <= 1e-30:
            P[b, b] = 1
            owners.append({'row': b, 'branch': 'tau<=1e-30', 'native_owner': 'FrozenHistoryMap.outgoing virtual bypass'})
            continue
        factor = -f._A[b]/(f.x1s*f._one_minus_P[b]*f._tvv[0, b])
        T[b, :2] = factor*f._tvr[:, b]
        if b > 0:
            T[b, b+1] = factor*f._tvv[1, b]
        if b < 310:
            T[b, b+3] = factor*f._tvv[2, b]
        P[b, b] = 1-f._A[b]
        owners.append({'row': b, 'branch': 'native_A_then_equilibrium', 'native_owner': 'hydrogen.c fminus_from_fplus / FrozenHistoryMap.outgoing'})
    T[311, 1] = 1/(3*f.x1s)
    T[312, 0] = math.exp(-native.E32/f.TR)/f.x1s
    T[313, 0] = math.exp(-native.E42/f.TR)/f.x1s
    owners += [{'row': 311, 'branch': 'opaque_Lyalpha', 'native_owner': 'xr_2p/(3*x1s)'},
               {'row': 312, 'branch': 'Lybeta', 'native_owner': 'xr_2s*exp(-E32/TR)/x1s'},
               {'row': 313, 'branch': 'Lygamma', 'native_owner': 'xr_2s*exp(-E42/TR)/x1s'}]
    iv.finite(M, B, T, P)
    return M, B, T, P, owners


def certify(M, B, T, P, V, Z, products=None):
    products = {} if products is None else products
    def dot(name, a, b):
        bound = iv.point_dot(a, b)
        products[name] = (a, b, bound)
        return bound
    ZM = dot('ZM', Z, M)
    Q = iv.sub(iv.point(np.eye(M.shape[0])), ZM)
    Qabs = iv.abs_bounds(Q)[1]
    rho = float(np.max(iv.sum_bounds(iv.point(Qabs))[1]))
    if rho >= 1:
        return {'status': 'CERTIFICATE_FAILURE_RHO', 'rho': rho}, {'Qlo': Q[0], 'Qhi': Q[1]}
    MV = dot('MV', M, V)
    R = iv.sub(iv.point(B), MV)
    Rabs = iv.abs_bounds(R)[1]
    Pr = dot('ABSZ_ABSR', np.abs(Z), Rabs)
    sigma = np.maximum(0.0, np.max(Pr[1], axis=0))
    denominator_lower = float(iv.down(1.0-rho))
    error = iv.positive_div_upper(sigma, denominator_lower)
    TV = dot('TV', T, V)
    K0 = iv.add(TV, iv.point(P))
    t = np.maximum(0, iv.sum_bounds(iv.point(np.abs(T)))[1])
    widening = iv.up(t[:, None]*error[None, :])
    Klo = iv.down(K0[0]-widening); Khi = iv.up(K0[1]+widening)
    gainlo, gainhi = iv.sum_bounds(iv.abs_bounds((Klo, Khi)))
    gainlo = np.maximum(0, gainlo)
    return {'status': 'CERTIFIED_REPRESENTED_BINARY64_OPERATOR', 'rho': rho,
            'denominator_lower': denominator_lower, 'norm_lower': float(np.max(gainlo)),
            'norm_upper': float(np.max(gainhi))}, {
                'Qlo': Q[0], 'Qhi': Q[1], 'Rlo': R[0], 'Rhi': R[1],
                'residual_product_upper': Pr[1], 'column_error_upper': error,
                'T_abs_rowsum_upper': t, 'Klo': Klo, 'Khi': Khi,
                'row_gain_lower': gainlo, 'row_gain_upper': gainhi}


def query_records(f):
    meta = {}
    with (ROOT/'inputs/target_native_snapshot.csv').open(newline='') as handle:
        for row in csv.reader(handle):
            if row and row[0] == 'META':
                meta[row[1]] = float(row[2])
    source, targets, sources = native.native_links(f.energies)
    z_face = meta['z']; eta_face = -math.log1p(z_face)
    return [{'incoming_index': j, 'source_index': int(source[j]),
             'target_energy_eV': float(targets[j]), 'source_energy_eV': float(sources[j]),
             'eta_face': eta_face, 'eta_emit': -math.log((1+z_face)*float(sources[j])/float(targets[j])),
             'z_emit': (1+z_face)*float(sources[j])/float(targets[j])-1,
             'epsilon_physical': None} for j in range(313)]


def event_coefficients(f, Khat, Klo, Khi):
    delta = np.zeros(313); delta[311] = 1
    jump = iv.sub((Klo[311], Khi[311]), iv.point(delta))
    # Each factor product is widened: no rounded factor is silently treated as exact.
    gn = iv.mul(iv.point(3.0e6), iv.point(native.LYA_FACT))
    rate_factor = iv.mul(gn, iv.point(f.H))
    number = iv.mul(rate_factor, jump)
    energy_factor = iv.mul(iv.point(native.E21), iv.point(native.EV_J))
    radiation = iv.mul(energy_factor, number)
    atomic = iv.neg(radiation)
    c = (3.0e6*native.LYA_FACT)*f.H*(Khat[311]-delta)
    rad = (native.E21*native.EV_J)*c
    return {'number_hat': c, 'number_lo': number[0], 'number_hi': number[1],
            'radiation_hat': rad, 'radiation_lo': radiation[0], 'radiation_hi': radiation[1],
            'atomic_hat': -rad, 'atomic_lo': atomic[0], 'atomic_hi': atomic[1]}
