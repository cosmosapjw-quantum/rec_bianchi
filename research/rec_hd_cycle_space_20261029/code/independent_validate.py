#!/usr/bin/env python3
"""Independent graph construction with a DIFFERENT spanning tree + Decimal.
Does not import cycle_space, calculate stationary population, or read external CDMS raw.
"""
import argparse,json,hashlib
from pathlib import Path
from decimal import Decimal,localcontext
import sympy as sp
import networkx as nx
S='0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb'
C=Decimal('299792458');H=Decimal('6.62607015e-34');K=Decimal('1.380649e-23')

def validate(src,result):
    data=src.read_bytes();assert len(data)==2289 and hashlib.sha256(data).hexdigest()==S
    r=json.loads(result.read_text());e=r['edges'];assert len(e)==26
    text=data.decode('ascii').splitlines()
    levp=text.index('!LEVEL + ENERGIES(cm^-1) + WEIGHT + J (or other quantum numbers)')
    levels=[text[levp+1+j].split() for j in range(9)]
    lp=text.index('!TRANS + U + L + A(s^-1) + FREQ(GHz) + E_u/k(K)')
    freqs=[Decimal(text[lp+1+j].split()[4]) for j in range(8)]
    # Generate independent multigraph from raw table, no dependency on primary edge list for counts.
    G=nx.MultiGraph();G.add_nodes_from(range(9))
    G.add_edges_from([(i,i+1) for i in range(8)])
    for block in ('2 HD-pH2','3 HD-oH2'):
        k=next(i for i,line in enumerate(text) if line.startswith(block))
        t=text.index('!TRANS + UP + LOW + RATES [cm3 s-1]',k)
        for j in range(9):
            row=text[t+1+j].split();G.add_edge(int(row[2])-1,int(row[1])-1)
    assert G.number_of_nodes()==9 and G.number_of_edges()==26 and nx.is_connected(G)
    cycle_rank=G.number_of_edges()-G.number_of_nodes()+1
    assert cycle_rank==18
    # Use photon edges (indices 0..7) as spanning tree, unlike the primary p-H2 tree.
    B=sp.zeros(9,26);edge_pairs=[]
    for idx,edge in enumerate(e):
        lower,upper=edge['lower'],edge['upper'];edge_pairs.append((lower,upper))
        B[lower,idx]=-1;B[upper,idx]=1
    Z=sp.zeros(26,18)
    for col,chord in enumerate(range(8,26)):
        l,u=edge_pairs[chord];Z[chord,col]=1
        for photon_index in range(l,u):Z[photon_index,col]-=1
    D=sp.zeros(26,8)
    for j in range(8):D[j,j]=1
    M=Z.T*D
    assert B*Z==sp.zeros(9,18) and Z.rank()==18 and M.rank()==8
    # Compare the two independently generated integral cycle bases' subspaces.
    C1=sp.Matrix(r['fundamental_cycle_matrix_integer'])
    assert sp.Matrix.hstack(C1,Z).rank()==18
    with localcontext() as c:
        c.prec=100;maxdiff=Decimal(0)
        for point in r['sample_cases']:
            T=Decimal(point['T_K'])
            f=[]
            for j in range(8):
                gap=Decimal(levels[j+1][1])-Decimal(levels[j][1])
                a=H*(C*Decimal(100)*gap-Decimal('1e9')*freqs[j])/(K*T)
                f.append(a)
                old=Decimal(point['source_defect_affinity_up_orientation'][j]);maxdiff=max(maxdiff,abs(a-old))
            predicted=[sum(int(M[i,j])*f[j] for j in range(8)) for i in range(18)]
            # nonzero magnitudes determined by the three source node temperatures
            assert sum(x!=0 for x in predicted)==18, (point['T_K'],[str(x) for x in predicted])
    assert maxdiff<Decimal('1e-48'),maxdiff
    return {'status':'PASS_ALTERNATE_TREE_AND_DECIMAL','graph_N':9,'graph_E':26,'cycle_rank':18,
            'alternative_photon_tree_cycle_basis_rank':Z.rank(),'defect_map_rank':M.rank(),
            'combined_basis_rank':18,'max_Decimal100_vs_saved_source_affinity':str(maxdiff),
            'independence_scope':'Independent graph algorithm/basis and numerical precision; same physical source model, no nonauthor scientific review'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--result',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    x=validate(args.source,args.result);args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(x,indent=2,default=int)+'\n');print(json.dumps(x,indent=2,default=int))
