"""Rebuild publication figures and CSV sources from verified saved histories only."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from thermal import ROOT,EV_J
from run import CASES,digest,identity

LABELS={'thermal_iso60':'isotropic 60 eV','thermal_split60':'split 60 eV',
 'thermal_opposed60':'opposed 60 eV','thermal_split40':'split 40 eV',
 'thermal_warm60':'warm 60 eV','thermal_uv_off':'UV off'}
COLORS=dict(zip(LABELS,('#5b6770','#0072b2','#cc79a7','#d55e00','#009e73','#999933')))
STYLES=dict(zip(LABELS,(':','-','--','-.',(0,(5,1)),(0,(2,2)))))


def load(name):
    path=ROOT/'data'/name/'trajectory.npz';receipt=json.loads(path.with_name('RESULT.json').read_text())
    if receipt['status']!='PASS':raise ValueError('cannot plot failed case '+name)
    if receipt['raw_sha256']!=digest(path):raise ValueError('raw hash mismatch '+name)
    if receipt['identity']['sha256']!=identity(name)['sha256']:raise ValueError('source/config changed '+name)
    data=np.load(path);D={k:data['diagnostics'][:,i] for i,k in enumerate(data['diagnostic_names'])}
    return data,D


def redshift_axis(ax,time,z,label='Redshift z (split60 reference)'):
    twin=ax.twiny();twin.set_xlim(ax.get_xlim())
    ticks=np.array([20,10,7,5,3,2]);positions=np.interp(ticks,z[::-1],time[::-1])
    twin.set_xticks(positions,labels=[str(t) for t in ticks]);twin.set_xlabel(label,labelpad=7)
    twin.tick_params(axis='x',labelsize=9);return twin


def positive(values):
    # Display masking only: saved arrays retain exact zero and signed values.
    return np.where(values>0,values,np.nan)


def csv_write(path,names,columns):
    with Path(path).open('w',newline='') as handle:
        writer=csv.writer(handle);writer.writerow(names);writer.writerows(zip(*columns))


def save(fig,stem):
    fig.savefig(ROOT/'figures'/(stem+'.png'),dpi=180,bbox_inches='tight')
    fig.savefig(ROOT/'figures'/(stem+'.pdf'),bbox_inches='tight')
    plt.close(fig)


def make_figures():
    plt.rcParams.update({'font.size':10,'axes.grid':True,'grid.alpha':.22,
        'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
    outputs={};loaded={name:load(name) for name in CASES}
    for name,(data,D) in loaded.items():
        names=['x','z']+list(D)+['f_'+str(n) for n in data['species_names']]+[
            'Sigma_F','Pi_m_signed','Pi_r_signed','Pi_total_signed','Pi_gamma_signed','Pi_nu_signed']+[
            'absorbed_cumulative_J','escaped_cumulative_J','work_cumulative_J',
            'energy_residual_J','energy_denominator_J','energy_normalized_residual','GL8_GL16_normalized_difference']
        columns=[data['x'],data['z']]+list(D.values())+list(data['scaled_populations'].T)+list(data['signed_observables'].T)+[
            *data['ledger_GL16'].T,data['ledger_residual_J'],data['ledger_denominator_J'],
            data['ledger_normalized_residual'],data['ledger_GL_difference']]
        path=ROOT/'results'/(name+'_plot_source.csv');csv_write(path,names,columns)
        outputs[str(path.relative_to(ROOT))]=digest(path)
    nominal,Dn=loaded['thermal_split60'];ref_time=Dn['elapsed_Myr'];ref_z=nominal['z']
    fig,axes=plt.subplots(3,1,figsize=(11,10),sharex=True,layout='constrained')
    for name in LABELS:
        data,D=loaded[name];t=D['elapsed_Myr'];kw=dict(color=COLORS[name],linestyle=STYLES[name],lw=1.7,label=LABELS[name])
        axes[0].plot(t,D['T_K'],**kw)
        axes[1].plot(t,data['scaled_populations'][:,2],**kw)
        axes[2].plot(t,data['scaled_populations'][:,12],**kw)
    axes[0].set_yscale('log');axes[0].set_ylabel('Gas temperature T [K] (log scale)')
    axes[1].set_ylabel('H II charge fraction');axes[2].set_ylabel('He III charge fraction')
    axes[2].set_xlabel('Elapsed proper time from z=20 [Myr]')
    axes[0].legend(ncol=3,loc='upper right',fontsize=9)
    for ax in axes:ax.set_xlim(0,max(v[1]['elapsed_Myr'][-1] for v in loaded.values()))
    redshift_axis(axes[0],ref_time,ref_z)
    fig.suptitle('THERM01 · dynamic temperature and charge evolution\nFinite 5–60 eV / 5–40 eV source slices; conditional source-fit cooling',fontsize=13)
    save(fig,'01_temperature_ionization')
    fig,axes=plt.subplots(2,1,figsize=(11,8.5),sharex=True,layout='constrained')
    t=ref_time;ledger=nominal['ledger_GL16']/EV_J
    for key,label,color in [('epsilon_th_J','thermal','#d55e00'),('epsilon_ion_J','ionization potential','#0072b2'),('epsilon_total_J','stored total','#000000')]:
        axes[0].plot(t,positive(Dn[key]/EV_J),label=label,color=color)
    for j,label in enumerate(('cumulative absorption','cumulative escape','cumulative adiabatic work')):
        axes[0].plot(t,positive(ledger[:,j]),label=label,ls=('--','-.',':')[j],lw=1.5)
    axes[0].set_yscale('log');axes[0].set_ylabel('Energy [eV per baryon] (log scale)')
    axes[0].legend(ncol=2,fontsize=9,loc='lower right')
    for name in LABELS:
        data,D=loaded[name]
        axes[1].plot(D['elapsed_Myr'],positive(data['ledger_normalized_residual']),
                     color=COLORS[name],ls=STYLES[name],label=LABELS[name])
    axes[1].plot(t,positive(nominal['ledger_GL_difference']),color='black',ls=':',lw=1.4,label='split60 GL8–GL16')
    axes[1].axhline(3e-6,color='#b2182b',ls='--',lw=1,label='frozen 3×10⁻⁶ gate')
    axes[1].set_yscale('log');axes[1].set_ylabel('Normalized absolute ledger residual (log)')
    axes[1].set_xlabel('Elapsed proper time from z=20 [Myr]');axes[1].legend(ncol=3,fontsize=8,loc='lower right')
    for ax in axes:ax.set_xlim(0,max(v[1]['elapsed_Myr'][-1] for v in loaded.values()))
    redshift_axis(axes[0],ref_time,ref_z)
    fig.suptitle('THERM01 · independent dense-output energy ledger\nUpper: split60; lower: six finite cases. Exact zero values omitted on log axes.',fontsize=13)
    save(fig,'02_energy_ledger')
    fig,axes=plt.subplots(2,2,figsize=(12,9),layout='constrained')
    for ax,name in zip(axes[0],('thermal_split60','thermal_opposed60')):
        data,D=loaded[name];t=D['elapsed_Myr']
        for j,label,color,style in ((1,'collisionless massive matter','#d55e00','-'),(2,'photons + neutrinos','#0072b2','--'),(3,'signed sum','#000000','-')):
            ax.plot(t,data['signed_observables'][:,j],label=label,color=color,ls=style)
        ax.axhline(0,color='gray',lw=.6);ax.set_ylabel('Signed normalized anisotropic stress')
        ax.set_title(LABELS[name]);ax.legend(fontsize=8);ax.set_xlim(0,t[-1])
        redshift_axis(ax,t,data['z'],label='Redshift z')
    for name,label,color in [('thermal_split60_tight34','tight34 − nominal','#0072b2'),('thermal_split60_oracle63','full63 − nominal','#d55e00')]:
        data,D=loaded[name];dt=(D['T_K']-Dn['T_K'])/Dn['T_K']
        stress=data['signed_observables'][:,3]-nominal['signed_observables'][:,3]
        axes[1,0].plot(ref_time,dt,label=label,color=color)
        axes[1,1].plot(ref_time,stress,label=label,color=color)
        csv_write(ROOT/'results'/(name+'_difference_source.csv'),
            ['elapsed_Myr','z','signed_relative_T_difference','signed_Pi_total_difference'],[ref_time,ref_z,dt,stress])
    axes[1,0].set_ylabel('Signed relative temperature difference')
    axes[1,1].set_ylabel('Signed normalized total-stress difference')
    for ax in axes[1]:
        ax.axhline(0,color='gray',lw=.6);ax.set_yscale('symlog',linthresh=1e-12)
        ax.set_xlabel('Elapsed proper time from z=20 [Myr]');ax.set_xlim(0,ref_time[-1]);ax.legend(fontsize=8)
    axes[1,0].set_title('Finite representative check · symlog, linear below 10⁻¹²')
    axes[1,1].set_title('Finite representative check · symlog, linear below 10⁻¹²')
    fig.suptitle('THERM01 · signed stresses and finite validation differences\nPhysical HOLD; global convergence NOT_RUN; production NOT_APPROVED',fontsize=13)
    save(fig,'03_signed_stress_validation')
    for path in sorted((ROOT/'figures').glob('*')):
        if path.suffix in ('.png','.pdf'):outputs[str(path.relative_to(ROOT))]=digest(path)
    for path in sorted((ROOT/'results').glob('*difference_source.csv')):outputs[str(path.relative_to(ROOT))]=digest(path)
    (ROOT/'results/FIGURE_SOURCES.json').write_text(json.dumps(dict(outputs=outputs,
        inputs={name:json.loads((ROOT/'data'/name/'RESULT.json').read_text())['raw_sha256'] for name in CASES},
        notes=['All figures read saved trajectories; no integration for plotting.',
               'Companion redshift axes use split60 reference except labeled per-case stress panels.',
               'Log axes omit exact zero display values; raw CSVs retain every value.']),indent=2)+'\n')
    print('FIGURES: 3 PNG + 3 PDF; 10 CSV plot sources',flush=True)

if __name__=='__main__':make_figures()
