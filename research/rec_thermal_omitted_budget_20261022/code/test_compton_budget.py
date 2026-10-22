"""Independent limiting identities and units for the finite Compton budget."""
import math
import unittest
import numpy as np
from scipy.integrate import quad
from numpy.polynomial.legendre import leggauss
from compton_budget import (hot_electron_power, planck_reference_power,
    dilute_spectrum_power, uv_reference_moments, fixed_path_logT_forcing,
    C_M_S, KB_J_K, H_J_S, EV_J, SIGMA_T_M2, ME_KG, MEC2_J, A_RAD_J_M3_K4)


class ComptonTests(unittest.TestCase):
    def test_hot_sign_zero_and_cgs_conversion(self):
        ne,T,U=123.,14000.,2e-11
        actual=hot_electron_power(ne,T,U)
        # Independent cgs path: erg/cm3/s → W/m3 multiplies by0.1.
        cgs=-4*(SIGMA_T_M2*1e4)*(C_M_S*100)*(ne*1e-6)*(
            KB_J_K*1e7)*T*(U*10)/((ME_KG*1000)*(C_M_S*100)**2)
        self.assertLess(actual,0)
        self.assertAlmostEqual(actual/(cgs*.1),1,places=14)
        self.assertEqual(hot_electron_power(0,T,U),0)
        self.assertEqual(hot_electron_power(ne,T,0),0)
        self.assertEqual(hot_electron_power(ne,0,U),0)

    def test_isotropic_electrons_angular_average(self):
        # Exact Thomson loss factor for a beam, averaged over electron directions.
        mu,w=leggauss(16)
        for beta in (.001,.02,.1):
            gamma2=1/(1-beta*beta)
            mean=float(w@(gamma2*(1-beta*mu)**2-(1-beta*mu)))/2
            expected=4/3*gamma2*beta*beta
            self.assertLess(abs(mean/expected-1),3e-10)

    def test_planck_induced_recoil_identity_and_equilibrium(self):
        def n(x): return 1/math.expm1(x) if x<700 else 0.
        e3=quad(lambda x:x**3*n(x),0,100,epsabs=1e-11)[0]
        e4=quad(lambda x:x**4*n(x)*(1+n(x)),0,100,epsabs=1e-11)[0]
        self.assertAlmostEqual(e3/(math.pi**4/15),1,places=12)
        self.assertAlmostEqual(e4/e3,4,places=12)
        for Tr in (2.7255,24.,1200.):
            self.assertEqual(planck_reference_power(50,Tr,Tr),0)
            self.assertGreater(planck_reference_power(50,Tr/2,Tr),0)
            self.assertLess(planck_reference_power(50,Tr*2,Tr),0)
        a_numeric=8*math.pi*KB_J_K**4/(H_J_S**3*C_M_S**3)*e3
        self.assertAlmostEqual(a_numeric/A_RAD_J_M3_K4,1,places=12)

    def test_number_energy_moments_do_not_fix_recoil(self):
        eps=np.array([1.,2.,3.])*EV_J
        n1=np.array([.5,0,.5]);n2=np.array([0,1.,0])
        self.assertEqual(float(n1.sum()),float(n2.sum()))
        self.assertEqual(float(n1@eps),float(n2@eps))
        m1=float(n1@(eps**2));m2=float(n2@(eps**2))
        self.assertAlmostEqual(m1/m2,1.25,places=14)
        q1=dilute_spectrum_power(1,0,float(n1@eps),m1)
        q2=dilute_spectrum_power(1,0,float(n2@eps),m2)
        self.assertAlmostEqual(q1/q2,1.25,places=14)

    def test_uv_bins_units_occupancy_and_detailed_balance(self):
        edges=np.geomspace(5.,200.,72);p=-2.5
        energy=np.sqrt(edges[:-1]*edges[1:])
        norm=1e10
        flux=norm*(edges[1:]**(p+1)-edges[:-1]**(p+1))/(p+1)
        m=uv_reference_moments(energy,flux,edges,p)
        # Direct sums in eV number density, converted after summing.
        U=sum(float(f)*float(e) for f,e in zip(flux,energy))*EV_J/C_M_S
        M=sum(float(f)*float(e)**2 for f,e in zip(flux,energy))*EV_J**2/C_M_S
        self.assertAlmostEqual(U/m['U_J_m3'],1,places=14)
        self.assertAlmostEqual(M/m['M_J2_m3'],1,places=14)
        Tc=m['Compton_temperature_K']
        self.assertLess(abs(dilute_spectrum_power(50,Tc,U,M))/(50*SIGMA_T_M2*C_M_S*M/MEC2_J),2e-15)
        self.assertGreater(dilute_spectrum_power(50,10000,U,M),0)
        self.assertLess(m['max_continuous_occupation_at_uv1'],1e-12)

    def test_particle_term_energy_storage_and_invalid_inputs(self):
        H,T,nb,eta=1e-17,1e4,100.,1.5
        event=1e-16;chi=13.598*EV_J
        qkin=-nb*event*chi
        expected=-(2*chi/(3*KB_J_K*T)+1)*event/(H*eta)
        actual=fixed_path_logT_forcing(qkin,event,H,T,nb,eta)
        self.assertAlmostEqual(actual/expected,1,places=14)
        without_particle=fixed_path_logT_forcing(qkin,0,H,T,nb,eta)
        self.assertLess(actual,without_particle)
        for args in ((-1,1,1),(1,-1,1),(1,1,float('nan'))):
            with self.assertRaises(ValueError): hot_electron_power(*args)
        with self.assertRaises(ValueError): dilute_spectrum_power(1,1,0,1)
        with self.assertRaises(ValueError): fixed_path_logT_forcing(1,0,0,1,1,1)


if __name__=='__main__': unittest.main(verbosity=2)
