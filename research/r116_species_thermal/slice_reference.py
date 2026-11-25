"""Prepare same-owner solver slices and a pointwise independent C helium oracle."""
import csv,ctypes,hashlib,json,math,pathlib,subprocess,sys,tempfile
from bisect import bisect_left
p=pathlib.Path(sys.argv[1]).resolve()
root=pathlib.Path(__file__).resolve().parent
src=root.parent/'rec_h5_native_path_20261028/inputs/original/HyRec'
receipt=json.loads((p/'reference_receipt.json').read_text())
assert hashlib.sha256((p/'species_native.tsv').read_bytes()).hexdigest()==receipt['native_species_sha256']
f=receipt['fhe']; t0=2.7255
rows=list(csv.DictReader((p/'species_native.tsv').open(),delimiter='\t'))
eta=[float(r['eta']) for r in rows]
def at(q):
    i=bisect_left(eta,q)
    if i==0:return rows[0]
    a,b=rows[i-1:i+1];u=(q-eta[i-1])/(eta[i]-eta[i-1])
    return {k:float(a[k])+u*(float(b[k])-float(a[k])) for k in a if k!='phase'}|{'phase':a['phase'],'next_phase':b['phase']}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
slices=[]
for name,z0,z1,mode,n in [('helium',2800,1650,'native_hei',512),('hydrogen',1600,20,'neutral',2048),
    ('helium_overlap',1700,1655,'native_hei',128),('thermal',800,20,'neutral',1024),('h_window',1400,900,'neutral',512),('thermal_window',250,100,'neutral',256)]:
    start=math.log(8001/(1+z0)); dur=math.log((1+z0)/(1+z1))
    dst=p/(name+'.tsv')
    a=at(start);n0=a['n_h_m3']
    # exact source density normalization; interpolation of nH would slightly bias the anchor.
    n0=11.223846333047*.0224*(1-.2454)*(1+z0)**3
    with dst.open('x') as w:
        w.write('rec_species_reference_v1\nf_he %.17g\nhelium %s\neta x_hi x_heii x_heiii w_k n_h_m3 h_s tr_k\n'%(f,mode))
        for j in range(n+1):
            t=dur*j/n;q=at(start+t)
            assert q['phase'] not in ('HEIII_SAHA',) and q['next_phase'] not in ('HEIII_SAHA',)
            if mode=='neutral':assert q['xheii']==q['xheiii']==0.
            else:assert q['phase'] in ('HEI_H_SAHA','H_HEI') and q['next_phase'] in ('HEI_H_SAHA','H_HEI')
            xp=q['xp'];h2=q['xheii'];h3=q['xheiii'];w0=q['tm_k']*(1+f+xp+h2+2*h3)
            w.write(' '.join('%.17g'%v for v in (t,1-xp,h2,h3,w0,n0*math.exp(-3*t),q['h_s'],t0*(1+z0)*math.exp(-t)))+'\n')
    slices.append(dict(name=name,z0=z0,z1=z1,duration=dur,mode=mode,n=n+1,sha256=sha(dst)))
with tempfile.TemporaryDirectory() as td:
    so=pathlib.Path(td)/'he.so'
    subprocess.run(['gcc','-O2','-shared','-fPIC',str(src/'helium.c'),'-lm','-o',str(so)],check=True)
    dll=ctypes.CDLL(str(so));fun=dll.rec_helium_dxHeIIdlna
    fun.argtypes=[ctypes.c_double]*9;fun.restype=ctypes.c_double
    with (p/'HEI_C_FIXTURE.tsv').open('x') as w:
        w.write('x_hi x_heii f_he n_h_m3 h_s tr_k rate_s\n')
        for z in (3500,3000,2800,2500,2200,2000,1800,1700,1655):
            q=at(math.log(8001/(1+z)));hi=1-q['xp'];h2=q['xheii'];n=q['n_h_m3'];h=q['h_s'];t=t0*(1+z)
            # Independently exercise off-equilibrium perturbations at same conditions.
            for factor in (1.,0.9,1.000001):
                v=h2*factor
                assert v<f
                rate=fun(hi,v,n,t,f,h,0.,1.,1.)*h
                w.write(' '.join('%.17g'%x for x in (hi,v,f,n,h,t,rate))+'\n')
if (root/'HEI_C_FIXTURE.tsv').exists():
    assert (root/'HEI_C_FIXTURE.tsv').read_bytes()==(p/'HEI_C_FIXTURE.tsv').read_bytes()
# compare source stdout to earlier accepted REC integer-z history (rounded stdout)
prev=root.parent/'rec_r3o_grid_frontiers_20261019/reused_h_trace_001/producer_inputs/independent_integer_z_history.csv'
old=list(csv.DictReader(prev.open()))
base=[list(map(float,l.split())) for l in (p/'original_stdout.txt').read_text().splitlines()]
assert len(old)==len(base)==8001
diff=max(abs(float(a['xe'])-b[1]) for a,b in zip(old,base))
diff_tm=max(abs(float(a['Tm_K'])-b[2]*t0*(1+b[0])) for a,b in zip(old,base))
out=dict(slices=slices,c_oracle_rows=27,c_oracle_sha256=sha(p/'HEI_C_FIXTURE.tsv'),prior_integer_history_sha256=sha(prev),max_prior_xe_abs_diff=diff,max_prior_tm_abs_diff_k=diff_tm)
(p/'slice_receipt.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
