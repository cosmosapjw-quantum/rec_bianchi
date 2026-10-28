#!/usr/bin/env python3
"""REC HD field-authority and conditional line-centre transport diagnostic.

No physical source choice, source correction, stationary solve, or IVP is made.
The original LAMDA bytes remain private and are never published in public Git.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from decimal import Decimal, InvalidOperation, localcontext
from fractions import Fraction
from pathlib import Path

C_M_S=299792458
ORIGINAL_HD_BYTES=2289
ORIGINAL_HD_SHA256='0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb'
TOKEN=re.compile(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z')

def finite_decimal(s):
    if not isinstance(s,str) or not TOKEN.fullmatch(s):
        raise ValueError('not a finite printed decimal token')
    try: d=Decimal(s)
    except InvalidOperation as e: raise ValueError('invalid decimal token') from e
    if not d.is_finite(): raise ValueError('nonfinite decimal token')
    return d

def rat(q): return f'{q.numerator}/{q.denominator}'

def parse_lamda_hd(source:bytes,*,require_original=True):
    """Strict source identity, or explicitly unverified metamorphic input."""
    sha=hashlib.sha256(source).hexdigest()
    if require_original and (len(source)!=ORIGINAL_HD_BYTES or sha!=ORIGINAL_HD_SHA256):
        raise ValueError('immutable original HD source byte/sha mismatch')
    try: s=source.decode('ascii')
    except UnicodeDecodeError as e: raise ValueError('HD must be ASCII') from e
    rows=[x.strip() for x in s.splitlines() if x.strip() and not x.lstrip().startswith('!')]
    it=iter(rows)
    def take():
        try: return next(it).split()
        except StopIteration as e: raise ValueError('truncated LAMDA source') from e
    def integer():
        r=take()
        if len(r)!=1 or not r[0].isdigit(): raise ValueError('bad LAMDA count')
        return int(r[0])
    name=' '.join(take()); mass=take()
    if name!='HD spectroscopy from CDMS version 2 of December 2011' or len(mass)!=1 or finite_decimal(mass[0])<=0:
        raise ValueError('unexpected molecule/mass')
    if integer()!=9: raise ValueError('unexpected HD levels')
    levels=[]
    for j in range(9):
        r=take()
        if len(r)!=4 or int(r[0])!=j+1 or int(r[3])!=j: raise ValueError('bad level index')
        w,g=finite_decimal(r[1]),finite_decimal(r[2])
        if w<0 or g!=2*j+1 or (j and w<=finite_decimal(levels[-1]['w_cm_inv'])):
            raise ValueError('bad HD level ordering/weight')
        levels.append({'id':j+1,'J':j,'w_cm_inv':r[1],'g':r[2]})
    if integer()!=8: raise ValueError('unexpected radiative count')
    rad=[]
    for j in range(1,9):
        r=take()
        if len(r) not in (4,5,6) or tuple(map(int,r[:3]))!=(j,j+1,j):
            raise ValueError('bad radiative transition')
        if finite_decimal(r[3])<=0: raise ValueError('bad Einstein A')
        if len(r)>=5 and finite_decimal(r[4])<=0: raise ValueError('bad optional frequency')
        if len(r)==6 and finite_decimal(r[5])<=0: raise ValueError('bad optional E/k')
        rad.append({'id':j,'upper':j+1,'lower':j,'A_s_inv':r[3],
                    'nu_GHz_optional':r[4] if len(r)>=5 else None,
                    'E_up_K_optional':r[5] if len(r)==6 else None})
    if integer()!=2: raise ValueError('expected separate p/o H2 blocks')
    partners=[]
    for pid in (2,3):
        desc=take()
        if not desc or int(desc[0])!=pid: raise ValueError('partner id mismatch')
        if integer()!=9 or integer()!=3: raise ValueError('bad collision block count')
        temps=take()
        if len(temps)!=3 or list(map(finite_decimal,temps))!=[Decimal(50),Decimal(100),Decimal(200)]:
            raise ValueError('bad collision temperature nodes')
        coll=[]
        for k in range(1,10):
            r=take()
            if len(r)!=6 or int(r[0])!=k: raise ValueError('bad collision row')
            up,lo=int(r[1]),int(r[2])
            if not 1<=lo<up<=9 or any(finite_decimal(v)<=0 for v in r[3:]):
                raise ValueError('bad collision transition/rate')
            coll.append({'id':k,'upper':up,'lower':lo,'rates_cm3_s':r[3:]})
        if [(x['upper'],x['lower']) for x in coll]!=[(2,1),(3,1)]+[(j+1,j) for j in range(2,9)]:
            raise ValueError('unexpected collision graph')
        partners.append({'id':pid,'temperatures_K':temps,'collisions':coll})
    try: next(it); raise ValueError('unexpected trailing LAMDA records')
    except StopIteration: pass
    core={'name':name,'mass_amu':mass[0],'levels':levels,
          'radiative':[{k:e[k] for k in ('id','upper','lower','A_s_inv')} for e in rad],
          'partners':partners}
    canon=json.dumps(core,sort_keys=True,separators=(',',':')).encode('ascii')
    return {'source_bytes':len(source),'source_sha256':sha,
            'raw_verified_this_execution':require_original,
            'core':core,'core_sha256':hashlib.sha256(canon).hexdigest(),
            'optional_line_metadata':[
                {'id':e['id'],'nu_GHz':e['nu_GHz_optional'],'E_up_K':e['E_up_K_optional']}
                for e in rad]}

def frequency_comparison(parsed:dict)->dict:
    """Exact-rational fixed-A, fixed-population, fixed-sigma_v line-centre ratios.

    Compares at EACH convention's own line centre, not a common observing
    frequency. No Bianchi-frame transport or velocity gradient is modelled.
    """
    levels=parsed['core']['levels']; rad=parsed['core']['radiative']
    meta=parsed['optional_line_metadata']
    out=[]
    for e,m in zip(rad,meta):
        up,lo=e['upper']-1,e['lower']-1
        nu_E=Fraction(C_M_S*100)*(Fraction(finite_decimal(levels[up]['w_cm_inv']))-
                                     Fraction(finite_decimal(levels[lo]['w_cm_inv'])))
        if nu_E<=0: raise ValueError('nonpositive energy-gap frequency')
        row={'upper_J':up,'lower_J':lo,'nu_E_Hz_exact':rat(nu_E),
             'printed_nu_available':m['nu_GHz'] is not None}
        if m['nu_GHz'] is not None:
            nu_P=Fraction(10**9)*Fraction(finite_decimal(m['nu_GHz']))
            if nu_P<=0: raise ValueError('nonpositive printed photon frequency')
            r=nu_P/nu_E
            alpha_ratio=(nu_E/nu_P)**3
            with localcontext() as ctx:
                ctx.prec=70
                f=lambda q:Decimal(q.numerator)/Decimal(q.denominator)
                row.update({'nu_P_Hz_exact':rat(nu_P),
                            'delta_nu_E_minus_P_Hz_exact':rat(nu_E-nu_P),
                            'nu_P_over_nu_E_exact':rat(r),
                            'nu_P_over_nu_E_minus_one':str(f(r-1)),
                            'j_peak_P_over_E_exact':'1/1',
                            'alpha_peak_P_over_E_exact':rat(alpha_ratio),
                            'alpha_peak_P_over_E_minus_one':str(f(alpha_ratio-1)),
                            'S_peak_P_over_E_exact':rat(r**3),
                            'integrated_j_P_over_E_exact':rat(r)})
        out.append(row)
    return {'schema':'REC_HD_LAMDA_FIELD_SEMANTICS_V1',
            'original_raw_verified_this_execution':parsed['raw_verified_this_execution'],
            'source_sha256':parsed['source_sha256'],
            'source_bytes':parsed['source_bytes'],
            'core_sha256':parsed['core_sha256'],
            'core_fields':'levels/degeneracies, A, collision partner IDs/temperatures/rates',
            'metadata_fields':'printed FREQ and E_up/k, excluded from core projection',
            'format_policy':'LAMDA official format: printed FREQ is optional/advisory to described program',
            'consumer_policy':'NOT_INFERRED: source-specific consumers can use printed FREQ',
            'line_center_model':{'fixed':'A_ul, level populations, Gaussian velocity dispersion sigma_v, independent own line centers',
                                 'j_peak_P_over_E':'1',
                                 'alpha_peak_P_over_E':'(nu_E/nu_P)^3',
                                 'S_peak_P_over_E':'(nu_P/nu_E)^3',
                                 'integrated_j_P_over_E':'nu_P/nu_E'},
            'lines':out,'physical_admission':False,
            'original_35Hz_gate':'FAIL_7_OF_8_PRESERVED',
            'cdms_v2_raw':'NOT_ACQUIRED',
            'H5_epsilon':None,'L4_ready':False,'REI_activation':False,
            'production':'HOLD'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    parsed=parse_lamda_hd(args.source.read_bytes(),require_original=True)
    out=frequency_comparison(parsed)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps({'source_verified':out['original_raw_verified_this_execution'],
                      'core_sha256':out['core_sha256'],
                      'line_count':len(out['lines']),
                      'max_abs_opacity_relative_change':str(max(abs(Decimal(x['alpha_peak_P_over_E_minus_one'])) for x in out['lines']))},indent=2))

if __name__=='__main__':main()
