import rec,numpy as np,time,json
from moving import Moving
c=rec.context(128);z=np.load(rec.H/'goal_q3_128_-0.5.npz');he=z['he']
c.v=np.stack([np.interp(he,c.he,c.v[:,j]) for j in range(c.v.shape[1])],axis=1);c.he=he
m,mm,mp=[rec.Map(c,l) for l in [-.5,-.501,-.499]]
A=np.broadcast_to(np.zeros((1,1,314,7)),(len(he)-1,c.nr,314,7))
class Probe(Moving):
 def td(self,u,du):
  U=np.broadcast_to(u,(self.m.nr,313));f,df=self.evald('f',U,np.broadcast_to(du,U.shape));t,dt=self.evald('g',f-self.m.lr,df)
  bad=~(np.isfinite(t)&np.isfinite(dt))
  if bad.any():
   idx=np.argwhere(bad);i,j=idx[0]
   x=f[i,j]-self.m.lr[j]
   tm,tc,tp=[q.t(U)[i,j] for q in (self.mm,self.m,self.mp)]
   print('BAD',len(idx),'ray/channel',idx[0].tolist(),'u',U[i,j],'du',np.broadcast_to(du,U.shape)[i,j],'fixed_inverse_arg',x,'base_range',[self.m.g[i].x[0],self.m.g[i].x[-1]],'minus_range',[self.mm.g[i].x[0],self.mm.g[i].x[-1]],'plus_range',[self.mp.g[i].x[0],self.mp.g[i].x[-1]],'composed',[tm,tc,tp],flush=True)
   raise ValueError('found actual map boundary')
  return t,dt
p=Probe(m,mm,mp,1e-3);tm=time.monotonic()
for i in range(1665,len(he)):
 try:p.integrate(i,he[i-1],he[i],A,A)
 except ValueError as e:
  print('FAILED_STEP',i,'z',np.expm1(-he[i]),str(e),'seconds',time.monotonic()-tm,flush=True);break
 if i%16==0:print('probe',i,flush=True)
