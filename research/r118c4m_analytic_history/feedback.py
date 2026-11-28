"""Actual C4L source replay with paired spectrum correction, depletion and Schur population response.
Baseline H/He emission histories stay prescribed. Both spectral source and sink are counted.
This is a conditional radiation feedback calculation, not a replacement HyRec solution."""
from pathlib import Path
D=Path(__file__).resolve().parent;K=D.parent/'r118c4l_directional_history'
src=(K/'instrumented_feedback.py').read_text()
helper=r'''
def paired_source(y,e,red,HH,hh,grid,N):
    a=1/(1+red);x=1-y;xe=x+e;Tr=cos.T0_K*(1+red);T=tm_steady_K(cos,xe,red,HH);t=KB_NATIVE_EV_K*Tr
    L=LAMBDA_2S1S_S_INV;upper=y*np.exp(-Eh/t)+HH*hh[0]/L
    fc=1/np.expm1((Eh-eh)/t);ft=1/np.expm1(eh/t)
    dc=stock_occupation(grid,N,Eh-eh,a);df=stock_occupation(grid,N,eh,a)
    assert np.all(fc+dc>=0) and np.all(ft+df>=0)
    stim=L*wh*upper*((1+fc)*df+(1+ft)*dc+dc*df)
    inv=L*wh*y*(fc*df+ft*dc+dc*df)
    g=stim-inv;G=float(g.sum())
    rt=source.table.evaluate(radiation_temperature_eV_rescaled=t,matter_to_radiation_temperature_ratio=T/Tr)
    bs,bp=rt.beta_s_inv;R=rt.R_2p2s_s_inv;ly=LYA_FACT_CM3*HH/(cos.nH0_m3*(1+red)**3*1e-6*y)
    A=np.array([[bs+L+3*R,-R],[-3*R,bp+ly+R]]);dx=np.linalg.solve(A,[-G,0.])
    pair=g+L*dx[0]*wh;lya=ly*dx[1];gas=(bs*dx[0]+bp*dx[1])/HH
    sp=deposit(grid,a*np.r_[eh,Eh-eh,Eh],np.r_[pair,pair,lya])/HH
    expectedN=(2*pair.sum()+lya)/HH;expectedQ=a*Eh*(pair.sum()+lya)/HH
    nerr=float(abs(sp.sum()-expectedN));qerr=float(abs(sp@grid-expectedQ));schur=float(abs((pair.sum()+lya)/HH+gas))
    assert nerr<1e-12*max(abs(expectedN),1e-40)+1e-30 and qerr<1e-12*max(abs(expectedQ),1e-40)+1e-30
    assert schur<1e-10*max(abs(gas),1e-50)+1e-30
    return sp,np.array([stim.sum()/HH,inv.sum()/HH,gas,expectedN,expectedQ,nerr,qerr,schur])
def depletion_step(y,e,red,HH,hh,grid,N,corr,dt):
    # Implicit backward-Euler correction at the same prescribed atomic stock.
    # Converge fixed-point iteration; do not clip negative occupations or stock.
    x=corr.copy()
    for it in range(60):
        rate,diag=paired_source(y,e,red,HH,hh,grid,N+x)
        nxt=corr+dt*rate
        error=float(np.linalg.norm(nxt-x,1));scale=max(float(np.linalg.norm(nxt-corr,1)),1e-30)
        x=nxt
        if error<=1e-10*scale+1e-19:break
    else:raise ValueError('depletion fixed point did not converge')
    rate,diag=paired_source(y,e,red,HH,hh,grid,N+x)
    res=float(np.linalg.norm(x-corr-dt*rate,1))
    # Comoving nodal occupation floor (same cell width as stock_occupation).
    edges=np.r_[grid[0]**2/np.sqrt(grid[0]*grid[1]),np.sqrt(grid[:-1]*grid[1:]),grid[-1]**2/np.sqrt(grid[-2]*grid[-1])]
    bb=grid**2*np.diff(edges)/(np.pi**2*HBARC**3*cos.nH0_m3)/np.expm1(grid/(KB_NATIVE_EV_K*cos.T0_K))
    margin=float(np.min((bb+N+x)/np.maximum(bb,1e-300)))
    return x,diag,it+1,res,margin
'''
a='rows=[];arrays={}'
assert src.count(a)==1;src=src.replace(a,helper+'\n'+a)
a='delta=np.zeros((3,2));';assert src.count(a)==1
src=src.replace(a,'corr=np.zeros_like(grid);corr_hist=[];pair_hist=[];depl_gas=[];deltad=np.zeros((3,2));dcap=1.5*KB_NATIVE_EV_K*(1+cos.fHe+1-stock[0]+stock[1]);dledger=np.zeros((3,6));delta=np.zeros((3,2));')
a='  delta,cap,bal=thermal_chem(y,e,red,HH,dt,Q,inv[6],delta,cap);'
assert src.count(a)==1
src=src.replace(a,'''  corr,dg,its,res,margin=depletion_step(y,e,red,HH,hh,grid,N+HN,corr,dt)
  deltad,dcap,dbal=thermal_chem(y,e,red,HH,dt,Q,dg[2],deltad,dcap);dledger+=dbal
  pair_hist.append(np.r_[dg,its,res,margin]);depl_gas.append(deltad.copy());corr_hist.append([corr.sum(),corr@grid,np.linalg.norm(corr,1)])
'''+a)
a=" arrays[f'linear_{n}']=dhist;";assert src.count(a)==1
src=src.replace(a,''' pair_hist=np.array(pair_hist);depl_gas=np.array(depl_gas);corr_hist=np.array(corr_hist)
 led=np.diff(u)@pair_hist[:,:5];nr=float(corr.sum()-led[3]);er=float(corr@grid-led[4])
 assert abs(nr)<1e-12 and abs(er)<1e-14
 row.update(depleted_source_integral=float(led[2]),undepleted_source_integral=row['inverse_effective_H_source_integral'],correction_photon_number=float(corr.sum()),correction_comoving_energy=float(corr@grid),pair_number_defect=nr,pair_energy_defect=er,max_pair_schur=float(max(pair_hist[:,7])),max_iteration=int(max(pair_hist[:,8])),max_fixed_point=float(max(pair_hist[:,9])),min_nodal_occupation_ratio=float(min(pair_hist[:,10])),depleted_max_x=float(max(abs(depl_gas[:,2,0]))),depleted_max_T=float(max(abs(depl_gas[:,2,1]))),depleted_terminal=depl_gas[-1,2].tolist())
 arrays[f'correction_{n}']=corr;arrays[f'pair_{n}']=pair_hist;arrays[f'depl_gas_{n}']=depl_gas;arrays[f'correction_history_{n}']=corr_hist
'''+a)
src=src.replace("'THERMAL_FEEDBACK.npz'","'DEPLETION.npz'").replace("'THERMAL_FEEDBACK.json'","'DEPLETION.json'")
src=src.replace("scope='C4K source replay plus prescribed-stock incremental two-photon forward/reverse detailed balance and Schur response, linearized HMLA gas/Compton temperature correction about prescribed steady thermal reference; no iterative spectral depletion, no excited-state line transfer or full non-linear thermochemistry'","scope='Prescribed original C4K H/He source replay with implicit signed spectral correction, both companion photons and Ly-alpha Schur-population response included; photon number/comoving-energy source ledger and linearized gas response. Nodal positivity diagnostic, no self-consistent nonlinear atomic populations, resonance transfer or feedback of correction on original HI continuum absorption.'")
p=D/'instrumented_depletion.py';p.write_text(src);compile(src,str(p),'exec');exec(compile(src,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
import numpy as np,json,hashlib
with np.load(K/'THERMAL_FEEDBACK.npz') as a,np.load(D/'DEPLETION.npz') as b:
 assert all(np.array_equal(a[x],b[x]) for x in a.files)
r=json.loads((D/'DEPLETION.json').read_text());r.update(C4L_replay_equal=True,source_sha=hashlib.sha256((K/'instrumented_feedback.py').read_bytes()).hexdigest());(D/'DEPLETION.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
