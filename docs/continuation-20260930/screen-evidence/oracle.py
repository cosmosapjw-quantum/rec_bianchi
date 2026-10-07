"""Independent Decimal closed spatial null-gauge formula, frozen 4096 eps.
No source import. Exact binary64 inputs; normalized absolute component residual.
"""
import decimal as de,json,math,random,subprocess,pathlib,sys
D=de.Decimal; de.getcontext().prec=100
ROOT=pathlib.Path(__file__).resolve().parent
TOL=4096*sys.float_info.epsilon
r=random.Random(20260930)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def unit(v):
 n=math.sqrt(dot(v,v));return [x/n for x in v]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def basis(e):
 j=min(range(3),key=lambda j:abs(e[j]));a=[float(i==j) for i in range(3)];u=unit(cross(e,a));v=cross(e,u);return [[u[i],v[i]] for i in range(3)]
def flattened(m):return [x for row in m for x in row]
rows=[]; refs=[]; scales=[]
for case in range(96):
 e=unit([r.uniform(-1,1) for _ in range(3)])
 beta=unit([r.uniform(-1,1) for _ in range(3)]);speed=[0.,.01,.3,.6,.8,.95][case%6];beta=[speed*x for x in beta]
 if case<3:e=[0.,0.,1.];beta=[0.,0.,[0.,.6,-.6][case]]
 n=basis(e);b=list(map(D,beta));ed=list(map(D,e));nd=[[D(x) for x in row] for row in n]
 g=1/(1-dot(b,b)).sqrt(); denom=1-dot(b,ed);dop=g*denom
 # Eq135 after analytic cancellation of the time component: independent of implementation's boost.
 carried=[[nd[i][j]+dot(b,[nd[k][j] for k in range(3)])/denom*(ed[i]-g/(g+1)*b[i]) for j in range(2)] for i in range(3)]
 angle=(case%11)*.231;c=math.cos(angle);s=math.sin(angle);orientation=-1 if case%7==0 else 1
 # Explicit independent component bases, including reflection.
 m=[[float(row[0]*D(c)+row[1]*D(s)),orientation*float(-row[0]*D(s)+row[1]*D(c))] for row in carried];md=[[D(x) for x in row] for row in m]
 overlap=[[sum(md[k][a]*carried[k][j] for k in range(3)) for j in range(2)] for a in range(2)]
 amp=[1.,1e-200,1e200][case%3]
 f=[amp*x for x in [2.,0.,.25,.4,.25,-.4,-1.,0.]]
 # Real congruence on a Hermitian indefinite collision matrix (not a PSD state).
 out=[]
 for a in range(2):
  for z in range(2):
   for part in range(2):out.append(sum(overlap[a][i]*D(f[4*i+2*j+part])*overlap[z][j] for i in range(2) for j in range(2)))
 back=[]
 for a in range(2):
  for z in range(2):
   for part in range(2):back.append(sum(overlap[i][a]*out[4*i+2*j+part]*overlap[j][z] for i in range(2) for j in range(2)))
 refs.append(flattened(carried)+flattened(overlap)+out+back+[dop*x for x in back]);scales.append([D(1)]*10+[D(amp)]*16+[D(amp)*max(D(1),dop)]*8)
 rows.append(beta+e+flattened(n)+flattened(m)+f)
text=''.join(' '.join(format(x,'.17g') for x in row)+'\n' for row in rows);(ROOT/'oracle-input.txt').write_text(text)
p=subprocess.run([str(ROOT/'probe')],input=text,text=True,capture_output=True);(ROOT/'oracle-stdout.txt').write_text(p.stdout);(ROOT/'oracle-stderr.txt').write_text(p.stderr);p.check_returncode();lines=p.stdout.splitlines();assert len(lines)==len(rows),(len(lines),len(rows))
maximum=D(0)
for i,(line,ref,scale) in enumerate(zip(lines,refs,scales)):
 assert not line.startswith('ERR'),(i,line)
 obs=list(map(D,line.split()));assert len(obs)==len(ref)==34
 for j,(x,y,s) in enumerate(zip(obs,ref,scale)):
  error=abs(x-y)/s;maximum=max(maximum,error);assert error<=D(TOL),(i,j,str(error),TOL)
res={'status':'PASS','cases':len(rows),'components':len(rows)*34,'tolerance':TOL,'max_scaled_residual':float(maximum),'oracle':'100-digit Decimal closed spatial null-gauge formula from exact binary64 inputs; scalar clock uses Doppler once','scales':'geometry absolute; matrices divided by declared input amplitude; clock by amplitude*max(1,D)','seed':20260930}
(ROOT/'oracle-result.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
