"""Admission of immutable actual original payload, never a history evolution."""
import csv, hashlib, json, math
from pathlib import Path
import numpy as np
from common import identity

def locate(q,eta,h,prefix):
    if q<eta[0]: return None
    if q>=eta[prefix-1]: raise ValueError('QUERY_FUTURE_OR_LATEST_KNOT')
    k=math.floor((q-eta[0])/h)
    if not 0<=k<prefix-1: raise ValueError('QUERY_CELL_OUTSIDE_PREFIX')
    return k,(q-eta[k])/h

def parameters_check(data,lead,provided=None):
    expected={'T0_K':2.728,'nH0_m3':.18745798773143102,'fsR':1.,'meR':1.}
    if provided is not None and provided!=expected: raise ValueError('COSMOLOGY_PARAMETER_MISMATCH')
    cp=lead['same_target_source_evidence']['canonical_fixture_parameters']; meta=data['meta']
    if cp['T0_K']!=expected['T0_K'] or cp['original_nH0_m3_from_prior_ADM01']!=expected['nH0_m3'] or meta['fsR']!=1 or meta['meR']!=1:
        raise ValueError('PROVENANCE_PARAMETER_MISMATCH')
    if meta['z']!=1099.9986525171403 or int(meta['iz_local'])!=5127: raise ValueError('TARGET_PREFIX_MISMATCH')
    # nH conversion is a retained scalar FLRW consistency check, not direct payload metadata.
    density=expected['nH0_m3']*(1+meta['z'])**3/1e6
    if abs(density-meta['nH_cm3'])>64*np.finfo(float).eps*max(density,1): raise ValueError('SCALAR_FLRW_DENSITY_MISMATCH')
    return expected

def admit(path,query_path,thermo,data):
    prov=json.loads((thermo/'provenance/source_intake/SOURCE_HISTORY_PROVENANCE.json').read_text())
    lead=json.loads((thermo/'provenance/source_intake/ORIGINAL_NATIVE_HISTORY_LEAD.json').read_text())
    ident=identity(path)
    if ident!={'bytes':35239470,'sha256':'d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1'}: raise ValueError('HISTORY_PAYLOAD_BYTE_IDENTITY')
    params=parameters_check(data,lead)
    with np.load(path,allow_pickle=False) as f: a={k:f[k].copy() for k in f.files}
    if str(a['schema'])!='PR05B2_ACCEPTED_HISTORY_V1': raise ValueError('HISTORY_SCHEMA')
    for k in ('average_virtual','energy_eV','eta','frequency_Hz','outgoing_lyman','outgoing_virtual','dlna','z_start'):
        if not np.all(np.isfinite(a[k])): raise ValueError('HISTORY_NONFINITE:'+k)
    eta=a['eta']; h=float(a['dlna']); prefix=5127
    if eta.shape!=(7489,) or h!=8.49e-5 or float(a['z_start'])!=1700.4825068138662: raise ValueError('HISTORY_GRID_METADATA')
    if not np.array_equal(a['source_indices'],np.arange(7489,dtype=np.int64)) or not np.all(np.diff(eta)>0): raise ValueError('HISTORY_INDEX_OWNERSHIP')
    expected_eta=-math.log1p(float(a['z_start']))+h*np.arange(7489,dtype=float)
    eta_error=np.abs(eta-expected_eta)
    if np.any(eta_error>32*np.finfo(float).eps*np.maximum(np.abs(eta),1)): raise ValueError('ETA_GRID_MISMATCH')
    raw={'pr05b2_energy_eV.f64':'energy_eV','pr05b2_Dfminus_hist.f64':'outgoing_virtual','pr05b2_Dfminus_Ly_hist.f64':'outgoing_lyman','pr05b2_Dfnu_hist.f64':'average_virtual'}
    checked={}
    for name,key in raw.items():
        b=np.asarray(a[key],dtype='<f8').tobytes(order='C'); got={'sha256':hashlib.sha256(b).hexdigest(),'size_bytes':len(b)}
        if got!=prov['raw_members'][name]: raise ValueError('HISTORY_RAW_MEMBER:'+name)
        checked[name]=got
    if not np.array_equal(a['energy_eV'],data['energy']): raise ValueError('HISTORY_ENERGY_IDENTITY')
    if a['outgoing_virtual'].shape!=(311,7489) or a['outgoing_lyman'].shape!=(3,7489): raise ValueError('HISTORY_SHAPE')
    source_hashes=dict(zip(a['source_hash_keys'].tolist(),a['source_hash_values'].tolist()))
    if source_hashes.get('HyRec/hydrogen.c')!='421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b' or source_hashes.get('HyRec_Oct2012.zip')!='48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27': raise ValueError('HISTORY_SOURCE_HASHES')
    with Path(query_path).open(newline='') as f: rows=list(csv.DictReader(f))
    if len(rows)!=313: raise ValueError('QUERY_COUNT')
    energies=np.r_[data['energy'],10.198714553953742,12.087365397278509,12.748393192442178]
    # Native upper-face ownership: each virtual target takes next energy except
    # virtual 139 -> alpha, virtual 270 -> beta; alpha -> virtual140, beta -> virtual271.
    source=np.arange(1,314,dtype=int); source[139]=311; source[270]=312; source[310]=313; source[311]=140; source[312]=271
    target=energies[:313]
    reconstructed=[]; records=[]
    for j,row in enumerate(rows):
        s=int(row['source_index']); q=-math.log((1+data['meta']['z'])*energies[s]/target[j])
        if int(row['incoming_index'])!=j or s!=source[j] or float(row['target_energy_eV'])!=target[j] or float(row['source_energy_eV'])!=energies[s]: raise ValueError('QUERY_SOURCE_TARGET_OWNER')
        if abs(q-float(row['eta_emit']))>32*np.finfo(float).eps*max(abs(q),1): raise ValueError('QUERY_TIME_MISMATCH')
        cell=locate(q,eta,h,prefix)
        if cell is None: value=0.; k=None; w=None; left=None; right=None; boundary='THERMAL_PREHISTORY_ZERO'
        else:
            k,w=cell; y=a['outgoing_virtual'][s] if s<311 else a['outgoing_lyman'][s-311]
            value=(1-w)*y[k]+w*y[k+1];left=q-eta[k];right=eta[k+1]-q;boundary='PREFIX_LINEAR_CELL'
        reconstructed.append(value)
        records.append({'incoming_index':j,'source_index':s,'eta_emit':q,'cell':k,'weight':w,'boundary':boundary,'left_margin':left,'right_margin':right,'upper_domain_margin':eta[prefix-1]-q,'stored':float(data['incoming'][j]),'reconstructed':value,'absolute_error':abs(value-data['incoming'][j])})
    u=np.asarray(reconstructed); diff=np.abs(u-data['incoming']); scale=max(np.max(np.abs(u)),np.max(np.abs(data['incoming'])),1e-280)
    normalized=float(np.max(diff)/scale)
    refused=False
    try: locate(float(eta[prefix-1]),eta,h,prefix)
    except ValueError: refused=True
    interior=locate(float((eta[prefix-2]+eta[prefix-1])/2),eta,h,prefix)
    mismatch_refused=False
    try: parameters_check(data,lead,{**params,'T0_K':2.7255})
    except ValueError: mismatch_refused=True
    assert refused and interior[0]==prefix-2 and mismatch_refused
    return {'status':'PASS' if normalized<=5e-9 else 'FAIL_RECONSTRUCTION','normalized_max_error':normalized,'absolute_max_error':float(np.max(diff)),'normalization':float(scale),'eta_max_absolute_error':float(np.max(eta_error)),'prefix_count':prefix,'last_available_index':prefix-1,'payload':ident,'raw_members':checked,'parameters':params,'parameter_evidence':'retained input.dat producer chain; payload does not encode cosmology','upper_endpoint_refused':refused,'last_cell_interior':interior,'different_cosmology_refused':mismatch_refused,'physical_epsilon':None,'records':records},u
