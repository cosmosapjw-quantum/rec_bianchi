"""고정 원본 2s 표 + 명시적 제조 격자의 다중-bin 연구. 생산 provider 아님."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import sys
import zipfile
import numpy as np
import mpmath as mp

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'docs/research/rec_2s_base_hires_response'))
from check_response import parse_table
from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import (
    PhysicalTwoPhotonRamanBin, OriginalHyRecTwoPhotonRamanTable,
    A2S_THRESHOLD_EV, L2S_1S_S_INV,
)
from full_bianchi_hyrec.trajectory.com_source_deposition import COMSourceDepositionPlan

EV_J = 1.602176634e-19
H_PLANCK = 6.62607015e-34
E21_J = A2S_THRESHOLD_EV * EV_J
U = np.array([2.0**-30, .25, .5, .75, 1-2.0**-30])
MU = np.array([2., 4., 8., 4., 2.])
PINS = {
    'src/full_bianchi_hyrec/trajectory/hyrec_two_photon_raman.py': '26ddc41e24fadf0bdd19f1924e1a429d602d9c19',
    'src/full_bianchi_hyrec/trajectory/com_source_deposition.py': 'a3662cf399f14b7148d880266825be12baf934a0',
    'docs/research/rec_2s_base_hires_response/check_response.py': '9c0151a93ff1ec8fb1ee8738f75f188e7d719cd8',
    'docs/research/rec_2s_base_hires_response/INPUTS.json': '2fbfc82cfb36ebcd9d461b23efaf209b4d864eb2',
}


def weights(nodes, queries, logarithmic=False):
    """격자 내부 두 이웃만 사용. 투영, 외삽, 재정규화 없음."""
    nodes = np.asarray(nodes, dtype=float)
    q = np.asarray(queries, dtype=float)
    if nodes.ndim != 1 or q.ndim != 1 or len(nodes) < 2:
        raise ValueError('격자 shape')
    if not np.isfinite(q).all() or np.any(q < nodes[0]) or np.any(q > nodes[-1]):
        raise ValueError('격자 밖 source: 외삽하지 않음')
    if np.any(nodes <= 0) or np.any(np.diff(nodes) <= 0):
        raise ValueError('양의 증가 격자 필요')
    j = np.clip(np.searchsorted(nodes, q, side='right')-1, 0, len(nodes)-2)
    if logarithmic:
        t = (np.log(q)-np.log(nodes[j]))/(np.log(nodes[j+1])-np.log(nodes[j]))
    else:
        t = (q-nodes[j])/(nodes[j+1]-nodes[j])
    B = np.zeros((len(nodes), len(q)))
    B[j, np.arange(len(q))] = 1-t
    B[j+1, np.arange(len(q))] = t
    return B


def load_tables():
    lock = json.loads((ROOT / 'docs/research/rec_2s_base_hires_response/INPUTS.json').read_text())
    archive = ROOT / lock['archive']['path']
    if hashlib.sha256(archive.read_bytes()).hexdigest() != lock['archive']['sha256']:
        raise ValueError('원본 archive 불일치')
    base_loader = OriginalHyRecTwoPhotonRamanTable.from_archive(archive)
    tables = []
    with zipfile.ZipFile(archive) as z:
        for label in ('base', 'hires'):
            cfg = lock['tables'][label]['configuration']
            member = 'HyRec/' + cfg['TWOG_FILE']
            data = z.read(member)
            if hashlib.sha256(data).hexdigest() != lock['members'][member]['sha256']:
                raise ValueError('원본 표 불일치')
            tokens, values = parse_table(data, cfg['NVIRT'])
            n = cfg['NSUBLYA']
            ut = values[:n, 0] / A2S_THRESHOLD_EV
            raw = values[:n, 2].copy()
            if not (np.all(ut > .5) and np.all(ut < 1) and np.all(raw > 0)):
                raise ValueError('2s 행/계수 정의역')
            factor = L2S_1S_S_INV / float(np.sum(raw))
            normalized = raw * factor
            if label == 'base':
                if not np.array_equal(normalized, base_loader.A2s_s_inv[:n]):
                    raise ValueError('기존 base loader와 불일치')
                normalized = base_loader.A2s_s_inv[:n].copy()
            us = np.r_[ut, 1-ut]
            B = weights(U, us)
            plan = COMSourceDepositionPlan(MU, E21_J*U, E21_J*us, B,
                np.array([1.]), np.array([[0.,0.,1.]]),
                'manufactured_symmetric_five_node_measure', 'manufactured_linear_energy_partition')
            tables.append(dict(label=label, n=n, ut=ut, us=us, raw=raw,
                normalized=normalized, factor=factor, B=B,
                L=weights(U, us, True), D=B[:,:n]+B[:,n:], plan=plan,
                tokens=tokens[:n], member=member, sha256=lock['members'][member]['sha256']))
    return tables, lock


def state(eta=0., odd=0., even=0.):
    phi = 2*U + odd*U*(1-U)*(2*U-1) + even*U*(1-U)
    if np.any(phi <= 0):
        raise ValueError('제조 Bose 지수의 양성')
    y = -np.log(np.expm1(phi))
    ratio = math.exp(eta-2)
    xg = (9/16)/(1+ratio)
    # z=(y[5],xu,xg,common_rate_scale,nH,H)
    return np.r_[y, ratio*xg, xg, 1., 8., 4.]


def directions():
    mixed = np.array([1/32,-1/16,1/8,-1/32,1/64,1/64,-1/32,1/8,2.,1.])
    return [*(np.eye(10)[j] for j in (1,5,6,7,8,9)), mixed]


def compose(t, z, dz=None, kind='chi', normalization='normalized'):
    z = np.asarray(z)
    dz = np.zeros(10) if dz is None else np.asarray(dz)
    if z.shape != (10,) or dz.shape != (10,) or z.dtype.kind not in 'fiu' or dz.dtype.kind not in 'fiu':
        raise ValueError('실수 상태/방향 벡터10개 필요')
    z = z.astype(float, copy=True); dz = dz.astype(float, copy=True)
    if not np.isfinite(z).all() or not np.isfinite(dz).all() or np.any(z[5:] <= 0):
        raise ValueError('유한한 양의 population/rate/density/H 필요')
    if kind not in ('chi','log_control') or normalization not in ('raw','normalized'):
        raise ValueError('명시되지 않은 연구 연산')
    n = t['n']; xu,xg,scale,nH,H = z[5:]; du,dg,ds,dn,dH = dz[5:]
    with np.errstate(over='raise', divide='raise', invalid='raise', under='ignore'):
        f = np.exp(z[:5]); chi = np.logaddexp(0,-z[:5]); dchi = -dz[:5]/(1+f)
        if np.any(f <= 0) or not np.isfinite(f).all():
            raise ValueError('유한한 양의 nodal occupation 필요')
        if kind == 'chi':
            chi_read = t['B'].T @ chi
            legs = 1/np.expm1(chi_read)
            dlegs = -legs*(1+legs)*(t['B'].T @ dchi)
        else:
            legs = np.exp(t['L'].T @ z[:5])
            dlegs = legs*(t['L'].T @ dz[:5])
            chi_read = np.log1p(1/legs)
        rates = t[normalization]
        F=[]; R=[]; gam=[]; dgam=[]
        for b in range(n):
            pair = PhysicalTwoPhotonRamanBin('two_photon', float(scale*rates[b]),
                E21_J/H_PLANCK, E21_J*t['us'][n+b]/H_PLANCK,
                E21_J*t['us'][b]/H_PLANCK, float(xu), float(xg), 1.)
            ft,fc = float(legs[b]),float(legs[n+b])
            ff,rr = pair.paired_rates(companion_occupation=fc, tracked_occupation=ft)
            F.append(ff); R.append(rr); gam.append(pair.net_action(fc,ft))
            dgam.append(pair.jvp(companion_occupation=fc, tracked_occupation=ft,
                d_integrated_rate_s_inv=float(ds*rates[b]), d_upper_population=float(du),
                d_ground_population=float(dg), d_companion_occupation=float(dlegs[n+b]),
                d_tracked_occupation=float(dlegs[b])))
        F=np.array(F); R=np.array(R); gam=np.array(gam); dgam=np.array(dgam)
        C=t['plan'].apply(np.r_[gam,gam],nH)[:,0]
        dC=t['plan'].jvp(np.r_[gam,gam],np.r_[dgam,dgam],nH,dn)[:,0]
        S=math.fsum(gam); dS=math.fsum(dgam)
        G=C/(H*f); dG=dC/(H*f)-G*(dz[:5]+dH/H)
        atoms=np.array([-S,S])/H
        datoms=np.array([-dS,dS])/H-atoms*dH/H
        asc=math.log(xu/xg)+t['D'].T@chi
        aread=math.log(xu/xg)+chi_read[:n]+chi_read[n:]
        dasc=du/xu-dg/xg+t['D'].T@dchi
        sigma=math.fsum(gam*asc)
        dsigma=math.fsum(dgam*asc+gam*dasc)
        sigma_from_nodal=S*math.log(xu/xg)+float((MU/nH*chi)@C)
        val=np.r_[atoms,G,sigma]; tangent=np.r_[datoms,dG,dsigma]
        if not np.isfinite(np.r_[val,tangent,F,R,legs]).all():
            raise FloatingPointError('비유한 합성 결과')
    return dict(value=val,jvp=tangent,f=f,legs=legs,F=F,R=R,gamma=gam,dgamma=dgam,
        C=C,dC=dC,S=S,dS=dS,asc=asc,aread=aread,delta=aread-asc,
        sigma=sigma,dsigma=dsigma,sigma_from_nodal=sigma_from_nodal,
        read_entropy=math.fsum(gam*aread))


def reference(t, z, kind='chi', normalization='normalized'):
    """고정 binary64 B/L/a를 lift한 독립 고정밀 primal. API/JVP 호출 없음."""
    y=z[:5]; xu,xg,scale,nH,H=z[5:]; n=t['n']
    f=[mp.exp(x) for x in y]; chi=[mp.log1p(1/v) for v in f]
    mat=t['B'] if kind=='chi' else t['L']
    legs=[]
    for s in range(2*n):
        q=mp.fsum(mp.mpf(float(mat[i,s]))*(chi[i] if kind=='chi' else y[i]) for i in range(5))
        legs.append(1/mp.expm1(q) if kind=='chi' else mp.exp(q))
    gamma=[]
    for b in range(n):
        ft,fc=legs[b],legs[n+b]
        gamma.append(mp.mpf(float(t[normalization][b]))*scale*(xu*(1+ft)*(1+fc)-xg*ft*fc))
    S=mp.fsum(gamma)
    # 고정 float B의 두 열을 별도로 더해, model의 미리 합산한 D를 재사용하지 않는다.
    C=[nH/mp.mpf(float(MU[i]))*mp.fsum((mp.mpf(float(t['B'][i,b]))+mp.mpf(float(t['B'][i,n+b])))*gamma[b] for b in range(n)) for i in range(5)]
    sig=S*mp.log(xu/xg)+mp.fsum(mp.mpf(float(MU[i]))/nH*chi[i]*C[i] for i in range(5))
    return [-S/H,S/H,*[C[i]/(H*f[i]) for i in range(5)],sig]


def independent(t,z,dz,kind,dps=80,power=32):
    with mp.workdps(dps):
        zz=[mp.mpf(float(x)) for x in z]; dd=[mp.mpf(float(x)) for x in dz]
        h=mp.mpf(2)**(-power)
        primal=reference(t,zz,kind)
        plus=reference(t,[x+h*d for x,d in zip(zz,dd)],kind)
        minus=reference(t,[x-h*d for x,d in zip(zz,dd)],kind)
        return primal,[(a-b)/(2*h) for a,b in zip(plus,minus)]


def effective_defect(t):
    r=compose(t,state(),kind='log_control')
    n=t['n'];ft=r['legs'][:n];fc=r['legs'][n:];a=t['normalized']
    P=math.fsum(a*(1+ft)*(1+fc)); Q=math.fsum(a*ft*fc)
    return math.log(P/Q)-2
