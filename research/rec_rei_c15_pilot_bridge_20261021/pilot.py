#!/usr/bin/env python3
"""Source-pinned warm C15 LRS Sigma/Pi pilot. No performance benchmark.

Donor physics is unmodified. Shared-node leases are cooperative, not exclusive
reservations against unrelated programs. An existing Codex PID is never a veto.
"""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import argparse, concurrent.futures as cf, csv, dataclasses, fcntl, functools
import hashlib, json, math, multiprocessing, platform, resource, signal, sys, time, zipfile
from pathlib import Path
ARCHIVE_SHA='a159546829ff963b354b2c8feaa5da8b5536363f870ce6a4d3a966746d9c06a4'
ROOT_NAME='REI_C15_EINSTEIN_SIGMA_PI_20261015'
SOURCE_COMMIT='f6a1c10aa6d3f7252a9e68a77c2c4b62c41e77f0'
GIB=1024**3
C=None
BASE=None
LEASES=None


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, value):
    data=json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n'
    with Path(path).open('x') as f:
        f.write(data);f.flush();os.fsync(f.fileno())


def norms(s, delta_p, h, kappa_t):
    if not all(math.isfinite(v) for v in (s,delta_p,h,kappa_t)) or h<=0 or kappa_t<=0:
        raise ValueError('INVALID_TENSOR_OR_CLOCK')
    sf=math.sqrt(6)*abs(s)/h;pf=math.sqrt(2/3)*kappa_t*abs(delta_p)/h**2
    return dict(Sigma_frobenius=sf,Pi_frobenius=pf,Sigma_half=sf/math.sqrt(2),
                Pi_half=pf/math.sqrt(2),signed_sigma_frobenius=math.copysign(sf,s),
                signed_pi_frobenius=math.copysign(pf,delta_p),
                alignment=(1 if s*delta_p>0 else -1 if s*delta_p<0 else 0))


def amplitude(signed_pi, h, kt, radiation_slope, bias):
    if not all(math.isfinite(v) for v in (signed_pi,h,kt,radiation_slope,bias)) or min(h,kt,radiation_slope)<=0:
        raise ValueError('INVALID_INITIAL_STRESS_MAP')
    aa=(signed_pi*h*h/(math.sqrt(2/3)*kt)-bias)/radiation_slope
    if not -1<=aa<=2:raise ValueError('POSITIVE_DISTRIBUTION_DOMAIN; no clipping')
    return aa


def grid_cases():
    return [dict(signed_sigma=s,signed_pi=p) for s in (-.002,-.001,0.,.001,.002)
            for p in (-.0004,-.0002,0.,.0002,.0004)]


def admit(allowed,quota,idle_target,total,available,per_worker,reserve,running):
    capacity=min(max(0,allowed-reserve),max(0,math.floor(quota)-reserve),idle_target,
                 max(0,int((available-max(256*1024**2,.15*total))//per_worker)))
    return max(0,capacity-running)


def ticks():
    return {int(x[0][3:]):[int(v) for v in x[1:9]] for line in Path('/proc/stat').read_text().splitlines()
            if (x:=line.split()) and x[0].startswith('cpu') and x[0][3:].isdigit()}


def observe(reserve):
    affinity=sorted(os.sched_getaffinity(0));a=ticks();time.sleep(.15);b=ticks()
    idle=[]
    for cpu in affinity:
        delta=[y-x for x,y in zip(a[cpu],b[cpu])];total=sum(delta)
        if total<=0 or (delta[3]+delta[4])/total>=.4:idle.append(cpu)
    mem={line.split(':')[0]:int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines()
         if line.startswith(('MemTotal:','MemAvailable:'))}
    total=mem['MemTotal'];available=mem['MemAvailable'];quota=float(len(affinity))
    cgline=next((x for x in Path('/proc/self/cgroup').read_text().splitlines() if x.startswith('0::')),None)
    if cgline is None:raise RuntimeError('CGROUP_V2_REQUIRED_FOR_THIS_RUNNER')
    mounts=[x.split(' - ') for x in Path('/proc/self/mountinfo').read_text().splitlines()]
    candidate=next(x[0].split() for x in mounts if x[1].split()[0]=='cgroup2')
    mount=Path(candidate[4]);root=Path(candidate[3]);relative=Path(cgline[3:]).relative_to(root)
    current=mount/relative;cg=[]
    while True:
        item={'path':str(current)}
        for name in ('cpu.max','memory.max','memory.current'):
            path=current/name
            if path.exists():item[name]=path.read_text().strip()
        if 'cpu.max' in item:
            limit,period=item['cpu.max'].split()
            if limit!='max':quota=min(quota,int(limit)/int(period))
        if item.get('memory.max','max')!='max':
            cap=int(item['memory.max']);usage=int(item['memory.current'])
            total=min(total,cap);available=min(available,max(0,cap-usage))
        cg.append(item)
        if current==mount:break
        current=current.parent
    return dict(affinity=affinity,idle=idle,quota=quota,total=total,available=available,
                cgroup=cg,reserve=reserve,scope='sampled headroom; not exclusive ownership')


def restore(archive, output):
    if sha(archive)!=ARCHIVE_SHA:raise ValueError('C15_ARCHIVE_IDENTITY_MISMATCH')
    dest=output/'donor';dest.mkdir()
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('BAD_DONOR_CRC')
        for item in z.infolist():
            if not (dest/item.filename).resolve().is_relative_to(dest.resolve()):raise ValueError('UNSAFE_PATH')
            if (item.external_attr>>16)&0o170000==0o120000:raise ValueError('SYMLINK_FORBIDDEN')
        z.extractall(dest)
    return dest/ROOT_NAME


def init_worker(root, leases, caches=True):
    global C,BASE,LEASES
    LEASES=Path(leases);LEASES.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(Path(root)/'research/rei_c15_sigma_pi_feedback_20261015'))
    import coupled
    C=coupled
    C.source_identity()
    if caches:
        # One immutable owner table and quadrature object per worker; no
        # coefficient approximation, geometry caching or state-array sharing.
        rates=C.c13.CaseARates
        @functools.lru_cache(maxsize=2)
        def rate_cache():return rates()
        C.c13.CaseARates=rate_cache
        grid=C.pr140.MassiveRadialGrid
        @functools.lru_cache(maxsize=4)
        def grid_cache(*args):
            g=grid(*args)
            for v in vars(g).values():
                if hasattr(v,'flags'):v.flags.writeable=False
            return g
        C.pr140.MassiveRadialGrid=grid_cache
    unit=C.EinsteinBoltzmann(C.Parameters(0.,0,0.,0.,.1,0.));st=unit.initial()
    f=unit._physical(0.,0.,0.,st.moments,unit.proxy,0.)
    BASE={'h':st.H,'radiation_slope':(f['E_gamma']+f['E_nu'])/5,
          'bias':f['Pi_total_source'],'kt':3*C.KAPPA}


def physics_case(case, steps):
    sf=abs(case['signed_sigma']);sh=sf/math.sqrt(2)
    if sf>=math.sqrt(6):raise ValueError('INITIAL_HAMILTONIAN_DOMAIN')
    h=BASE['h']/math.sqrt(1-sf*sf/6)
    aa=amplitude(case['signed_pi'],h,BASE['kt'],BASE['radiation_slope'],BASE['bias'])
    sign=1 if case['signed_sigma']>0 else -1 if case['signed_sigma']<0 else 0
    m=C.EinsteinBoltzmann(C.Parameters(sh,sign,aa,aa,.1,0.))
    initial=m.initial();fields=m._physical(0.,0.,initial.s/m.H0_ref,initial.moments,m.proxy,0.)
    initial_norm=norms(initial.s,fields['Pi_total_source'],initial.H,BASE['kt'])
    if abs(initial_norm['signed_pi_frobenius']-case['signed_pi'])>3e-16:
        raise ArithmeticError('INITIAL_PI_TARGET_MISMATCH')
    if abs(initial_norm['signed_sigma_frobenius']-case['signed_sigma'])>3e-16:
        raise ArithmeticError('INITIAL_SIGMA_TARGET_MISMATCH')
    result=m.run(nsteps=steps,compress=True,feedback=True)
    for row in result['history']:
        row.update(norms(row['s_inv_s'],row['Pi_total_source'],row['H'],BASE['kt']))
    result.update(case=case,initial_normalized=initial_norm,initial_A=aa,
                  norm='FROBENIUS_WITH_HALF_CONTRACTION_COLUMNS',
                  kappa_t=BASE['kt'],source_commit=SOURCE_COMMIT,
                  gate='EXPLORATORY_C15_WARM_LRS; NOT_FULL_EOR',performance_benchmark=False)
    return result


def worker(task):
    case,steps,directory,cpus=task
    path=Path(directory);before=time.process_time();wall=time.monotonic();lease=None
    original_affinity=os.sched_getaffinity(0);status='FAIL'
    try:
        for cpu in cpus:
            f=(LEASES/f'cpu{cpu}.lock').open('a+')
            try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);lease=f;os.sched_setaffinity(0,{cpu});break
            except BlockingIOError:f.close()
        if lease is None:return {'status':'DEFERRED_SHARED_LEASE','case':case}
        resource.setrlimit(resource.RLIMIT_AS,(min(2*GIB,resource.getrlimit(resource.RLIMIT_AS)[1])
                    if resource.getrlimit(resource.RLIMIT_AS)[1]!=-1 else 2*GIB,)*2)
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('CASE_WALL_LIMIT')))
        signal.alarm(45)
        result=physics_case(case,steps);status='PASS_SCOPED'
        write_new(path/'result.json',result)
        receipt={'status':status,'case':case,'cpu_id':next(iter(os.sched_getaffinity(0))),
                 'result_sha256':sha(path/'result.json'),'cpu_s_case':time.process_time()-before,
                 'wall_s_case':time.monotonic()-wall,'maxrss_kib_process_lifetime':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                 'resource_scope':'case starts after worker initialization; lifetime peak RSS; not aggregate peak',
                 'physics_gate':'EXPLORATORY_WARM_LRS_ONLY'}
    except Exception as e:
        receipt={'status':'FAIL','case':case,'error_type':type(e).__name__,'error':str(e)}
    finally:
        signal.alarm(0);os.sched_setaffinity(0,original_affinity)
        if lease is not None:lease.close()
    write_new(path/'receipt.json',receipt)
    return receipt


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--archive',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--max-workers',type=int,default=64);ap.add_argument('--reserve-cpus',type=int,default=2)
    ap.add_argument('--steps',type=int,choices=(16,32,64),default=16)
    ap.add_argument('--leases',type=Path,default=Path('/tmp/rei_shared_pilot_leases'))
    ap.add_argument('--run',action='store_true');a=ap.parse_args()
    if not 1<=a.max_workers<=64 or not 0<=a.reserve_cpus<=16:ap.error('invalid capacity')
    output=a.output.resolve();output.mkdir(parents=True,exist_ok=False)
    root=restore(a.archive,output);cases=grid_cases()
    inputs={str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()}
    manifest={'source_commit':SOURCE_COMMIT,'donor_archive_sha256':ARCHIVE_SHA,
              'adapter_sha256':sha(__file__),'cases':cases,'nsteps':a.steps,'inputs_sha256':inputs,
              'scope':'LRS subset; warm near z=4; external stellar reservoir; no full Q^a closure',
              'norm':'Frobenius; also report sqrt(half contraction)',
              'resource_contract':{'maximum_cases':25,'worker_AS_bytes':2*GIB,'per_case_wall_s':45,
               'campaign_wall_s':300,'memory_admission_bytes_per_worker':GIB,'reserve_memory_fraction':.15,
               'max_workers':a.max_workers,'reserve_cpus':a.reserve_cpus,'legacy_allocations_reused':False}}
    write_new(output/'MANIFEST.json',manifest)
    if not a.run:return
    started=time.monotonic();initial=observe(a.reserve_cpus)
    # Re-observe admission throughout this finite run; unrelated sessions do
    # not trigger a process-name veto. Leases bind only cooperating dispatchers.
    nmax=min(a.max_workers,len(cases),max(1,len(initial['affinity'])-a.reserve_cpus),max(1,math.floor(initial['quota'])-a.reserve_cpus))
    pending=list(enumerate(cases));active={};receipts=[];observations=[]
    with cf.ProcessPoolExecutor(max_workers=nmax,mp_context=multiprocessing.get_context('spawn'),
          initializer=init_worker,initargs=(str(root),str(a.leases))) as pool:
        while pending or active:
            for future in [f for f in active if f.done()]:
                index,case=active.pop(future)
                try:r=future.result()
                except Exception as e:r={'status':'FAIL_WORKER','case':case,'error':str(e)}
                if r['status']=='DEFERRED_SHARED_LEASE':pending.append((index,case))
                else:receipts.append(r)
            elapsed=time.monotonic()-started
            if elapsed>=250:
                break  # leave finite reserve for active jobs (45 s each, concurrent)
            obs=observe(a.reserve_cpus)
            observations.append({**obs,'elapsed_s':elapsed,'running':len(active)})
            free=admit(len(obs['affinity']),obs['quota'],len(obs['idle'])+len(active),obs['total'],obs['available'],GIB,a.reserve_cpus,len(active))
            for _ in range(min(free,nmax-len(active),len(pending))):
                index,case=pending.pop(0);d=output/f'case_{index:03d}';d.mkdir(exist_ok=True)
                future=pool.submit(worker,(case,a.steps,str(d),obs['idle'] or obs['affinity']))
                active[future]=(index,case)
        for future,(index,case) in active.items():
            try:receipts.append(future.result())
            except Exception as e:receipts.append({'status':'FAIL_WORKER','case':case,'error':str(e)})
    unchanged=all(sha(root/name)==value for name,value in inputs.items())
    own=resource.getrusage(resource.RUSAGE_SELF);child=resource.getrusage(resource.RUSAGE_CHILDREN)
    final={'status':'PASS_SCOPED' if len(receipts)==25 and all(r['status']=='PASS_SCOPED' for r in receipts) and unchanged else 'PARTIAL_OR_FAILED',
           'executed':len(receipts),'pending':len(pending),'receipts':receipts,'donor_unchanged':unchanged,
           'parent_and_reaped_children_cpu_s':own.ru_utime+own.ru_stime+child.ru_utime+child.ru_stime,
           'wall_s_from_post_restore':time.monotonic()-started,'max_pool_workers':nmax,
           'runtime':{'python':sys.version,'platform':platform.platform()},'observations':observations,
           'execution_hostname':platform.node(),'speedup':'NOT_MEASURED','scientific_admission':'PRELIMINARY_WARM_LRS_ONLY'}
    write_new(output/'CAMPAIGN.json',final)
    if final['status']!='PASS_SCOPED':raise SystemExit(2)

if __name__=='__main__':main()
