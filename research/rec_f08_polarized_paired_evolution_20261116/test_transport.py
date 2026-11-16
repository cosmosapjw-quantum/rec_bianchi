"""Physical tests of spectral and screen transport on the original F08 grid."""
from pathlib import Path
import math
from decimal import Decimal, localcontext
import unittest
import numpy as np
from scipy.integrate import solve_ivp
from collision import screen_basis
from transport import (
    physical_directions,screen_rotation_angle,rotate_stokes,
    advance_native_endpoint,SOURCE_RATE_PER_H_S,BIRTH_ENERGY_EV,
    native_g_point,native_source_j,
)


def original_nodes():
    edges = (10.,13.598434599702,13.6,13.7,20.)
    return np.array([edges[k]+(edges[k+1]-edges[k])*j/4 for k in range(4) for j in range(4)]+[20.])


def audit_for(h,t0,t1,factors=None):
    dt=t1-t0
    return {
        'time_s':t1,'dt_s':dt,'n_h_cm3':1e-4*np.exp(-np.sum(h)*t1),
        'f_he':.083,'h_mean_per_s':np.sum(h)/3,
        'source_n':dt*SOURCE_RATE_PER_H_S,'source_u':dt*SOURCE_RATE_PER_H_S*BIRTH_ENERGY_EV,
        'group_indices':list(range(17)),
        'point_factors':np.ones(17).tolist() if factors is None else np.asarray(factors).tolist(),
    }


class NativeTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here=Path(__file__).resolve().parent
        cls.q=np.loadtxt(here.parent/'rec_f08_native_thomson_polarization_20261115/source_inputs/F08_ORIGINAL_SOURCE_Q128.csv',delimiter=',',skiprows=1)[:,1:]
        cls.nodes=original_nodes()

    def initial(self):
        s=np.zeros((17,128,4))
        s[12,:,0]=.05/128
        return s,np.zeros((128,4)),np.zeros((128,4))

    def test_triaxial_screen_rotation_against_independent_vector_ode(self):
        # The comparison integrates transported Cartesian screen vectors,
        # not the scalar connection used by the producer.
        for h,t0,t1 in ((np.array([.4,.1,.2]),.2,.5),
                        (np.array([1.01,.99,1.])*1e-14,8.8125e10,8.875e10)):
            n0,_,_=physical_directions(self.q,h,t0)
            n1,_,_=physical_directions(self.q,h,t1)
            e0,_=screen_basis(n0);et1,ep1=screen_basis(n1)
            def rhs(u,y):
                n,_,_=physical_directions(self.q,h,t0+(t1-t0)*u)
                e=y.reshape(128,3)
                return ((t1-t0)*n*np.sum(n*h*e,axis=1)[:,None]).ravel()
            solution=solve_ivp(rhs,(0.,1.),e0.ravel(),method='DOP853',rtol=3e-13,atol=3e-15)
            self.assertTrue(solution.success)
            e1=solution.y[:,-1].reshape(128,3)
            omega=screen_rotation_angle(self.q,h,t0,t1)
            predicted=np.cos(omega)[:,None]*et1-np.sin(omega)[:,None]*ep1
            np.testing.assert_allclose(predicted,e1,rtol=0,atol=3e-13)
            # A fully theta-polarized beam has Q+iU rotated by -2 Omega.
            stokes=np.column_stack((np.ones(128),np.ones(128),np.zeros((128,2))))
            out=rotate_stokes(stokes,omega)
            a=np.sum(e1*et1,axis=1);b=np.sum(e1*ep1,axis=1)
            np.testing.assert_allclose(out[:,1],a*a-b*b,atol=5e-13)
            np.testing.assert_allclose(out[:,2],2*a*b,atol=5e-13)

    def test_axisymmetric_connection_exactly_zero(self):
        h=np.array([.4,.4,.1])
        np.testing.assert_array_equal(screen_rotation_angle(self.q,h,.2,.8),np.zeros(128))

    def test_screen_rotation_preserves_I_V_and_polarization_norm(self):
        rng=np.random.default_rng(390)
        s=rng.normal(size=(17,128,4))
        omega=np.linspace(-.7,.8,128)
        out=rotate_stokes(s,omega)
        np.testing.assert_array_equal(out[...,0],s[...,0])
        np.testing.assert_array_equal(out[...,3],s[...,3])
        np.testing.assert_allclose(np.linalg.norm(out[...,1:],axis=-1),np.linalg.norm(s[...,1:],axis=-1),rtol=3e-15)

    def test_positive_redshift_remap_number_energy_and_guards(self):
        h=np.array([.4,.1,.2]);t0,t1=.2,.5
        s,gn,gu=self.initial()
        s[0,:,0]=2e-5
        s[5,:,0]=1e-5
        s[...,1]=.4*s[...,0];s[...,2]=.2*s[...,0];s[...,3]=.1*s[...,0]
        gn[:,0]=1e-6;gn[:,1]=.5e-6;gu[:]=8*gn
        factors=np.linspace(.88,1,17)
        out,ng,ug,diag=advance_native_endpoint(s,gn,gu,self.q,h,self.nodes,audit_for(h,t0,t1,factors))
        self.assertGreater(float(ng[:,0].sum()),float(gn[:,0].sum()))
        self.assertLess(abs(diag['remap_number_residual_per_H']),3e-17)
        self.assertLess(abs(diag['remap_energy_residual_eV_per_H']),3e-16)
        self.assertLess(abs(diag['number_ledger_residual_per_H']),3e-17)
        self.assertLess(abs(diag['energy_ledger_residual_eV_per_H']),3e-16)
        self.assertGreater(diag['redshift_work_eV_per_H'],0.)
        self.assertLessEqual(diag['max_stokes_cone_violation'],0.)
        self.assertTrue(np.all(ug[:,0]<10*ng[:,0]))

    def test_original_isotropic_source_no_polarization_injection(self):
        h=np.array([1.01,.99,1.])*1e-14;t0,t1=0.,3.125e8
        s,gn,gu=self.initial()
        s[:]=0
        out,ng,ug,diag=advance_native_endpoint(s,gn,gu,self.q,h,self.nodes,audit_for(h,t0,t1))
        _,_,jac=physical_directions(self.q,h,t1)
        expected=(t1-t0)*5e-15*jac/jac.sum()
        np.testing.assert_allclose(out[12,:,0],expected,rtol=3e-15,atol=0)
        np.testing.assert_array_equal(out[...,1:],0)
        self.assertLess(abs(diag['number_ledger_residual_per_H']),1e-20)
        self.assertFalse(np.any(ng));self.assertFalse(np.any(ug))

    def test_scalar_absorption_same_factor_for_all_stokes_channels(self):
        h=np.zeros(3);t0,t1=0.,3.125e8
        s,gn,gu=self.initial();s[12,:,1]=.6*s[12,:,0];s[12,:,2]=.2*s[12,:,0]
        factors=np.ones(17);factors[12]=.7
        out,_,_,_=advance_native_endpoint(s,gn,gu,self.q,h,self.nodes,audit_for(h,t0,t1,factors))
        np.testing.assert_allclose(out[12,:,1:],.7*s[12,:,1:],rtol=2e-15,atol=0)
        expected=.7*(s[12,:,0]+(t1-t0)*5e-15/128)
        np.testing.assert_allclose(out[12,:,0],expected,rtol=2e-15)

    def test_source_clock_tampering_and_missing_absorption_group_rejected(self):
        h=np.array([1.01,.99,1.])*1e-14
        s,gn,gu=self.initial();a=audit_for(h,0,3.125e8)
        a['source_n']*=2
        with self.assertRaisesRegex(ValueError,'source mismatch'):
            advance_native_endpoint(s,gn,gu,self.q,h,self.nodes,a)
        a=audit_for(h,0,3.125e8);a['group_indices']=a['group_indices'][:-5];a['point_factors']=a['point_factors'][:-5]
        with self.assertRaisesRegex(ValueError,'absent from native audit'):
            advance_native_endpoint(s,gn,gu,self.q,h,self.nodes,a)

    def test_native_scalar_arithmetic_near_HI_hat_regression(self):
        # Source contract from original paired_runtime.rs g_point/source_weights.
        # Keep an independently written scalar reference, including the full
        # original hat evaluation and sequential (non-compensated) reduction.
        h=np.array([1.01,.99,1.])*1e-14;t0,t1=6.25e8,9.375e8
        hh=tuple(float(x) for x in h)
        def original_g(ray,t):
            x,y,z=(float(v) for v in ray)
            a=(x*x)*math.exp((-2.0*hh[0])*t)
            b=(y*y)*math.exp((-2.0*hh[1])*t)
            c=(z*z)*math.exp((-2.0*hh[2])*t)
            return math.sqrt(((0.0+a)+b)+c)
        ref0=np.asarray([original_g(ray,t0) for ray in self.q])
        ref1=np.asarray([original_g(ray,t1) for ray in self.q])
        np.testing.assert_array_equal(native_g_point(self.q,h,t0),ref0)
        np.testing.assert_array_equal(native_g_point(self.q,h,t1),ref1)
        volume=math.exp(-((hh[0]+hh[1])+hh[2])*t1)
        raw=[volume/((float(g)*float(g))*float(g)) for g in ref1]
        total=0.0
        for v in raw:total+=v
        np.testing.assert_array_equal(native_source_j(self.q,h,t1),raw)
        s,gn,gu=self.initial();s[:]=0;s[5,:,0]=.05/128
        actual,_,_,_=advance_native_endpoint(s,gn,gu,self.q,h,self.nodes,audit_for(h,t0,t1))
        expected=np.zeros((17,128))
        for d in range(128):
            e=float(self.nodes[5])*(ref1[d]/ref0[d])
            for k in range(1,16):
                if e<=self.nodes[k-1] or e>=self.nodes[k+1]:a=0.
                elif e<=self.nodes[k]:a=(e-self.nodes[k-1])/(self.nodes[k]-self.nodes[k-1])
                else:a=(self.nodes[k+1]-e)/(self.nodes[k+1]-self.nodes[k])
                expected[k,d]=(.05/128)*a
            expected[12,d]+=(t1-t0)*5e-15*(raw[d]/total)
        np.testing.assert_array_equal(actual[...,0],expected)
        # Check the binary64 scalar ratio against 60-digit real arithmetic,
        # independently of its exact expression-order regression above.
        with localcontext() as ctx:
            ctx.prec=60
            def high_g(ray,t):
                z=Decimal(0)
                for qi,hi in zip(ray,hh):
                    dq,dh=Decimal.from_float(float(qi)),Decimal.from_float(hi)
                    z+=dq*dq*(-2*dh*Decimal.from_float(t)).exp()
                return z.sqrt()
            for d in (0,17,45,79,127):
                ratio=high_g(self.q[d],t1)/high_g(self.q[d],t0)
                self.assertLess(abs(Decimal.from_float(float(ref1[d]/ref0[d]))-ratio),Decimal('4e-16'))


if __name__=='__main__':
    unittest.main()
