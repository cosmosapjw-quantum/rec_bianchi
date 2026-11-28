"""Replay C4K fresh HeI feedback, add conditional two-photon detailed-balance response and thermal ledger."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;K=D.parent/'r118c4k_lambda_tangent';src=(K/'feedback.py').read_text()
# Preserve all original photon/gas evolutions and add diagnostics/linearized postprocessing.
helper=r'''
from scipy.constants import hbar, e as qe
HBARC=hbar*clight/qe
def stock_occupation(grid,N,energies,a):
    # Convert nodal number/H to a piecewise-interpolated number density in comoving energy.
    # Cell edges are geometric means; number and comoving energies are in eV.
    edges=np.r_[grid[0]**2/np.sqrt(grid[0]*grid[1]),np.sqrt(grid[:-1]*grid[1:]),grid[-1]**2/np.sqrt(grid[-2]*grid[-1])]
    occ=np.pi**2*HBARC**3*cos.nH0_m3*N/(grid**2*np.diff(edges))
    return np.interp(a*energies,grid,occ,left=0.,right=0.)
def inverse_source(y,e,red,HH,hh,grid,HeN,HN):
    a=1/(1+red);x=1-y;xe=x+e;Tr=cos.T0_K*(1+red);T=tm_steady_K(cos,xe,red,HH);t=KB_NATIVE_EV_K*Tr
    L=LAMBDA_2S1S_S_INV;upper=y*np.exp(-Eh/t)+HH*hh[0]/L
    assert upper>=0
    fc=1/np.expm1((Eh-eh)/t);ft=1/np.expm1(eh/t)
    rates=L*wh
    def action(N):
        dc=stock_occupation(grid,N,Eh-eh,a);dt=stock_occupation(grid,N,eh,a)
        assert np.all(fc+dc>=0) and np.all(ft+dt>=0)
        stim=rates*upper*((1+fc)*dt+(1+ft)*dc+dc*dt)
        inv=rates*y*(fc*dt+ft*dc+dc*dt)
        # incremental emission events, relative to exact same frozen-population Planck bath
        return float(stim.sum()),float(inv.sum()),max(float(np.max(abs(dc)/fc)),float(np.max(abs(dt)/ft)))
    sh,ih,rh=action(HN);se,ie,re=action(HeN);sb,ib,rb=action(HN+HeN);G=sb-ib
    # Linear real-level response of the HMLA atom to the extra two-photon net action.
    rt=source.table.evaluate(radiation_temperature_eV_rescaled=t,matter_to_radiation_temperature_ratio=T/Tr)
    bs,bp=rt.beta_s_inv;R=rt.R_2p2s_s_inv;ly=LYA_FACT_CM3*HH/(cos.nH0_m3*(1+red)**3*1e-6*y)
    A=np.array([[bs+L+3*R,-R],[-3*R,bp+ly+R]])
    dx=np.linalg.solve(A,[-G,0.])
    g=(bs*dx[0]+bp*dx[1])/HH
    check=abs(g+(G+L*dx[0]+ly*dx[1])/HH)
    assert check<1e-10*max(abs(g),1e-50)+1e-30
    # Independent detailed-balance test with Planck and Boltzmann populations.
    eq=y*np.exp(-Eh/t);err=float(np.max(abs(eq*(1+fc)*(1+ft)-y*fc*ft))/max(np.max(y*fc*ft),1e-300))
    assert err<1e-12
    return np.array([sh,ih,se,ie,sb,ib,g,rb,err,check])
def thermal_chem(y,e,red,HH,h,Q,inv,old,Cprev):
    x=1-y;xe=x+e;Tr=cos.T0_K*(1+red);T=tm_steady_K(cos,xe,red,HH);cap=1.5*KB_NATIVE_EV_K*(1+cos.fHe+xe)
    gamma=cos.fsR**2/cos.meR**3*4.91466895548409e-22;sc=gamma*Tr**4/HH;B=sc*xe/(1+cos.fHe+xe);Bx=sc*(1+cos.fHe)/(1+cos.fHe+xe)**2
    fun=lambda x,T:source.hydrogen_rhs_ln_a(z=red,x_HII=x,x_e=x+e,Tm_K=T)
    ex=1e-6;et=.001
    fx=(fun(x+ex,T)-fun(x-ex,T))/(2*ex);ft=(fun(x,T+et)-fun(x,T-et))/(2*et)
    M=np.array([[fx,ft],[Bx*(Tr-T),-2-B]])
    rhs=np.array([[0.,Q/cap],[h*inv,0.],[h*inv,Q/cap]])
    out=np.linalg.solve(np.eye(2)-h*M,(old+rhs).T).T
    # exact discrete heat ledger in the conditional linear temperature equation.
    capwork=(cap-Cprev)*old[:,1];source_heat=rhs[:,1]*cap;mix=h*cap*Bx*(Tr-T)*out[:,0];ad=h*cap*2*out[:,1];com=h*cap*B*out[:,1]
    balance=cap*out[:,1]-Cprev*old[:,1]-capwork-source_heat-mix+ad+com
    assert np.max(abs(balance))<1e-18
    return out,cap,np.stack([source_heat,mix,ad,com,capwork,balance],axis=1)
'''
a='rows=[];arrays={}'
assert src.count(a)==1;src=src.replace(a,helper+'\n'+a)
a='em=absn=emK=absK=heat=0.;'
assert src.count(a)==1
src=src.replace(a,'delta=np.zeros((3,2));dhist=[delta.copy()];ledger=np.zeros((3,6));inv_hist=[];heat_hist=[];cap0=1.5*KB_NATIVE_EV_K*(1+cos.fHe+1-stock[0]+stock[1]);cap=cap0;'+a)
a='  hist.append(stock.copy());hb.append(base.copy())';assert src.count(a)==1
src=src.replace(a,'''  Q=float(L1@np.maximum(E1-thr,0)+L2@np.maximum(E2-thr,0))
  inv=inverse_source(y,e,red,HH,hh,grid,N,HN)
  delta,cap,bal=thermal_chem(y,e,red,HH,dt,Q,inv[6],delta,cap);ledger+=bal;dhist.append(delta.copy());inv_hist.append(inv);heat_hist.append(Q)
'''+a)
a=' rows.append(row);arrays[f';assert src.count(a)==1
src=src.replace(a,''' inv_hist=np.array(inv_hist);dhist=np.array(dhist);heats=np.array(heat_hist)
 assert abs(heats.sum()-heat)<1e-18 and np.max(abs(dhist[:,0]+dhist[:,1]-dhist[:,2]))<1e-10
 rr=np.expm1(-u[1:]);Hrate=np.array([cos.hubble_s(float(t)) for t in rr]);du=np.diff(u);integrals=(du/Hrate)@inv_hist[:,:6]
 row.update(incremental_two_photon_integrals=integrals.tolist(),inverse_effective_H_source_integral=float(du@inv_hist[:,6]),max_distortion_to_planck=float(max(inv_hist[:,7])),max_detailed_balance_defect=float(max(inv_hist[:,8])),max_schur_identity_defect=float(max(inv_hist[:,9])),linear_heat_only_max_x=float(max(abs(dhist[:,0,0]))),linear_heat_only_max_T_K=float(max(abs(dhist[:,0,1]))),linear_inverse_only_max_x=float(max(abs(dhist[:,1,0]))),linear_inverse_only_max_T_K=float(max(abs(dhist[:,1,1]))),linear_combined_max_x=float(max(abs(dhist[:,2,0]))),linear_combined_max_T_K=float(max(abs(dhist[:,2,1]))),terminal=dhist[-1].tolist(),heat_ledger=ledger.tolist(),energy_stock=(cap*delta[:,1]).tolist())
 arrays[f'linear_{n}']=dhist;arrays[f'inverse_{n}']=inv_hist;arrays[f'heat_{n}']=heats
 rows.append(row);arrays[f''')
src=src.replace("'FRESH_HEI.npz'","'THERMAL_FEEDBACK.npz'").replace("'FRESH_HEI.json'","'THERMAL_FEEDBACK.json'")
src=src.replace("scope='fresh HeI net 2s source from actual helium RHS split, H continuum absorption in HMLA-valid window and coupled H/He ionization; H 2s/Ly-alpha net emissivity from effective 2-level Schur solve and original spontaneous 2s shape diagnostic; no H excited-state feedback, thermal feedback or new He 2p double counting'","scope='C4K source replay plus prescribed-stock incremental two-photon forward/reverse detailed balance and Schur response, linearized HMLA gas/Compton temperature correction about prescribed steady thermal reference; no iterative spectral depletion, no excited-state line transfer or full non-linear thermochemistry'")
p=D/'instrumented_feedback.py';p.write_text(src);compile(src,str(p),'exec');exec(compile(src,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
# Verify unmodified original gas and spectral stocks bitwise, plus record actual source hash.
import numpy as np
with np.load(K/'FRESH_HEI.npz') as a,np.load(D/'THERMAL_FEEDBACK.npz') as b:
 assert all(np.array_equal(a[x],b[x]) for x in a.files)
r=json.loads((D/'THERMAL_FEEDBACK.json').read_text());r.update(C4K_replay_equal=True,source_sha=hashlib.sha256((K/'feedback.py').read_bytes()).hexdigest());(D/'THERMAL_FEEDBACK.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
