#!/usr/bin/env python3
"""Create pinned file-level source audit, not an exhaustive absence claim."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ref={'REC':'861b7f8b3e52d580437a1b4ad448d9669b0d2706',
     'BASS':'9c6506e4e2087129a8b674ff10438e5db1a55c9d',
     'REI':'ae3402713c4b6530ab2b27f008f5f5d5c6a999ed'}
entries=[
('REC','research/rec_hd_multichannel_affinity_20261029/code/multichannel.py','029255494bf0a63b93bf8b2715327a8585afb5f3','generate','55-75','MIXED_PRINTED_PHOTON_LEVEL_ENERGY','nu=e[nu_GHz]*1e9 by default; dE from w; source_consistent flag recomputes nu from dE; collision detailed balance uses dE','DIRECT_IMPORTED_AND_METAMORPHIC_TESTED'),
('REC','research/rec_hd_field_semantics_20261029/field_semantics.py','21517960f912efbd2dc9df8b94fd577e03ca2e27','frequency_comparison','101-150','DUAL_POLICY_DIAGNOSTIC','Explicit exact nu_E vs nu_P ratios; core projection excludes optional metadata; not production','DIRECT_IMPORTED_AND_REUSED'),
('REC','src/full_bianchi_hyrec/trajectory/hyrec_source_adapter.py','00b9eceec888839a0d1cd7644e569a397d4f7279','one_photon_paired_action / one_photon_planck_null_residual','123-166','GENERIC_HYDROGEN_FREQUENCY_PARAMETER','One-photon action takes occupation and A; null helper constructs both Boltzmann upper population and Planck occupation from same frequency_Hz, so cannot test independent HD level gap','STATIC_SOURCE_INSPECTED_NO_HD_INPUT'),
('REC','src/full_bianchi_hyrec/recoil/frequency_liouville.py','95ad73d8095e5b5c19667661e1680a48bd6a5765','ConservativeFrequencyLiouville.from_network','93-145','LOCKED_HYDROGEN_LINE_FREQUENCY_GRID','Frequency faces = line.nu_abs_Hz + faces*line.Doppler_width_Hz; changing grid requires recompile/remap; no HD LAMDA loader demonstrated','STATIC_SOURCE_INSPECTED_NO_HD_INPUT'),
('REC','src/full_bianchi_hyrec/recoil/nonlinear_bose_runtime.py','67c39313fdaf29100296ba1381293f2478107e09','LineBoundaryConfig','145-159','EXPLICIT_LINE_FREQUENCY_INPUT','nu_abs_Hz and Doppler_width_Hz must be positive; source is original hydrogen Ly-alpha interface, not HD v2 catalog','STATIC_SOURCE_INSPECTED_NO_HD_INPUT'),
('BASS','bianchi/thermo/recombination.py','de989015b29965e203c10bf258f12cf05195e530','saha_xe / peebles_xe','37-105','H_ATOMIC_NOT_HD','Hydrogen atomic ionization E_ion, 2s-1s two-photon and Ly-alpha; no HD LAMDA frequency input in inspected functions','STATIC_SOURCE_INSPECTED_NO_HD_INPUT'),
('BASS','bianchi/matter/collision_ladder.py','a4e1a1109057c474fb203d1db83b49108139e4d2','physical_frame / thomson_operator / collide','42-118','THOMSON_BGK_NOT_HD','Massless angular Boltzmann Thomson/BGK kernel; no molecular HD LAMDA input in inspected functions','STATIC_SOURCE_INSPECTED_NO_HD_INPUT'),
('REI','src/rei_bianchi/multigroup_hhe_transmission.py','5b74a4036c8cb21a2cb772dd3d373c5f96d5a36c','GROUPS / SPECIES / transmission','1-78','H_HE_CONTINUUM_NOT_HD','HI/HeI/HeII continuum photoionization groups 13.60–100 eV; not neutral HD rotational lines','STATIC_SOURCE_INSPECTED_NO_HD_INPUT'),
('REI','src/rei_bianchi/absorption_decomposition.py','5f797469eaa67847fa3c5f3701a5b8416a55d98e','atomic_kappa_arrays','307-340','H_HE_CONTINUUM_NOT_HD','Continuum absorption components evaluated on energy_eV grids; no HD rotational line ingestion evidenced','STATIC_SOURCE_INSPECTED_NO_HD_INPUT'),
]
rows=[]
for owner,path,sha,fun,lines,cl,why,evidence in entries:
    repo={'REC':'rec_bianchi','BASS':'bass','REI':'rei_bianchi'}[owner]
    rows.append(dict(owner=owner,repository=f'cosmosapjw-quantum/{repo}',commit=ref[owner],path=path,git_blob_sha=sha,function=fun,line_range=lines,classification=cl,evidence=why,verification=evidence,link=f'https://github.com/cosmosapjw-quantum/{repo}/blob/{ref[owner]}/{path}'))
obj={'schema':'REC_HD_CONSUMER_CALLSITE_MATRIX_V1','date_kst':'2026-10-29','scope':'Selected exact code files/functions only, not an exhaustive search of all archive, branches, generated C/Rust or external consumer implementations','pinned_refs':ref,'entries':rows,'confirmed_direct_HD_consumers':['REC PR151 generate','REC PR155 frequency_comparison'],'not_demonstrated':'No direct HD LAMDA binding was established in the inspected REC production, BASS atomic/Thomson or REI H/He continuum functions. This is not a proof of absence elsewhere.','cross_repo_import':False,'source_replacement':False,'physical_promotion':False,'canonical':'28/88 (+0)','REC_physical':'0/313 (+0)'}
(ROOT/'CALLSITE_MATRIX.json').write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
print('matrix_entries',len(rows))
