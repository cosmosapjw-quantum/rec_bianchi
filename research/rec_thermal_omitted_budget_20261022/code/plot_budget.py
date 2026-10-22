"""Publication figures of immutable saved-grid budgets; no trajectory execution."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

UNIT=Path(__file__).resolve().parents[1]
PRIMARY=('s00_m02_r02','s02_m04_r01','s03_m03_r03','s04_m04_r04')
COLORS=('#0072B2','#009E73','#D55E00','#CC79A7')
REP='s03_m03_r03_mao2017_nominal'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def json_write(p,value):
    with p.open('x') as f: json.dump(value,f,indent=2,allow_nan=False);f.write('\n')

def run(source,output):
    source=Path(source);output=Path(output);output.mkdir(parents=True,exist_ok=False)
    s=json.loads((source/'SUMMARY.json').read_text());receipt=json.loads((source/'RESULT.json').read_text())
    for rel,v in receipt['files'].items():
        if sha(source/rel)!=v['sha256']: raise ValueError('RESULT_IDENTITY_CHANGED:'+rel)
    data={}
    for label in s['cases']:
        with np.load(source/label/'budget.npz',allow_pickle=False) as d:
            data[label]={k:d[k].copy() for k in d.files}
    d=data[REP];z=d['z'];pn=d['process_names'].tolist();fn=d['forcing_names'].tolist()
    plt.rcParams.update({'font.size':10,'axes.titlesize':12,'axes.labelsize':11,
        'figure.dpi':150,'savefig.dpi':180,'axes.spines.top':False,'axes.spines.right':False,
        'legend.frameon':False,'pdf.fonttype':42})
    arrays={};figfiles=[]
    def save(fig,name):
        for ext in ('png','pdf'):
            p=output/(name+'.'+ext)
            buffer=io.BytesIO();fig.savefig(buffer,format=ext,bbox_inches='tight')
            payload=buffer.getvalue()
            if ext=='png':
                with Image.open(io.BytesIO(payload)) as check:check.verify()
            p.write_bytes(payload)
            if p.read_bytes()!=payload:raise IOError('FIGURE_WRITE_MISMATCH:'+p.name)
            figfiles.append(p)
        plt.close(fig)
    def z_axis(ax):
        ax.set_xlim(float(z[0]),float(z[-1]));ax.set_xlabel('Redshift z  (time increases to the right)')
        ax.grid(alpha=.2)
    def E(label,p):return s['cases'][label]['energy_eV_per_baryon'][p]['trapezoid_109']

    # Figure 1: directly signed energy; reference curve is visibly separate.
    fig,axs=plt.subplots(1,2,figsize=(14.5,5.7),gridspec_kw={'width_ratios':[1.15,1]})
    for case,color in zip(PRIMARY,COLORS):
        a=data[case+'_mao2017_nominal'];v=a['energy_cumulative_eV_baryon'][:,pn.index('compton_hot_cmb')]
        axs[0].plot(a['z'],v,color=color,label=case,linewidth=1.8)
        arrays[case+'_z']=a['z'];arrays[case+'_hot_cumulative_eV_baryon']=v
    ref=d['energy_cumulative_eV_baryon'][:,pn.index('compton_planck_reference')]
    axs[0].plot(z,ref,'k--',lw=1.15,label='s03: separate Planck reference')
    arrays['representative_planck_cumulative_eV_baryon']=ref
    axs[0].set_ylabel('Cumulative gas energy input  [eV / baryon]')
    axs[0].set_title('(a) Accumulated Compton energy on four paths')
    axs[0].legend(fontsize=8.8,loc='lower left');z_axis(axs[0])
    processes=('photo_primary','adiabatic_work','compton_hot_cmb','rr_kinetic','ce_HI','compton_uv','ci_kinetic','ci_binding')
    names=('Photo heat (existing)','Expansion work (existing)','Compton hot (actual U)','RR kinetic loss (existing)',
           'H I excitation','UV Compton','CI kinetic transfer','CI binding transfer')
    vals=np.array([E(REP,p) for p in processes]);yy=np.arange(len(vals))
    axs[1].barh(yy,vals,color=['#D55E00' if v>0 else '#0072B2' for v in vals],height=.65)
    axs[1].set_yticks(yy,names);axs[1].invert_yaxis();axs[1].set_xscale('symlog',linthresh=1e-5,linscale=.7)
    axs[1].set_xlim(-12,12);axs[1].axvline(0,color='.4',lw=.7)
    axs[1].set_xticks([-10,-1e-2,-1e-4,0,1e-4,1e-2,10])
    for y,v in zip(yy,vals):
        axs[1].text(1.025,y,f'{v:+.4g}',transform=axs[1].get_yaxis_transform(),
                    ha='left',va='center',fontsize=9)
    axs[1].set_title('(b) Signed integrated budget: s03')
    axs[1].set_xlabel('Energy input  [eV / baryon]; symlog scale')
    axs[1].grid(axis='x',alpha=.2)
    fig.suptitle('REC: omitted thermal energy on saved paths | z = 7.964 to 2',fontsize=15,y=.98)
    fig.subplots_adjust(left=.07,right=.89,top=.83,bottom=.22,wspace=.62)
    fig.text(.5,.012,'109-node trapezoid. Positive = gas energy gain. CI transfers kinetic energy into binding; their sum is zero.\n'
             'The Planck curve is a separate spectral reference. These integrals do not predict the coupled temperature response.',
             ha='center',fontsize=9)
    arrays['bar_process_names']=np.array(processes);arrays['bar_energy_eV_baryon']=vals
    save(fig,'01_compton_energy_budget')

    # Figure 2: source support, reference difference, sign-aware forcing and transfer.
    fig,axs=plt.subplots(2,2,figsize=(13,9.8))
    axs[0,0].plot(z,d['T_K']/1000,color='k',lw=1.8,label='saved gas temperature')
    axs[0,0].axhline(10,color='#D55E00',ls='--',lw=1.2,label='CI fit lower limit: 10 kK')
    axs[0,0].axhline(5,color='#0072B2',ls=':',lw=1.4,label='CE fit lower limit: 5 kK')
    axs[0,0].fill_between(z,0,16,where=d['T_K']<10000,color='#D55E00',alpha=.08,step='mid')
    axs[0,0].set_ylim(0,16);axs[0,0].set_ylabel('Temperature [kK]');axs[0,0].legend(fontsize=8.7,loc='lower right')
    axs[0,0].set_title('(a) Published fit support')
    axs[0,0].text(.03,.96,'CI: 10 / 109 nodes below range\nCE: 3 / 109 nodes below range',transform=axs[0,0].transAxes,
                  va='top',fontsize=9)
    arrays['representative_T_K']=d['T_K'];arrays['representative_support_mask']=d['in_published_accuracy_domain']
    for case,color in zip(PRIMARY,COLORS):
        a=data[case+'_mao2017_nominal'];hot=a['Q_W_m3'][:,pn.index('compton_hot_cmb')]
        ref=a['Q_W_m3'][:,pn.index('compton_planck_reference')]
        difference=100*(hot-ref)/abs(hot)
        axs[0,1].plot(z,difference,color=color,lw=1.6,label=case)
        arrays[case+'_hot_minus_reference_percent']=difference
    axs[0,1].axhline(0,color='.4',lw=.7);axs[0,1].set_ylabel('100 (hot actual U − Planck reference) / |hot| [%]')
    axs[0,1].set_title('(b) Spectral reference comparison')
    axs[0,1].legend(fontsize=8.6,loc='best')
    names2=(('compton_hot_cmb','Compton hot: cooling','#CC79A7','-'),
            ('ce_HI','H I CE: cooling','#0072B2','-'),
            ('ci_full','H/He CI incl. new electron: cooling','#009E73','-'),
            ('compton_uv','UV Compton: heating','#D55E00','--'))
    for p,label,color,style in names2:
        val=d['fixed_path_logT_forcing_per_x'][:,fn.index(p)]
        axs[1,0].plot(z,np.abs(val),color=color,ls=style,lw=1.7,label=label)
        arrays['representative_forcing_'+p]=val
    axs[1,0].set_yscale('log');axs[1,0].set_ylim(1e-9,10)
    axs[1,0].set_ylabel('|Direct fixed-path d ln T / dx forcing|')
    axs[1,0].set_title('(c) Direct fixed-path forcing')
    axs[1,0].legend(fontsize=8.3,loc='upper right')
    for p,label,color,style in (('ce_HI','H I CE (kinetic loss)','#0072B2','-'),
                               ('compton_uv','UV Compton (gain)','#D55E00','-'),
                               ('ci_kinetic','CI kinetic (transfer out)','#009E73','-'),
                               ('ci_binding','CI binding (transfer in)','#009E73','--')):
        val=d['energy_cumulative_eV_baryon'][:,pn.index(p)]
        axs[1,1].plot(z,val,color=color,ls=style,lw=1.7,label=label)
        arrays['representative_cumulative_'+p]=val
    axs[1,1].set_yscale('symlog',linthresh=1e-7);axs[1,1].axhline(0,color='.4',lw=.7)
    axs[1,1].set_ylabel('Cumulative energy input [eV / baryon]; symlog')
    axs[1,1].set_title('(d) Smaller terms and internal transfer')
    axs[1,1].legend(fontsize=8.3,loc='lower left')
    for ax in axs.flat:z_axis(ax)
    fig.suptitle('Source support and energy ownership\nRepresentative s03; four paths in panel (b)',fontsize=14,y=.98)
    fig.subplots_adjust(left=.08,right=.98,top=.88,bottom=.12,wspace=.28,hspace=.38)
    fig.text(.5,.01,'Below-range fit values are labeled analytic continuations. Supported intervals require both endpoints in range.\n'
             'Panel (c) shows magnitudes above its displayed floor; all signed values remain in the source arrays. No solved ΔT is plotted.',
             ha='center',fontsize=9)
    save(fig,'02_source_support_and_transfer')

    # Figure 3: retained-grid and inherited-trajectory comparisons, not error bars.
    fig,axs=plt.subplots(1,2,figsize=(12.8,5.7))
    qs=('photo_primary','adiabatic_work','compton_hot_cmb','rr_kinetic')
    qnames=('Photo heat','Expansion work','Compton hot','RR kinetic')
    coarse=np.array([abs(s['cases'][REP]['energy_eV_per_baryon'][p]['coarse_minus_primary']) for p in qs])
    simp=np.array([abs(s['cases'][REP]['energy_eV_per_baryon'][p]['simpson_minus_primary']) for p in qs])
    xx=np.arange(len(qs));axs[0].bar(xx-.18,coarse,.36,label='|trap55 − trap109|',color='#0072B2')
    axs[0].bar(xx+.18,simp,.36,label='|Simpson109 − trap109|',color='#D55E00')
    axs[0].set_xticks(xx,qnames,rotation=12);axs[0].set_yscale('log');axs[0].set_ylabel('Absolute integral difference [eV / baryon]')
    axs[0].set_title('(a) Retained-grid quadrature: s03');axs[0].legend(fontsize=9)
    arrays['quadrature_processes']=np.array(qs);arrays['quadrature_abs_coarse_delta']=coarse;arrays['quadrature_abs_simpson_delta']=simp
    paircases=('s03_m03_r03','s04_m04_r04');xx=np.arange(2)
    for off,typ,label,color in ((-.18,'refinement','Existing refined trajectory','#009E73'),(.18,'RR_trajectory_alternative','Existing RR alternative','#CC79A7')):
        vals=np.array([abs(s['pair_comparisons'][case+'_'+typ]['energy_delta_eV_per_baryon']['compton_hot_cmb']) for case in paircases])
        axs[1].bar(xx+off,vals,.36,color=color,label=label)
        for x,v in zip(xx+off,vals):axs[1].text(x,v*1.25,f'{v:.2g}',ha='center',fontsize=9)
        arrays['trajectory_abs_hot_energy_delta_'+typ]=vals
    axs[1].set_xticks(xx,paircases);axs[1].set_yscale('log');axs[1].set_ylim(5e-8,4e-3)
    axs[1].set_ylabel('|Change in hot Compton integral| [eV / baryon]')
    axs[1].set_title('(b) Inherited trajectory sensitivity');axs[1].legend(fontsize=9,loc='upper center')
    for ax in axs:ax.grid(axis='y',alpha=.2)
    fig.suptitle('Numerical comparisons on the saved trajectories',fontsize=15,y=.98)
    fig.subplots_adjust(left=.08,right=.98,top=.83,bottom=.24,wspace=.3)
    fig.text(.5,.012,'The 55-node grid is a subset of the same 109 samples. No interpolation, new ODE, or continuum error bound.\n'
             'RR alternatives change a source model; their differences are not numerical uncertainty estimates.',ha='center',fontsize=9)
    save(fig,'03_numerical_comparisons')

    np.savez_compressed(output/'plot_data.npz',**arrays)
    rows=[]
    for case in PRIMARY:
        label=case+'_mao2017_nominal';r=s['cases'][label]
        rows.append(dict(case=case,hot_eV_baryon=E(label,'compton_hot_cmb'),planck_reference_eV_baryon=E(label,'compton_planck_reference'),
            ci_kinetic_eV_baryon=E(label,'ci_kinetic'),ce_HI_eV_baryon=E(label,'ce_HI'),UV_eV_baryon=E(label,'compton_uv'),
            added_logT_forcing=r['fixed_path_logT_forcing']['added_primary']['trapezoid_109'],
            hot_to_photo_ratio=abs(E(label,'compton_hot_cmb'))/E(label,'photo_primary'),
            hot_to_rr_ratio=abs(E(label,'compton_hot_cmb')/E(label,'rr_kinetic')),
            hot_to_expansion_ratio=abs(E(label,'compton_hot_cmb')/E(label,'adiabatic_work'))))
    with (output/'PRIMARY_TABLE.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    json_write(output/'FIGURE_MANIFEST.json',dict(status='RENDERED_AWAITING_VISUAL_REVIEW',
        source_result_sha256=sha(source/'RESULT.json'),source_identity=s['source_identity'],
        plotter_sha256=sha(__file__),matplotlib=matplotlib.__version__,
        inputs={str((source/label/'budget.npz').relative_to(UNIT)):sha(source/label/'budget.npz') for label in data},
        outputs={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(output.iterdir()) if p.is_file()},
        new_ODE_integrations=0))
    print(json.dumps(dict(status='RENDERED',output=str(output),figures=3,matplotlib=matplotlib.__version__)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=UNIT/'results/budget_v1')
    p.add_argument('--output',type=Path,default=UNIT/'figures/v1');a=p.parse_args();run(a.source,a.output)
