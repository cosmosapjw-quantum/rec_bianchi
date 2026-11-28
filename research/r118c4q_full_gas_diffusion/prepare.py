from pathlib import Path
import hashlib
D=Path(__file__).resolve().parent;P=D.parent;prev=P/'r118c4p_composed_gas'
def ch(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
s=(prev/'history.py').read_text()
s=ch(s,'N=128;assert len(he)==1774','N=1773;assert len(he)==1774')
s=ch(s,'in [1,32,63,99,128]:','in [1,32,63,99,128,512,918,919,974,1773]:')
# Preserve native temperature domain for late snapshots; explicitly inward if needed.
s=ch(s,'dv=np.eye(2)[k]*ep;ap=owner(u,yy+dv,wj,j,*ang);am=owner(u,yy-dv,wj,j,*ang);gfd=(ap[0]-am[0])/(2*ep);ofd=(ap[1]-am[1])/(2*ep)','''dv=np.eye(2)[k]*ep;am=owner(u,yy-dv,wj,j,*ang)
   if k==1 and (yy[1]+ep)*3000>Tr:
    am2=owner(u,yy-2*dv,wj,j,*ang);gfd=(3*f-4*am[0]+am2[0])/(2*ep);ofd=(3*o-4*am[1]+am2[1])/(2*ep)
   else:
    ap=owner(u,yy+dv,wj,j,*ang);gfd=(ap[0]-am[0])/(2*ep);ofd=(ap[1]-am[1])/(2*ep)''')
s=ch(s,'out=dict(steps=N,seconds=','out=dict(active=active,event_checks=checks,atomic_checks=atomic_checks,atomic_base_gap=atomic_base_gap,atomic_gas_gap=atomic_gas_gap,events=events.events,aligned=len(events.aligned),steps=N,seconds=')
s=ch(s,"scope='128 actual steps of C4N event/retarded history, analytic abundance and temperature gas columns, fixed H, accepted baseline endpoints; not full 1773 steps or autonomous owner'","scope='1773 actual steps of C4N event/retarded history, analytic abundance and temperature gas columns, fixed H and accepted baseline endpoints; not autonomous owner'")
s=ch(s,"refs=[]\n for ep","assert np.array_equal(np.array(lims)[:,:3],old['limits'][:,:3]),(len(lims),len(old['limits']))\n refs=[]\n for ep")
(D/'history.py').write_text(s)
(D/'thermal.py').write_bytes((prev/'thermal.py').read_bytes())
print('history_sha',hashlib.sha256(s.encode()).hexdigest())
