"""연구용 고정 제조 map만 사용한다. 생산 보간법이나 공급자가 아니다."""
from __future__ import annotations
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'src'))
from full_bianchi_hyrec.trajectory.hyrec_two_photon_raman import PhysicalTwoPhotonRamanBin
from full_bianchi_hyrec.trajectory.com_source_deposition import COMSourceDepositionPlan

E0=2.0**-60  # 제조 에너지 눈금, J
H_PLANCK=6.62607015e-34  # SI의 h. c=1 또는 h=1로 변환하지 않는다.


def real_vector(value,name):
    raw=np.asarray(value)
    if raw.shape!=(7,) or raw.dtype.kind not in 'fiu':
        raise ValueError(name+'는 실수 벡터7개여야 한다')
    v=np.array(raw,dtype=float,copy=True)
    if not np.isfinite(v).all():raise ValueError(name+'는 유한해야 한다')
    return v


def make_plan():
    # 열 순서: tracked, companion. 실제 원자 map으로 인증하지 않는다.
    return COMSourceDepositionPlan(
        np.array([2.,4.]),E0*np.array([1.,4.]),E0*np.array([2.,1.]),
        np.array([[2/3,1.],[1/3,0.]]),np.array([1.]),np.array([[0.,0.,1.]]),
        'manufactured_fixed_measure','manufactured_fixed_two_leg_map')


def make_pair(z):
    return PhysicalTwoPhotonRamanBin('two_photon',float(z[4]),3*E0/H_PLANCK,
        E0/H_PLANCK,2*E0/H_PLANCK,float(z[2]),float(z[3]),1.)


def compose(z,dz,read_kind='chi'):
    """z=(ln f0,ln f1,xu,xg,a,nH,H). 반환은 (dxu/dtau,dxg/dtau,G0,G1).

    fixed-map JVP만 계산한다. 원본 paired.jvp와 COM.jvp를 호출하며,
    원본 source/deposition 공식을 연구 합성층에서 재구현하지 않는다.
    """
    z=real_vector(z,'상태');dz=real_vector(dz,'방향')
    if np.any(z[2:]<=0):raise ValueError('이 연구의 population/rate/density/H는 양수 영역이다')
    if read_kind not in ('chi','log_control'):raise ValueError('미등록 읽기 연산')
    plan=make_plan();pair=make_pair(z)
    y=z[:2];dy=dz[:2];H=z[6]
    with np.errstate(over='raise',under='ignore',divide='raise',invalid='raise'):
        f=np.exp(y)
        if np.any(f<=0) or not np.isfinite(f).all():
            raise ValueError('로그 상태에서 유한한 양의 occupation이 필요하다')
        if read_kind=='chi':
            chi=np.logaddexp(0.,-y)
            query_chi=plan.number_fractions.T@chi
            legs=1/np.expm1(query_chi)
            dlegs=legs*(1+legs)*(plan.number_fractions.T@(dy/(1+f)))
        else:
            # 과거2점 log-f 읽기의 별도 대조. BASS 원본을 재실행하지 않는다.
            L=np.array([[.5,1.],[.5,0.]])
            legs=np.exp(L.T@y)
            dlegs=legs*(L.T@dy)
            query_chi=np.log1p(1/legs)
        if not np.isfinite(legs).all() or np.any(legs<=0) or not np.isfinite(dlegs).all():
            raise FloatingPointError('질의 occupation 또는 방향미분이 비유한')
        ft,fc=legs;dft,dfc=dlegs
        forward,reverse=pair.paired_rates(companion_occupation=fc,tracked_occupation=ft)
        gamma=pair.net_action(fc,ft)
        dgamma=pair.jvp(companion_occupation=fc,tracked_occupation=ft,
            d_integrated_rate_s_inv=dz[4],d_upper_population=dz[2],d_ground_population=dz[3],
            d_companion_occupation=dfc,d_tracked_occupation=dft)
        C=plan.apply(np.array([gamma,gamma]),z[5])[:,0]
        dC=plan.jvp(np.array([gamma,gamma]),np.array([dgamma,dgamma]),z[5],dz[5])[:,0]
        G=C/(H*f)
        dG=dC/(H*f)-G*(dy+dz[6]/H)
        atom=np.array([-gamma,gamma])/H
        datom=np.array([-dgamma,dgamma])/H-atom*dz[6]/H
        rhs=np.r_[atom,G];drhs=np.r_[datom,dG]
        if not np.isfinite(np.r_[rhs,drhs,forward,reverse,gamma,dgamma]).all():
            raise FloatingPointError('합성 source 또는 JVP가 비유한')
    return {'f':f,'legs':legs,'dlegs':dlegs,'query_chi':query_chi,
        'gamma':gamma,'dgamma':dgamma,'forward':forward,'reverse':reverse,
        'C':C,'dC':dC,'G':G,'rhs':rhs,'drhs':drhs,
        'physical_source_authenticated':False,'provider_admitted':False}
