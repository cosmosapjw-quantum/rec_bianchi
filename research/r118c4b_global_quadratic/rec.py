"""Exact reuse of C4A quadratic owner at nt128, independent conditional H/He donor audit."""
from pathlib import Path
import sys,json,numpy as np,hashlib,subprocess,gzip
D=Path(__file__).resolve().parent;P=D.parent;A=P/'r118c4a_quadratic_pair'
# Reuse byte-identical source; functions resolve all new output paths to C4B.
ns={'__file__':str(D/'rec.py'),'__name__':'c4b_quad'}
exec(compile((A/'rec.py').read_text(),str(A/'rec.py'),'exec'),ns)
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def donor():
 from scipy.constants import k,electron_volt,c
 p=P/'rec_r3c_rei_bridge_20261015';j=json.loads((p/'REI_DONOR_CANDIDATE_OPTIN_ONLY.json').read_text());csv=p/'HYREC_FLRW_Z20_TO_1600.csv'
 raw=np.genfromtxt(csv,names=True,delimiter=',');print('donor fields',raw.dtype.names,flush=True)
 # actual CSV and opt-in packet; conditional initial gas only
 f=float(j['source_conversion']['fHe_REI']);source_f=float(j['source_conversion']['fHe_source'])
 chi=np.array([13.598434599702,24.587389011,54.41776]);kb=k/electron_volt
 cases={'original_REI':j['original_REI_gas_initial'],'full_HHe_candidate':j['candidate_initial_gas'],'HMLA_used_C3X':dict(Tgas_K=9.304371943681256,x_HII=.00021014665671400957,x_HeII=0.,x_HeIII=0.)}
 rows={}
 for name,a in cases.items():
  x,y,z,T=[a[n] for n in ['x_HII','x_HeII','x_HeIII','Tgas_K']];xe=x+f*(y+2*z);w=1.5*kb*T*(1+f+xe);b=chi[0]*x+f*(chi[1]*y+(chi[1]+chi[2])*z)
  rows[name]=dict(xe=xe,T=T,thermal_eV_H=w,binding_eV_H=b,gas_energy_eV_H=w+b,charge_res=xe-f*(y+2*z)-x)
 ref=rows['HMLA_used_C3X'];delta={}
 for n,r in rows.items():delta[n]=dict(opacity_relative=r['xe']/ref['xe']-1,thermal_relative=r['thermal_eV_H']/ref['thermal_eV_H']-1,binding_relative=r['binding_eV_H']/ref['binding_eV_H']-1,energy_difference=r['gas_energy_eV_H']-ref['gas_energy_eV_H'])
 # Compare exact z=20 row against packet, not infer absent species.
 zname=next((n for n in raw.dtype.names if n.lower() in ['z','zbar','redshift']),None);assert zname is not None
 idx=int(np.argmin(abs(raw[zname]-20.)));row={n:float(raw[n][idx]) for n in raw.dtype.names};assert abs(row[zname]-20)<1e-8
 actual={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in ['HYREC_FLRW_Z20_TO_1600.csv','REI_DONOR_CANDIDATE_OPTIN_ONLY.json','SOURCE_EXECUTION_RECEIPT.json']}
 original=gzip.decompress((p/'HYREC_ORIGINAL_REI_MATCHED_STDOUT.gz').read_bytes());rawsha=hashlib.sha256(original).hexdigest()
 out=dict(physical_cases=rows,relative_to_HMLA=delta,native_REI_fHe=f,source_fHe=source_f,source_csv_z20=row,source_hashes=actual,original_stdout_sha256=rawsha,packet_stdout_hash_matches=rawsha==j['source_rec_full_C_stdout_sha256'],scope='conditional fixed REI density/clock composition translation, no activation, no HHe anisotropic history or physical energy exchange claim')
 write('DONOR_AUDIT.json',out);print(out,flush=True)
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='donor':donor()
 else:ns[mode](128,float(sys.argv[2]),1)

