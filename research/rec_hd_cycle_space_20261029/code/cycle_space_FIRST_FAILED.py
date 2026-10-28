#!/usr/bin/env python3
"""Exact HD marked-graph cycle basis and source-energy obstruction.
No population IVP, 9x9 stationary solve, source replacement or producer admission.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from decimal import Decimal, localcontext
import sympy as sp
import mpmath as mp

SOURCE_SHA='0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb'
PRIOR151_SHA='e6e795921ee4af730edbdebd1faf52c7b902cc14e3d0c15ab56fba423b696881'
H=mp.mpf('6.62607015e-34'); KB=mp.mpf('1.380649e-23'); C_SI=mp.mpf('299792458')
TEMPS=(50,100,200)

def load(raw:bytes):
    assert len(raw)==2289 and hashlib.sha256(raw).hexdigest()==SOURCE_SHA, 'SOURCE_BYTES_MISMATCH'
    txt=raw.decode('ascii').splitlines()
    k=txt.index('!LEVEL + ENERGIES(cm^-1) + WEIGHT + J (or other quantum numbers)')
    levels=[txt[k+i+1].split() for i in range(9)]
    k=txt.index('!TRANS + U + L + A(s^-1) + FREQ(GHz) + E_u/k(K)')
    radiative=[txt[k+i+1].split() for i in range(8)]
    collisions=[]
    for marker,kind in [('2 HD-pH2','pH2'),('3 HD-oH2','oH2')]:
        k=next(i for i,line in enumerate(txt) if line.startswith(marker))
        k=txt.index('!TRANS + UP + LOW + RATES [cm3 s-1]',k)
        rows=[txt[k+i+1].split() for i in range(9)]
        collisions.append((kind,rows))
    assert [int(x[3]) for x in levels]==list(range(9))
    assert all(int(x[2])==2*int(x[3])+1 for x in levels)
    assert [(int(x[2])-1,int(x[1])-1) for x in radiative]==[(i-1,i) for i in range(1,9)]
    edges=[]
    for r in radiative:
        edges.append({'kind':'photon','lower':int(r[2])-1,'upper':int(r[1])-1,'A':r[3],'nu_GHz':r[4]})
    for kind,rows in collisions:
        for r in rows:
            edges.append({'kind':kind,'lower':int(r[2])-1,'upper':int(r[1])-1,'rates_cm3_s':r[3:]})
    assert len(edges)==26
    assert [(x['lower'],x['upper']) for x in edges[8:17]]==[(0,1),(0,2)]+[(i-1,i) for i in range(2,9)]
    assert [(x['lower'],x['upper']) for x in edges[17:]]==[(0,1),(0,2)]+[(i-1,i) for i in range(2,9)]
    return levels,edges

def graph_matrices(edges):
    n=9; m=len(edges)
    B=sp.zeros(n,m)
    for j,e in enumerate(edges):
        B[e['lower'],j]=-1;B[e['upper'],j]=1
    # pH2 adjacent tree: J0-1 is channel 8, J1-2 is channel10, ... J7-8 is channel16
    tree=[8]+list(range(10,17))
    chords=[j for j in range(m) if j not in tree]
    tree_edges={edges[j]['upper']:j for j in tree}
    assert len(tree_edges)==8 and set(tree_edges)==set(range(1,9))
    Z=sp.zeros(m,len(chords))
    for k,edge_idx in enumerate(chords):
        e=edges[edge_idx];Z[edge_idx,k]=1
        for upper in range(e['lower']+1,e['upper']+1):
            Z[tree_edges[upper],k]-=1
    D=sp.zeros(m,8)
    for j in range(8):D[j,j]=1
    M=Z.T*D
    return B,Z,D,M,tree,chords

def decimal_source_failures(levels,edges):
    with localcontext() as dc:
        dc.prec=60
        C=Decimal('299792458'); errors=[]
        for j in range(8):
            E=Decimal(levels[j+1][1])-Decimal(levels[j][1]);nu=Decimal(edges[j]['nu_GHz'])
            delta=C*100*E-Decimal('1e9')*nu
            errors.append({'J_upper':j+1,'signed_defect_Hz':str(delta),'35Hz_pass':abs(delta)<=Decimal(35)})
        assert [e['J_upper'] for e in errors if not e['35Hz_pass']]==list(range(2,9))
        return errors

def evaluate(levels,edges,graph,prior):
    B,Z,D,M,tree,chords=graph
    results=[];max_closure=mp.mpf(0);max_reuse=mp.mpf(0);max_decomp=mp.mpf(0)
    E=[H*C_SI*100*mp.mpf(x[1]) for x in levels]
    g=[mp.mpf(x[2]) for x in levels]
    for T in TEMPS:
        beta=1/(KB*T)
        for den in [1000,1000000]:
            u=[]
            for e in edges:
                l=e['lower'];j=e['upper'];de=E[j]-E[l]
                if e['kind']=='photon':
                    photon=H*mp.mpf(e['nu_GHz'])*mp.mpf('1e9')
                    nbar=1/mp.expm1(beta*photon)
                    down=mp.mpf(e['A'])*(1+nbar)
                    up=mp.mpf(e['A'])*g[j]/g[l]*nbar
                else:
                    down=mp.mpf(e['rates_cm3_s'][TEMPS.index(T)])*den
                    up=down*g[j]/g[l]*mp.exp(-beta*de)
                u.append(mp.log(up/down)-mp.log(g[j]/g[l]))
            uv=mp.matrix(u)
            a=mp.matrix([beta*(E[j+1]-E[j]-H*mp.mpf(edges[j]['nu_GHz'])*mp.mpf('1e9')) for j in range(8)])
            phi=mp.matrix([-beta*ei for ei in E])
            observed=mp.matrix(Z.T.tolist())*uv
            prediction=mp.matrix(M.tolist())*a
            decomposition=uv-mp.matrix(B.T.tolist())*phi-mp.matrix(D.tolist())*a
            closure=max(abs(x-y) for x,y in zip(observed,prediction))
            path=max(abs(x) for x in decomposition)
            max_closure=max(max_closure,closure);max_decomp=max(max_decomp,path)
            old=next(x for x in prior['rows'] if x['T_K']==T and x['pH2_and_oH2_density_each_cm3']==den)
            reuse=max(abs(a[j]+mp.mpf(old['pairs'][j]['A_rad_down_col_up'])) for j in range(8))
            max_reuse=max(max_reuse,reuse)
            zero=max(abs(observed[j]) for j in range(8,len(chords)))
            results.append({'T_K':T,'n_pH2_each_cm3':den,'cycle_affinities':[mp.nstr(x,55) for x in observed],'source_defect_affinity_up_orientation':[mp.nstr(x,55) for x in a],
                 'max_cycle_closure_abs':mp.nstr(closure,10),'max_zero_chord_cycle_abs':mp.nstr(zero,10),
                 'max_gauge_decomposition_abs':mp.nstr(path,10),'max_saved_PR151_affinity_abs':mp.nstr(reuse,10)})
    assert max_closure<mp.mpf('1e-75') and max_decomp<mp.mpf('1e-75') and max_reuse<mp.mpf('1e-55')
    return results,max_closure,max_reuse,max_decomp

def run(src:Path, prior_path:Path):
    raw=src.read_bytes();p=prior_path.read_bytes()
    assert hashlib.sha256(p).hexdigest()==PRIOR151_SHA, 'PR151_RESULT_CHANGED'
    prior=json.loads(p);assert prior['input_SHA256']==SOURCE_SHA and len(prior['rows'])==6
    levels,edges=load(raw)
    graph=graph_matrices(edges);B,Z,D,M,tree,chords=graph
    # EXACT INTEGER structural computations, no rank-inference from floating singular values
    assert B.rank()==8 and Z.rank()==18 and M.rank()==8
    assert B*Z==sp.zeros(9,18)
    assert M[:8,:]==sp.eye(8) and M[8:,:]==sp.zeros(10,8)
    # second independent exact construction: kernel rank and rank-nullity
    nullspace=B.nullspace();assert len(nullspace)==18
    with mp.workdps(100):
        results,max_closure,max_reuse,max_decomp=evaluate(levels,edges,graph,prior)
    return {'schema':'REC_HD_26CHANNEL_CYCLE_SPACE01_RESULT_V1',
        'original_source_SHA256':SOURCE_SHA,'prior_PR151_result_SHA256':PRIOR151_SHA,
        'status':'PASS_SCOPED_INTEGER_GRAPH_AND_SAVED_SOURCE_CROSSCHECK',
        'edges':edges,'states':9,'marked_channels':26,'incidence_rank':8,'cycle_space_dim':18,
        'driven_defect_dimension':8,'zero_cycle_coordinate_dimension':10,
        'tree_edge_indices_zero_based':tree,'chord_edge_indices_zero_based':chords,
        'incidence_matrix_integer':B.tolist(),'fundamental_cycle_matrix_integer':Z.tolist(),
        'defect_injection_matrix_integer':D.tolist(),'defect_to_cycle_map_integer':M.tolist(),
        'original_35Hz_rows':decimal_source_failures(levels,edges),
        'sample_cases':results,'max_cycle_closure_abs':mp.nstr(max_closure,12),
        'max_saved_PR151_affinity_abs':mp.nstr(max_reuse,12),'max_gauge_decomposition_abs':mp.nstr(max_decomp,12),
        'scientific_scope':'graph-space obstruction of source-locked synthetic same-T two-energy model, not physical entropy/energy source, source replacement or global error certificate',
        'historical_CDMS_2011_version2_raw':'NOT_ACQUIRED','CDMS_archive_directory':'INDEX_LOCATED_ONLY',
        'canonical_DAG':'28/88+0','physical':'0/313','H5_epsilon':None,'REI_activation':False}

def main():
    a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--prior',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
    r=run(args.source,args.prior);args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k in ['status','states','marked_channels','incidence_rank','cycle_space_dim','driven_defect_dimension','zero_cycle_coordinate_dimension','max_cycle_closure_abs','max_saved_PR151_affinity_abs','max_gauge_decomposition_abs']},indent=2))
if __name__=='__main__':main()
