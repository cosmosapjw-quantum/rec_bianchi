"""Blind-style adversarial check: source frequency vs term-energy detailed balance.

Not an independent author review; quantify physical exact-equilibrium defect
without modifying source or the original 35 Hz production gate.
"""
from pathlib import Path
import json,math,hashlib
from pr169_neufeld15_reference import parse_lamda,SI_CONVERSION,C,H,K_B
from hd_cmb15 import solve_cmb,TCMB0_K

S='f07f36fd56fe351fe4032235abbc863319b652838e635cd76bbf09664ce099cb'
A='66033b44196bf8a57735b9c541c4f1c8bc8585449050dfd91152e6444d8d73ac'

def run(path:Path,out:Path):
    original=[]
    for kind,file,sha in [('standard','hd_lamda.dat',S),('alternate','hd_lamda_altex.dat',A)]:
        b=(path/file).read_bytes()
        if hashlib.sha256(b).hexdigest()!=sha: raise ValueError('Immutable rate source changed')
        m=parse_lamda(b,verify=(kind=='standard'))
        freqs=[]
        for u,l,rate,nu in m.rad:
            _,eu,_=m.levels[u]
            _,el,_=m.levels[l]
            nu_E=100*C*(eu-el)
            gap=nu-nu_E
            freqs.append({'Jupper':u,'Jlower':l,'nu_source_Hz':nu,'nu_energy_Hz':nu_E,
                          'delta_nu_Hz':gap,'relative_delta':gap/nu})
        cells=[]
        for T in (100.,200.,400.,1000.):
            z=T/TCMB0_K-1
            for density in (1e2,1e4,1e6,1e8):
                x=solve_cmb(m,T,density,z)
                cells.append({'Tgas_K':T,'nH2_cm3':density,'z_exact_equal':z,
                    'residual_net_W_per_HD':x['net_cooling_W_per_HD'],
                    'ratio_to_spontaneous':x['net_cooling_W_per_HD']/x['spont_power_W_per_HD'],
                    'master_residual_s_inverse':x['max_stationary_residual_s_inverse']})
        original.append({'source_kind':kind,'frequency_line_differences':freqs,'equal_bath_cases':cells,
                         'max_absolute_relative_equilibrium_defect':max(abs(y['ratio_to_spontaneous']) for y in cells),
                         'max_absolute_source_frequency_mismatch_Hz':max(abs(x['delta_nu_Hz']) for x in freqs)})
    output={'schema':'HD15_SOURCE_FREQUENCY_VERSUS_TERM_ENERGY_AUDIT','sources':original,
      'scientific_interpretation':'Source-rounded frequencies and rotational term energies do not impose an exactly common Boltzmann equilibrium; do not assert mathematical net-zero at Tgas=Tcmb for these unaltered source values',
      'not_a_35_Hz_owner_source_gate':'Separate Neufeld2026 source, no relaxation of frozen CDMS2011 35 Hz FAIL7/8',
      'canonical_DAG':'28/88','REC_physical_DAG':'0/313','production':'HOLD'}
    out.parent.mkdir(exist_ok=True,parents=True)
    out.write_text(json.dumps(output,indent=2)+'\n',encoding='utf8')
    return output

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 a=p.parse_args()
 o=run(a.source,a.output)
 print(json.dumps({x['source_kind']:{'max_Hz':x['max_absolute_source_frequency_mismatch_Hz'],'max_equilibrium_defect':x['max_absolute_relative_equilibrium_defect']} for x in o['sources']},indent=2))
