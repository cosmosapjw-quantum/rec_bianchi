"""Lossless binary64 transport of frozen JSON inputs to a dependency-free Rust example.

This module only encodes inputs. It computes no source outputs or error verdicts.
Nonfinite test values are explicit tagged JSON objects, never JSON NaN numbers.
"""
from __future__ import annotations
import copy
import math
from reference_v2 import canonical, CONSTANT_NAMES


def number(x):
    if isinstance(x,dict):return {'nan':'NaN','+inf':'inf','-inf':'-inf'}[x['float']]
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x):raise ValueError('invalid input number')
    return repr(float(x))


def flat(x):
    if isinstance(x,list):
        return [t for y in x for t in flat(y)]
    return [number(x)]


def state(s):
    co=s.get('constants',canonical())
    return flat([s[k] for k in ['ng','ns','n_he_plus','ne','temperature_k']])+flat(s['wp'])+flat(s['f'])+flat(s['v'])+flat([co[k] for k in CONSTANT_NAMES])+['0' if s.get('electron_frame','CommonMaterialMaxwell')=='CommonMaterialMaxwell' else '1']


def bbm(n):return flat(n['v'])+flat(n['f'])+[number(n['weight_sr'])]

def bfm(n):return [n['channel'],n['gauge'],number(n['energy_ev'])]+flat(n['f'])+flat(n['v'])+flat(n['direction'])+[number(n['weight_energy_j']),number(n['weight_omega_sr'])]

def pinput(p):return [number(p['y'])]+flat(p['f1'])+flat(p['f2'])+flat(p['v1'])+flat(p['v2'])

def pm(n):return pinput(n['input'])+flat([n['weight_dy'],n['weight_omega1_sr'],n['weight_omega2_sr']])+[str(n['exchange_partner'])]

def many(xs,fn):return [str(len(xs))]+[t for x in xs for t in fn(x)]


def energy(d,co):
    v=d['value'];chi=co['chi_'+d['channel'].lower()+'_ev']
    if 'literal_ev' in v:return v['literal_ev']
    e=chi*v['chi_multiplier'] if 'chi_multiplier' in v else chi+v['q']*co['rydberg_ev']
    if 'nextafter' in v:e=math.nextafter(e,float(v['nextafter']))
    return e


def encode_case(c):
    op=c['op'];out=[]
    if op in ['bb','bb_jvp']:
        out=['BB',c['channel'],number(c['n_lower'])]+flat(c['wp'])+[number(c.get('h',0.))]+many(c['modes'],bbm)
    elif op=='bf':out=['BF',c['channel'],c['gauge'],number(c['energy_ev'])]+state(c['state'])
    elif op=='pair':out=['PAIR']+state(c['state'])+pinput(c['input'])
    elif op=='bfgrid':out=['BFGRID']+state(c['state'])+many(c['nodes'],bfm)
    elif op=='pairgrid':out=['PAIRGRID',c['convention']]+state(c['state'])+many(c['nodes'],pm)
    elif op=='selected':
        out=['SELECTED',c['convention']]+state(c['state'])+many(c['bb584'],lambda x:bbm(x)+flat(x['direction']))+many(c['ir'],lambda x:bbm(x)+flat(x['direction']))+many(c['bf'],bfm)+many(c['pairs'],lambda x:pm(x)+flat(x['direction1'])+flat(x['direction2']))
    elif op=='ledger':out=['LEDGER']+flat(c['rates'])+flat([c['bf_power_j'],c['heat_j']])
    elif op=='d86':out=['D86',number(c['y'])]
    elif op=='domain':
        d=c['source_case'];k=d['kind']
        if k=='scalar':
            s=copy.deepcopy(c['state']);s[d['field']]=d['value'];out=['GUARD']+state(s)
        elif k=='matrix':out=['MAT'+str(len(d['value']))]+flat(d['value'])
        elif k=='screen':out=['SCREEN']+flat(d['value'])+[str(int(d['direction'] is not None))]+([] if d['direction'] is None else flat(d['direction']))
        elif k=='constants':
            co=canonical()
            for field,val in d['value'].items():
                if field=='chi_p_delta_ev':co['chi_p_ev']+=val
                else:co[field]=val
            out=['CONSTANTS']+flat([co[k] for k in CONSTANT_NAMES])
        elif k=='energy':out=['ENERGY',d['channel'],number(energy(d,canonical()))]+state(c['state'])
        elif k=='width_ev':out=['WIDTH',number(d['value'])]
        else:raise ValueError('unknown domain case')
    else:raise ValueError('unknown operation')
    return ' '.join([c['id'],*out])


def encode(inputs):
    cases=inputs['cases']
    return ('REC_HE_WIRE_V2 '+str(len(cases))+'\n'+'\n'.join(encode_case(c) for c in cases)+'\n').encode()
