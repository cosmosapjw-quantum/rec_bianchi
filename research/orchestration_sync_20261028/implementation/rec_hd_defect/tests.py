"""New exact source-defect ledger; does not import/replay the old HD adapter."""
import pathlib,json,hashlib,argparse
from fractions import Fraction as F

ROOT=pathlib.Path(__file__).resolve().parent
SOURCE=ROOT.parents[1]/'authority/thermal/lamda_hd_20261025.dat'
PIN='0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb'
C=F(29979245800);h=F('6.62607015e-34');kb=F('1.380649e-23');a=F('0.5e-9');f=F(5)

def propagate(defects,c,radius,freq_tol):
    lo,hi=-radius,radius;trace=[{'level':0,'interval':[str(lo),str(hi)]}];empty=False
    for j,d in enumerate(defects,1):
        if not empty:
            lo=max(-radius,lo+(d-freq_tol)/c);hi=min(radius,hi+(d+freq_tol)/c)
            empty=lo>hi
        trace.append({'level':j,'interval':None if empty else [str(lo),str(hi)],'empty':empty})
    return trace

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();raw=SOURCE.read_bytes();assert len(raw)==2289 and hashlib.sha256(raw).hexdigest()==PIN
    lines=raw.decode().splitlines();li=next(i for i,x in enumerate(lines) if x.startswith('!LEVEL +'));ri=next(i for i,x in enumerate(lines) if x.startswith('!TRANS + U + L'))
    levels=[F(lines[li+1+j].split()[1]) for j in range(9)];radiative=[lines[ri+1+j].split() for j in range(8)];nu=[F(x[4])*10**9 for x in radiative]
    assert [int(x[0]) for x in radiative]==list(range(1,9));assert [(int(x[1]),int(x[2])) for x in radiative]==[(j+2,j+1) for j in range(8)]
    ds=[nu[j]-C*(levels[j+1]-levels[j]) for j in range(8)];deltas=[h*d for d in ds];baseline=json.loads((ROOT/'BASELINE_GAPS.json').read_text());assert [abs(d) for d in ds]==[F(z['absolute_gap_Hz']) for z in baseline['frequency_gap_Hz']]
    S=[[F(0)]*8 for _ in range(9)]
    for j in range(8):S[j][j]=F(1);S[j+1][j]=F(-1)
    assert all(sum(S[i][j] for i in range(9))==0 for j in range(8))
    fluxes=[[F(int(i==j)) for i in range(8)] for j in range(8)]+[[F(v) for v in [1,-2,3,-4,5,-6,7,-8]]];checks=[]
    for R in fluxes:
        pop=[sum(S[i][j]*R[j] for j in range(8)) for i in range(9)];matrix=h*C*sum(levels[i]*pop[i] for i in range(9))+h*sum(nu[j]*R[j] for j in range(8));direct=sum(deltas[j]*R[j] for j in range(8));assert matrix==direct
        reverse=h*C*sum(levels[i]*(-pop[i]) for i in range(9))-h*sum(nu[j]*R[j] for j in range(8));assert reverse==-direct
        checks.append({'R':list(map(str,R)),'matrix_residual_J_m-3_s-1':str(matrix),'direct_defect_flux':str(direct),'sign_reverse':str(reverse),'exact_equal':True})
    ladder=[levels[0]]
    for v in nu:ladder.append(ladder[-1]+v/C)
    shifts=[ladder[j]-levels[j] for j in range(9)]
    assert all(ladder[j+1]-ladder[j]==nu[j]/C for j in range(8));assert all(shifts[j]==sum(ds[:j])/C for j in range(9))
    trace=propagate(ds,C,a,f);zero=propagate([F(0)]*8,C,a,f);assert not any(x.get('empty',False) for x in zero)
    artificial=propagate([F(2),F(2)],F(1),F(1),F(0));assert artificial[1]['interval']==['1','1'] and artificial[2]['empty'];assert all(not propagate([F(2)],F(1),F(1),F(0))[-1]['empty'] for _ in range(2))
    reversed_trace=propagate([-d for d in ds],C,a,f)
    for x,y in zip(trace,reversed_trace):
        assert (x['interval'] is None)==(y['interval'] is None)
        if x['interval'] is not None:assert list(map(F,y['interval']))==[-F(x['interval'][1]),-F(x['interval'][0])]
    # Boundary-equality interval intersections are retained, as in the first artificial edge.
    edge=[]
    for j,d in enumerate(ds):
        radius=max(F(0),(abs(d)-f)/(2*C));edge.append({'line_id':j+1,'frequency_Hz':str(nu[j]),'level_defined_frequency_Hz':str(C*(levels[j+1]-levels[j])),'signed_defect_Hz':str(d),'signed_energy_defect_J_event-1':str(h*d),'signed_energy_defect_K_event-1':str(h*d/kb),'minimum_uniform_level_radius_cm-1':str(radius),'exceeds_original_radius':radius>a,'linewise_printed_precision_necessary_bound_Hz':str(2*C*a+f),'linewise_necessary_condition':abs(d)<=2*C*a+f})
    baseline_result=json.loads((ROOT/'BASELINE_RESULT.json').read_text());assert baseline_result['original_35Hz_frequency_gate']=='FAIL_7_OF_8'
    output={'unit':'REC-HD-ENERGY-DEFECT01','source_sha256':PIN,'literal_rows':[{'source_line_1based':li+2+j,'literal':lines[li+1+j]} for j in range(9)]+[{'source_line_1based':ri+2+j,'literal':lines[ri+1+j]} for j in range(8)],'constants':{'C_cm_s-1':str(C),'h_J_s':str(h),'kB_J_K-1':str(kb),'level_rounding_radius_cm-1':str(a),'frequency_rounding_radius_Hz':str(f)},'edges':edge,'frequency_defined_ladder_cm-1':list(map(str,ladder)),'level_shifts_cm-1':list(map(str,shifts)),'chain_trace':trace,'first_empty_level':next((x['level'] for x in trace if x.get('empty')),None),'basis_and_mixed_flux_controls':checks,'zero_mismatch_trace':zero,'manufactured_joint_failure_trace':artificial,'sign_reversed_trace':reversed_trace,'counts':{'source_edges':8,'source_levels':9,'baseline_gap_equalities':8,'basis_flux_checks':8,'mixed_flux_checks':1,'roundtrip_equalities':8,'telescoping_equalities':9,'column_conservation_checks':8,'sign_reversed_flux_checks':9,'chain_symmetry_levels':len(trace),'manufactured_chains':2},'exact_checks_pass':True,'old_35Hz_status':'UNCHANGED_FAIL_7_OF_8','physical_bridge':'HOLD_SOURCE_DISCREPANCY_UNQUALIFIED','thermal_heating':None,'independent_energy_compensation':None,'source_ladder_alternative':'DIAGNOSTIC_ONLY_NOT_ADOPTED','original_HD_cumulative_cpu_seconds':baseline_result['known_sampled_process_tree_CPU_seconds'],'claim':'source-column signed energy defect interface only'}
    pathlib.Path(args.output).write_text(json.dumps(output,indent=2)+'\n')
if __name__=='__main__':main()
