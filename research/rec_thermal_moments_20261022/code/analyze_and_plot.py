#!/usr/bin/env python3
"""Source-bound figures and comparisons of saved thermal restarts; no ODE calls.

All differences use exactly paired saved x/redshift nodes. A plotted time axis
is explicitly the nominal Mao case's elapsed proper time since donor z=20;
it is neither the cosmic age nor time since the z~8 restart. Raw signed values
and zero-inventory states are retained in NPZ/CSV. No clipping/renormalization.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'rec_thermal_mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

UNIT = Path(__file__).resolve().parents[1]
DONOR = UNIT.parent/'rec_rei_hheli_sandbox_20261021'
sys.path.insert(0, str(DONOR/'code'))
from atomic_network import AtomicNetwork
from thermal_sources import ThermalSources

CASES = ('s00_m02_r02','s03_m03_r03','s04_m04_r04','s02_m04_r01')
PAIRS = ('s03_m03_r03','s04_m04_r04')
SIGNED = ('S_F','P_m_F','P_r_F','P_total_F','P_gamma_F','P_nu_F')
COLORS = ('#0072B2','#D55E00','#009E73','#CC79A7')
GATES = dict(lnT=3e-5, ionic=3e-5, signed=3e-7, tau=3e-7)
SECONDS_PER_MYR = 31557600e6


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False,
        default=lambda v: v.item() if isinstance(v,np.generic) else str(v))+'\n')


def save_csv(path, rows):
    if not rows:
        raise ValueError('empty CSV: '+str(path))
    with Path(path).open('w', newline='') as stream:
        w=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader(); w.writerows(rows)


def read_npz(path):
    with np.load(path,allow_pickle=False) as data:
        return {k:data[k].copy() for k in data.files}


def diag(data,name):
    return data['diagnostics'][:,data['diagnostic_names'].tolist().index(name)]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def finish_figure(fig, stem, directory, manifest, source, caption):
    fig.savefig(directory/(stem+'.png'),dpi=190,bbox_inches='tight',facecolor='white')
    fig.savefig(directory/(stem+'.pdf'),bbox_inches='tight',facecolor='white',
                metadata={'Title':stem,'Subject':caption,'Creator':'Matplotlib'})
    plt.close(fig)
    manifest.append(dict(stem=stem,source=source,caption=caption,
                         outputs={suffix:dict(sha256=sha(directory/(stem+'.'+suffix)),
                         bytes=(directory/(stem+'.'+suffix)).stat().st_size) for suffix in ('png','pdf')}))


def style():
    plt.rcParams.update({'font.size':10,'axes.titlesize':11,'axes.labelsize':10,
                         'legend.fontsize':9,'figure.titlesize':14,'axes.grid':True,
                         'grid.alpha':.2,'lines.linewidth':1.6,'pdf.fonttype':42})


def clock_axis(ax, time, z, case, label=True):
    require(np.all(np.diff(time)>0) and np.all(np.diff(z)<0),'nonmonotone reference clock')
    ax.set_xlim(time[0],time[-1])
    sec=ax.secondary_xaxis('top',functions=(
        lambda t:np.interp(t,time,z),lambda zz:np.interp(zz,z[::-1],time[::-1])))
    sec.set_xticks([v for v in (8,7,6,5,4,3,2) if z[-1]-1e-10<=v<=z[0]+1e-10])
    sec.set_xlabel('Redshift (Mao reference clock)',fontsize=9)
    if label:
        ax.set_xlabel('Elapsed since donor z=20 [Myr]')
    return sec


def source_figure(out, figures, manifest):
    atomic=AtomicNetwork()
    mao=ThermalSources(atomic,'mao2017'); derivative=ThermalSources(atomic,'rate_derivative')
    temperature=np.geomspace(100,1e6,801)
    selected=json.loads((UNIT/'data/mao2017_selected.json').read_text())
    indices=[next(i for i in atomic.recombination_indices if
                  atomic.Z[i]==row['initial_Z'] and atomic.q[i]==row['initial_q'])
             for row in selected['rows']]
    fmao=np.array([mao.coefficients(float(t))['rr_loss_factor'][indices] for t in temperature])
    fder=np.array([derivative.coefficients(float(t))['rr_loss_factor'][indices] for t in temperature])
    labels=('H II → H I','He II → He I','He III → He II',
            'Li II → Li I','Li III → Li II','Li IV → Li III')
    relative=fder/fmao-1
    np.savez_compressed(out/'SOURCE_FACTORS.npz',temperature_K=temperature,mao=fmao,
                        rate_derivative=fder,relative_difference=relative,channel=np.array(labels))
    rows=[]
    fig,axes=plt.subplots(2,3,figsize=(12.4,7.5),layout='constrained')
    for j,(row,ax,label) in enumerate(zip(selected['rows'],axes.flat,labels)):
        peak=int(np.argmax(abs(relative[:,j])))
        old=temperature<=12000
        rows.append(dict(channel=label,initial_Z=row['initial_Z'],initial_q=row['initial_q'],
            max_abs_relative_100_1e6=float(abs(relative[peak,j])),at_T_K=float(temperature[peak]),
            max_abs_relative_100_12000=float(np.max(abs(relative[old,j])))))
        ax.axvspan(100,12000,color='#D9EAF2',alpha=.6,zorder=0)
        ax.plot(temperature,fmao[:,j],color=COLORS[0],label='Mao factor')
        ax.plot(temperature,fder[:,j],color=COLORS[1],ls='--',label='Rate derivative')
        tt=np.array(row['table_temperature_K']); ff=np.array(row['source_unparameterized_f'])
        mask=(tt>=100)&(tt<=1e6)
        ax.scatter(tt[mask],ff[mask],s=15,facecolor='none',edgecolor='black',linewidth=.65,
                   zorder=4,label='Published rounded table')
        ax.set_xscale('log');ax.set_yscale('log');ax.set_xlim(100,1e6)
        ax.set_title(label);ax.set_xlabel('Temperature [K]');ax.set_ylabel(r'$f=L_{RR}/(k_B T\alpha_{RR})$')
        ax.text(.04,.08,f'max |derivative/Mao − 1| = {100*abs(relative[peak,j]):.2f}%',
                transform=ax.transAxes,fontsize=8.5,bbox=dict(facecolor='white',alpha=.85,edgecolor='none'))
        if j==0:ax.legend(loc='lower left',bbox_to_anchor=(0,.17),fontsize=8)
    fig.suptitle('RR kinetic-energy factors: source sensitivity at unchanged number rates\n'
                 'Shading: inherited 100–12000 K bath range; dots: source table, no refit',fontsize=13)
    save_csv(out/'SOURCE_FACTOR_MAXIMA.csv',rows)
    finish_figure(fig,'01_rr_source_factors',figures,manifest,'SOURCE_FACTORS.npz; SOURCE_FACTOR_MAXIMA.csv',
        'Mao-factor hybrid versus derivative-implied kinetic loss at fixed parent number coefficients. Extrema are sampled on801 logarithmic temperature nodes. Differences are closure sensitivity, not confidence bounds.')
    return rows


def load_case(label,source):
    directory=source/label
    result=json.loads((directory/'RESULT.json').read_text())
    require(result['status']=='COMPLETE' and all(result['gates'].values()),'unaccepted case '+label)
    require(result['label']==label,'label mismatch')
    path=directory/'trajectory.npz'
    require(sha(path)==result['trajectory_sha256'],'trajectory hash mismatch '+label)
    for p,h in result['source_files'].items():
        require(sha(UNIT/p)==h,'execution dependency changed '+p)
    data=read_npz(path)
    donor_path=DONOR/result['donor'];parent=read_npz(donor_path)
    require(sha(donor_path)==result['donor_sha256'],'donor hash mismatch '+label)
    i=int(data['source_index'])
    require(i==result['start_index'],'restart index mismatch')
    require(np.array_equal(data['x'],parent['x'][i:]),'saved-node mismatch')
    require(np.array_equal(data['raw_state'][0,:62],parent['raw_state'][i]),'restart altered donor state')
    require(np.array_equal(data['isotope_scales'],parent['isotope_scales']),'isotope scale mismatch')
    require(data['raw_state'].shape==(len(data['x']),63),'state shape mismatch')
    require(np.array_equal(data['T_K'],np.exp(data['raw_state'][:,62])),'temperature field mismatch')
    require(np.all(np.isfinite(data['raw_state'])),'nonfinite saved state')
    require(np.all(data['Y'][:,[0,5,6]]==0),'unsupported nuclear source')
    return dict(label=label,result=result,data=data,parent=parent,index=i,
                time=diag(data,'elapsed_Myr'),donor_time=diag(parent,'elapsed_s')[i:]/SECONDS_PER_MYR,
                names=parent['species_names'].tolist(),sha256=sha(path))


def metrics(a,b,kind):
    da,db=a['data'],b['data']
    require(np.array_equal(da['x'],db['x']),'comparison saved grids differ')
    require(np.array_equal(da['initial_state'],db['initial_state']),'comparison restarts differ')
    d=dict(lnT=da['raw_state'][:,62]-db['raw_state'][:,62],
           ionic=(da['Y']-db['Y'])/da['isotope_scales'],
           signed=da['signed_observables']-db['signed_observables'],
           tau=da['raw_state'][:,61]-db['raw_state'][:,61])
    maxima={k:float(np.max(abs(v))) for k,v in d.items()}
    peaks={}
    for key,value in d.items():
        ij=np.unravel_index(np.argmax(abs(value)),value.shape)
        peaks[key]=dict(sample=int(ij[0]),redshift=float(da['z'][ij[0]]),
                        signed_difference=float(value[ij]),channel=(a['names'][ij[1]] if key=='ionic'
                            else SIGNED[ij[1]] if key=='signed' else key))
    checks={key:maxima[key]<limit for key,limit in GATES.items()}
    row=dict(a=a['label'],b=b['label'],kind=kind,max_abs=maxima,peaks=peaks,
             max_temperature_difference_K=float(np.max(abs(da['T_K']-db['T_K']))),
             final_T_difference_K=float(da['T_K'][-1]-db['T_K'][-1]),
             final_tau_difference=float(d['tau'][-1]),
             signed_max_abs_by_channel=dict(zip(SIGNED,np.max(abs(d['signed']),axis=0).tolist())),
             signed_endpoint_difference=dict(zip(SIGNED,d['signed'][-1].tolist())),
             final_ionic_difference=dict(zip(a['names'],d['ionic'][-1].tolist())),
             a_sha256=a['sha256'],b_sha256=b['sha256'])
    if kind=='refinement':row.update(limits=GATES,gates=checks,status='PASS' if all(checks.values()) else 'FAIL')
    else:row.update(status='SOURCE_SENSITIVITY',interpretation='Not a probability interval or complete model error.')
    return row,d


def thermal_figures(cases,out,figures,manifest):
    fig,axes=plt.subplots(2,2,figsize=(12.4,8.4),layout='constrained')
    rows=[]; endpoints=[]; sources={}
    for j,(case,ax) in enumerate(zip(CASES,axes.flat)):
        item=cases[case+'_mao2017_nominal'];d=item['data'];p=item['parent'];i=item['index'];t=item['time']
        bath=diag(p,'T_K')[i:]
        ax.plot(t,bath,color='0.35',ls=':',label='Inherited prescribed bath T(z)')
        ax.plot(t,d['T_K'],color=COLORS[j],label='Dynamic T: Mao-factor hybrid')
        alt=cases.get(case+'_rate_derivative_nominal')
        if alt is not None:ax.plot(t,alt['data']['T_K'],color='black',ls='--',label='Dynamic T: rate derivative')
        ax.set_yscale('log');ax.set_ylabel('Gas temperature [K]');ax.set_title(case)
        clock_axis(ax,t,d['z'],case)
        ax.legend(loc='best',fontsize=8)
        f=d['Y']/d['isotope_scales'];fp=p['Y'][i:]/d['isotope_scales']
        parent_diff=dict(lnT=float(np.max(abs(np.log(d['T_K']/bath)))),
                         ionic=float(np.max(abs(f-fp))),
                         signed=float(np.max(abs(d['signed_observables']-p['signed_observables'][i:]))),
                         tau=float(np.max(abs(d['raw_state'][:,61]-p['raw_state'][i:,61]))))
        temperature_peak=int(np.argmax(d['T_K']))
        ion_peak=np.unravel_index(np.argmax(abs(f-fp)),f.shape)
        pd=d['signed_observables']-p['signed_observables'][i:]
        endpoints.append(dict(case_id=case,temperature_end_K=float(d['T_K'][-1]),
            temperature_peak_K=float(d['T_K'][temperature_peak]),
            temperature_peak_z=float(d['z'][temperature_peak]),
            temperature_peak_elapsed_Myr=float(t[temperature_peak]),
            parent_temperature_end_K=float(bath[-1]),tau_end=float(d['raw_state'][-1,61]),
            parent_tau_end=float(p['raw_state'][-1,61]),max_abs_parent_differences=parent_diff,
            parent_ionic_peak=dict(channel=item['names'][ion_peak[1]],redshift=float(d['z'][ion_peak[0]]),
                                  signed_difference=float((f-fp)[ion_peak])),
            signed_trajectory_max_abs=dict(zip(SIGNED,np.max(abs(d['signed_observables']),axis=0).tolist())),
            parent_signed_difference_max_abs=dict(zip(SIGNED,np.max(abs(pd),axis=0).tolist())),
            parent_signed_endpoint_difference=dict(zip(SIGNED,pd[-1].tolist())),
            final_scaled_ionic=dict(zip(item['names'],f[-1].tolist())),
            final_parent_scaled_ionic=dict(zip(item['names'],fp[-1].tolist())),
            final_signed=dict(zip(SIGNED,d['signed_observables'][-1].tolist()))))
        sources[case+'_x']=d['x'];sources[case+'_z']=d['z'];sources[case+'_elapsed_Myr']=t
        sources[case+'_T_K']=d['T_K'];sources[case+'_bath_T_K']=bath
        sources[case+'_ionic']=f;sources[case+'_parent_ionic']=fp
        sources[case+'_signed']=d['signed_observables'];sources[case+'_parent_signed']=p['signed_observables'][i:]
        for k in range(len(t)):
            row=dict(case_id=case,x=float(d['x'][k]),z=float(d['z'][k]),elapsed_Myr=float(t[k]),
                     parent_elapsed_Myr=float(item['donor_time'][k]),T_K=float(d['T_K'][k]),
                     bath_T_K=float(bath[k]),tau=float(d['raw_state'][k,61]))
            row.update({name:float(f[k,n]) for n,name in enumerate(item['names'])});rows.append(row)
    fig.suptitle('Four saved-state thermal restarts: z ≈ 7.964 → 2\n'
                 'Each panel uses its own nominal Mao clock; earlier evolution is inherited',fontsize=13)
    save_csv(out/'THERMAL_HISTORIES.csv',rows)
    np.savez_compressed(out/'THERMAL_PLOT_SOURCE.npz',**sources)
    finish_figure(fig,'02_dynamic_temperature',figures,manifest,'THERMAL_PLOT_SOURCE.npz; THERMAL_HISTORIES.csv',
        'Distinct new thermal restarts from exact donor node84; prescribed-bath and alternative-source curves sampled at the same redshift on each panel reference clock.')
    # The two most anisotropic reviewed cases carry all displayed representative
    # ion channels; the machine-readable output retains all21 census entries.
    channels=((2,'H1 II'),(11,'He4 II'),(12,'He4 III'),(17,'Li7 I'),(18,'Li7 II'),(20,'Li7 IV'))
    fig,axes=plt.subplots(2,2,figsize=(12.5,8.7),layout='constrained')
    for row,case in enumerate(PAIRS):
        item=cases[case+'_mao2017_nominal'];d=item['data'];p=item['parent'];i=item['index'];t=item['time']
        f=d['Y']/d['isotope_scales'];fp=p['Y'][i:]/d['isotope_scales']
        for j,(k,label) in enumerate(channels):
            color=plt.get_cmap('tab10')(j)
            axes[row,0].plot(t,f[:,k],color=color,label=label)
            axes[row,0].plot(t,fp[:,k],color=color,ls=':',alpha=.8)
            axes[row,1].plot(t,f[:,k]-fp[:,k],color=color,label=label)
        axes[row,0].set_yscale('symlog',linthresh=1e-10,linscale=.4)
        axes[row,1].set_yscale('symlog',linthresh=1e-7,linscale=.4)
        axes[row,0].set_ylabel('Conditional ion fraction');axes[row,1].set_ylabel('Dynamic − prescribed fraction')
        axes[row,0].set_title(case+' | solid: dynamic; dotted: prescribed')
        axes[row,1].set_title(case+' | signed differences at common redshift')
        axes[row,0].legend(loc='best',ncol=2,fontsize=8)
        for ax in axes[row]:clock_axis(ax,t,d['z'],case)
    fig.suptitle('Representative ionization response to the thermal closure\n'
                 'All21 states are exported; n/T remain exactly zero by the frozen no-nuclear-source model',fontsize=13)
    finish_figure(fig,'03_ionic_response',figures,manifest,'THERMAL_PLOT_SOURCE.npz; THERMAL_HISTORIES.csv',
        'Signed conditional-ion differences are shown without clipping. Symlog linear bands are1e-10 for fractions and1e-7 for differences. Isotope-normalized fractions are not absolute abundances.')
    return endpoints


def comparison_figure(cases,out,figures,manifest):
    comparisons=[];sources={};fig,axes=plt.subplots(2,4,figsize=(14.2,7.7),layout='constrained')
    labels=dict(lnT=r'$|\Delta\ln T|$',ionic=r'$\max_i |\Delta f_i|$',
                signed=r'$\max_A |\Delta (S_F,P_{A,F})|$',tau=r'$|\Delta\tau_T|$')
    for row,case in enumerate(PAIRS):
        a=cases[case+'_mao2017_nominal'];t=a['time'];d=a['data']
        for other,kind,color,ls in (('mao2017_refined','refinement',COLORS[0],'-'),
                                   ('rate_derivative_nominal','source',COLORS[1],'--')):
            record,delta=metrics(a,cases[case+'_'+other],kind);comparisons.append(record)
            for col,key in enumerate(GATES):
                value=abs(delta[key]);value=np.max(value,axis=1) if value.ndim==2 else value
                sources[case+'_'+kind+'_'+key]=value
                axes[row,col].plot(t,value,color=color,ls=ls,label='Tolerance refinement' if kind=='refinement' else 'RR source sensitivity')
                if kind=='refinement':axes[row,col].axhline(GATES[key],color='0.4',ls=':',lw=1,label='Frozen refinement gate')
        sources[case+'_elapsed_Myr']=t;sources[case+'_z']=d['z'];sources[case+'_x']=d['x']
        for col,key in enumerate(GATES):
            ax=axes[row,col];ax.set_yscale('symlog',linthresh=1e-12,linscale=.35)
            ax.set_ylim(bottom=0)
            ax.set_ylabel(labels[key]);ax.set_title(case if col==0 else labels[key])
            clock_axis(ax,t,d['z'],case)
            if row==0 and col==0:ax.legend(loc='best',fontsize=7.5)
    fig.suptitle('Separate numerical refinement from RR closure sensitivity\n'
                 'Maxima over exactly paired saved nodes; source differences are not convergence errors',fontsize=13)
    np.savez_compressed(out/'COMPARISON_PLOT_SOURCE.npz',**sources)
    finish_figure(fig,'04_source_and_refinement',figures,manifest,'COMPARISON_PLOT_SOURCE.npz; SUMMARY.json',
        'Nominal-minus-refined and Mao-minus-derivative differences are distinct. Only nominal/refined differences are subject to frozen gates. Exact zeros preserved in symlog linear band1e-12.')
    return comparisons


def optional_saved126(out,figures,manifest):
    path=UNIT/'results/saved126/REPRESENTATIVE.csv'
    if not path.exists():return dict(status='NOT_AVAILABLE_AT_ANALYSIS')
    with path.open(newline='') as stream: rows=list(csv.DictReader(stream))
    require(bool(rows),'empty saved126 representative')
    t=np.array([float(r['elapsed_Myr']) for r in rows]);z=np.array([float(r['z']) for r in rows])
    source={name:np.array([float(r[name]) for r in rows]) for name in
        ('Qext_W_m3','Qext_rate_derivative_W_m3','Qrequired_W_m3','photo_primary_W_m3','rr_cooling_W_m3','dr_cooling_W_m3')}
    fig,axes=plt.subplots(1,2,figsize=(12.6,5.2),layout='constrained')
    for key,label,color,ls in [('Qext_W_m3','Required external bath: Mao',COLORS[0],'-'),
                             ('Qext_rate_derivative_W_m3','Required external bath: derivative',COLORS[1],'--')]:
        axes[0].plot(t,source[key],color=color,ls=ls,label=label)
    for key,label,color in [('Qrequired_W_m3','Kinetic energy requirement',COLORS[0]),
                           ('photo_primary_W_m3','Primary photoelectron heating',COLORS[1]),
                           ('rr_cooling_W_m3','RR kinetic loss',COLORS[2]),
                           ('dr_cooling_W_m3','DR kinetic loss',COLORS[3])]:
        axes[1].plot(t,source[key],color=color,label=label)
    for ax in axes:
        ax.set_yscale('symlog',linthresh=1e-38,linscale=.35);ax.set_ylabel('Signed power density [W m⁻³]')
        # The representative spans inherited z20..2; its own donor clock is used.
        ax.set_xlim(t[0],t[-1]);sec=ax.secondary_xaxis('top',functions=(
            lambda tt:np.interp(tt,t,z),lambda zz:np.interp(zz,z[::-1],t[::-1])))
        sec.set_xticks([20,10,7,5,3,2]);sec.set_xlabel('Redshift (saved donor clock)')
        ax.set_xlabel('Elapsed since donor z=20 [Myr]');ax.legend(loc='best',fontsize=8)
    fig.suptitle('Thermal forcing hidden by the inherited prescribed T(z)\n'
                 +rows[0]['case_id']+' | saved-data diagnostic; zero new integrations\n'
                 'Qext < 0: external cooling/extraction. DR is below the symlog linear threshold, not identically zero.',fontsize=11.5)
    np.savez_compressed(out/'SAVED_BATH_PLOT_SOURCE.npz',elapsed_Myr=t,z=z,**source)
    finish_figure(fig,'05_prescribed_bath_forcing',figures,manifest,'SAVED_BATH_PLOT_SOURCE.npz; ../saved126/REPRESENTATIVE.csv',
        'Signed external bath power required to enforce the inherited temperature. Positive means input, negative means cooling/extraction. DR lies below the symlog linear threshold and is not identically zero. Source terms evaluated on unchanged donor data; no dynamical trajectory produced.')
    return dict(status='PLOTTED_EXISTING_DIAGNOSTIC',source=str(path.relative_to(UNIT)),sha256=sha(path),case=rows[0]['case_id'])


def run(source,out,figures,source_only=False):
    out.mkdir(parents=True,exist_ok=True);figures.mkdir(parents=True,exist_ok=True);style();manifest=[]
    maxima=source_figure(out,figures,manifest)
    if source_only:
        save_json(out/'SOURCE_FIGURE_MANIFEST.json',dict(figures=manifest,code_sha256=sha(__file__)))
        return dict(status='SOURCE_FIGURE_COMPLETE',source_factor_maxima=maxima)
    specs=[c+'_mao2017_nominal' for c in CASES]+[c+'_'+suffix for c in PAIRS
                         for suffix in ('mao2017_refined','rate_derivative_nominal')]
    cases={label:load_case(label,source) for label in specs}
    endpoints=thermal_figures(cases,out,figures,manifest)
    comparisons=comparison_figure(cases,out,figures,manifest)
    saved=optional_saved126(out,figures,manifest)
    passed=all(row.get('status')=='PASS' for row in comparisons if row['kind']=='refinement')
    inputs={label:dict(sha256=c['sha256'],donor_sha256=c['result']['donor_sha256'],
                     source_identity=c['result']['source_identity'],initial_state_sha256=c['result']['initial_state_sha256'])
            for label,c in cases.items()}
    summary=dict(status='PASS_SCOPED_NUMERICAL_COMPARISON' if passed else 'REFINEMENT_GATE_FAIL',
        completed_new_configurations=len(cases),old_ivps_rerun=0,analysis_ode_calls=0,
        source_factor_maxima=maxima,comparisons=comparisons,nominal_endpoints=endpoints,
        temperature_range_K=[float(min(c['data']['T_K'].min() for c in cases.values())),
                             float(max(c['data']['T_K'].max() for c in cases.values()))],
        thermal_case_results={label:dict(gates=c['result']['gates'],energy_integrals=c['result']['energy_integrals'],
              energy_grid_delta_scaled=c['result']['energy_grid_delta_scaled']) for label,c in cases.items()},
        inputs=inputs,saved126=saved,clock='Elapsed proper time since donor z20, never cosmic age; common-redshift comparison on each Mao nominal clock.',
        fraction_policy='Y_i / positive isotope inventory; zero n/T scale retained only as numerical coordinates; all21 states exported.',
        claim_ceiling='Finite restart thermal test-fluid closure. Global convergence NOT_RUN; Physical HOLD; no complete thermal/radiation production admission.')
    save_json(out/'SUMMARY.json',summary)
    products=('SOURCE_FACTORS.npz','SOURCE_FACTOR_MAXIMA.csv','THERMAL_HISTORIES.csv',
              'THERMAL_PLOT_SOURCE.npz','COMPARISON_PLOT_SOURCE.npz','SAVED_BATH_PLOT_SOURCE.npz','SUMMARY.json')
    save_json(out/'FIGURE_MANIFEST.json',dict(figures=manifest,inputs=inputs,code_sha256=sha(__file__),
               data_files={name:sha(out/name) for name in products if (out/name).is_file()},
               manifest_scope='Explicit analytical products; open execution logs and later visual review records are excluded.'))
    if not passed:raise RuntimeError('Frozen nominal/refined gate failed; evidence preserved.')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,default=UNIT/'results/thermal8')
    parser.add_argument('--output',type=Path,default=UNIT/'results/analysis')
    parser.add_argument('--figures',type=Path,default=UNIT/'figures')
    parser.add_argument('--source-only',action='store_true')
    args=parser.parse_args()
    result=run(args.source,args.output,args.figures,args.source_only)
    print(json.dumps(result,indent=2,allow_nan=False))
