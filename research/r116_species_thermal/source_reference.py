"""Instrument *only* output of the pinned original HyRec C history, verify stdout.
No modification of the archived source or its integration. SI, species per H."""
import hashlib,json,pathlib,subprocess,sys,tempfile,shutil,csv,math
HERE=pathlib.Path(__file__).resolve().parent
SRC=HERE.parent/'rec_h5_native_path_20261028/inputs/original/HyRec'
# Exact cosmology used by the earlier REC independent integer-z history.
INPUT='2.7255\n0.0224\n0.14309694000000003\n0\n0.31113726660800006\n-1 0\n0.2454\n3.03821934419124\n1.\n1.\n'
OUT=pathlib.Path(sys.argv[1]).resolve(); OUT.mkdir(parents=True,exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources={p.name:sha(p) for p in SRC.iterdir() if p.is_file()}
def build_run(w,name):
    argv=['gcc','-O2','-o',name,'hyrectools.c','helium.c','hydrogen.c','history.c','hyrec.c','-lm']
    subprocess.run(argv,cwd=w,check=True,capture_output=True)
    p=subprocess.run([str(w/name)],input=INPUT.encode(),cwd=w,capture_output=True,check=True)
    return p.stdout,p.stderr
with tempfile.TemporaryDirectory(prefix='r116_hyrec_') as td:
    w=pathlib.Path(td)/'HyRec';shutil.copytree(SRC,w)
    original,err=build_run(w,'original')
    p=w/'history.c';s=p.read_text();pos=s.index('void rec_build_history(')
    a,b=s[:pos],s[pos:]
    needle='   double **Dfminus_hist;'
    assert b.count(needle)==1
    b=b.replace(needle,needle+'\n   FILE *species_trace = fopen("species_native.tsv", "w");\n   if (!species_trace) exit(20);\n   fprintf(species_trace, "eta\\tz\\txp\\txheii\\txheiii\\ttm_k\\txe\\tn_h_m3\\th_s\\tphase\\n");')
    lines=b.splitlines();n=0
    # Every assignment to Tm_output[iz] or joint update ends at the correct
    # accepted native row; the last three loops have H-only ownership.
    out=[]
    for line in lines:
        out.append(line)
        if 'Tm_output[iz] =' in line:
            assert n<4, line
            phase=['HEIII_SAHA','HEI_H_SAHA','H_HEI','H_STEADY_TM'][n]
            exp=[('1.','param->fHe-Delta_xe','Delta_xe'),('(1.-xH1s)','xHeII','0.'),('(1.-xH1s)','xHeII','0.'),('xe_output[iz]','0.','0.')][n]
            out.append('      fprintf(species_trace, "%.17g\\t%.17g\\t%.17g\\t%.17g\\t%.17g\\t%.17g\\t%.17g\\t%.17g\\t%.17g\\t%s\\n", DLNA*iz,z,'+','.join(exp)+',Tm_output[iz],xe_output[iz],param->nH0*cube(1.+z),rec_HubbleConstant(param,z),"'+phase+'");')
            n+=1
        # Both H+Tm loops assign z immediately after joint update, rather
        # than assigning Tm_output[iz] explicitly.
        elif n>=4 and 'z = (1.+ZSTART)*exp(-DLNA*iz) - 1.;' in line:
            phase='H_TM' if n==4 else 'H_TM_PEEBLES'
            out.append('      fprintf(species_trace, "%.17g\\t%.17g\\t%.17g\\t%.17g\\t%.17g\\t%.17g\\t%.17g\\t%.17g\\t%.17g\\t%s\\n", DLNA*iz,z,xe_output[iz],0.,0.,Tm_output[iz],xe_output[iz],param->nH0*cube(1.+z),rec_HubbleConstant(param,z),"'+phase+'");')
            n+=1
    assert n==6,n
    b='\n'.join(out)+'\n'
    b=b.replace('   free_2D_array(Dfminus_hist, NVIRT);','   fclose(species_trace);\n   free_2D_array(Dfminus_hist, NVIRT);')
    p.write_text(a+b)
    patched,err2=build_run(w,'instrumented')
    assert original==patched,'instrumentation changed original output'
    shutil.copy(w/'species_native.tsv',OUT/'species_native.tsv')
    (OUT/'original_stdout.txt').write_bytes(original)
    (OUT/'instrumented_history.c').write_bytes(p.read_bytes())
rows=list(csv.DictReader((OUT/'species_native.tsv').open(),delimiter='\t'))
fhe=.2454/((1-.2454)*3.97153)
assert len(rows)>100000
phases={}
max_charge=0.
for i,r in enumerate(rows):
    eta,z,xp,h2,h3,tm,xe,nh,h=[float(r[k]) for k in ['eta','z','xp','xheii','xheiii','tm_k','xe','n_h_m3','h_s']]
    assert all(map(math.isfinite,[eta,z,xp,h2,h3,tm,xe,nh,h]))
    assert abs(eta-i*8.49e-5)<1e-13 and 0<=xp<=1 and min(h2,h3)>=0 and h2+h3<=fhe+1e-15 and min(tm,nh,h)>0
    max_charge=max(max_charge,abs(xe-xp-h2-2*h3))
    q=phases.setdefault(r['phase'],{'n':0,'z_first':z,'z_last':z});q['n']+=1;q['z_last']=z
assert max_charge<1e-14
meta=dict(source_sha256=sources,input=INPUT,fhe=fhe,rows=len(rows),max_charge_error=max_charge,phases=phases,original_stdout_sha256=sha(OUT/'original_stdout.txt'),instrumented_history_sha256=sha(OUT/'instrumented_history.c'),native_species_sha256=sha(OUT/'species_native.tsv'),instrumented_stdout_byte_equal=True,compiler=subprocess.check_output(['gcc','--version'],text=True).splitlines()[0])
(OUT/'reference_receipt.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(meta,indent=2))
