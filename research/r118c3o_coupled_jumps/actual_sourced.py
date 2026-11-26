"""Directional Ly-alpha QSS using actual accepted angular incoming history, not mean bath."""
import json,sys,numpy as np,hashlib
from pathlib import Path
from dataclasses import replace
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3g_causal_shared_gas'))
sys.path.insert(0,str(D.parent/'r118c3f_directional_history'))
sys.path.insert(0,str(D.parent/'r118c3j_integrated_history'))
from shared_gas import Clock,stf,B,P,R,_canonical_twophoton_table,OriginalHyRecPrimitiveRateTable,populate_original_full_atomic,KB_NATIVE_EV_K
from canonical_history import raymap,interpF,incoming_canonical,step
from line_cell import phase,A21,EL
from scipy.constants import k,m_p,c
from sourced_line import advance
LY=4.662899067555897e15
def run():
 path=D.parent/'r118c3g_causal_shared_gas/ACCEPTED_LOCAL_DIRECTIONAL.npz';v=np.load(path);orig=np.load(P);eta=-np.log1p(orig['z']);o=np.r_[orig['virtual_out'],orig['lyman_out']].T
 assert str(v['prefix_sha'])==hashlib.sha256(P.read_bytes()).hexdigest()
 g=np.genfromtxt(B/'plusfine.csv',names=True,delimiter=',');ge=np.log(g['a']);F=np.stack([g[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=1).reshape(-1,3,3)
 n=v['rays'];w=v['weights0'];Fref=v['reference_F'];tab=_canonical_twophoton_table(R)
 m=Clock(h=.6735837,omega_cb=.31242079216478097,omega_r_h2=4.1578740068818545e-5,omega_de_h2=.3119234221656212,omega_b_h2=.02242,y_he_mass=.245,tcmb0_K=2.7255,table=OriginalHyRecPrimitiveRateTable.from_archive(R))
 rows=[]
 for j in np.unique(np.linspace(0,len(v['eta'])-1,33).astype(int)):
  u=v['eta'][j];z=np.expm1(-u);Tr=m.tcmb0_K*(1+z);x=v['rows'][j+1,1];T=v['rows'][j+1,2];H=np.interp(u,ge,g['h'])*2.1842852410855023e-18;source=replace(m,H=H);_,nh=source.cosmology(z)
  he=np.r_[eta[:64],v['eta'][:j]];hist=np.concatenate([np.broadcast_to(o[:64,None,:],(64,len(n),314)),v['outgoing'][:j]])
  inc,delay=incoming_canonical(ge,F,u,Fref,n,tab.energy_eV,he,hist,Tr)
  nf,ww=raymap(interpF(ge,F,u),Fref,n,w);ww/=ww.sum();S=stf([np.interp(u,ge,g[f'S{i}']) for i in range(5)]);rates=1+np.einsum('ni,ij,nj->n',nf,S,nf)
  snap=populate_original_full_atomic(source,z=z,xHII=x,xe=x,Tm_K=T,incoming_virtual=ww@inc[:,:311],incoming_lyman=ww@inc[:,311:]);rr,oo,dd=step(snap,rates,inc,ww)
  x1=1-x;bol=np.exp(-EL/(KB_NATIVE_EV_K*Tr));pop=3*x1*bol+rr.real_departures[1];fin=1/np.expm1(EL/(KB_NATIVE_EV_K*Tr))+inc[:,311]
  dln=np.sqrt(2*k*T/(m_p*c*c));C=phase(nh,dln);kc=C*H*rates/dln
  num=rr.real_departures[1]*(1+fin)-3*x1*(1-bol)*inc[:,311]
  df=A21*num/(A21*(3*x1-pop)+kc);J=kc*df
  atom=A21*(num-(3*x1-pop)*df)
  native=LY*H/(nh*1e-6*x1)*rates*(rr.real_departures[1]-3*x1*inc[:,311])
  direct=float(abs(ww@(atom-J))/max(abs(ww@J),1e-300))
  # Native shared real-level equation gives the local net balance of all
  # other sources: the native line net rate must be replenished at the
  # stationary native population. This fixes only the net, not its Jacobian.
  # Two closures share that net: fixed pumping; relaxation with a positive
  # loss chosen as the non-Ly-alpha diagonal contribution when available.
  ks=H*rates/dln;nn0=C*ww*fin;X=x1+pop;duration=1/(ww@ks);dyn=[]
  jnative=float(ww@native)
  # Native line flux uses the stable departure form; net can be signed.
  loss0=max(0.,float(snap.Trr[1,1]-LY*H/(nh*1e-6*x1)))
  for tag,loss in [('net_only',max(0.,-jnative/pop)),('local_diagonal',max(loss0,-jnative/pop,0.))]:
   pump=jnative+loss*pop
   if pump<0 and abs(pump)<1e-12*max(abs(jnative),1e-300):pump=0.
   for ns in [16,32,64]:
    dp=0.;nn=nn0.copy();esc=inj=ext=0.;maxres=0.;scale=pop+nn0.sum()+duration*abs(jnative)
    for _ in range(ns):
     dp,nn,e,i,ee,rrr=advance(dp,nn,X,C,ww,ks,fin,duration/ns,pop,jnative,loss)
     esc+=e;inj+=i;ext+=ee;maxres=max(maxres,abs(rrr))
    # gross source/loss can cancel; keep external net as separate reservoir.
    dyn.append(dict(closure=tag,steps=ns,pump=float(pump),loss=float(loss),excited=float(pop+dp),photons=float(nn.sum()),net_escape=float(esc-inj),external_net=float(ext),relative_ledger=float(abs(dp+nn.sum()-nn0.sum()+esc-inj-ext)/scale),max_residual=float(maxres/scale)))
  assert max(q['relative_ledger'] for q in dyn)<1e-11
  assert min(fin)>=0 and min(fin+df)>=0 and direct<1e-5
  rows.append(dict(u=float(u),tau_min=float(min(A21*(3*x1-pop)/kc)),tau_max=float(max(A21*(3*x1-pop)/kc)),ratio=float((ww@J)/(ww@native)),atom_balance_rel=direct,actual_incoming_range=[float(fin.min()),float(fin.max())],native_outgoing_diff=float(np.max(abs(oo-v['outgoing'][j]))),dynamic=dyn))
 o=dict(rows=rows,source_sha=hashlib.sha256(path.read_bytes()).hexdigest(),scope='actual directional accepted incoming reconstructed from C3G native source history and common atom; time-integrated shared real line with actual directional incoming and native stationary non-line net; optional local diagonal closure, not full native feedback or exact off-diagonal response')
 (D/'LINE_SOURCED.json').write_text(json.dumps(o,indent=2)+'\n');print('ratio range',min(x['ratio'] for x in rows),max(x['ratio'] for x in rows),'balance',max(x['atom_balance_rel'] for x in rows),'outgoing diff',max(x['native_outgoing_diff'] for x in rows))
if __name__=='__main__':run()
