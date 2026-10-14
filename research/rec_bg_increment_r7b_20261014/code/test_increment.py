import math, unittest
from increment_clock import Background, RateHermite, local_width, photon_step, exp_moment

class IncrementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=RateHermite(Background(q=.01),1024)
        cls.m=RateHermite(Background(q=-.01),1024)
        cls.z=RateHermite(Background(q=0.),1024)
    def test_01_local_width_adjacent(self):
        a=.1;b=math.nextafter(a,math.inf)
        self.assertGreater(local_width(a,b),0)
    def test_02_invalid_width(self):
        for a,b in [(0,1),(.1,.1),(.2,.1),(math.nan,.2),(.1,math.inf)]:
            with self.assertRaises(ValueError):local_width(a,b)
    def test_03_domain(self):
        for a,b in [(.04,.1),(.1,.3),(math.nan,.1)]:
            with self.assertRaises(ValueError):self.p.increment(a,b)
    def test_04_positive_increment(self):
        for a in [.048,.07,.1,.199]:
            for dx in [1e-14,1e-10,1e-6,.001]:
                dt,db=self.p.increment(a,a*math.exp(dx))
                self.assertGreater(dt,0);self.assertGreater(db,0)
    def test_05_reflection(self):
        for a,b in [(.05,.051),(.1,math.nextafter(.1,math.inf)),(.15,.151)]:
            tp,bp=self.p.increment(a,b);tm,bm=self.m.increment(a,b)
            self.assertEqual(tp,tm);self.assertEqual(bp,-bm)
    def test_06_zero_shear(self):
        self.assertEqual(self.z.increment(.05,.19)[1],0.)
    def test_07_partition(self):
        a,b,c=.073,.102,.178
        x=self.p.increment(a,c);y=self.p.increment(a,b);z=self.p.increment(b,c)
        for i in [0,1]:self.assertLess(abs(x[i]-y[i]-z[i])/abs(x[i]),5e-14)
    def test_08_cell_positivity(self):
        self.assertGreater(self.p.minimum_bernstein_control,0)
    def test_09_bound(self):
        self.assertLess(self.p.ideal_relative_bound,3.082e-10)
        self.assertLess(RateHermite(Background(q=.01),2048).ideal_relative_bound,1.923e-11)
    def test_10_same_h(self):
        x=RateHermite(Background(q=.01,same_h=True),1024)
        self.assertEqual(x.increment(.06,.09)[0],self.z.increment(.06,.09)[0])
        self.assertGreater(x.increment(.06,.09)[1],0)
    def test_11_exp_moment_zero(self):
        for k in range(4):self.assertEqual(exp_moment(k,0),1/(k+1))
    def test_12_exp_moment_integral(self):
        z=.003
        self.assertLess(abs(exp_moment(0,z)-(-math.expm1(-z)/z)),3e-16)
    def test_13_node_slopes(self):
        f,d=self.p.background.integrand(.1)
        eps=1e-5
        numerical=(self.p.background.integrand(.1*math.exp(eps))[0]-self.p.background.integrand(.1*math.exp(-eps))[0])/(2*eps)
        self.assertLess(abs(numerical/d-1),1e-8)
    def test_14_invalid_model(self):
        for opts in [{'omega_m':-1},{'h0':0},{'q':math.nan},{'a_end':.01}]:
            with self.assertRaises(ValueError):Background(**opts)
    def test_15_photon_axes(self):
        for mu,expected in [(0,-.1+.002),(1,-.1-.004),(-1,-.1-.004)]:
            e,m,j=photon_step(.1,.002,mu)
            self.assertAlmostEqual(e,expected,places=15)
            self.assertEqual(m,mu)
    def test_16_photon_composition(self):
        a=photon_step(.1,.002,.37);b=photon_step(.07,-.0003,a[1]);c=photon_step(.17,.0017,.37)
        self.assertLess(abs(a[0]+b[0]-c[0]),2e-16)
        self.assertLess(abs(b[1]-c[1]),2e-16)
        self.assertLess(abs(a[2]*b[2]/c[2]-1),5e-16)
    def test_17_invalid_photon(self):
        with self.assertRaises(ValueError):photon_step(.1,.1,1.001)
    def test_18_first_held_endpoints(self):
        import struct
        a=struct.unpack('d',struct.pack('Q',4587023449039406616))[0]
        b=struct.unpack('d',struct.pack('Q',4587023449040092879))[0]
        dt,db=self.z.increment(a,b)
        self.assertLess(abs(dt/844944.3803639700-1),1e-9)
    def test_19_zero_interval_rejected(self):
        with self.assertRaises(ValueError):self.p.increment(.1,.1)
    def test_20_immutability(self):
        with self.assertRaises((AttributeError,TypeError)):self.p.background.q=.4

    def test_21_model_replacement_rejected(self):
        table=RateHermite(Background(q=.01),64)
        with self.assertRaises(AttributeError):
            table.background=Background(q=-.01)

if __name__=='__main__':unittest.main(verbosity=2)
