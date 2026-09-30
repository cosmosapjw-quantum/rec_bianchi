import decimal, json, pathlib, subprocess, sys
D=decimal.Decimal; decimal.getcontext().prec=100
root=pathlib.Path(__file__).parent
betas=[(0.,0.,0.),(.6,0.,0.),(-.6,0.,0.),(.3,-.4,.2),(.1,.2,-.7),(.9,0.,0.),(1e-160,0.,0.)]
base=[(1.,0.,0.,0.),(5.,2.,-1.,3.),(-5.,-2.,1.,-3.),(0.,1.,2.,-4.),(1.,.6,.8,0.)]
cases=[(b,tuple(s*x for x in q)) for b in betas for q in base for s in (1e-120,1.,1e120)]
wire=''.join(' '.join(repr(x) for x in (*b,*q))+'\n' for b,q in cases)
r=subprocess.run([str(root/'boost_probe')],input=wire,text=True,capture_output=True,check=True)
rows=r.stdout.splitlines(); assert len(rows)==len(cases)
worst=0.; tolerance=4096*sys.float_info.epsilon
for i,((b,q),row) in enumerate(zip(cases,rows)):
 b=list(map(D.from_float,b)); q=list(map(D.from_float,q)); b2=sum(x*x for x in b); g=1/(1-b2).sqrt(); dot=sum(x*y for x,y in zip(b,q[1:])); k=g*g/(g+1)
 expected=[g*(q[0]-dot)]+[q[j+1]+(k*dot-g*q[0])*b[j] for j in range(3)]
 actual=list(map(float,row.split())); assert len(actual)==8
 gross=max(abs(x) for x in q)*max(D(1),g*g)*D(8)
 for j,(a,e) in enumerate(zip(actual,expected+q)):
  err=float(abs(D.from_float(a)-e)/gross) if gross else abs(a)
  assert err <= tolerance,(i,j,a,str(e),err)
  worst=max(worst,err)
report={'status':'PASS','cases':len(cases),'components':len(cases)*8,'oracle':'100-digit Decimal from exact input binary64 values','scaling':'8*max_abs_input*max(1,gamma^2), no dimensional unit floor','tolerance':tolerance,'max_gross_scaled_difference':worst}
(root/'boost-decimal-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
