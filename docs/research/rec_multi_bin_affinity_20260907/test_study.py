"""다중-bin source의 표적 검증. 원본 API 검사 및 독립 고정밀 primal."""
from fractions import Fraction as Q
import math
import unittest
import numpy as np
import mpmath as mp
import study as m

OBS = {}
BINS = []
TABLES = []
ETA = None
TOL = 4096*np.finfo(float).eps


def scaled(a,b):
    a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
    return float(np.max(np.abs(a-b)/(1+np.abs(b))))


def cases():
    return [('thermal',m.state()),('thermal_common_eta',m.state(ETA)),
            ('odd_nonthermal',m.state(odd=.125)),('even_nonthermal',m.state(even=.125))]


def exact_weights(u):
    nodes=[Q(float(x)) for x in m.U]
    for j in range(4):
        if nodes[j] <= u <= nodes[j+1]:
            v=[Q(0)]*5;t=(u-nodes[j])/(nodes[j+1]-nodes[j])
            v[j]=1-t;v[j+1]=t
            return v
    raise ValueError('exact source outside fixed domain')


def exact_rank(t):
    basis=[]
    for b,u in enumerate(t['ut']):
        u=Q(float(u));a=exact_weights(u);c=exact_weights(1-u)
        d=[x+y for x,y in zip(a,c)]
        assert d[0]==d[4] and d[1]==d[3] and sum(d)==2
        v=[Q(-1),Q(1),*d]
        for p,w,_ in basis:
            coeff=v[p];v=[a-coeff*z for a,z in zip(v,w)]
        pivot=next((i for i,x in enumerate(v) if x),None)
        if pivot is not None:
            scale=v[pivot];basis.append((pivot,[x/scale for x in v],b))
    return len(basis),[b for _,_,b in basis]


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global TABLES,ETA
        TABLES,_=m.load_tables()
        delta=[m.effective_defect(t) for t in TABLES]
        if min(delta)<=1e-6:
            raise AssertionError('선언한 제조 log 읽기의 양의 aggregate 결함이 관측되지 않음')
        ETA=-min(delta)/2
        OBS['construction']={'effective_defects':dict(zip(['base','hires'],delta)),
            'common_eta':ETA,'rule':'-min(delta_base,delta_hires)/2; same populations for both tables',
            'target_u':m.U.tolist(),'mode_measure_m3':m.MU.tolist(),
            'atom_sum':9/16,'lambda':2,'claim':'MANUFACTURED_TARGET_NOT_PHYSICAL_ADMISSION'}

    def close(self,a,b,tol=TOL):
        self.assertTrue(np.isfinite(np.asarray(a,dtype=float)).all())
        self.assertTrue(np.isfinite(np.asarray(b,dtype=float)).all())
        self.assertLessEqual(scaled(a,b),tol)

    def test_01_original_tables_and_fixed_partition(self):
        rows=[]
        for t in TABLES:
            self.assertEqual(t['n'],140 if t['label']=='base' else 408)
            self.close(math.fsum(t['normalized']),8.2206)
            self.close(t['B'].sum(axis=0),np.ones(2*t['n']))
            self.close(m.U@t['B'],t['us'])
            self.assertTrue(np.all(t['B']>=0))
            rows.append({'table':t['label'],'bins':t['n'],'raw_sum_s_inv':math.fsum(t['raw']),
                         'normalized_sum_s_inv':math.fsum(t['normalized']),
                         'factor':t['factor'],'member_sha256':t['sha256'],
                         'min_source_u':float(t['us'].min()),'max_source_u':float(t['us'].max())})
        OBS['tables']=rows

    def test_02_binwise_affinity_and_both_normalizations(self):
        rows=[]
        for t in TABLES:
            for name,z in cases():
                for kind in ('chi','log_control'):
                    for norm in ('raw','normalized'):
                        r=m.compose(t,z,kind=kind,normalization=norm);nH=z[8]
                        self.close(m.MU@r['C'],2*nH*r['S'])
                        self.close((m.MU*m.U)@r['C'],nH*r['S'])
                        self.close(r['sigma'],r['sigma_from_nodal'])
                        self.close(r['sigma'],r['read_entropy']-math.fsum(r['gamma']*r['delta']))
                        if kind=='chi':
                            self.close(r['delta'],np.zeros(t['n']))
                            self.assertGreaterEqual(r['sigma'],-TOL*(1+math.fsum(r['F']+r['R'])))
                        row={'table':t['label'],'case':name,'read':kind,'normalization':norm,
                             'event_sum_per_H_s':r['S'],'entropy_per_H_kB_s':r['sigma'],
                             'read_entropy_proxy_per_H_kB_s':r['read_entropy'],
                             'max_abs_delta':float(np.max(np.abs(r['delta']))),
                             'min_delta':float(r['delta'].min()),'max_delta':float(r['delta'].max()),
                             'negative_entropy_bins':int(np.count_nonzero(r['gamma']*r['asc'] < -TOL)),
                             'number_residual':float(m.MU@r['C']-2*nH*r['S']),
                             'energy_residual_in_E21':float((m.MU*m.U)@r['C']-nH*r['S'])}
                        rows.append(row)
                        for b in range(t['n']):
                            BINS.append(dict(table=t['label'],case=name,read=kind,normalization=norm,
                                bin=b,tracked_u=float(t['ut'][b]),a_s_inv=float(t[norm][b]),
                                gamma_per_H_s=float(r['gamma'][b]),affinity_read=float(r['aread'][b]),
                                affinity_scatter=float(r['asc'][b]),delta=float(r['delta'][b]),
                                entropy_per_H_kB_s=float(r['gamma'][b]*r['asc'][b])))
        OBS['cases']=rows

    def test_03_common_population_aggregate_counterexample(self):
        rows=[]
        for t in TABLES:
            z=m.state(ETA)
            a=m.compose(t,z,kind='chi');b=m.compose(t,z,kind='log_control')
            self.assertGreater(a['sigma'],0.)
            self.assertLess(b['sigma'],0.)
            self.assertGreater(b['read_entropy'],0.)
            self.close(b['asc'],np.full(t['n'],ETA))
            self.close(b['sigma'],ETA*b['S'])
            # 같은 스펙트럼과 원자 ratio에서 원시/정규화 계수를 비교한다.
            raw=m.compose(t,z,kind='log_control',normalization='raw')
            self.close(b['value'],raw['value']*t['factor'])
            rows.append({'table':t['label'],'eta':ETA,'chi_entropy':a['sigma'],
                         'log_entropy':b['sigma'],'log_positive_proxy':b['read_entropy'],
                         'chi_event_sum':a['S'],'log_event_sum':b['S']})
        OBS['counterexample']=rows

    def test_04_composite_jvp_against_independent_nonlinear_primal(self):
        rows=[]
        for t in TABLES:
            for name,z in [cases()[0],cases()[1],cases()[3]]:
                for kind in ('chi','log_control'):
                    for j,dz in enumerate(m.directions()):
                        r=m.compose(t,z,dz,kind)
                        p80,d80=m.independent(t,z,dz,kind,80,32)
                        p120,d120=m.independent(t,z,dz,kind,120,32)
                        with mp.workdps(120):
                            precision=max(abs(a-b)/(1+abs(b)) for a,b in zip(p80+d80,p120+d120))
                            self.assertLess(precision,mp.mpf('1e-60'))
                        self.close(r['value'],p120);self.close(r['jvp'],d120)
                        if j==6:
                            _,fine=m.independent(t,z,dz,kind,120,36)
                            with mp.workdps(120):
                                hdiff=max(abs(a-b)/(1+abs(b)) for a,b in zip(d120,fine))
                                self.assertLess(hdiff,mp.mpf('1e-16'))
                        else:hdiff=None
                        self.close(m.MU@r['dC'],2*(dz[8]*r['S']+z[8]*r['dS']))
                        self.close((m.MU*m.U)@r['dC'],dz[8]*r['S']+z[8]*r['dS'])
                        rows.append(dict(table=t['label'],case=name,read=kind,direction=j,
                            scaled_jvp_error=scaled(r['jvp'],d120),scaled_primal_error=scaled(r['value'],p120),
                            precision_80_120=mp.nstr(precision,20),
                            central_step_refinement=None if hdiff is None else mp.nstr(hdiff,20)))
        OBS['jvp']={'comparisons':len(rows),'max_scaled_error':max(x['scaled_jvp_error'] for x in rows),
                    'max_scaled_primal_error':max(x['scaled_primal_error'] for x in rows),'rows':rows,
                    'reference':'independent full primal, 80/120-digit central difference h=2^-32; mixed h=2^-36 check',
                    'tolerance':TOL,'scale':'abs(error)/(1+abs(reference))'}

    def test_05_finite_nonthermal_null_and_its_tangent(self):
        rows=[]
        z=m.state(odd=.125);thermal=m.state();h=m.U*(1-m.U)*(2*m.U-1)
        dz=np.zeros(10);dz[:5]=-(1+np.exp(z[:5]))*h
        self.assertGreater(float(np.max(np.abs(np.exp(z[:5]-thermal[:5])-1))),1e-4)
        for t in TABLES:
            r=m.compose(t,z,dz,kind='chi')
            rate_scale=math.fsum(r['F']+r['R'])
            err=float(np.max(np.abs(r['gamma'])/(r['F']+r['R'])))
            self.assertLessEqual(err,TOL)
            self.assertLessEqual(abs(r['S']),TOL*rate_scale)
            self.assertLessEqual(float(np.max(np.abs(r['dgamma']))),TOL*(1+rate_scale))
            rows.append(dict(table=t['label'],nonthermal_relative_nodal_change=float(np.max(np.abs(np.exp(z[:5]-thermal[:5])-1))),
                             max_bin_rate_relative_activity=err,net_event_rate=r['S'],
                             max_abs_null_tangent=float(np.max(np.abs(r['dgamma'])))))
        OBS['nonthermal_null']=rows

    def test_06_multi_bin_linearized_metric_and_rank(self):
        rows=[]
        for t in TABLES:
            rank,pivots=exact_rank(t)
            self.assertEqual(rank,3)
            z=m.state();r=m.compose(t,z);beta=m.MU/z[8];f=r['f']
            V=np.vstack([-np.ones(t['n']),np.ones(t['n']),t['D']])
            W=np.diag(np.r_[1/z[5],1/z[6],1/(beta*f*(1+f))])
            expected=-(V*r['R'])@V.T@W
            cols=[]
            for j in range(7):
                dz=np.zeros(10)
                if j<2:dz[5+j]=1
                else:dz[j-2]=1/(beta[j-2]*f[j-2])
                a=m.compose(t,z,dz)
                cols.append(np.r_[-a['dS'],a['dS'],beta*a['dC']])
            J=np.column_stack(cols)
            self.close(J,expected)
            self.close(W@J,(W@J).T)
            left=np.array([[1,1,0,0,0,0,0],[2,0,1,1,1,1,1],[1,0,*m.U.tolist()]])
            self.close(left@V,np.zeros((3,t['n'])))
            self.close(left@J,np.zeros((3,7)))
            sqrtW=np.diag(np.sqrt(np.diag(W)))
            symmetric=sqrtW@J@np.diag(1/np.diag(sqrtW))
            self.close(symmetric,symmetric.T)
            eig=np.linalg.eigvalsh((symmetric+symmetric.T)/2)
            self.assertLessEqual(float(eig.max()),TOL*(1+float(np.max(np.abs(eig)))))
            rows.append(dict(table=t['label'],rank_exact_rational_stencil=rank,
                nullity_in_seven_count_variables=7-rank,independent_bin_indices=pivots,
                scaled_matrix_error=scaled(J,expected),physical_time_eigenvalues_s_inv=eig.tolist(),
                count_jacobian=J.tolist(),
                qualification='rank from exact rational interpolation before floating rounding; numerical J independently assembled from original API JVP'))
        OBS['linearization']=rows

    def test_07_invalid_input_and_no_mutation(self):
        t=TABLES[0];z=m.state();saved=z.copy();m.compose(t,z)
        np.testing.assert_array_equal(saved,z)
        for bad in (np.ones(10,dtype=bool),np.ones(10,dtype=complex),np.ones((1,10))):
            with self.assertRaises(ValueError):m.compose(t,bad)
        with self.assertRaises(ValueError):m.weights(m.U,np.array([0.]))
        for i in (5,6,7,8,9):
            bad=z.copy();bad[i]=0
            with self.assertRaises(ValueError):m.compose(t,bad)
        with self.assertRaises(ValueError):m.compose(t,z,kind='unknown')
        with self.assertRaises(ValueError):m.compose(t,z,normalization='unknown')
        for y in (-1000.,1000.):
            bad=z.copy();bad[0]=y
            with self.assertRaises((ValueError,FloatingPointError)):m.compose(t,bad)
