"""Generic represented-matrix certifier adapted verbatim from RESP01; no native owner import."""
import numpy as np
import interval as iv

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

