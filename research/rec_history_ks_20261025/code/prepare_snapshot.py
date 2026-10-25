"""Preparation only: byte snapshot, syntax compilation and pending budget."""
import argparse, py_compile
from pathlib import Path
from common import UNIT,defaults,files,identity,save

def main():
    p=argparse.ArgumentParser();t,h,q=defaults();p.add_argument('--thermo',type=Path,default=t);p.add_argument('--history',type=Path,default=h);p.add_argument('--query-map',type=Path,default=q);a=p.parse_args()
    for folder in ('code','tests'):
        for path in (UNIT/folder).glob('*.py'):py_compile.compile(str(path),doraise=True)
    manifest={name:identity(path) for name,path in files(a.thermo,a.history,a.query_map).items()}
    save(UNIT/'inputs/EXACT_IDENTITIES.json',{'schema':'REC_HISTORY_KS01_EXACT_BYTES_V1','files':manifest,'requested_model':'gpt-6.1-sol','observed_model':None,'scientific_execution':0,'canonical_thermo_snapshot':'adddf7381edfb7d670025c651cf813594107a260acce308702f33b1d415fad54'})
    save(UNIT/'BUDGET_LEDGER_PENDING.json',{'status':'PREPARED_NOT_RUN','primary':{'cpu_cap':45,'wall_cap':135,'large_rhs_cap':639,'small_rhs_cap':12},'reserved_repair':{'cpu_cap':5,'wall_cap':15,'authorized':False},'figures_scalar':{'cpu_cap':10,'wall_cap':30},'unit_total':{'cpu_cap':60,'wall_cap':180},'scientific_execution':0,'measured_scientific_cpu':0,'prior_known_lineage_cpu':24.120157,'older_unknown':'unknown','remote_cas_cpu':'unknown_separate','model_requested':'gpt-6.1-sol','model_observed':None})
    print('Prepared exact byte snapshot; no source build or solve executed.')
if __name__=='__main__':main()
