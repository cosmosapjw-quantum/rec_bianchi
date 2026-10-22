"""New THERM01 unit checks only. Never imports any old test/campaign wrapper."""
import json
import math
from pathlib import Path
import numpy as np
from thermal import (ROOT,ThermalAtomic,ThermalSystem,KB,EV_J,R_EXT,P_EXT,
                     restrict63,lift34,verify_donor)

def run_checks(output=None):
    evidence={'source_quadrature':'AMENDMENT_Q1 fixed GL4 within each unchanged threshold-split energy bin',
              'supersedes_failure':'evidence/UNIT_CHECKS_MIDPOINT_FAILURE.json'};gates={}
    manifest=verify_donor();evidence['immutable_donor_file_count']=len(manifest['files'])
    gates['immutable_donor']=len(manifest['files'])==57
    rejected=[]
    for emax in (60.0001,200.,float('nan')):
        try:ThermalAtomic(emax)
        except ValueError:rejected.append(True)
        else:rejected.append(False)
    gates['unsupported_source_rejection']=all(rejected)
    max_partition=0.;max_moment=0.
    for cutoff in (40.,60.):
        atom=ThermalAtomic(cutoff);fine=ThermalAtomic(cutoff,128)
        gates[f'core_exact_zero_{cutoff}']=bool(np.all(atom._core_W==0) and np.all(atom._li1s_photo_s==0))
        sigma,_=atom.photo_cross_sections(atom.photon_energy_eV)
        energy=atom.photon_energy_eV[None,:]*EV_J
        chi=atom.transition_energy_eV[:,None]*EV_J
        heat=energy-chi
        active=sigma>0
        max_partition=max(max_partition,float(np.max(abs((energy-chi-heat)[active])/np.broadcast_to(energy,sigma.shape)[active])))
        gates[f'nonnegative_event_heat_{cutoff}']=bool(np.all(heat[active]>=0))
        gain=atom.q[atom.photo_indices+1]-atom.q[atom.photo_indices]
        gates[f'unit_electron_yield_{cutoff}']=bool(np.all(gain==1))
        sub=np.maximum(0,atom.transition_energy_eV[atom.photo_indices]-1e-8)
        below,_=atom.photo_cross_sections(sub)
        gates[f'threshold_zeros_{cutoff}']=bool(np.all(below[atom.photo_indices,np.arange(len(sub))]==0))
        for name in ('_photo_s','_absorbed_W','_primary_W'):
            a=getattr(atom,name);b=getattr(fine,name);mask=(a!=0)|(b!=0)
            error=float(np.max(abs(a[mask]-b[mask])/np.maximum(abs(a[mask]),abs(b[mask]))))
            max_moment=max(max_moment,error)
        gates[f'GammaHI_normalization_{cutoff}']=abs(atom._photo_s[1]/1e-12-1)<5e-15 and abs(fine._photo_s[1]/1e-12-1)<5e-15
    evidence['max_event_energy_relative_error']=max_partition
    evidence['max_photon64_128_relative_error']=max_moment
    gates['event_partition']=max_partition<5e-14
    gates['photon64_128_moments']=max_moment<5e-3
    atom=ThermalAtomic();max_deriv=0.;underflow=0;worst={}
    mesh=np.geomspace(100.,1e6,121)
    for T in mesh:
        rates=atom.rates(T,0);betas=atom.moments(T,rates)
        # Endpoint derivatives can use algebraic extrapolation of fits solely
        # for derivative checking, without calling outside-domain rates/IVPs.
        def fit(t,kind):
            if kind=='rr':
                a,b,t0,t1,c,t2=atom._rr_parameters.T
                B=b+c*np.exp(-t2/t);u=np.sqrt(t/t0);v=np.sqrt(t/t1)
                out=np.zeros(21);out[atom.recombination_indices]=1e-6*a/(u*(1+u)**(1-B)*(1+v)**(1+B))
            else:
                out=np.zeros(21);out[atom._dr_indices]=1e-6*t**(-1.5)*np.sum(atom._dr_c*np.exp(-atom._dr_E/t),axis=1)
            return out
        for kind,beta in zip(('rr','dr'),betas):
            alpha=rates[kind+'_m3_s'];h=2e-6
            finite_beta=KB*T*(1.5*alpha+(fit(T*math.exp(h),kind)-fit(T*math.exp(-h),kind))/(2*h))
            mask=alpha>1e-280;underflow+=int(np.sum((alpha>0)&~mask))
            scales=np.maximum(abs(beta[mask]),KB*T*alpha[mask])
            errors=abs(beta[mask]-finite_beta[mask])/scales
            error=float(np.max(errors)) if errors.size else 0.
            if error>max_deriv:max_deriv=error;worst=dict(T_K=T,kind=kind)
            if not (np.isfinite(alpha).all() and np.isfinite(beta).all() and np.all(alpha>=0) and np.all(beta>=0)):
                raise AssertionError('nonfinite/negative summed source fit')
    evidence.update(max_derivative_moment_mixed_relative_error=max_deriv,
        derivative_worst=worst,underflow_excluded_positive_rates=underflow,fit_mesh_K=mesh.tolist(),
        derivative_log_step=2e-6,derivative_scale='max(abs(beta),kB*T*alpha); alpha>1e-280')
    gates['summed_fit_finite_nonnegative']=True;gates['fit_derivative_moment']=max_deriv<2e-5
    gates['RP_identity']=bool(np.array_equal(R_EXT@P_EXT,np.eye(34)))
    config=dict(Sigma_F=.15,matter_A=.6,radiation_A=.15,T0_K=1000.,Emax_eV=60.,uv_multiplier=1.)
    compact=ThermalSystem(config);full=ThermalSystem(config,True)
    parity=[];thermal_identity=[];local=[];off=[]
    for x,T,ion in ((0.,1000.,.01),(.8,5000.,.4),(1.4,15000.,.9)):
        y=full.y0.copy()
        for name,indices in atom.isotope_groups.items():
            if name in ('n','T'):continue
            y[40+np.array(indices)]=0
            y[40+indices[0]]=1-ion;y[40+indices[1]]=ion
        Y=y[40:61]*atom.scales;eta=float(Y.sum()+atom.q@Y);y[62]=1.5*eta*T
        a=compact.rhs(x,restrict63(y));b=full.rhs(x,y)
        parity.append(float(np.max(abs(lift34(a)-b)/np.maximum(1,abs(b)))))
        p=full.point(x,y);n=p[-2];H=p[-1]['H'];d=full.full_rhs_from_point(p)
        # Full derivative of eta includes nuclei as well as electron counts.
        etap=float(np.sum(n['dY_dt'])+atom.q@n['dY_dt'])/H
        Tprime=2*d[62]/(3*eta)-T*etap/eta
        direct=-2*T-T*float(atom.q@n['dY_dt'])/(eta*H)+2*(n['heat']-n['cooling'])/(3*eta*p[5]*KB*H)
        thermal_identity.append(abs(Tprime-direct)/max(1,abs(direct)))
        diag=full.diagnostics(x,y)
        local.append(abs(diag['local_ledger_W_baryon'])/max(diag['absorbed_W_baryon'],diag['escaped_W_baryon'],1e-100))
        n0=atom.thermal_evaluate(Y,T,0.,p[5])
        dion=float(atom.ionization_energy_J@n0['dY_dt'])
        off.append(abs(dion+(n0['escape']-n0['cooling'])/p[5])/max(n0['escape']/p[5],1e-100))
        M=atom.rates(T,1)['G0']+n['ne']*atom.rates(T,1)['Gne']
        offdiag=M.copy();np.fill_diagonal(offdiag,0)
        assert np.min(offdiag)>=0
        assert np.max(abs(M.sum(axis=0)))<1e-25
    evidence.update(rhs_parity_errors=parity,electron_heat_capacity_identity_errors=thermal_identity,
        local_ledger_errors=local,source_off_binding_escape_errors=off)
    gates.update(extended_RHS_parity=max(parity)<1e-12,
        electron_count_thermal_identity=max(thermal_identity)<1e-12,
        frozen_local_ledger=max(local)<1e-12,source_off_recombination_identity=max(off)<1e-12,
        generator_conservation=True)
    # Explicit zero-process frozen derivative, without integrating a ninth IVP.
    p=list(full.point(0,full.y0));p[6]=dict(p[6],dY_dt=np.zeros(21),heat=0.,cooling=0.)
    d=full.full_rhs_from_point(p);w=full.y0[62];T=p[3];eta=p[2]
    evidence['zero_process_wprime_plus_2w']=float(d[62]+2*w)
    evidence['zero_process_Tprime_plus_2T']=float(2*d[62]/(3*eta)+2*T)
    gates['zero_process_adiabatic']=d[62]==-2*w and abs(2*d[62]/(3*eta)+2*T)<1e-12
    evidence['gates']=gates;evidence['status']='PASS' if all(gates.values()) else 'FAIL'
    if output:
        output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(evidence,indent=2,allow_nan=False,default=lambda x:x.item())+'\n')
    return evidence

if __name__=='__main__':
    result=run_checks(ROOT/'evidence/UNIT_CHECKS.json')
    print(json.dumps({k:v for k,v in result.items() if k not in ('fit_mesh_K',)},indent=2,default=lambda x:x.item()))
    raise SystemExit(0 if result['status']=='PASS' else 1)
