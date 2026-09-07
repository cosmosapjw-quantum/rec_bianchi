"""제조 고정-map 합성 JVP의 독립 기준. 기존 진단을 재실행하지 않는다."""
from __future__ import annotations
import math
from fractions import Fraction as Q
import unittest
import numpy as np
import mpmath as mp
import sympy as sp
from composite_probe import compose, make_plan, make_pair

OBSERVATIONS = {}
EPS = np.finfo(float).eps
TOL = 4096 * EPS


def reference(z, kind='chi'):
    """생산 component를 호출하지 않는 고정밀 primal만 정의한다."""
    y0,y1,xu,xg,a,n,H = z
    f = [mp.exp(y0),mp.exp(y1)]
    if kind == 'chi':
        c = [mp.log1p(1/v) for v in f]
        ft = 1/mp.expm1(mp.mpf(2)/3*c[0]+mp.mpf(1)/3*c[1])
        fc = 1/mp.expm1(c[0])
    elif kind == 'log_control':
        ft = mp.exp((y0+y1)/2)
        fc = f[0]
    else:
        raise ValueError(kind)
    g = a*(xu*(1+fc)*(1+ft)-xg*fc*ft)
    C = [n/2*(mp.mpf(5)/3)*g,n/4*(mp.mpf(1)/3)*g]
    return [-g/H,g/H,C[0]/(H*f[0]),C[1]/(H*f[1])]


def high_precision(z,dz,kind,dps):
    with mp.workdps(dps):
        zz = [mp.mpf(float(x)) for x in z]
        dd = [mp.mpf(float(x)) for x in dz]
        v = reference(zz,kind)
        d = [mp.diff(lambda t: reference([x+t*h for x,h in zip(zz,dd)],kind)[j],mp.mpf(0)) for j in range(4)]
        return v,d


def bases():
    # 모두 명시적 제조 상태다. 원자 table 또는 우주론 입력이 아니다.
    return [np.array([0.,-math.log(15),1/16,1/2,1.,8.,4.]),
            np.array([0.,-math.log(127),1/16,1/2,1.,8.,4.]),
            np.array([math.log(2),math.log(1/8),1/32,3/4,2.,4.,2.])]


def directions():
    return [*np.eye(7),np.array([1/4,-1/8,1/64,-1/32,1/8,2.,1.])]


class Checks(unittest.TestCase):
    def close(self,a,b):
        aa=np.asarray(a,dtype=float);bb=np.asarray(b,dtype=float)
        self.assertTrue(np.isfinite(aa).all() and np.isfinite(bb).all())
        self.assertLessEqual(float(np.max(np.abs(aa-bb)/(1+np.abs(bb)))),TOL)

    def test_01_exact_thermal_fixture(self):
        r=compose(bases()[0],directions()[-1])
        self.close(r['legs'],[1/3,1])
        self.close(r['dlegs'],[Q(17,864),Q(1,4)])
        self.assertLessEqual(abs(r['gamma']),256*EPS*(r['forward']+r['reverse']))
        self.close(r['dgamma'],Q(55,2304))
        self.close(r['drhs'],[-Q(55,9216),Q(55,9216),Q(275,6912),Q(275,4608)])
        # 정확한 기준은 코드 출력으로 다시 생성하지 않는다.
        OBSERVATIONS['thermal_exact']={
            'dlegs':['17/864','1/4'],'dgamma':'55/2304',
            'drhs':['-55/9216','55/9216','275/6912','275/4608'],
            'observed_drhs':r['drhs'].tolist(),'observed_gamma':r['gamma']}

    def test_02_full_jvp_against_80_and_120_digits(self):
        records=[]
        for b,z in enumerate(bases()):
            for d,dz in enumerate(directions()):
                r=compose(z,dz)
                v80,j80=high_precision(z,dz,'chi',80)
                v120,j120=high_precision(z,dz,'chi',120)
                with mp.workdps(120):
                    e=max(abs(x-y)/(1+abs(y)) for x,y in zip(v80+j80,v120+j120))
                    self.assertLess(e,mp.mpf('1e-70'))
                self.close(r['rhs'],v120);self.close(r['drhs'],j120)
                re=max(abs(float(x)-float(y))/(1+abs(float(y))) for x,y in zip(r['drhs'],j120))
                records.append({'base':b,'direction':d,'scaled_jvp_error':re,'reference_80_120':str(e)})
        OBSERVATIONS['full_jvp']=records

    def test_03_log_read_control_is_a_different_operator(self):
        z=bases()[0];dz=directions()[-1]
        r=compose(z,dz,'log_control')
        v,j=high_precision(z,dz,'log_control',100)
        self.close(r['rhs'],v);self.close(r['drhs'],j)
        self.close(r['gamma'],(1-3/math.sqrt(15))/8)
        self.assertGreater(r['gamma'],0)
        OBSERVATIONS['log_control']={'gamma':r['gamma'],'drhs':r['drhs'].tolist(),
                                   'original_radial_reexecuted':False}

    def test_04_linearity_and_no_input_mutation(self):
        z=bases()[1];d=directions()[-1];e=directions()[1]
        original=z.copy();rd=compose(z,d);re=compose(z,e)
        self.close(compose(z,2*d-3*e)['drhs'],2*rd['drhs']-3*re['drhs'])
        np.testing.assert_array_equal(z,original)
        self.close(compose(z,np.zeros(7))['drhs'],np.zeros(4))

    def test_05_number_energy_and_directional_ledgers(self):
        for z in bases():
            for dz in directions():
                r=compose(z,dz);n=z[5];dn=dz[5]
                mu=np.array([2.,4.]);En=np.array([1.,4.])
                self.close(mu@r['C'],2*n*r['gamma'])
                self.close((mu*En)@r['C'],3*n*r['gamma'])
                self.close(mu@r['dC'],2*(dn*r['gamma']+n*r['dgamma']))
                self.close((mu*En)@r['dC'],3*(dn*r['gamma']+n*r['dgamma']))
                self.close(r['rhs'][0]+r['rhs'][1],0)
                self.close(r['drhs'][0]+r['drhs'][1],0)

    def test_06_equilibrium_linearized_metric_structure(self):
        # z_count=(xu,xg,mu0*f0/nH,mu1*f1/nH). 이 고정 반응만 다룬다.
        R=sp.Rational
        v=sp.Matrix([-1,1,R(5,3),R(1,3)])
        W=sp.diag(16,2,2,R(225,8))
        J=-R(1,6)*v*v.T*W
        self.assertEqual(W*J,(W*J).T)
        self.assertEqual(J.rank(),1)
        self.assertEqual(sp.trace(J),-R(1921,432))
        self.assertEqual(J*J-sp.trace(J)*J,sp.zeros(4))
        self.assertEqual(sp.Matrix([[1,1,0,0]])*J,sp.zeros(1,4))
        self.assertEqual(sp.Matrix([[3,0,1,4]])*J,sp.zeros(1,4))
        z=bases()[0];beta=np.array([1/4,1/2]);f=np.exp(z[:2]);cols=[];logcols=[]
        for j in range(4):
            dz=np.zeros(7)
            if j<2:dz[2+j]=1
            else:dz[j-2]=1/(beta[j-2]*f[j-2])
            r=compose(z,dz)
            cols.append(np.r_[-r['dgamma'],r['dgamma'],beta*r['dC']])
        numeric=np.column_stack(cols)
        self.close(numeric,np.array(J).astype(float))
        T=np.diag([1,1,*list(beta*f)])
        for j in range(4):
            dz=np.zeros(7)
            if j<2:dz[2+j]=1
            else:dz[j-2]=1
            logcols.append(compose(z,dz)['drhs'])
        self.close(np.column_stack(logcols),np.linalg.solve(T,numeric@T)/z[6])
        OBSERVATIONS['equilibrium_matrix']={'count_jacobian':numeric.tolist(),
            'exact_count_eigenvalue_s_inv':'-1921/432','exact_tau_eigenvalue':'-1921/1728',
            'rank':1,'other_eigenvalues':[0,0,0],
            'hypotheses':'fixed positive measure/density, same read and scatter, detailed balance'}

    def test_07_entropy_rate_agrees_with_affinity(self):
        rows=[]
        for z in bases():
            r=compose(z,np.zeros(7));chi=np.logaddexp(0,-z[:2])
            beta=np.array([2.,4.])/z[5]
            lhs=r['gamma']*math.log(z[2]/z[3])+float((beta*chi)@r['C'])
            aff=math.log(z[2]/z[3])+float(np.sum(r['query_chi']))
            rhs=r['gamma']*aff
            self.close(lhs,rhs)
            self.assertGreaterEqual(rhs,-TOL*(1+r['forward']+r['reverse']))
            rows.append({'entropy_rate_per_H_kB':lhs,'gamma_affinity':rhs})
        OBSERVATIONS['entropy']=rows

    def test_08_chain_omission_mutants(self):
        z=bases()[1];dz=directions()[-1];r=compose(z,dz)
        wrong={
            'omit_density':r['drhs'][2:]-r['G']*dz[5]/z[5],
            'omit_H':r['drhs'][2:]+r['G']*dz[6]/z[6],
            'omit_log_return':r['drhs'][2:]+r['G']*dz[:2]}
        z0=bases()[0];r0=compose(z0,dz);pair=make_pair(z0);plan=make_plan()
        bad=pair.jvp(companion_occupation=r0['legs'][1],tracked_occupation=r0['legs'][0],
            d_integrated_rate_s_inv=dz[4],d_upper_population=dz[2],d_ground_population=dz[3],
            d_companion_occupation=0.,d_tracked_occupation=r0['dlegs'][0])
        badC=plan.jvp([r0['gamma']]*2,[bad]*2,z0[5],dz[5])[:,0]
        badG=badC/(z0[6]*r0['f'])-r0['G']*(dz[:2]+dz[6]/z0[6])
        gaps={name:float(np.max(np.abs(value-r['drhs'][2:]))) for name,value in wrong.items()}
        gaps['freeze_companion']=float(np.max(np.abs(badG-r0['drhs'][2:])))
        for gap in gaps.values():self.assertGreater(gap,1e-6)
        OBSERVATIONS['detected_omissions']=gaps

    def test_09_input_domain_is_not_silently_projected(self):
        z=bases()[0];dz=np.zeros(7)
        bad=[np.ones((1,7)),np.ones(7,dtype=bool),np.ones(7,dtype=complex)]
        for v in bad:
            with self.assertRaises(ValueError):compose(v,dz)
        for j in range(7):
            b=z.copy();b[j]=np.nan
            with self.assertRaises(ValueError):compose(b,dz)
        for j in range(2,7):
            b=z.copy();b[j]=0
            with self.assertRaises(ValueError):compose(b,dz)
        for y in (-1000.,1000.):
            b=z.copy();b[0]=y
            with self.assertRaises((ValueError,FloatingPointError)):compose(b,dz)
        with self.assertRaises(ValueError):compose(z,dz,'unregistered')

    def test_10_small_step_independent_nonlinear_path(self):
        z=bases()[1];dz=directions()[-1];errs=[]
        with mp.workdps(100):
            zz=[mp.mpf(float(x)) for x in z];dd=[mp.mpf(float(x)) for x in dz]
            _,target=high_precision(z,dz,'chi',100)
            for h in [mp.mpf(2)**-8,mp.mpf(2)**-12,mp.mpf(2)**-16]:
                plus=reference([x+h*d for x,d in zip(zz,dd)])
                minus=reference([x-h*d for x,d in zip(zz,dd)])
                err=max(abs((a-b)/(2*h)-d)/(1+abs(d)) for a,b,d in zip(plus,minus,target))
                errs.append(err)
            self.assertLess(errs[1],errs[0]/100)
            self.assertLess(errs[2],errs[1]/100)
        OBSERVATIONS['independent_central_difference']=[mp.nstr(e,30) for e in errs]
