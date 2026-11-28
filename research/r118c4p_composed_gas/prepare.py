"""Generate bounded native history driver from exact pinned C4N and scale C4O thermal derivative."""
from pathlib import Path
import hashlib
D=Path(__file__).resolve().parent;P=D.parent;N=P/'r118c4n_exact_spline_atomic';O=P/'r118c4o_thermal_atomic'
def change(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
s=(O/'study.py').read_text()
s=s[:s.index('def main():')]
s=change(s,'def jvp(c,s,a,w,I,T):','def jvp(c,s,a,w,I,T,scale=1.):')
s=change(s,'br=s.sr-3*L*x1*s.incoming_lyman[::-1]*k+3*L*x1*ly[::-1]*k','br=scale*(s.sr-3*L*x1*s.incoming_lyman[::-1]*k)+3*L*x1*ly[::-1]*k')
s=change(s,'rb=ds-drr@r-drv@v','rb=scale*ds-drr@r-drv@v')
s=change(s,'gas=(r@s.Beta_s_inv-np.sum','gas=(r@s.Beta_s_inv-scale*np.sum')
s=change(s,'dg=(dr@s.Beta_s_inv-ds.sum())','dg=(dr@s.Beta_s_inv-scale*ds.sum())')
(D/'thermal.py').write_text(s)
s=(N/'rec.py').read_text()
s=change(s,'from event import Events','sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"r118c4n_exact_spline_atomic"))\nfrom event import Events\nfrom atomic_x import jvp as xjvp\nfrom thermal import jvp as tjvp')
s=change(s,'N=len(he)-1;assert N==1773','N=128;assert len(he)==1774')
s=change(s,'for i,r in enumerate(he[1:],1):','for i,r in enumerate(he[1:N+1],1):')
a=s.index(' for k,ep in enumerate([1e-6,.01/3000]):');b=s.index(' df=[];dout=[];',a)
s=s[:a]+''' x,T=yy*np.array([1.,3000]);s,HH,Tr=c.snap(u,x,T,c.zero);a,w,da,dw=events.ang(u)
 # Same represented a,w as owner, not the derivative object's rounded variant.
 aa,ww=ang
 gx=[];gt=[];ox=[];ot=[];basegap=0.;res=0.
 for k in range(3):
  G,O,dG,dO=xjvp(s,aa,ww,wj[k],mass[k,j])
  H,Q,dH,dQ,rr,dp=tjvp(c,s,aa,ww,wj[k],T,mass[k,j])
  gx.append(dG);gt.append(dH*3000/T);ox.append(dO);ot.append(dQ*3000/T)
  basegap=max(basegap,float(np.linalg.norm(O-o[k])/max(np.linalg.norm(o[k]),1e-300)),float(np.linalg.norm(Q-o[k])/max(np.linalg.norm(o[k]),1e-300)))
  res=max(res,rr)
 gg=[gx[0],gt[0]];oo=[np.array(ox),np.array(ot)]
 gascheck=None
 # Independent source-rebuilt finite columns on exact selected endpoint stages.
 if j==2 and int(np.argmin(abs(c.he-u))) in [1,32,63,99,128]:
  errs=[]
  for k,ep in enumerate([1e-6,.01/3000]):
   dv=np.eye(2)[k]*ep;ap=owner(u,yy+dv,wj,j,*ang);am=owner(u,yy-dv,wj,j,*ang);gfd=(ap[0]-am[0])/(2*ep);ofd=(ap[1]-am[1])/(2*ep)
   errs.append(dict(column=k,gas_relative=float(abs(gfd-gg[k])/max(abs(gg[k]),1e-300)),outgoing_relative=float(np.linalg.norm(ofd-oo[k])/max(np.linalg.norm(oo[k]),1e-300))))
  gascheck=dict(u=float(u),errors=errs)
''' + s[b:]
s=change(s,'return f,o,gg,np.stack(oo,axis=-1),np.array(df),np.array(dout),nom,ng,check','return f,o,gg,np.stack(oo,axis=-1),np.array(df),np.array(dout),nom,ng,check,basegap,res,gascheck')
s=change(s,'atomic_gas_gap=0.','atomic_gas_gap=0.;gas_checks=[];gas_base_gap=0.;gas_matrix_res=0.')
s=change(s,'for f,o,gg,oo,gdf,gdo,nom,ng,ck in pool.map(stage_job,args):','for f,o,gg,oo,gdf,gdo,nom,ng,ck,bgap,rres,gcheck in pool.map(stage_job,args):\n    gas_base_gap=max(gas_base_gap,bgap);gas_matrix_res=max(gas_matrix_res,rres)\n    if gcheck is not None:gas_checks.append(gcheck)')
s=change(s,'np.savez_compressed(tmp,u=he[:i+1],dy=np.array(dys),last=A[i-1],last_d=DA[:,i-1])','np.savez_compressed(tmp,u=he[:i+1],dy=np.array(dys),last=A[i-1],last_d=DA[:,i-1])') if False else s
a=s.index(" ex=z['limits']")
s=s[:a]+''' dy=np.array(dys);prior=P/'r118c4n_exact_spline_atomic'/'EXACT_HISTORY.npz';old=np.load(prior);assert np.array_equal(he[:N+1],old['u'][:N+1]);g=dy-old['dy'][:N+1]
 refs=[]
 for ep in [.003,.001,.0003]:
  for k,sg in enumerate([1,-1]):
   path=K/f'{"FD" if ep==.003 else "PREFIX_FD"}_{sg*ep:g}.npz';q=np.load(path);n=min(len(q['u']),N+1);assert np.array_equal(q['u'][:n],he[:n]);f=(q['y'][:n]-v[:n])/ep;err=f-dy[:n,k]
   refs.append(dict(eps=ep,direction=sg,steps=n-1,terminal=dy[n-1,k].tolist(),fd=f[-1].tolist(),max_gap=np.max(abs(err),axis=0).tolist(),source_sha=sha(path)))
 np.savez_compressed(D/'COMPOSED.npz',u=he[:N+1],y=v[:N+1],dy=dy,last=A[N-1],last_d=DA[:,N-1],limits=np.array(lims))
 out=dict(steps=N,seconds=time.monotonic()-t0,nominal_residual=resmax,min_positive=mi0,limiter_count=len(lims),gas_base_gap=gas_base_gap,gas_matrix_residual=gas_matrix_res,gas_checks=gas_checks,prior_direction_max_gap=np.max(abs(g),axis=0).tolist(),prior_direction_max=np.max(abs(old['dy'][:N+1]),axis=0).tolist(),terminal=dy[-1].tolist(),finite_refs=refs,prior_sha=sha(prior),baseline_sha=sha(ref),scope='128 actual steps of C4N event/retarded history, analytic abundance and temperature gas columns, fixed H, accepted baseline endpoints; not full 1773 steps or autonomous owner')
 write('COMPOSED.json',out);print(json.dumps(out),flush=True)
if __name__=='__main__':run()
'''
(D/'history.py').write_text(s)
print('generated',hashlib.sha256(s.encode()).hexdigest())
