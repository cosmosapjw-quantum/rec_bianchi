"""Source-qualified HD J1 CMB thermal balance and nine-level diagnostic.

Scientific inputs: 2021 LAMDA 9-level/Flower rate TRANSCRIPTION from immutable
PR161; reported 2023 Sung four measured line centers from immutable PR164.
Under original 35-Hz source gate only J=1->0 is eligible for source-qualified
calculation; full-nine outputs are CONDITIONAL_DIAGNOSTICS, never production.
No external background other than Planck CMB, no trapping or cosmic IVP.
"""
from __future__ import annotations
import argparse
import csv
from decimal import Decimal, getcontext
from pathlib import Path
import hashlib
import json
from mpmath import mp

getcontext().prec = 60
C = Decimal('299792458')
H = Decimal('6.62607015e-34')
KB = Decimal('1.380649e-23')
T0 = Decimal('2.72548')  # Fixsen (2009) combined-literature central estimate; K
SOURCE_SHA = 'd44406daf59616c982ca7a33bb3ee962138130588dfb74c7b801972c933da796'
SUNG_SHA = 'e568752432b1dc45e2b5ca37f8b767dad0ced0cea2c289fa29dc77ccdbf8da32'


def require(pred, message):
    if not pred:
        raise ValueError(message)


def load_sources(source_file, sung_file):
    a,b=Path(source_file).read_bytes(),Path(sung_file).read_bytes()
    require(hashlib.sha256(a).hexdigest() == SOURCE_SHA, 'Source PR161 digest mismatch')
    require(hashlib.sha256(b).hexdigest() == SUNG_SHA, 'Sung PR164 digest mismatch')
    src,sung=json.loads(a),json.loads(b)
    require(src['schema']=='REC_HD_LAMDA_20210607_SOURCE_TRANSCRIPTION_V1', 'LAMDA source schema')
    require(src['exact_source_bytes_acquired'] is False, 'Do not promote source transcription to raw')
    require(len(src['levels'])==9 and len(src['radiative_lines'])==8,'Source levels mismatch')
    require(src['2011_source_gate_pass_J']==[1] and src['2011_source_gate_fail_J']==list(range(2,9)), '35Hz gate altered')
    require(src['temperature_nodes_K']==[50,100,200], 'Source temperatures altered')
    require(sung['primary_source']['joint_covariance'] is None, 'Unexpected joint covariance')
    require(len(sung['line_parameters'])==4 and len(sung['inherited_measurements'])==5, 'Sung source mismatch')
    return src,sung


def frequency_ledger(src):
    out=[]
    for i,l in enumerate(src['radiative_lines'],start=1):
        e1=Decimal(src['levels'][i]['E_cm1'])
        e0=Decimal(src['levels'][i-1]['E_cm1'])
        nu_e=(e1-e0)*Decimal(100)*C
        nu_p=Decimal(l['nu_GHz'])*Decimal(10)**9
        diff=nu_e-nu_p
        out.append({'J':i,'nu_from_term_Hz':str(nu_e), 'nu_printed_Hz':str(nu_p),
                    'nu_term_minus_printed_Hz':str(diff),
                    'frozen_35Hz_gate': 'PASS' if abs(diff)<=35 else 'FAIL'})
    require(sum(x['frozen_35Hz_gate']=='PASS' for x in out)==1, 'Original gate must remain FAIL7/8')
    return out


def mpv(x):
    return mp.mpf(str(x))


def weight(src,j):
    return mpv(src['levels'][j]['g'])


def gap(src,u,l):
    return mpv(src['levels'][u]['E_cm1'])-mpv(src['levels'][l]['E_cm1'])


def x_gap(src,u,l,T):
    return mpv('100')*mpv(C)*mpv(H)*gap(src,u,l)/(mpv(KB)*mpv(T))


def nu_gap(src,u,l):
    return mpv(C)*mpv('100')*gap(src,u,l)


def bose(src,u,l,Tbg):
    require(mpv(Tbg)>0,'background temperature must be > 0')
    return 1/mp.expm1(x_gap(src,u,l,Tbg))


def collision_rates(src,Tgas,nH2,ortho):
    require(type(Tgas) is int and Tgas in (50,100,200),'Only actual LAMDA source temperature nodes')
    require(mpv(nH2)>=0 and mp.isfinite(mpv(nH2)),'negative/nonfinite density')
    require(0<=mpv(ortho)<=1,'ortho range')
    i=src['temperature_nodes_K'].index(Tgas)
    p=src['collision_partner_para_H2']['rates_cm3_s1']
    o=src['collision_partner_ortho_H2']['rates_cm3_s1']
    result=[]
    for v,w in zip(p,o):
        u,l=v['upper_J'],v['lower_J']
        require((u,l)==(w['upper_J'],w['lower_J']),'collision source edge mismatch')
        q=(1-mpv(ortho))*mpv(v['values'][i])+mpv(ortho)*mpv(w['values'][i])
        down=mpv(nH2)*q
        up=down*(weight(src,u)/weight(src,l))*mp.exp(-x_gap(src,u,l,Tgas))
        result.append((u,l,down,up))
    require(len(result)==9, '9 collision edges required')
    return result


def radrates(src,Tbg):
    out=[]
    for j,line in enumerate(src['radiative_lines'],start=1):
        u,l=j,j-1
        A=mpv(line['A_s1'])
        n=bose(src,u,l,Tbg)
        out.append((u,l,A*(1+n),A*(weight(src,u)/weight(src,l))*n))
    return out


def twolevel(src,Tgas,nH2,ortho,Tbg):
    """Exact 2-state formula with source-qualified J1 gap and frequency ledger."""
    mp.dps=80
    c=collision_rates(src,Tgas,nH2,ortho)
    d=next((cdown,cup) for (u,l,cdown,cup) in c if (u,l)==(1,0))
    down,up=d
    rad_down,rad_up=radrates(src,Tbg)[0][2:]
    norm=down+up+rad_down+rad_up
    p1=(up+rad_up)/norm
    p0=1-p1
    energy=mpv(H)*nu_gap(src,1,0)
    # Emission/absorption are large individually for Tbg > 0, net is signed.
    net=energy*(p1*rad_down-p0*rad_up)
    coll=energy*(p0*up-p1*down)
    require(mp.almosteq(net,coll,rel_eps=mp.mpf('1e-52'),abs_eps=mp.mpf('1e-80')),'J1 energy identity')
    return {'p1':p1,'net':net,'coll':coll,'emitted':energy*p1*rad_down,
            'absorbed':energy*p0*rad_up,'p0':p0}


def full9(src,Tgas,nH2,ortho,Tbg):
    """Nine-level conditional diagnostic; all level energies from CDMS-derived LAMDA term fields."""
    mp.dps=80
    Q=mp.matrix(9,9)
    def add(u,l,r):
        require(r>=0 and mp.isfinite(r), 'invalid transition rate')
        Q[l,u]+=r;Q[u,u]-=r
    rad=radrates(src,Tbg)
    coll=collision_rates(src,Tgas,nH2,ortho)
    for u,l,d,up in rad:
        add(u,l,d);add(l,u,up)
    for u,l,d,up in coll:
        add(u,l,d);add(l,u,up)
    bal=mp.matrix(Q)
    for j in range(9):bal[8,j]=1
    rhs=mp.matrix([0,0,0,0,0,0,0,0,1])
    p=mp.lu_solve(bal,rhs)
    require(abs(sum(p)-1)<mp.mpf('1e-60'),'normalization failed')
    require(max(abs(sum(Q[i,j]*p[j] for j in range(9))) for i in range(9))<mp.mpf('1e-60'),'steady state failed')
    require(min(p)>-mp.mpf('1e-60'),'negative physical populations beyond calculation error')
    total_rad=mp.mpf(0);total_col=mp.mpf(0);records=[]
    for u,l,d,up in rad:
        energy=mpv(H)*nu_gap(src,u,l)
        emit=energy*p[u]*d
        absor=energy*p[l]*up
        net=emit-absor
        total_rad+=net
        records.append({'J':u,'net':net,'emitted':emit,'absorbed':absor,'pupper':p[u],'plower':p[l]})
    for u,l,d,up in coll:
        total_col+=mpv(H)*nu_gap(src,u,l)*(p[l]*up-p[u]*d)
    require(mp.almosteq(total_rad,total_col,rel_eps=mp.mpf('1e-48'),abs_eps=mp.mpf('1e-73')),
            'radiative/collisional energy ledger failed')
    return {'p':list(p),'net':total_rad,'coll':total_col,'lines':records,
            'emitted':sum(r['emitted'] for r in records),'absorbed':sum(r['absorbed'] for r in records)}


def fmt(v,digits=19):
    return mp.nstr(v,digits)


def build_tables(src,sung):
    rows=[];lines=[];J1=[];results={}
    zs=[0,10,30,50]
    dens=['1','100','10000','1000000']
    fracs=['0','0.5','1']
    for Tgas in src['temperature_nodes_K']:
        for zz in zs:
            Tbg=mpv(T0)*(zz+1)
            for n in dens:
                for f in fracs:
                    a=twolevel(src,Tgas,n,f,Tbg)
                    b=full9(src,Tgas,n,f,Tbg)
                    pk=f'{Tgas}:{zz}:{n}:{f}'
                    def em(v):return fmt(v,23)
                    rows.append({'case':pk,'Tgas_K':Tgas,'z':zz,'Tcmb_K':fmt(Tbg,10),'n_H2_cm_minus3':n,
                         'f_ortho':f,'J1_net_W_per_HD':em(a['net']),
                         'full9_net_W_per_HD_DIAGNOSTIC':em(b['net']),
                         'full9_emitted_W_per_HD':em(b['emitted']),
                         'full9_absorbed_W_per_HD':em(b['absorbed']),
                         'full9_population_J0':em(b['p'][0]),
                         'full9_population_J1':em(b['p'][1]),
                         '9level_source_35Hz_gate':'FAIL7/8_DIAGNOSTIC_ONLY'})
                    J1.append({'case':pk,'Tgas_K':Tgas,'z':zz,'Tcmb_K':fmt(Tbg,10),'n_H2_cm_minus3':n,
                          'f_ortho':f,'p0':em(a['p0']),'p1':em(a['p1']),
                          'net_W_per_HD':em(a['net']),'emitted_W_per_HD':em(a['emitted']),
                          'absorbed_W_per_HD':em(a['absorbed']),
                          'source_35Hz_gate':'PASS_J1_ONLY'})
                    for v in b['lines']:
                        lines.append({'case':pk,'upper_J':v['J'],'lower_J':v['J']-1,
                           'net_W_per_HD_DIAGNOSTIC':em(v['net']),
                           'emitted_W_per_HD':em(v['emitted']),
                           'absorbed_W_per_HD':em(v['absorbed']),
                           'pupper':em(v['pupper']),
                           'source_35Hz_gate':'PASS' if v['J']==1 else 'FAIL'})
    obs=[]
    for p in sung['line_parameters']:
        for z in zs:
            nu=Decimal(p['nu0_cm_minus1'])*100*C
            nu_obs=nu/(z+1)
            obs.append({'R':p['R'],'upper_J':p['upper_J'],'lower_J':p['lower_J'],
                        'z':z,'measured_source_center_cm_minus1':p['nu0_cm_minus1'],
                        'rest_frequency_Hz':str(nu), 'observed_frequency_Hz_if_FRW':str(nu_obs),
                        'observed_wavelength_m_if_FRW':str(C/nu_obs),
                        'source_DOI':sung['primary_source']['doi'],
                        'not_telescope_observation':True})
    return rows,lines,J1,obs


def writecsv(path,rows):
    with open(path,'w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)


def produce(source_file,sung_file,output_dir):
    mp.dps=80
    src,sung=load_sources(source_file,sung_file)
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    freq=frequency_ledger(src)
    rows,lines,j1,sung_obs=build_tables(src,sung)
    assert len(rows)==144 and len(lines)==1152 and len(j1)==144 and len(sung_obs)==16
    writecsv(out/'HD9_CMB_144_DIAGNOSTIC_CASES.csv',rows)
    writecsv(out/'HD9_CMB_PERLINE_1152.csv',lines)
    writecsv(out/'HD_J1_CMB_144_SOURCE_GATED.csv',j1)
    writecsv(out/'SUNG4_REDSHIFT_MAPPING_16.csv',sung_obs)
    writecsv(out/'LAMDA_ORIGINAL_35HZ_LEDGER.csv',freq)
    def one(T,z,n='10000',f='0.5'):
        return next(v for v in rows if (v['Tgas_K'],v['z'],v['n_H2_cm_minus3'],v['f_ortho'])==(T,z,n,f))
    signed=[]
    for T in (50,100,200):
        for z in [0,10,30,50]:
            x=one(T,z)
            signed.append({'Tgas_K':T,'z':z,'Tcmb_K':x['Tcmb_K'],
                           'J1_net_W_per_HD':x['J1_net_W_per_HD'],
                           'HD9_net_W_per_HD_DIAGNOSTIC':x['full9_net_W_per_HD_DIAGNOSTIC']})
    summary={
     'schema':'REC_HD_CMB_SOURCE_QUALIFIED_J1_AND_NINE_LEVEL_DIAGNOSTIC_V1',
     'source_LAMDA_transcription_sha256':SOURCE_SHA,'source_Sung_SHA256':SUNG_SHA,
     'LAMDA_original_raw_bytes_acquired':False,'CDMS_original_2011_v2_raw_acquired':False,
     'Neufeld2026_Zenodo_original_bytes_acquired':False,
     'source_frequency_gate':{'J1':'PASS','J2_to_J8':'FAIL7/8'},
     'model':{'CMB_T0_K':str(T0),'CMB_T0_reference':'Fixsen 2009 DOI 10.1088/0004-637X/707/2/916',
              'temperature_nodes_K':[50,100,200], 'redshift_nodes':[0,10,30,50],
              'density_cm_minus3':['1','100','10000','1000000'], 'ortho_H2_fractions':['0','0.5','1'],
              'optically_thin':True,'only_CMB_radiative_bath':True,'colliders':'para/ortho-H2 only',
              'steady_state':True,'cosmic_IVP':False,'spectral_transfer':False},
     'new_conditional_physical_data':{'J1_source_gated_cases':len(j1),'nine_level_diagnostic_cases':len(rows),
        'nine_level_perline_photons':len(lines),'Sung_source_bound_redshifted_frequency_rows':len(sung_obs)},
     'critical_redshifts_Tgas_equals_Tcmb':{str(T):str(Decimal(T)/T0-1) for T in (50,100,200)},
     'sample_steady_state':signed,
     'statistical_sigma':None,'chi_square':None,'canonical_DAG':'28/88',
     'REC_physical_DAG':'0/313','REC_EXP_SPECTRAL':'PARTIAL',
     'original_35Hz':'FAIL7/8','H5_epsilon':None,'H6':'OPEN','H7':'OPEN',
     'L4_ready':False,'REI_activation':False,'production':'HOLD','auto_next_node':False,
     'auxiliary_model_claim':'J1_SOURCE_GATED_ONLY; FULL9_DIAGNOSTIC_ONLY',
    }
    (out/'RESULTS.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser()
    base=Path(__file__).resolve().parents[1]
    p.add_argument('--LAMDA',default=str(base/'input/LAMDA_HD_PR161_SOURCE_TRANSCRIPTION.json'))
    p.add_argument('--Sung',default=str(base/'input/SUNG_HD_PR164_SOURCE.json'))
    p.add_argument('--out',default=str(base/'evidence'))
    args=p.parse_args()
    print(json.dumps(produce(args.LAMDA,args.Sung,args.out)['new_conditional_physical_data'],indent=2))
