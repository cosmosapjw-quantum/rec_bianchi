"""New target-grid research checks; old PR79/80 suites are never invoked.

Authored before the new implementation. Main runtime failed before process
start, so no RED/GREEN execution is claimed by this source checkpoint.
"""
from __future__ import annotations
from fractions import Fraction as Q
import math
import unittest
import numpy as np
import mpmath as mp
import refinement as r

OBS = {}
WEAK_ROWS = []
STATE_ROWS = []
JVP_ROWS = []
BIN_ROWS = []
TOL = 4096*np.finfo(float).eps


def error(a, b):
    aa, bb = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if aa.shape != bb.shape or not np.isfinite(aa).all() or not np.isfinite(bb).all():
        raise ValueError('finite equal-shaped comparisons required')
    return float(np.max(np.abs(aa-bb)/(1+np.abs(bb))))


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables, _ = r.previous.load_tables()
        OBS['tables'] = [{k:t[k] for k in ('label','n','member','sha256','factor')}
                         for t in cls.tables]
        OBS['measure'] = {'definition':'8 m^-3 (1+u^2) du; mass-lumped linear hats',
                          'physical_authority':False,'levels':list(r.LEVELS),
                          'nodes':[4*2**j+1 for j in r.LEVELS]}

    def close(self, a, b):
        self.assertLessEqual(error(a,b), TOL)

    def test_01_common_measure_and_nested_partition(self):
        rows = []
        for level in r.LEVELS:
            nodes = r.nodes(level)
            if level:
                np.testing.assert_array_equal(nodes[::2], r.nodes(level-1))
            np.testing.assert_array_equal(nodes+nodes[::-1], np.ones(len(nodes)))
            mu = r.measure(nodes)
            self.assertTrue(np.all(mu>0))
            a, b = nodes[0], nodes[-1]
            mass = r.MU0*((b-a)+(b**3-a**3)/3)
            self.close(math.fsum(mu),mass)
            # Independent two-point Gauss evaluation of each cubic hat*rho.
            qmu = np.zeros(len(nodes))
            for j,(left,right) in enumerate(zip(nodes[:-1],nodes[1:])):
                h=right-left
                for s in (.5-.5/math.sqrt(3), .5+.5/math.sqrt(3)):
                    u=left+h*s; w=.5*h*r.MU0*(1+u*u)
                    qmu[j]+=w*(1-s);qmu[j+1]+=w*s
            self.close(mu,qmu)
            for t in self.tables:
                g=r.grid(t,level)
                self.close(g['B'].sum(axis=0),np.ones(2*t['n']))
                self.close(nodes@g['B'],t['us'])
                self.assertTrue(np.all(g['B']>=0))
            rows.append({'level':level,'nodes':len(nodes),'max_du':float(np.diff(nodes).max()),
                         'total_measure_m3':math.fsum(mu)})
        OBS['grid_measure']=rows
        for bad in (-1, True, 1.5):
            with self.assertRaises(ValueError):r.nodes(bad)

    def test_02_exact_quadratic_error_witness(self):
        a,b,u=Q(1,4),Q(1,2),Q(3,8)
        theta=(u-a)/(b-a)
        interp2=(1-theta)*a*a+theta*b*b
        self.assertEqual(interp2-u*u,(u-a)*(b-u))
        self.assertEqual(interp2-u*u,Q(1,64))
        chi=lambda x:Q(1,2)+x+x*(1-x)/8
        self.assertEqual((1-theta)*chi(a)+theta*chi(b)-chi(u),-Q(1,512))
        for t in self.tables:
            for level in r.LEVELS:
                g=r.grid(t,level);x=g['u'];q=t['us']
                j=np.clip(np.searchsorted(x,q,side='right')-1,0,len(x)-2)
                defect=(q-x[j])*(x[j+1]-q)
                self.close((x*x)@g['B']-q*q,defect)
                self.assertGreaterEqual(float(defect.min()),0.)
                self.close(g['B'].T@r.polynomial(r.CASES[1].coeff,x)
                           -r.polynomial(r.CASES[1].coeff,q),-defect/8)
        OBS['exact_witness']={'u':'3/8','interval':['1/4','1/2'],
                              'u2_defect':'1/64','chi_defect':'-1/512'}

    def test_03_affine_and_odd_equilibria_and_nodal_entropy(self):
        rows=[]
        for t in self.tables:
            for level in r.LEVELS:
                g=r.grid(t,level)
                for case in r.CASES:
                    out=r.evaluate(t,g,case,r.ZERO,'chi')
                    self.close(out['affinity_defect'],np.zeros(t['n']))
                    self.close(out['sigma'],out['sigma_from_nodal'])
                    activity=math.fsum(out['F']+out['R'])
                    self.assertGreaterEqual(out['sigma'],-TOL*(1+activity))
                    if case.name!='curved':
                        self.assertLessEqual(float(np.max(np.abs(out['gamma'])/(out['F']+out['R']))),TOL)
                    rows.append({'table':t['label'],'level':level,'case':case.name,
                                 'sigma_s_inv':out['sigma'],'activity_s_inv':activity})
        OBS['entropy_and_limits']=rows

    def test_04_weak_split_and_second_order_bounds(self):
        for t in self.tables:
            for case in r.CASES:
                for direction in r.DIRECTIONS:
                    direct=r.direct(t,case,direction)
                    for level in r.LEVELS:
                        g=r.grid(t,level)
                        bounds=r.bounds(t,case,direction,g['h'])
                        for kind in ('chi','log_control'):
                            out=r.evaluate(t,g,case,direction,kind)
                            split=r.split_errors(t,g,out,direct)
                            self.close(out['M']-direct['M'],sum(split[k] for k in ('read','scatter','cross')))
                            self.close(out['dM']-direct['dM'],sum(split[k] for k in ('dread','dscatter','dcross')))
                            self.close(out['M'][:2],[2*out['S'],out['S']])
                            self.close(out['dM'][:2],[2*out['dS'],out['dS']])
                            if kind=='chi':
                                self.assertTrue(np.all(np.abs(out['M']-direct['M']) <= bounds['M']+TOL*(1+np.abs(direct['M']))))
                                self.assertTrue(np.all(np.abs(out['dM']-direct['dM']) <= bounds['dM']+TOL*(1+np.abs(direct['dM']))))
                            for k,power in enumerate(r.POWERS):
                                WEAK_ROWS.append(dict(table=t['label'],case=case.name,direction=direction.name,
                                    read_kind=kind,level=level,nodes=len(g['u']),h=g['h'],power=power,
                                    M=float(out['M'][k]),reference_M=float(direct['M'][k]),
                                    error=float(out['M'][k]-direct['M'][k]),
                                    read_error=float(split['read'][k]),scatter_error=float(split['scatter'][k]),
                                    cross_error=float(split['cross'][k]),
                                    dM=float(out['dM'][k]),reference_dM=float(direct['dM'][k]),
                                    jvp_error=float(out['dM'][k]-direct['dM'][k]),
                                    read_jvp_error=float(split['dread'][k]),scatter_jvp_error=float(split['dscatter'][k]),
                                    cross_jvp_error=float(split['dcross'][k]),
                                    chi_M_bound=float(bounds['M'][k]) if kind=='chi' else None,
                                    chi_dM_bound=float(bounds['dM'][k]) if kind=='chi' else None,
                                    max_leg_read_error=float(np.max(np.abs(out['legs']-direct['legs']))),
                                    max_affinity_defect=float(np.max(np.abs(out['affinity_defect']))),
                                    sigma_s_inv=out['sigma'],max_abs_C_s_inv=float(np.max(np.abs(out['C'])))))
                            if case.name=='curved' and direction.name=='photon' and level in (0,5):
                                for b in range(t['n']):
                                    BIN_ROWS.append(dict(table=t['label'],level=level,read_kind=kind,bin=b,
                                        tracked_u=float(t['ut'][b]),gamma=float(out['gamma'][b]),
                                        reference_gamma=float(direct['gamma'][b]),
                                        delta=float(out['affinity_defect'][b])))
        # Measures affect state quadrature even though they cancel in weak source moments.
        for case in r.CASES:
            q80=r.state_reference(case,80);q120=r.state_reference(case,120)
            with mp.workdps(120):
                self.assertLess(max(abs(x-y) for x,y in zip(q80,q120)),mp.mpf('1e-60'))
            for level in r.LEVELS:
                u=r.nodes(level);mu=r.measure(u);f=1/np.expm1(r.polynomial(case.coeff,u))
                q=np.array([mu@f,(mu*u)@f]);qb=r.state_bound(case,float(np.diff(u).max()))
                self.assertTrue(np.all(np.abs(q-np.array(q120,dtype=float)) <= qb+TOL))
                STATE_ROWS.append(dict(case=case.name,level=level,nodes=len(u),
                    count_m3=float(q[0]),reference_count_m3=float(q120[0]),
                    energy_in_E21_m3=float(q[1]),reference_energy_in_E21_m3=float(q120[1]),
                    count_error=float(q[0]-float(q120[0])),energy_error=float(q[1]-float(q120[1]))))
        self.assertEqual(len(WEAK_ROWS),576)
        OBS['weak_rows']=len(WEAK_ROWS)
        OBS['convergence_claim']='finite-grid data and conditional chi O(h^2) bounds; no fitted order acceptance'

    def test_05_independent_nonlinear_discrete_jvp(self):
        case=r.CASES[1]
        for t in self.tables:
            for level in (1,4):
                g=r.grid(t,level)
                for kind in ('chi','log_control'):
                    for direction in r.DIRECTIONS:
                        out=r.evaluate(t,g,case,direction,kind)
                        p80,d80=r.independent(t,g,case,direction,kind,80,32)
                        p120,d120=r.independent(t,g,case,direction,kind,120,32)
                        _,fine=r.independent(t,g,case,direction,kind,120,36)
                        with mp.workdps(120):
                            precision=max(abs(a-b)/(1+abs(b)) for a,b in zip(p80+d80,p120+d120))
                            step=max(abs(a-b)/(1+abs(b)) for a,b in zip(d120,fine))
                            self.assertLess(precision,mp.mpf('1e-60'))
                            self.assertLess(step,mp.mpf('1e-16'))
                        self.close(out['vector'],p120);self.close(out['jvp'],fine)
                        JVP_ROWS.append(dict(table=t['label'],level=level,read_kind=kind,direction=direction.name,
                            primal_scaled_error=error(out['vector'],p120),jvp_scaled_error=error(out['jvp'],fine),
                            precision_80_120=mp.nstr(precision,25),step_refinement=mp.nstr(step,25)))
        self.assertEqual(len(JVP_ROWS),16)
        OBS['independent_jvp']={'comparisons':len(JVP_ROWS),
            'max_scaled_error':max(x['jvp_scaled_error'] for x in JVP_ROWS)}

    def test_06_measure_blindness_and_packet_mutation(self):
        rows=[]
        for t in self.tables:
            g=r.grid(t,2);out=r.evaluate(t,g,r.CASES[1],r.DIRECTIONS[1],'chi')
            mu_wrong=np.full(len(g['u']),math.fsum(g['mu'])/len(g['u']))
            plan=r.plan(t,g['u'],mu_wrong,g['B'])
            C_wrong=plan.apply(np.r_[out['gamma'],out['gamma']],r.NH)[:,0]
            M_wrong=(r.psi(g['u'])*mu_wrong/r.NH)@C_wrong
            self.close(M_wrong,out['M'])
            measure_mismatch=float(np.max(np.abs(mu_wrong-g['mu'])))
            self.assertGreater(measure_mismatch,1e-6)
            # Deleting the companion leg is a diagnostic mutation, not a source edit.
            C_drop=g['plan'].apply(np.r_[out['gamma'],np.zeros(t['n'])],r.NH)[:,0]
            missing_leg=float(abs(g['mu']@C_drop/r.NH-2*out['S']))
            self.assertGreater(missing_leg,1e-6)
            rows.append(dict(table=t['label'],wrong_measure_weak_change=error(M_wrong,out['M']),
                wrong_measure_max_delta_m3=measure_mismatch,missing_companion_number_residual_s_inv=missing_leg))
        OBS['adversarial']=rows
