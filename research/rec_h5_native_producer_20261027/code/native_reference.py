"""Actual 313 native Wien reference producer; no ODE or native solver replay."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from decimal import Decimal, localcontext
from fractions import Fraction

from interval80 import I, derivatives, envelopes
from point_reference140 import evaluate as independent_point

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
LOCKS = {
    'context': ('research/program_expansion_20261025/h5_input_binding/inputs/SOURCE_CONTEXT.json', '5ccd8955bc9ea7484ddc1fca1dcf8b5a0a789e07c36ce0af3e692b959f002fe8'),
    'native_csv': ('research/rec_history_geometry_response_20261026/inputs/target_native_snapshot.csv', '3a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7'),
    'history': ('research/rec_history_geometry_response_20261026/inputs/history.npz', 'd4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1'),
    'hydrogen_h': ('research/rec_history_thermo_20261024/vendor/hydrogen.h', 'e89a3a447928cbe31dc273c11c4a8bc7f7a8e297be4a11270e453c101f96ccba'),
    'native_py': ('research/rec_history_thermo_20261024/vendor/original_hyrec_native.py', 'd7bc38346281951fdd5f2677e25f3b558333124a2319786b9b7afb0ab1f7a89c'),
}

def require(condition, message):
    if not condition: raise AssertionError(message)

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def fraction64(x):
    x = float.fromhex(x) if isinstance(x, str) and '0x' in x else float(x)
    if not math.isfinite(x) or (x != 0 and abs(x) < sys.float_info.min):
        raise ValueError('nonfinite or subnormal binary64 input')
    return Fraction.from_float(x)

def write_json(path, obj):
    with path.open('x') as f: json.dump(obj, f, indent=2, sort_keys=True); f.write('\n')

def read_sources():
    identities = {}
    for key, (name, expected) in LOCKS.items():
        p = REPO/name
        got = sha(p)
        require(got == expected, f'BYTE_IDENTITY_MISMATCH immutable {key}: {got}')
        identities[key] = {'path': name, 'sha256': got, 'bytes': p.stat().st_size}
    ctx = json.loads((REPO/LOCKS['context'][0]).read_text())
    meta, energy_tokens = {}, {}
    with (REPO/LOCKS['native_csv'][0]).open(newline='') as f:
        for record in csv.reader(f):
            if not record: continue
            if record[0] == 'META': meta[record[1]] = record[2]
            elif record[0] == 'VIRTUAL':
                index = int(record[1])
                require(index not in energy_tokens, 'duplicate virtual energy')
                energy_tokens[index] = record[2]
    require(sorted(energy_tokens) == list(range(311)), 'virtual energies 0..310')
    header = (REPO/LOCKS['hydrogen_h'][0]).read_text()
    constants = {}
    for key in ('E21', 'E31', 'E41', 'kBoltz'):
        constants[key] = re.search(r'^#define\s+'+key+r'\s+([\d.eE+\-]+)', header, re.M).group(1)
    require(float(constants['kBoltz']).hex() == float(8.617343e-5).hex(), 'native kN')
    energies = {i: float(v) for i,v in energy_tokens.items()}
    energies.update({311: float(constants['E21']), 312: float(constants['E31']), 313: float(constants['E41'])})
    identity = ctx['source_identity']
    require(identity['query_count'] == 313 and len(ctx['queries']) == 313, '313 actual rows')
    require(identity['prefix'] == 5127 and identity['fsR'] == identity['meR'] == 1, 'native prefix/fsR/meR')
    require(float(meta['z']).hex() == identity['z_hex'], 'z exact source match')
    require(float(meta['TR_eV_rescaled']).hex() == float(0.25882399309326415).hex(), 'TR exact source match')
    require(float(meta['iz_local']) == identity['prefix'], 'prefix CSV match')
    special = {139:311, 270:312, 310:313, 311:140, 312:271}
    bindings = []
    for i, row in enumerate(ctx['queries']):
        require(row['incoming_index'] == i, 'ordered unique incoming index')
        require(row['source_index'] == special.get(i, i+1), f'source route {i}')
        a,b,q = (fraction64(row[k]) for k in ('eta_left_hex','eta_right_hex','query_hex'))
        require(a < q < b, 'strict stored geometric cell query containment')
        require(0 <= row['cell'] < identity['prefix']-1, 'causal cell prefix')
        alpha = (q-a)/(b-a)
        require(alpha == Fraction(row['geometric_alpha_exact']), 'exact geometric alpha')
        coefficient = (q-a)*(b-q)/2
        require(coefficient == Fraction(row['pointwise_curvature_coefficient_exact']), 'exact chord coefficient')
        yL,yR,u = (fraction64(row[k]) for k in ('sample_left_hex','sample_right_hex','nominal_incoming_hex'))
        anchor = u-((1-alpha)*yL+alpha*yR)
        require(abs(anchor) == Fraction(row['anchor_representation_radius_exact']), 'preserved old exact anchor')
        raw = {'a': row['eta_left_hex'], 'b': row['eta_right_hex'], 'q':row['query_hex'],
               'Es':energies[row['source_index']], 'Et':energies[i], 'kN':float(constants['kBoltz']),
               'T0':identity['T0_K_hex'], 'z':identity['z_hex'], 'TR':float(meta['TR_eV_rescaled']),
               'yL':row['sample_left_hex'], 'yR':row['sample_right_hex'], 'u':row['nominal_incoming_hex']}
        binding = dict(row, prefix=identity['prefix'], source_energy_hex=raw['Es'].hex(),
                       target_energy_hex=raw['Et'].hex(), kN_hex=raw['kN'].hex(),
                       T0_K_hex=identity['T0_K_hex'], z_hex=identity['z_hex'],
                       TRhat_hex=raw['TR'].hex(), signed_anchor_exact=str(anchor))
        bindings.append((binding, raw))
    return identities, constants, bindings

def produce(raw, binding=None):
    def get(k): return I.exact(fraction64(raw[k]))
    a,b,q = (get(k) for k in ('a','b','q'))
    Es,Et,k,T0,z,TR = (get(k) for k in ('Es','Et','kN','T0','z','TR'))
    require(min(Es.lo,Et.lo,k.lo,T0.lo,TR.lo,(1+z).lo)>0, 'positive reference domain')
    require(a.hi <= q.lo and q.hi <= b.lo and a.hi < b.lo, 'ordered geometric reference domain')
    af,bf,qf = (fraction64(raw[k]) for k in ('a','b','q'))
    alpha = I.exact((qf-af)/(bf-af))
    coefficient = I.exact((qf-af)*(bf-qf)/2)
    x = [Es*t.exp()/(k*T0) for t in (a,b,q)]
    d = [derivatives(v) for v in x]
    m1,m2,critical,monotone = envelopes(x[0],x[1])
    qstar = -((1+z)*Es/Et).ln()
    delta = q-qstar
    xt = Et/(k*T0*(1+z))
    wideal, wnative = (-xt).exp(), (-(Et/TR)).exp()
    bchar = wideal*(-xt*delta.expm1()).expm1()
    btr = wideal-wnative
    btotal = bchar+btr
    btotal_direct = d[2][0]-wnative
    j = (1-alpha)*d[0][0]+alpha*d[1][0]-d[2][0]
    yL,yR,u = (get(k) for k in ('yL','yR','u'))
    # Anchor computed exactly in Fraction before directed conversion.
    yLf,yRf,uf = (fraction64(raw[k]) for k in ('yL','yR','u'))
    alphaf = (qf-af)/(bf-af)
    anchorf = uf-((1-alphaf)*yLf+alphaf*yRf)
    anchor = I.exact(anchorf)
    old = I.exact(abs(anchorf))
    if binding is not None:
        require(abs(anchorf) == Fraction(binding['anchor_representation_radius_exact']), 'old anchor retained')
    direct = (u+wnative)-((1-alpha)*(yL+d[0][0])+alpha*(yR+d[1][0]))
    decomposition = anchor-j-btotal
    # Upper operands are represented Decimal numbers interpreted exactly.
    rbridge = old+I(abs(j).hi)+I(abs(btotal).hi)
    chordbound = m2*coefficient
    curvature_radius = old+I(chordbound.hi)+I(abs(btotal).hi)
    lower = I(min(yL.lo,yR.lo),min(yL.hi,yR.hi))+d[1][0]
    values = dict(x_left=x[0],x_right=x[1],x_query=x[2],
                  w_left=d[0][0],w_right=d[1][0],w_query=d[2][0],
                  w_prime_query=d[2][1],w_second_query=d[2][2],w_third_query=d[2][3],
                  G_f=I(1),G_ff=I(0),G_eta_f=I(0),
                  G_eta=-d[2][1],G_etaeta=-d[2][2],scalar_occupation_K=I(1),
                  M1_ref=m1,M2_ref=m2,qstar=qstar,delta_q=delta,
                  w_ideal=wideal,w_native=wnative,B_char=bchar,B_TR=btr,B_total=btotal,
                  B_total_direct=btotal_direct,B_total_identity_residual=btotal-btotal_direct,
                  J_ref=j,chord_coefficient=coefficient,chord_bound=chordbound,
                  r_anchor=anchor,direct_bridge=direct,decomposed_bridge=decomposition,
                  bridge_identity_residual=direct-decomposition,R_bridge=rbridge,
                  R_bridge_curvature=curvature_radius,old_anchor_radius=old,
                  represented_occupation_lower_bound=lower)
    require(values['bridge_identity_residual'].contains(Decimal(0)), 'signed direct/decomposed identity')
    require(values['B_total_identity_residual'].contains(Decimal(0)), 'split/direct total reference bridge')
    return values, {'critical_points_included':critical, 'left_endpoint_monotone_proved':monotone,
                    'x_greater_than_one_proved':x[0].lo > 1,
                    'represented_reconstruction_positive_proved':lower.lo > 0}

def primary(output):
    identities, constants, bindings = read_sources()
    write_json(output/'SOURCE_BINDINGS.json',{'source_identities':identities,'constants_literal_tokens':constants,
        'binary64_interpretation':'exact rational from represented float; occupation dimensionless',
        'bindings':[binding for binding,_ in bindings]})
    rows, references, max_width, worst, failures = [], [], Decimal(0), None, []
    containment_count = 0
    with localcontext() as c:
        c.prec=160
        for binding,raw in bindings:
            values,flags=produce(raw,binding)
            point=independent_point(raw)
            for key,ref in point.items():
                require(values[key].contains(ref), f'140-digit containment {binding["incoming_index"]}/{key}')
                containment_count += 1
            for key,v in values.items():
                exact_zero = point.get(key) == 0 or key in ('bridge_identity_residual','B_total_identity_residual')
                if not exact_zero and not (v.lo == v.hi == 0):
                    mid=(v.lo+v.hi)/2
                    width=(v.hi-v.lo)/(Decimal('1e-100')+abs(mid))
                    if width > max_width: max_width,worst=width,[binding['incoming_index'],key]
                    if width > Decimal('1e-40'): failures.append([binding['incoming_index'],key,str(width)])
            require(abs(point['J_ref']) <= values['chord_bound'].hi, 'independent chord inequality')
            require(abs(values['J_ref']).hi <= values['chord_bound'].hi, 'outward endpoint chord inequality')
            require(abs(point['direct_bridge']) <= values['R_bridge'].hi, 'independent representation bound')
            if flags['x_greater_than_one_proved']:
                require(values['J_ref'].lo >= 0, 'whole cell convex chord sign')
            # Both interval forms must contain the independent direct point value.
            require(values['decomposed_bridge'].contains(point['direct_bridge']), 'direct point/decomposition containment')
            require(values['direct_bridge'].contains(point['decomposed_bridge']), 'decomposed point/direct containment')
            rows.append({'binding':binding, 'reference_bounds':{k:v.packed() for k,v in values.items()}, 'flags':flags})
            references.append({'incoming_index':binding['incoming_index'], 'point_reference140':{k:str(v) for k,v in point.items()}})
    packet={'schema':'REC_H5_NATIVE_REFERENCE_PARTIAL_V1', 'unit_id':'REC-H5-NATIVE-REFERENCE01',
            'precision':80, 'independent_point_precision':140, 'source_identities':identities,
            'conversion_rule':'native literal/CSV decimal reconstructs binary64; all source binary64 values become exact Fraction before interval conversion',
            'reference_model':'native Wien exp(-E*exp(eta)/(kN*T0)); no occupation degeneracy',
            'units':{'eta':'dimensionless ln(a)','photon_occupation':'dimensionless','energy':'eV'},
            'scalar_norm':'abs(delta_f); scalar_occupation_K=1 is not full_state_K',
            'reference_bounds':rows, 'reference_coverage':{'computed':313,'total':313},
            'physical_coverage':{'computed':0,'total':313},
            **{k:None for k in ('physical_query_bounds','full_state_K','physical_M2','physical_defect',
                               'stability_L','positive_uniform_ode_tube','initial_error','physical_epsilon','physical_outgoing_bound')},
            'H6':'OPEN','H7':'OPEN','L4':False,'REI_activation':False}
    write_json(output/'REFERENCE_PACKET.json',packet)
    with (output/'POINT_REFERENCE140.jsonl').open('x') as f:
        for row in references: f.write(json.dumps(row,sort_keys=True)+'\n')
    summary={'status':'PASS' if not failures else 'ACCURACY_TARGET_HOLD', 'actual_rows':313,
             'independent_containment_count':containment_count,'all_source_bindings_pass':True,
             'direct_decomposed_identity_rows':313, 'physical_coverage':'0/313',
             'max_relative_interval_width':str(max_width), 'worst_width_field':worst,
             'width_target':'1e-40', 'width_target_failures':failures,
             'left_monotone_rows':sum(r['flags']['left_endpoint_monotone_proved'] for r in rows),
             'convex_rows':sum(r['flags']['x_greater_than_one_proved'] for r in rows),
             'representation_positive_rows':sum(r['flags']['represented_reconstruction_positive_proved'] for r in rows),
             'physical_epsilon':None,'physical_outgoing_bound':None}
    write_json(output/'SUMMARY.json',summary)
    # Plotting consumes completed raw intervals; it performs no solver work.
    from plot_results import plot_packet
    plot_packet(packet, output)
    require(not failures, 'useful-width target: diagnosis required, no automatic precision increase')
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mode',choices=['primary','controls'],required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    require(sys.version_info[:2] == (3,12), 'frozen Python3.12 runtime')
    if args.mode == 'primary': summary=primary(args.output)
    else:
        from controls import run_controls
        summary=run_controls(args.output)
    print(json.dumps(summary,sort_keys=True))

if __name__ == '__main__': main()
