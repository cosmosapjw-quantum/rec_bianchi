#!/usr/bin/env python3
"""One finite new cross-energy diagnostic; no source alteration or IVP.

Original 35Hz result is rechecked only to label each saved row in a new thermal
question, NOT used to declare the historical HD adapter passed or re-run it.
"""
import argparse,csv,hashlib,json
from pathlib import Path
from decimal import Decimal,localcontext
import mpmath

SHA='0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb'
C=Decimal('299792458'); H=Decimal('6.62607015e-34'); KB=Decimal('1.380649e-23')
SOURCE_GAP_35_HZ=Decimal('35')
# CDMS v2 December 2011 webpage calls these reported fit inputs.
# It does NOT prove every printed LAMDA line is that measured observation.
DOC_REFS={1:'Drouin_2011_Jlower0',2:'Ulivi_1991_Jlower1',3:'Ulivi_1991_Jlower2',4:'Ulivi_1991_Jlower3',7:'Essenwanger_Gush_1984_Jlower6'}

def extract(data):
    s=data.decode('ascii').splitlines()
    a=s.index('!LEVEL + ENERGIES(cm^-1) + WEIGHT + J (or other quantum numbers)')+1
    b=s.index('!NUMBER OF RADIATIVE TRANSITIONS')
    lev=[]
    for line in s[a:b]:
        row=line.split();assert len(row)==4
        i,w,g,j=row; lev.append(dict(id=int(i),w=Decimal(w),w_literal=w,g=Decimal(g),J=int(j)))
    a=s.index('!TRANS + U + L + A(s^-1) + FREQ(GHz) + E_u/k(K)')+1
    b=s.index('!NUMBER OF COLL PARTNERS')
    lines=[]
    for line in s[a:b]:
        row=line.split();assert len(row)==6
        i,u,l,A,nu,ek=row
        lines.append(dict(id=int(i),upper=int(u),lower=int(l),A=Decimal(A),nu=Decimal(nu),nu_literal=nu,Eu_K=Decimal(ek)))
    assert len(lev)==9 and len(lines)==8
    assert [x['id'] for x in lev]==list(range(1,10))
    assert all(x['g']==2*x['J']+1 for x in lev)
    assert [x['J'] for x in lev]==list(range(9))
    assert [(x['upper'],x['lower']) for x in lines]==[(i+1,i) for i in range(1,9)]
    return lev,lines

def compute(b):
    lev,lines=extract(b)
    with localcontext() as ctx:
        ctx.prec=80
        mpmath.mp.dps=120
        rows=[]; maxoracle=Decimal(0)
        for t in lines:
            i=t['id']; lo=lev[t['lower']-1];up=lev[t['upper']-1]
            ew=up['w']-lo['w']; hz=Decimal(10)**9*t['nu']; eghz=C*Decimal(100)*ew
            residual_hz=eghz-hz
            relative_frequency_gap=residual_hz/hz
            kvals={}
            for Tk in [50,100,200]:
                T=Decimal(Tk)
                Enu=H*hz;Eg=H*eghz
                # j/alpha divided by Planck B(nu,T), using level LTE E and line nu.
                j_over_a_over_B=( (Enu/(KB*T)).exp()-1 )/((Eg/(KB*T)).exp()-1)
                kappa=j_over_a_over_B-1
                with mpmath.workdps(120):
                    xx=mpmath.mpf(str(Enu/(KB*T)))
                    yy=mpmath.mpf(str(Eg/(KB*T)))
                    mm=mpmath.expm1(xx)/mpmath.expm1(yy)-1
                error=abs(kappa-Decimal(mpmath.nstr(mm,110)))
                maxoracle=max(maxoracle,error)
                # Physical sign test: Eg > Enu => j/alpha < Planck.
                assert (kappa<0)==(residual_hz>0) or residual_hz==0
                kvals[str(Tk)]={'Kirchhoff_ratio_minus_1':str(kappa),
                    'one_plus_ratio':str(j_over_a_over_B),'mpmath_absolute_difference':str(error)}
            rows.append({'line_id':i,'upper_J':up['J'],'lower_J':lo['J'],
                'upper_cm_inv':up['w_literal'],'lower_cm_inv':lo['w_literal'],
                'line_GHz':t['nu_literal'],'signed_delta_hz':str(residual_hz),
                'absolute_delta_hz':str(abs(residual_hz)),
                'relative_frequency_gap':str(relative_frequency_gap),
                'printed_rounding_35Hz_gate':bool(abs(residual_hz)<=SOURCE_GAP_35_HZ),
                '2011_cdms_document_reported_fit_input':DOC_REFS.get(i),
                'direct_2011_v2_catalog_row_archive_verified':False,
                'thermal':kvals})
        assert len(rows)==8 and sum(r['printed_rounding_35Hz_gate'] for r in rows)==1
        assert [r['line_id'] for r in rows if r['printed_rounding_35Hz_gate']]==[1]
        assert maxoracle<Decimal('1e-65'),maxoracle
        assert sum(1 for r in rows if r['2011_cdms_document_reported_fit_input'])==5
        # Along a chain, adjusting unqualified level values to photon frequency
        # always yields a gauge-dependent closed ladder. This is NOT a repair.
        ladder=[Decimal(0)];nu_by_line={r['line_id']:Decimal(r['line_GHz'])*Decimal(10)**9 for r in rows}
        for i in range(1,9):ladder.append(ladder[-1]+nu_by_line[i]/(Decimal(100)*C))
        unconstrained_ladder_end=ladder[-1]
        # Without independently qualified level energies, the chain offers no
        # cycle constraint to decide which column is physically authoritative.
        assert len(ladder)==9
        return {'schema':'REC_HD_V2_DOCUMENT_LINEAGE_AND_THERMAL01','source_SHA256':SHA,
            'original_gate_status':'PRESERVED_FAIL_7_OF_8','model':'Boltzmann populations from printed levels, Einstein source at printed line frequencies, 50/100/200K',
            'status':'PASS_SCOPED_DIAGNOSTIC_HOLD_SOURCE_RECONCILIATION',
            'data':rows,'max_oracle_abs':str(maxoracle),
            'hypothetical_line_frequency_ladder_J8_cm_inv':str(unconstrained_ladder_end),
            'hypothetical_ladder_is_not_repair':True,
            '2011_v2_catalog_byte_source':'NOT_ACQUIRED',
            'LAMDA_2021_raw_recovered':True,
            'CODATA_SI_exact_constants':{'c':'299792458 m/s','h':'6.62607015e-34 J s','k_B':'1.380649e-23 J/K'},
            'not_admitted':['7 original source rows','full joint Kirchhoff thermal source','any collision rate or physical uncertainty','new H-Li atomic/anion/metastable species','production or REI']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    b=a.source.read_bytes();assert len(b)==2289 and hashlib.sha256(b).hexdigest()==SHA
    out=compute(b)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'RESULT.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    with (a.out/'LINES.csv').open('w',newline='') as f:
        cols=['line_id','upper_J','lower_J','line_GHz','signed_delta_hz','relative_frequency_gap',
              'thermal_50','thermal_100','thermal_200','reported_fit_input']
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for r in out['data']:
            w.writerow(dict(line_id=r['line_id'],upper_J=r['upper_J'],lower_J=r['lower_J'],line_GHz=r['line_GHz'],
               signed_delta_hz=r['signed_delta_hz'],relative_frequency_gap=r['relative_frequency_gap'],
               **{'thermal_'+str(T):r['thermal'][str(T)]['Kirchhoff_ratio_minus_1'] for T in [50,100,200]},
               reported_fit_input=r['2011_cdms_document_reported_fit_input'] or 'UNASSIGNED_DOC'))
    print(json.dumps({k:v for k,v in out.items() if k not in ('data','not_admitted')},indent=2))

if __name__=='__main__':main()
