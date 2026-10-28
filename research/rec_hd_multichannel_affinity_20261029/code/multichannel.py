#!/usr/bin/env python3
"""Source-locked HD independent-channel Markov affinity diagnostic.

9 original level identities, 8 original radiative lines, para/ortho H2
collisional downward rates at EXACT 50/100/200 K. Two collider densities
are arbitrary explicitly declared non-physical diagnostic parameters.
No physical entropy production, no time IVP and no source replacement.
"""
import argparse, csv, hashlib, json
from pathlib import Path
import mpmath as mp

SRC_SHA='0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb'
C='299792458'; H='6.62607015e-34'; KB='1.380649e-23'
TEMPS=(50,100,200); DENSITIES=(1000,1000000)

def decode(src):
    if len(src)!=2289 or hashlib.sha256(src).hexdigest()!=SRC_SHA: raise ValueError('IMMUTABLE_INPUT_HASH_FAIL')
    lines=src.decode('ascii').splitlines()
    ia=lines.index('!LEVEL + ENERGIES(cm^-1) + WEIGHT + J (or other quantum numbers)')+1
    ib=lines.index('!NUMBER OF RADIATIVE TRANSITIONS')
    level=[]
    for line in lines[ia:ib]:
        row=line.split();assert len(row)==4
        i,w,g,j=row;level.append({'index':int(i),'w':w,'g':g,'J':int(j)})
    ia=lines.index('!TRANS + U + L + A(s^-1) + FREQ(GHz) + E_u/k(K)')+1
    ib=lines.index('!NUMBER OF COLL PARTNERS')
    rad=[]
    for line in lines[ia:ib]:
        row=line.split();assert len(row)==6
        i,u,l,A,nu,Ek=row;rad.append({'index':int(i),'u':int(u)-1,'l':int(l)-1,'A':A,'nu_GHz':nu,'upper_K_print':Ek})
    cols=[]
    for marker,ctype in [('2 HD-pH2','p-H2'),('3 HD-oH2','o-H2')]:
        ia=next(i for i,x in enumerate(lines) if x.startswith(marker))+1
        hdr=lines.index('!TRANS + UP + LOW + RATES [cm3 s-1]',ia)+1
        rows=[]
        for line in lines[hdr:hdr+9]:
            v=line.split();assert len(v)==6
            i,u,l,*q=v;rows.append({'index':int(i),'u':int(u)-1,'l':int(l)-1,'q_cm3_s':q})
        cols.append({'type':ctype,'rows':rows})
    assert len(level)==9 and [x['index'] for x in level]==list(range(1,10))
    assert [x['J'] for x in level]==list(range(9))
    assert len(rad)==8 and [(e['u'],e['l']) for e in rad]==[(j,j-1) for j in range(1,9)]
    assert len(cols)==2 and all(len(c['rows'])==9 for c in cols)
    assert all([(r['u'],r['l']) for r in c['rows']]==[(1,0),(2,0)]+[(j,j-1) for j in range(2,9)] for c in cols)
    return level,rad,cols

def parameters(level):
    c=mp.mpf(C);h=mp.mpf(H);k=mp.mpf(KB)
    W=[mp.mpf(x['w']) for x in level]
    E=[h*c*100*w for w in W]
    G=[mp.mpf(x['g']) for x in level]
    return c,h,k,E,G

def generate(level,rad,cols,T,den,source_consistent=False):
    if T not in TEMPS or den not in DENSITIES:raise ValueError('SOURCE_UNSUPPORTED_T_OR_N')
    c,h,k,E,G=parameters(level)
    beta=1/(k*mp.mpf(T))
    edges=[]
    for e in rad:
        i,j=e['l'],e['u']; dE=E[j]-E[i]
        nu= dE/h if source_consistent else mp.mpf(e['nu_GHz'])*mp.mpf('1e9')
        nbar=1/mp.expm1(beta*h*nu)
        A=mp.mpf(e['A'])
        edges.append({'type':'rad','key':f'J{j}->J{i}','l':i,'u':j,
                      'down':A*(1+nbar),'up':A*(G[j]/G[i])*nbar,'dE':dE,'photon_E':h*nu})
    for col in cols:
        ctype=col['type']
        for row in col['rows']:
            i,j=row['l'],row['u'];dE=E[j]-E[i]
            q=mp.mpf(row['q_cm3_s'][TEMPS.index(T)])
            down=q*mp.mpf(den)  # cm^3 /s times cm^-3 -> s^-1
            up=down*(G[j]/G[i])*mp.exp(-beta*dE)
            edges.append({'type':ctype,'key':f'J{j}->J{i}','l':i,'u':j,
                          'down':down,'up':up,'dE':dE,'photon_E':None})
    assert len(edges)==8+2*9
    return edges,beta,E,G

def solve_stationary(edges):
    n=9;Q=mp.matrix(n)
    for e in edges:
        i,j=e['l'],e['u'];down=e['down'];up=e['up']
        Q[j,i]+=up;Q[i,i]-=up
        Q[i,j]+=down;Q[j,j]-=down
    S=Q.copy();b=mp.matrix(n,1)
    for i in range(n):S[n-1,i]=mp.mpf(1)
    b[n-1]=mp.mpf(1)
    p=mp.lu_solve(S,b)
    resid=max([abs(sum(Q[i,j]*p[j] for j in range(n))) for i in range(n)])
    assert abs(sum(p)-1)<mp.mpf('1e-60') and min(p)>0
    return Q,p,resid

def entropy_rate(edges,p):
    sigma=mp.mpf(0);source_rates={}
    for e in edges:
        i,j=e['l'],e['u'];f=p[i]*e['up'];b=p[j]*e['down']
        term=(f-b)*mp.log(f/b)
        if term < -mp.mpf('1e-75'):raise AssertionError('negative branch entropy')
        sigma+=term
        source_rates.setdefault(e['type'],mp.mpf(0))
        source_rates[e['type']]+=term
    return sigma,source_rates

def saved_source_results(level,rad,T):
    c,h,k,E,G=parameters(level)
    vals=[]
    for e in rad:
        i,j=e['l'],e['u']; delta=h*c*100*(mp.mpf(level[j]['w'])-mp.mpf(level[i]['w']))-h*mp.mpf(e['nu_GHz'])*mp.mpf('1e9')
        a=-delta/(k*mp.mpf(T)) # pair orientation rad down + collision up
        x=(E[j]-E[i])/(k*mp.mpf(T))
        K=mp.expm1(a)/(-mp.expm1(-x))
        vals.append({'line':j,'delta_hz':delta/h,'affinity_rad_down_collision_up':a,'K_from_A':K})
    triangle=-vals[0]['affinity_rad_down_collision_up']-vals[1]['affinity_rad_down_collision_up']
    return vals,triangle

def check_exact_affinities(level,rad,cols,T,den,edges,thermal,triangle,beta):
    # Derive from actual positive channel rate products, not source delta formula.
    by={(e['type'],e['u'],e['l']):e for e in edges}
    errors=[]
    for j in range(1,9):
        r=by['rad',j,j-1]
        for typ in ('p-H2','o-H2'):
            c=by[typ,j,j-1]
            actual=mp.log(r['down']*c['up']/(r['up']*c['down']))
            errors.append(abs(actual-thermal[j-1]['affinity_rad_down_collision_up']))
    r01=by['rad',1,0];r12=by['rad',2,1]
    for typ in ('p-H2','o-H2'):
        c20=by[typ,2,0]
        tr=mp.log((r01['up']*r12['up']*c20['down'])/(r01['down']*r12['down']*c20['up']))
        errors.append(abs(tr-triangle))
    return max(errors)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--prior',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    source=args.source.read_bytes()
    levels,radiation,colliders=decode(source)
    prior=json.loads(args.prior.read_text())
    assert prior['source_SHA256']==SRC_SHA and len(prior['data'])==8
    mp.mp.dps=90
    rows=[];maxKerr=mp.mpf(0);maxAerr=mp.mpf(0);maxStationarity=mp.mpf(0)
    for T in TEMPS:
        thermal,trangle=saved_source_results(levels,radiation,T)
        for j,v in enumerate(thermal):
            K0=mp.mpf(prior['data'][j]['thermal'][str(T)]['Kirchhoff_ratio_minus_1'])
            maxKerr=max(maxKerr,abs(v['K_from_A']-K0))
        for den in DENSITIES:
            es,beta,E,G=generate(levels,radiation,colliders,T,den)
            Q,p,resid=solve_stationary(es)
            sigma, parts=entropy_rate(es,p)
            Aerr=check_exact_affinities(levels,radiation,colliders,T,den,es,thermal,trangle,beta)
            maxAerr=max(maxAerr,Aerr); maxStationarity=max(maxStationarity,resid)
            # Negative control: synthetic single energy reference across both channels.
            eq,beta,E,G=generate(levels,radiation,colliders,T,den,source_consistent=True)
            Q0,p0,r0=solve_stationary(eq);sigma0,parts0=entropy_rate(eq,p0)
            expected=[G[i]*mp.exp(-beta*E[i]) for i in range(9)];norm=sum(expected);expected=[x/norm for x in expected]
            assert max(abs(p0[i]-expected[i]) for i in range(9)) < mp.mpf('1e-65')
            assert abs(sigma0) < mp.mpf('1e-65')
            assert sigma > 0, (T,den,mp.nstr(sigma,15))
            row={
             'T_K':T,'pH2_and_oH2_density_each_cm3':den,
             'original_source_sigma_formal_per_s':mp.nstr(sigma,65),
             'synthetic_equal_energy_sigma_formal_per_s':mp.nstr(sigma0,65),
             'affinity_max_absolute':mp.nstr(max(abs(v['affinity_rad_down_collision_up']) for v in thermal),65),
             'triangle_affinity_0_rad_1_rad_2_col_0':mp.nstr(trangle,65),
             'max_affinity_direct_rate_residual':mp.nstr(Aerr,65),
             'generator_infty_residual_per_s':mp.nstr(resid,65),
             'stationary_population':list(map(lambda x:mp.nstr(x,50),p)),
             'entropy_by_channel_per_s':{typ:mp.nstr(value,50) for typ,value in parts.items()},
             'pairs':[{'line':j,'delta_hz':mp.nstr(v['delta_hz'],45),'A_rad_down_col_up':mp.nstr(v['affinity_rad_down_collision_up'],55),'previous_K_from_A':mp.nstr(v['K_from_A'],55)} for j,v in enumerate(thermal,start=1)]}
            rows.append(row)
    assert maxKerr<mp.mpf('1e-65')
    assert maxAerr<mp.mpf('1e-65')
    assert maxStationarity<mp.mpf('1e-65')
    result={'schema':'REC_HD_MULTICHANNEL_AFFINITY01_PRIMARY_V1','input_SHA256':SRC_SHA,'units':{'affinity':'dimensionless','sigma':'per s, entropy units kB per molecule','q_down':'cm3 s^-1','density':'cm^-3'},
      'models':'Blackbody radiative channels at each frozen T; detailed-balance-upfilled H2 collider channels; arbitrary equal p/o densities for diagnostics only',
      'temperature_nodes_K':TEMPS,'density_pairs_cm3_each':DENSITIES,'channel_count':26,
      'source_collisions_by_partner':9,'original_35Hz_gate':'FAIL_7_OF_8_PRESERVED',
      'max_K_identity_error':mp.nstr(maxKerr,65),'max_direct_rate_affinity_error':mp.nstr(maxAerr,65),
      'max_stationarity_absolute':mp.nstr(maxStationarity,65),
      'rows':rows,'status':'PASS_SCOPED_SYNTHETIC_MARKOV_DIAGNOSTIC',
      'limits':['no CDMS v2 numerical raw archive','no physical radiation/collider density history','no physical entropy production claim','no spectroscopy repair','no original historical campaign or IVP'],
      'central_DAG':'28/88+0','REI_activation':False}
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))

if __name__=='__main__': main()
