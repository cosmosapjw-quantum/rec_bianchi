"""Tests of genuine input identities and conditional algebra, not covariance inference."""
import copy, importlib.util, json, pathlib, tempfile, unittest
from fractions import Fraction as F
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cycles',ROOT/'src/correlated_cycles.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
INPUT=ROOT/'input/LAB_INPUT_PR164_IMMUTABLE.json'

class TestActualMeasurements(unittest.TestCase):
    def test_rows(self):
        a=m.read_source(INPUT)
        self.assertEqual(len(a['line_parameters'])+len(a['inherited_measurements']),9)
        self.assertEqual(len(m.measurements_mhz(a)),9)
    def test_cycle_differentials(self):
        out=m.calculate(INPUT)
        self.assertEqual(out['cycle_residuals_nominal_MHz'],
           ['-3.921711314000','-17.890385768000','-60.258284058000'])
    def test_graph_rank(self):
        self.assertEqual(m.rank(m.incidence()),6)
        self.assertEqual(m.rank(m.C),3)
        self.assertEqual(m.matmul(m.C,m.incidence()),[[0]*9 for _ in range(3)])
    def test_invariants(self):
        out=m.calculate(INPUT)
        self.assertEqual(out['conditional_calibration_model']['cycle_invariant_count'],1)
        self.assertEqual(out['conditional_calibration_model']['calibration_invariant_nominal_cycle_MHz'], '-41.050579792116')
    def test_gauge_independence(self):
        a=m.read_source(INPUT); y=m.measurements_mhz(a)
        levels=[F(7*i+3) for i in range(9)]
        shift=[m.dot(row,levels) for row in m.incidence()]
        self.assertEqual([m.dot(row,y) for row in m.C],
                         [m.dot(row,[x+q for x,q in zip(y,shift)]) for row in m.C])
    def test_calibration_invariance(self):
        a=m.read_source(INPUT);y=m.measurements_mhz(a)
        x=[F(z['nu0_cm_minus1']) for z in a['line_parameters']]
        b=m.two_parameter_sung_calibration(x)
        r=[m.dot(row,y) for row in m.C]
        d=m.calculate(INPUT);ell=[F(s) for s in d['conditional_calibration_model']['left_null_normalized']]
        # Use exact analytical ell, not truncated JSON display values.
        ell0=((x[1]+x[2])/2-x[3])/(x[0]-x[2]);ell=[ell0,-F(1,2)-ell0,F(1)]
        original=m.dot(ell,r)
        for u,v in [(F(0),F(0)),(F(2000),F(7,3)),(-F(9,2),F(17))]:
            delta=[m.dot(row,[u,v]) for row in b]
            self.assertEqual(m.dot(ell,[m.dot(row,[f+t for f,t in zip(y,delta)]) for row in m.C]),original)
    def test_algebraic_covariance_projection(self):
        # SYNTHETIC: test matrix identity only, no actual experiment likelihood.
        v=[[F(i==j)*(i+1) for j in range(9)] for i in range(9)]
        projected=m.project_covariance(v)
        expected=[[sum(m.C[i][k]*m.C[j][k]*(k+1) for k in range(9)) for j in range(3)] for i in range(3)]
        self.assertEqual(projected,expected)
    def test_missing_9x9_rejected(self):
        with self.assertRaises(ValueError):m.project_covariance([[1]])
    def test_asymmetric_rejected(self):
        v=[[F(i==j) for j in range(9)] for i in range(9)];v[0][1]=3
        with self.assertRaises(ValueError):m.project_covariance(v)
    def test_status_null(self):
        out=m.calculate(INPUT)
        self.assertIsNone(out['covariance']['actual_full_9x9'])
        for key in ['chi_square','p_value','statistical_sigma']:self.assertIsNone(out['covariance'][key])
        self.assertEqual(out['protection']['original_35Hz'],'FAIL7/8')
        self.assertEqual(out['protection']['canonical_DAG'],'28/88')
        self.assertEqual(out['protection']['REC_physical_DAG'],'0/313')
        self.assertEqual(out['protection']['production'],'HOLD')
    def test_protected_source_change_rejected(self):
        d=json.loads(INPUT.read_text())
        d['protection']['original_35Hz']='PASS'
        with tempfile.TemporaryDirectory() as td:
            fp=pathlib.Path(td)/'LAB_INPUT.json';fp.write_text(json.dumps(d))
            with self.assertRaises(ValueError):m.read_source(fp)
    def test_no_covariance_injected(self):
        d=json.loads(INPUT.read_text());d['primary_source']['joint_covariance']=[[1]]
        with tempfile.TemporaryDirectory() as td:
            fp=pathlib.Path(td)/'LAB_INPUT.json';fp.write_text(json.dumps(d))
            with self.assertRaises(ValueError):m.read_source(fp)

if __name__=='__main__':unittest.main()
