"""Create explicit source-scoped witness graph from pinned PR157 guard.

Actual owner and native pathways are recorded as REMOTE_STATIC_INSPECTED / NO_RUN.
If --owner points at a complete owner checkout, verify its Git blob and derive
its direct line-coefficient path with AST. Never use this output to activate HD.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from guard_graph import (read_pinned_py, body_for, calls, stage_guard_evidence,
                        reachable_without_cuts, git_blob_id, SourceMismatch)

ROOT=Path(__file__).resolve().parents[1]
FIREWALL_PIN='e170417a8a205e17d45ae50e5c0f14641d020387'
OWNER_PIN='632a8a094e7eedd24a1ec3132fec20765d6e39da'
BASE_PR158='ee78d209281c28ad7b8a9fe04a1634da80b7ad54'


def analyse(firewall:Path,owner:Path|None=None):
    fm=read_pinned_py(firewall,FIREWALL_PIN)
    result={
      'schema':'REC_HD_SCOPED_GUARD_GRAPH_EVIDENCE_V1',
      'parent_repo':'cosmosapjw-quantum/rec_bianchi',
      'parent_pr':158,
      'parent_head':BASE_PR158,
      'source_lamda_sha256':'0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb',
      'source_lamda_bytes':2289,
      'cdms_2011_v2_raw':'NOT_ACQUIRED',
      'firewall_blob':FIREWALL_PIN,
      'owner_blob':OWNER_PIN,
      'actual_firewall_AST':stage_guard_evidence(fm),
      'graph_model':'HAND_INSPECTED_REPO_CODE_LINES_PLUS_PINNED_FIREWALL_AST; FINITE_TYPED_EVENT_GRAPH',
      'unknown_dynamic_ffi_edges':'OPEN',
      'exact_35hz_gate':'FAIL_7_OF_8',
      'physical':'HOLD',
      'production':'HOLD',
      'canonical_DAG':'28/88 (+0)',
      'REC_physical_DAG':'0/313 (+0)',
    }
    # The event graph models the *sequential* effect of a guard call finishing
    # successfully BEFORE the consuming call. Ordinary function-call graphs
    # are not CFGs and would omit this program-order relation.
    graph={
      'research_direct_entry':('owner.line_coefficients',),
      'research_thermal_entry':('owner.thermal_line',),
      'owner.line_coefficients':('owner.einstein_B',),
      'owner.thermal_line':('owner.einstein_B',),
      'owner.einstein_B':('printed_nu_P_coefficient',),
      'firewall_optin_entry':('firewall.source_identity_pass',),
      'firewall.source_identity_pass':('firewall.owner_35Hz_gate_pass',),
      'firewall.owner_35Hz_gate_pass':('owner.line_coefficients',),
      'printed_nu_P_coefficient':(),
    }
    cut={'firewall.source_identity_pass','firewall.owner_35Hz_gate_pass'}
    endpoint={'printed_nu_P_coefficient'}
    gated=reachable_without_cuts(graph,{'firewall_optin_entry'},endpoint,cut)
    direct=reachable_without_cuts(graph,{'research_direct_entry'},endpoint,cut)
    thermal=reachable_without_cuts(graph,{'research_thermal_entry'},endpoint,cut)
    assert not gated and direct and thermal
    result['event_graph']={'adjacency':graph,'cuts':sorted(cut),'consumer':sorted(endpoint),
       'optin_bypass_paths':gated,'direct_research_bypass_paths':direct,
       'thermal_research_bypass_paths':thermal,
       'universal_runtime_coverage_claim':False}
    if owner is None:
        result['local_owner_AST']='NOT_RUN_OWNER_FILE_NOT_IN_CONTAINER'
    else:
        om=read_pinned_py(owner,OWNER_PIN)
        direct_c=calls(body_for(om,'line_coefficients'))
        thermal_c=calls(body_for(om,'thermal_line'))
        result['local_owner_AST']={
           'verified_blob':git_blob_id(owner.read_bytes()),
           'line_coefficients_calls_einstein_B':'einstein_B' in direct_c,
           'line_coefficients_calls_owner_gate':'require_energy_frequency_bridge' in direct_c,
           'thermal_line_calls_einstein_B':'einstein_B' in thermal_c,
           'thermal_line_calls_owner_gate':'require_energy_frequency_bridge' in thermal_c}
    return result


def plot(result:dict,out:Path):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import networkx as nx
    except ImportError:
        return 'MATPLOTLIB_OR_NETWORKX_MISSING'
    g=nx.DiGraph(result['event_graph']['adjacency'])
    pos={
     'research_direct_entry':(-2,2),
     'research_thermal_entry':(-2,0),
     'firewall_optin_entry':(-2,-2),
     'firewall.source_identity_pass':(-.65,-2),
     'firewall.owner_35Hz_gate_pass':(.75,-2),
     'owner.line_coefficients':(1.9,1.2),
     'owner.thermal_line':(-.65,0),
     'owner.einstein_B':(3.0,.9),
     'printed_nu_P_coefficient':(4.4,.9),
    }
    fig,ax=plt.subplots(figsize=(11.5,4.6))
    colors=['#d3e6ff' if 'firewall.' in n else ('#f2dfd5' if 'research_' in n else '#e6e6e6') for n in g.nodes]
    nx.draw_networkx_nodes(g,pos,ax=ax,node_color=colors,node_size=1800,edgecolors='#555555',linewidths=.5)
    nx.draw_networkx_edges(g,pos,ax=ax,arrows=True,arrowsize=12,node_size=1800,width=1.5,edge_color='#555555')
    labels={n:n.replace('research_','research\n').replace('firewall.','guard:\n').replace('owner.','owner:\n').replace('_','\n') for n in g.nodes}
    nx.draw_networkx_labels(g,pos,labels,ax=ax,font_size=7)
    ax.set_xlim(-3.35,5.45);ax.set_ylim(-2.9,2.75)
    ax.set_title('Source-scoped HD event graph: opt-in guard vs direct research call',fontsize=11)
    ax.annotate('Not an exhaustive REC/BASS/REI native call graph',(-2.9,-2.75),fontsize=8)
    ax.axis('off');fig.tight_layout();fig.savefig(out,dpi=160);plt.close(fig)
    return 'GENERATED_SYNTHETIC_TOPOLOGY_NOT_NATIVE_TRACE'

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--firewall',type=Path,required=True)
    ap.add_argument('--owner',type=Path)
    ap.add_argument('--out',type=Path,default=ROOT/'evidence'/'CALLGRAPH_RESULT.json')
    ap.add_argument('--plot',type=Path,default=ROOT/'evidence'/'GUARD_TOPOLOGY.png')
    a=ap.parse_args();r=analyse(a.firewall,a.owner);r['plot_status']=plot(r,a.plot)
    a.out.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'optin_unguarded':len(r['event_graph']['optin_bypass_paths']),
                      'research_unguarded':len(r['event_graph']['direct_research_bypass_paths'])+
                      len(r['event_graph']['thermal_research_bypass_paths']),
                      'owner_ast':r['local_owner_AST'],'plot':r['plot_status']}))
