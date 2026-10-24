Clear[x, lam, del, q, tau, hh, ss, ux, dl, dd, dq, dt, dh, ds,
 w1, w2, a1, a2, a3, lo, hi];
xs=x Exp[lam-del];
din=hh+Exp[-xs]-Exp[-x];
tr=Exp[-tau/q];
out=tr din+(1-tr) ss;
direct=D[out,x] x ux+D[out,lam] dl+D[out,del] dd+
 D[out,q] dq+D[out,tau] dt+D[out,hh] dh+D[out,ss] ds;
ddin=dh+x Exp[-x] ux-xs Exp[-xs] (ux+dl-dd);
closed=tr ddin+(1-tr) ds+(ss-din) tr (dt/q-tau dq/q^2);
composite=Simplify[direct-closed];
ww={w1,w2,1-w1-w2}; aa={a1,a2,a3};
qm=ww.aa; variance=ww.(aa^2)-qm^2;
popoviciu=Expand[(hi-qm)(qm-lo)-variance-
 Sum[ww[[i]] (aa[[i]]-lo)(hi-aa[[i]]),{i,3}]];
<|"composite_Wien_boundary_differential"->composite,
  "variance_interval_identity"->popoviciu|>

