"""Discriminating analytical and interval controls, no ODE solve."""
from decimal import Decimal, localcontext
from fractions import Fraction
from interval80 import I, derivatives, envelopes
from native_reference import produce, require, write_json
from point_reference140 import evaluate as independent_point

def run_controls(output):
    records=[]
    def record(name, passed, detail):
        records.append({'name':name,'pass':bool(passed),'detail':detail})
        # Preserve the failed prefix before raising.
        if not passed:
            write_json(output/'CONTROLS_FAILED.json',{'status':'FAIL','controls':records})
            raise AssertionError(name)
    def refuses(name, fn):
        try: fn()
        except (ValueError, AssertionError, ArithmeticError) as e:
            record(name,True,{'exception_type':type(e).__name__,'message':str(e)})
        else: record(name,False,'invalid domain accepted')

    general = I(-2,3)*I(-5,7)
    record('general four-endpoint signed multiplication',general.lo == -15 and general.hi == 21,general.packed())
    exact_rational=I.exact(Fraction(1,3))
    record('directed nonterminating rational conversion',Fraction(exact_rational.lo) <= Fraction(1,3) <= Fraction(exact_rational.hi),exact_rational.packed())
    for name,interval in [('ln1',I(1).ln()),('sqrt0',I(0).sqrt()),('exp0_minus1',I(0).exp()-1)]:
        record('exact elementary '+name,interval.lo == interval.hi == 0,interval.packed())
    record('exact identities at nonsingleton endpoints',
           I(1,2).ln().lo == 0 and I(0,1).sqrt().lo == 0 and I(0,1).exp().lo == 1,
           'endpoint branch applies separately')
    rm,rp=(3-I(5).sqrt())/2,(3+I(5).sqrt())/2
    for name,r,span in [('r_minus',rm,(I('0.1'),I('0.7'))),('r_plus',rp,(I(2),I(4)))]:
        m1,m2,included,monotone=envelopes(*span)
        third=derivatives(r)[3]
        with localcontext() as c:
            c.prec=140
            rr=(3-Decimal(5).sqrt())/2 if name=='r_minus' else (3+Decimal(5).sqrt())/2
            value=abs((rr*rr-rr)*(-rr).exp())
        record('curvature maximum crossing '+name,name in included and m2.contains(value) and third.contains(Decimal(0)),
               {'included':included,'M2':m2.packed(),'critical_w_third':third.packed(),'reference140':str(value)})
    for label,xa,xb,actual_left,order in [
            ('ambiguous_rminus',I('0.38','0.39'),I('0.6','0.7'),'0.39',2),
            ('ambiguous_x1',I('0.99','1.01'),I(2,'2.1'),'1.01',1)]:
        m1,m2,included,_=envelopes(xa,xb)
        env=m1 if order==1 else m2
        with localcontext() as c:
            c.prec=140
            xx=Decimal(actual_left)
            actual=xx*(-xx).exp() if order==1 else abs((xx*xx-xx)*(-xx).exp())
        record(label+' overlap does not raise lower bound',env.contains(actual),
               {'supremum_interval':env.packed(),'possible_true_left':actual_left,
                'independent_true_supremum140':str(actual),'included':included})
    for name,xa,xb in [('below_x1',I('0.2'),I('0.8')),('above_x1',I('1.2'),I(2)),('cross_x1',I('0.5'),I(2))]:
        m1,m2,included,monotone=envelopes(xa,xb)
        xx=I(xa.lo,xb.hi)
        sign=xx*(xx-1)*(-xx).exp()
        good=(sign.hi<0 if name=='below_x1' else sign.lo>0 if name=='above_x1' else 'x=1' in included)
        record(name,good,{'w_second':sign.packed(),'included':included})
    m1,m2,included,monotone=envelopes(I(1),I(1))
    record('degenerate cell at x1 has zero curvature',m2.lo == m2.hi == 0 and derivatives(I(1))[2].contains(Decimal(0)),
           {'M1':m1.packed(),'M2':m2.packed(),'included':included})
    m1,m2,included,monotone=envelopes(I(4),I(5))
    record('proved decreasing regime beyond rplus',monotone and not included,{'M2':m2.packed()})
    refuses('negative sqrt',lambda:I(-1).sqrt())
    refuses('nonpositive logarithm',lambda:I(0).ln())
    refuses('zero-containing denominator',lambda:I(1)/I(-1,1))
    refuses('nonfinite endpoint',lambda:I('Infinity'))
    refuses('subnormal endpoint',lambda:I('1e-1000000'))
    refuses('underflow exponential',lambda:I('-1e10').exp())
    refuses('reversed x interval',lambda:envelopes(I(2),I(1)))
    raw={'a':-1.0,'b':1.0,'q':0.0,'Es':1.0,'Et':1.0,'kN':1.0,'T0':1.0,'z':0.0,'TR':1.0,
         'yL':0.125,'yR':0.25,'u':0.1875}
    values,flags=produce(raw)
    record('characteristic equality',values['B_char'].lo == values['B_char'].hi == 0,
           {'B_char':values['B_char'].packed(),'qstar':values['qstar'].packed()})
    record('native-temperature equality',values['B_TR'].contains(Decimal(0)),values['B_TR'].packed())
    for q,expected_sign in [(0.125,-1),(-0.125,1)]:
        v,_=produce(dict(raw,q=q))
        record('characteristic shift sign '+str(q),v['B_char'].hi<0 if expected_sign<0 else v['B_char'].lo>0,v['B_char'].packed())
    v,_=produce(dict(raw,TR=2.0))
    record('isolated native-temperature mismatch',v['B_char'].lo == v['B_char'].hi == 0 and v['B_TR'].hi<0,
           {'B_char':v['B_char'].packed(),'B_TR':v['B_TR'].packed()})
    for name,changes in [('negative_energy',{'Es':-1.0}),('zero_temperature',{'T0':0.0}),
                         ('reversed_cell',{'a':2.0}),('query_outside_cell',{'q':2.0})]:
        refuses(name,lambda changes=changes:produce(dict(raw,**changes)))
    a,b,q,alpha=I(0),I(1),I.exact(Fraction(1,4)),I.exact(Fraction(1,4))
    coefficient=(q-a)*(b-q)/2
    for name,func,expected in [('constant',lambda t:I(3),Fraction(0)),
                               ('affine',lambda t:2*t+3,Fraction(0)),
                               ('quadratic',lambda t:t*t,Fraction(3,16))]:
        chord=(1-alpha)*func(a)+alpha*func(b)-func(q)
        target=I.exact(expected)
        record('exact '+name+' chord',chord.lo == target.lo and chord.hi == target.hi,
               {'J':chord.packed(),'coefficient':coefficient.packed()})
        if name=='quadratic': record('quadratic sharp factor one half',
                                     chord.lo == (2*coefficient).lo and chord.hi == (2*coefficient).hi,
                                     'f_second=2, J=2*(q-a)*(b-q)/2')
    convex=dict(raw,a=0.0,b=1.0,q=0.25,Es=10.0,Et=10.0)
    v,flags=produce(convex)
    point=independent_point(convex)
    record('convex reference chord and outward curvature inequality',flags['x_greater_than_one_proved'] and v['J_ref'].lo>0 and abs(v['J_ref']).hi <= v['chord_bound'].hi,
           {'J':v['J_ref'].packed(),'bound':v['chord_bound'].packed()})
    record('direct absolute interpolant versus decomposition',
           v['bridge_identity_residual'].contains(Decimal(0)) and v['direct_bridge'].contains(point['direct_bridge']) and v['decomposed_bridge'].contains(point['direct_bridge']),
           {'residual':v['bridge_identity_residual'].packed(),'independent_direct':str(point['direct_bridge'])})
    # Smooth toy fhat=t^2+3, Ff(t,f)=f+t. Exact w translation;
    # no trajectory, physical closure or IVP is inferred from this identity.
    t=I.exact(Fraction(1,4)); w,wp,_,_=derivatives(t.exp())
    fhat=t*t+3; yhat=fhat-w
    df=2*t; dy=df-wp
    defect_f=df-(fhat+t)
    defect_y=dy-((yhat+w)+t-wp)
    residual=defect_y-defect_f
    exact_defect=I.exact(Fraction(-45,16))
    record('smooth toy defect translation',residual.contains(Decimal(0)) and defect_f.contains(exact_defect.lo) and defect_y.contains(exact_defect.lo),
           {'Ff':'f+t','fhat':'t^2+3','t':'1/4','defect_exact':'-45/16',
            'defect_f':defect_f.packed(),'defect_y':defect_y.packed(),'difference':residual.packed()})
    summary={'status':'PASS','controls_count':len(records),'all_pass':True,'precision':80,
             'independent_precision':140,'physical_coverage':'0/313','physical_epsilon':None}
    write_json(output/'CONTROLS.json',{'summary':summary,'controls':records})
    write_json(output/'SUMMARY.json',summary)
    return summary
