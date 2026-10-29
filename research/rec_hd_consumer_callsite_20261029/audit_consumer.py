#!/usr/bin/env python3
"""REC HD source-only consumer audit. No IVP, stationary solve or source repair."""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json, sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

C=Fraction(299792458)
H=Fraction(Decimal('6.62607015e-34'))
KB=Fraction(Decimal('1.380649e-23'))
SOURCE_SHA='0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb'
MC_BLOB='029255494bf0a63b93bf8b2715327a8585afb5f3'
FS_BLOB='21517960f912efbd2dc9df8b94fd577e03ca2e27'

def exact(s):
    if not isinstance(s,str): raise TypeError('exact input requires source decimal string')
    d=Decimal(s)
    if not d.is_finite(): raise ValueError('nonfinite source literal')
    return Fraction(d)

def rat(q): return f'{q.numerator}/{q.denominator}'

def git_blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def load_module(path,expected,name):
    b=Path(path).read_bytes()
    if git_blob(b)!=expected: raise ValueError(f'PARENT_CODE_IDENTITY_MISMATCH:{name}:{git_blob(b)}')
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise ValueError('bad module path')
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
    return m

def check_source(b):
    if len(b)!=2289 or hashlib.sha256(b).hexdigest()!=SOURCE_SHA:
        raise ValueError('ORIGINAL_LAMDA_SOURCE_IDENTITY_MISMATCH')

def per_event(wu,wl,nu):
    nu_e=100*C*(exact(wu)-exact(wl));nu_p=10**9*exact(nu)
    if nu_e<=0 or nu_p<=0: raise ValueError('nonpositive source frequency')
    delta=nu_e-nu_p
    return {'nu_E_Hz':rat(nu_e),'nu_P_Hz':rat(nu_p),
            'nu_E_minus_nu_P_Hz':rat(delta),
            'matter_plus_radiation_J_per_down_event':rat(-H*delta),
            'relative_photon_energy_defect':rat(-delta/nu_e)}

def analytic_bath_rate(A,g,nu_e,nu_p,T=100):
    import mpmath as mp
    if T<=0 or g<=0 or exact(A)<=0 or nu_e<=0 or nu_p<=0:raise ValueError('bad bath')
    m=lambda q:mp.mpf(q.numerator)/q.denominator
    xe=m(H*nu_e/(KB*T));xp=m(H*nu_p/(KB*T))
    return m(exact(A))*m(g)*mp.expm1(xp-xe)/mp.expm1(xp)

def planck_self_null(nu,T=100):
    import mpmath as mp
    if nu<=0 or T<=0:raise ValueError('bad null input')
    x=H*nu/(KB*T);z=mp.exp(-mp.mpf(x.numerator)/x.denominator);f=z/(1-z)
    return z*(1+f)-f

def run(source,mc_path,fs_path,T=100,den=1000):
    import mpmath as mp
    if T not in (50,100,200) or den not in (1000,1000000):raise ValueError('unsupported source node')
    check_source(source)
    mc=load_module(mc_path,MC_BLOB,'rec_hd_pr151_multichannel')
    fs=load_module(fs_path,FS_BLOB,'rec_hd_pr155_field_semantics')
    parsed=fs.parse_lamda_hd(source,require_original=True)
    lev,rad,cols=mc.decode(source)
    if (len(lev),len(rad),len(cols))!=(9,8,2):raise AssertionError('source topology')
    with mp.workdps(95):
        p,beta,E,G=mc.generate(lev,rad,cols,T,den,source_consistent=False)
        q,_,_,_=mc.generate(lev,rad,cols,T,den,source_consistent=True)
        if len(p)!=26 or len(q)!=26:raise AssertionError('channel count')
        if any(a['down']!=b['down'] or a['up']!=b['up'] for a,b in zip(p[8:],q[8:])):
            raise AssertionError('collision edges changed under photon policy')
        rows=[]
        for j in range(1,9):
            e=rad[j-1];gap=per_event(lev[j]['w'],lev[j-1]['w'],e['nu_GHz'])
            nu_e=Fraction(gap['nu_E_Hz']);nu_p=Fraction(gap['nu_P_Hz'])
            g=Fraction(2*j+1,2*j-1)
            direct=mp.exp(-beta*(E[j]-E[j-1]))*mp.mpf(g.numerator)/g.denominator*p[j-1]['down']-p[j-1]['up']
            oracle=analytic_bath_rate(e['A'],g,nu_e,nu_p,T)
            if abs(direct-oracle)>mp.mpf('1e-78'):
                raise AssertionError(f'Einstein bath rate discrepancy J{j}')
            defect=-H*(nu_e-nu_p);energy=mp.mpf(defect.numerator)/defect.denominator*direct
            if energy < -mp.mpf('1e-75'):raise AssertionError('LTE+Planck ledger sign')
            if abs(q[j-1]['photon_E']-q[j-1]['dE'])>mp.mpf('1e-80'):
                raise AssertionError('energy-gap switch failed')
            rows.append({**gap,'J_upper':j,'J_lower':j-1,'A_s_inv':e['A'],
                         'synthetic_T_K':T,'synthetic_n_lower_m_minus_3':'1',
                         'synthetic_net_down_events_m_minus_3_s_minus_1':mp.nstr(direct,45),
                         'synthetic_total_energy_residual_W_m_minus_3':mp.nstr(energy,45),
                         'synthetic_analytic_rate_abs_diff':mp.nstr(abs(direct-oracle),8)})
        mutant=copy.deepcopy(rad)
        mutant[1]['nu_GHz']=str(Decimal(mutant[1]['nu_GHz'])+Decimal('0.001'))
        mutated,_,_,_=mc.generate(lev,mutant,cols,T,den,source_consistent=False)
        changed=[i for i,(a,b) in enumerate(zip(p,mutated)) if a['up']!=b['up'] or a['down']!=b['down']]
        if changed!=[1]:raise AssertionError(f'optional frequency mutation changed {changed}')
        if len(fs.frequency_comparison(parsed)['lines'])!=8:raise AssertionError('field semantics count')
        return {'schema':'REC_HD_CONSUMER_CALLSITE_SOURCE_ONLY_V1',
                'source':{'bytes':len(source),'sha256':SOURCE_SHA,'verified':True,
                          'core_sha256':parsed['core_sha256'],'CDMS_2011_v2_raw':'NOT_ACQUIRED'},
                'pinned_code':{'PR151_multichannel_git_blob':git_blob(Path(mc_path).read_bytes()),
                               'PR155_field_semantics_git_blob':git_blob(Path(fs_path).read_bytes())},
                'policy':{'PR151_default':'MIXED_PRINTED_PHOTON_WITH_LEVEL_ENERGY',
                          'PR151_source_consistent':'ENERGY_GAP_DIAGNOSTIC_SWITCH',
                          'PR151_collisions':'LEVEL_ENERGY_ONLY',
                          'PR155':'TWO_POLICY_COMPARISON_ONLY'},
                'metamorphic':{'J2_optional_frequency_shift_GHz':'0.001',
                               'changed_radiative_edge_zero_based_indices':changed,
                               'changed_collision_edges':0,'unchanged_other_radiative_edges':7,
                               'original_source_bytes_mutated':False},
                'rows':rows,'original_35Hz_gate':'FAIL_7_OF_8_PRESERVED',
                'H5_epsilon':None,'H6':'OPEN','H7':'OPEN','L4_ready':False,
                'REI_activation':False,'production':'HOLD',
                'canonical_DAG':'28/88 (+0)','REC_physical_DAG':'0/313 (+0)',
                'scientific_claim':'SCOPED_CONDITIONAL_LOCAL_ENERGY_LEDGER_ONLY'}

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--source',required=True,type=Path)
    a.add_argument('--multichannel',required=True,type=Path)
    a.add_argument('--field-semantics',required=True,type=Path)
    a.add_argument('--T',type=int,default=100)
    a.add_argument('--den-cm3',type=int,default=1000)
    a.add_argument('--output',required=True,type=Path)
    args=a.parse_args()
    result=run(args.source.read_bytes(),args.multichannel,args.field_semantics,args.T,args.den_cm3)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    print(json.dumps({'rows':len(result['rows']),'source_sha256':SOURCE_SHA,
                      'changed_edges':result['metamorphic']['changed_radiative_edge_zero_based_indices'],
                      'output':str(args.output)},indent=2))

if __name__=='__main__':main()
