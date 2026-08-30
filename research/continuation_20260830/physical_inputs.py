"""Additive reference helpers; not the PR34 COM replacement or restart route.

The moving-map JVP differentiates a DECLARED KL reconstruction, not atomic
physics. Snapshot envelopes bind all supplied dataclass fields, constants,
measure, frame and topology; the local source adapter must prove completeness.
"""
from dataclasses import asdict,is_dataclass
from fractions import Fraction
from hashlib import sha256
import json,math
import numpy as np


def canonical(value):
    if is_dataclass(value):return {'dataclass':type(value).__qualname__,'fields':canonical(asdict(value))}
    if isinstance(value,np.ndarray):
        if value.dtype.kind not in 'fiu' or not np.isfinite(value).all():raise ValueError('finite numeric arrays only')
        return {'shape':list(value.shape),'dtype':value.dtype.newbyteorder('<').str,'bytes':value.astype(value.dtype.newbyteorder('<')).tobytes(order='C').hex()}
    if isinstance(value,np.generic):return canonical(value.item())
    if value is None or type(value) in (bool,int,str):return value
    if isinstance(value,float):
        if not math.isfinite(value):raise ValueError('nonfinite scientific input')
        return {'binary64':value.hex()}
    if isinstance(value,Fraction):return {'rational':[str(value.numerator),str(value.denominator)]}
    if isinstance(value,(list,tuple)):return [canonical(x) for x in value]
    if isinstance(value,dict):
        if any(not isinstance(k,str) for k in value):raise ValueError('string keys required')
        return {k:canonical(value[k]) for k in sorted(value)}
    raise TypeError('unsupported scientific input; supply its explicit semantics')


def input_identity(inputs):
    required={'snapshot','frequency_measure','atomic_constants','source_provenance','frame','time_variable','event_topology'}
    if not isinstance(inputs,dict) or not required.issubset(inputs):raise ValueError('incomplete declared physical inputs')
    if not inputs['frame'] or not inputs['time_variable'] or not inputs['source_provenance']:
        raise ValueError('missing frame/time/source convention')
    data=json.dumps(canonical(inputs),sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    return sha256(data).hexdigest()


def seal_checkpoint(payload:bytes,inputs):
    if not isinstance(payload,bytes):raise TypeError('raw checkpoint bytes required')
    return {'schema':'declared-physical-input-envelope/v1','input_sha256':input_identity(inputs),
            'payload_sha256':sha256(payload).hexdigest(),'claim':'INPUT_BINDING_ONLY_NOT_COM_PHYSICS'}


def validate_checkpoint(payload:bytes,inputs,envelope):
    expected=seal_checkpoint(payload,inputs)
    if envelope!=expected:raise ValueError('checkpoint physical-input or payload mismatch')
    return payload


def moving_deposition_jvp(matrix,solution,d_matrix,d_target,d_log_prior):
    """dq for Mq=b, q=q0 exp(M^T lambda), allowing dM AND prior changes.

    Uses the same positive interior solution; O(m^3+m^2*n). This numerical
    derivative is not an interval enclosure. Rejects rank loss/ill conditioning.
    """
    M=np.array(matrix,dtype=float,copy=True);dM=np.asarray(d_matrix,dtype=float)
    if M.ndim!=2 or dM.shape!=M.shape:raise ValueError('matrix shapes')
    m,n=M.shape;q=np.asarray(solution.weights);lam=np.asarray(solution.dual)
    db=np.asarray(d_target,dtype=float);dlog=np.asarray(d_log_prior,dtype=float)
    if q.shape!=(n,) or lam.shape!=(m,) or db.shape!=(m,) or dlog.shape!=(n,):raise ValueError('JVP shapes')
    if not all(np.isfinite(v).all() for v in (M,dM,q,lam,db,dlog)) or np.any(q<=0):raise ValueError('finite interior inputs required')
    scales=np.max(abs(M),axis=1)
    if np.any(scales==0):raise ValueError('zero moment row')
    A=M/scales[:,None];H=(A*q[None,:])@A.T
    cond=float(np.linalg.cond(H))
    if not math.isfinite(cond) or cond>1e13:raise ArithmeticError('ill-conditioned moving-map derivative')
    direct=dlog+dM.T@lam
    rhs=(db-dM@q-M@(q*direct))/scales
    dl=np.linalg.solve(H,rhs)/scales
    dq=q*(direct+M.T@dl)
    if not np.isfinite(dq).all():raise ArithmeticError('derivative overflow')
    return dq
