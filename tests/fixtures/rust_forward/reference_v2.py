"""Independent fixed-source oracle. Python standard library only.

Uses explicit component-index contractions, not Rust output or source imports.
Values/scales are reference calculations, NOT observations of the Rust library.
Scales are sums of absolute source terms; they are not interval certificates.
"""
from __future__ import annotations
import copy
import json
import math
from pathlib import Path

C = 299792458.0
H = 6.62607015e-34
KB = 1.380649e-23
EV = 1.602176634e-19
ME = 9.1093837139e-31
AG = 1.0 / (H*C)**3
XS_CONVERSION = 8.06728372576034e-22  # WU30: f/Ryd -> Mb -> m^2
D86 = [7.736,25.158,43.302,59.693,73.920,86.112,96.523,105.407,112.986,119.447,
       124.942,129.596,133.508,136.760,139.416,141.525,143.128,144.253,144.921,145.142]
EVENT = [[1,0,0,0,1],[0,1,0,-1,-1],[-1,-1,-1,0,0],[0,0,1,1,0],[0,0,1,1,0],[1,1,-1,-1,2]]
CONSTANT_NAMES = ['delta_s_ev','delta_p_ev','i_he_ev','epsilon_ir_ev','chi_p_ev','chi_s_ev','rydberg_ev']
SCHEMA = 'REC_HE_OBSERVABLES_V2'


def canonical():
    hc = H*C/EV
    ds,dp,ih = [x*100*hc for x in [166277.4403,171134.8970,198310.6691]]
    return dict(zip(CONSTANT_NAMES,[ds,dp,ih,dp-ds,ih-dp,ih-ds,13.6056931228436]))


def zmat(m):
    return [[complex(*z) for z in row] for row in m]


def zsum(xs):
    xs=list(xs)
    return complex(math.fsum(complex(x).real for x in xs),math.fsum(complex(x).imag for x in xs))


def entries(n,m,terms):
    out=[];gross=0.0
    for a in range(n):
        for b in range(m):
            ts=list(terms(a,b));z=zsum(ts)
            out.extend([z.real,z.imag])
            gross=max(gross,math.fsum(abs(x) for x in ts))
    return out,gross


def matrix(flat,n):
    return [[complex(flat[2*(i*n+j)],flat[2*(i*n+j)+1]) for j in range(n)] for i in range(n)]


def trace(flat,n):
    return math.fsum(flat[2*(i*n+i)] for i in range(n))


def record(id,status='ok',values=None,scales=None,tags=None):
    return {'id':id,'status':status,'values':values or {},'scales':scales or {},'tags':tags or {}}


def d86(y):
    # Interpolate the printed nodes directly in y; no production snap routine.
    y=min(y,1-y)
    for j in range(1,20):
        lo=j/40;hi=(j+1)/40
        if lo <= y <= hi:
            t=(y-lo)/(hi-lo)
            return (1-t)*D86[j-1]+t*D86[j]
    if math.isclose(y,.025,rel_tol=0.,abs_tol=2e-17):return D86[0]
    raise ValueError('reference outside D86 support')


def bb_node(channel,lower,wp,mode):
    w=zmat(wp);f=zmat(mode['f']);v=mode['v']
    h=[[complex(i==j)+f[i][j] for j in range(2)] for i in range(2)]
    a=1.7989e9 if channel=='He584' else 1.9746e6
    b=a*3/(8*math.pi);en=canonical()['delta_p_ev' if channel=='He584' else 'epsilon_ir_ev']*EV
    def atom(x,y):
        for i in range(2):
            for j in range(2):
                yield b*lower*v[x][i]*f[i][j]*v[y][j]
                for z in range(3):
                    yield -b*.5*v[x][i]*h[i][j]*v[z][j]*w[z][y]
                    yield -b*.5*w[x][z]*v[z][i]*h[i][j]*v[y][j]
    def photon(i,j):
        yield -b*lower*f[i][j]
        for k in range(2):
            for x in range(3):
                for y in range(3):
                    yield b*.5*h[i][k]*v[x][k]*w[x][y]*v[y][j]
                    yield b*.5*v[x][i]*w[x][y]*v[y][k]*h[k][j]
    ab,ga=entries(3,3,atom);j,gj=entries(2,2,photon);fac=AG*en*en
    return dict(atomic_b=ab,photon_j=j,occupation_c=[x/fac for x in j],event_rate=[trace(j,2)],energy_j=[en]),dict(atomic_b=ga,photon_j=gj,occupation_c=gj/fac,event_rate=2*gj,energy_j=en)


def bb(case):
    vals={'atomic_b':[0.]*18,'angular_j':[],'angular_c':[],'node_b':[],'event_rate':[0.], 'energy_j':[], 'weight_sum':[0.], 'projector_sum':[0.]*9}
    gs={k:0. for k in vals}
    for mode in case['modes']:
        v,g=bb_node(case['channel'],case['n_lower'],case['wp'],mode);w=mode['weight_sr']
        vals['atomic_b']=[a+w*b for a,b in zip(vals['atomic_b'],v['atomic_b'])]
        vals['node_b']+=v['atomic_b'];vals['angular_j']+=v['photon_j'];vals['angular_c']+=v['occupation_c']
        vals['event_rate'][0]+=w*v['event_rate'][0];vals['weight_sum'][0]+=w;vals['energy_j']=v['energy_j']
        gs['atomic_b']+=abs(w)*g['atomic_b'];gs['event_rate']+=abs(w)*g['event_rate'];gs['weight_sum']+=abs(w);gs['energy_j']=g['energy_j']
        for k,src in [('node_b','atomic_b'),('angular_j','photon_j'),('angular_c','occupation_c')]:gs[k]=max(gs[k],g[src])
        for a in range(3):
            for b in range(3):vals['projector_sum'][3*a+b]+=w*math.fsum(mode['v'][a][i]*mode['v'][b][i] for i in range(2))
    gs['projector_sum']=2*gs['weight_sum']
    if case['op']=='bb_jvp':
        hi=copy.deepcopy(case);lo=copy.deepcopy(case)
        hi.update(op='bb',n_lower=case['n_lower']+case['h']);lo.update(op='bb',n_lower=case['n_lower']-case['h'])
        a=bb(hi);b=bb(lo)
        for k in ['atomic_b','event_rate']:
            for name,row in [('plus',a),('minus',b)]:vals[name+'_'+k]=row['values'][k];gs[name+'_'+k]=row['scales'][k]
        fac=3*(1.7989e9 if case['channel']=='He584' else 1.9746e6)/(8*math.pi)
        def derivative(a,b):
            for m in case['modes']:
                f=zmat(m['f']);v=m['v']
                for i in range(2):
                    for j in range(2):yield fac*m['weight_sr']*v[a][i]*f[i][j]*v[b][j]
        d,gd=entries(3,3,derivative)
        vals['jvp_atomic_b']=d;gs['jvp_atomic_b']=gd
        vals['jvp_event_rate']=[-fac*math.fsum(m['weight_sr']*trace([t for row in m['f'] for z in row for t in z],2) for m in case['modes'])]
        gs['jvp_event_rate']=3*gd
    return record(case['id'],values=vals,scales=gs,tags={'spectral':'SharpLineDeltaPerJoule'})


def table(ch,gauge,q):
    # WU30 high-family printed rows. Separate L/V and s/d, no low-family splice.
    p={'Length':([.002114,.001486,.001134],[.003201,.001247,.0003970]),
       'Velocity':([.001935,.001380,.001075],[.002810,.001010,.0002663])}
    s={'Length':[.06737,.04812,.03526],'Velocity':[.06635,.04696,.03398]}
    def ip(x):
        a=0 if q<=1.2 else 1;t=(q-[1.,1.2][a])/.2
        return XS_CONVERSION*((1-t)*x[a]+t*x[a+1])
    return tuple(ip(x) for x in p[gauge]) if ch=='P' else (ip(s[gauge]),)


def bf(case):
    st=case['state'];con=st.get('constants',canonical());ch=case['channel'];en=case['energy_ev'];chi=con['chi_'+ch.lower()+'_ev']
    zero=en<chi
    if zero:
        ss=sd=sig=eta=0.
    else:
        q=(en-chi)/con['rydberg_ev']
        for node in [1.,1.2,1.4]:
            if en==chi+node*con['rydberg_ev']:q=node
        xs=table(ch,case['gauge'],q)
        sig=sum(xs);ss=xs[0];sd=xs[1] if ch=='P' else 0.
        phi=(ME*KB*st['temperature_k']/(2*math.pi*(H/(2*math.pi))**2))**1.5
        eta=st['n_he_plus']*st['ne']*math.exp(-(en-chi)*EV/(KB*st['temperature_k']))/(4*phi)
    f=zmat(st['f']);w=zmat(st['wp']);v=st['v'];h=[[complex(i==j)+f[i][j] for j in range(2)] for i in range(2)];phase=AG*(en*EV)**2
    if ch=='P':
        def te(a,b,c,d):return (3*ss-3*sd/5)*(a==c)*(b==d)+9*sd/10*((a==d)*(b==c)+(a==b)*(c==d))
        kw=[[zsum(v[a][i]*te(a,b,c,d)*w[d][c]*v[b][j] for a in range(3) for b in range(3) for c in range(3) for d in range(3)) for j in range(2)] for i in range(2)]
        kf=[[zsum(te(a,b,c,d)*v[c][i]*f[j][i]*v[d][j] for c in range(3) for d in range(3) for i in range(2) for j in range(2)) for b in range(3)] for a in range(3)]
        def cterms(i,j):
            yield C*3*eta*sig*h[i][j]
            for k in range(2):yield -C*.5*f[i][k]*kw[k][j];yield -C*.5*kw[i][k]*f[k][j]
        def bterms(a,b):
            for c in range(3):
                for d in range(3):
                    for i in range(2):
                        for j in range(2):yield C*phase*eta*te(a,b,c,d)*v[c][i]*h[j][i]*v[d][j]
            for k in range(3):yield -C*phase*.5*kf[a][k]*w[k][b];yield -C*phase*.5*w[a][k]*kf[k][b]
        cp,gc=entries(2,2,cterms);ab,gb=entries(3,3,bterms);av=ab;ag=gb
    else:
        def cterms(i,j):yield C*sig*eta*h[i][j];yield -C*sig*st['ns']*f[i][j]
        cp,gc=entries(2,2,cterms)
        at=[C*sig*phase*eta*2,C*sig*phase*eta*(f[0][0]+f[1][1]).real,-C*sig*phase*st['ns']*(f[0][0]+f[1][1]).real]
        av=[math.fsum(at)];ag=math.fsum(abs(x) for x in at)
    vout={'photon_c':cp,'atomic':av,'event_rate_density':[-phase*trace(cp,2)]}
    gout={'photon_c':gc,'atomic':ag,'event_rate_density':phase*2*gc}
    return record(case['id'],values=vout,scales=gout,tags={'coverage':'PhysicalZeroBelowThreshold' if zero else 'Represented','density_measure':'ContinuousPerJoulePerSteradian'})


def pair(case):
    p=case['input'];s=case['state'];ng,ns=s['ng'],s['ns']
    f1,f2=zmat(p['f1']),zmat(p['f2']);v1,v2=p['v1'],p['v2']
    t=[[math.fsum(v1[a][i]*v2[a][j] for a in range(3)) for j in range(2)] for i in range(2)]
    def calc(f,g,t):
        h=[[complex(i==j)+f[i][j] for j in range(2)] for i in range(2)];k=[[complex(i==j)+g[i][j] for j in range(2)] for i in range(2)]
        def terms(i,j):
            for a in range(2):
                for b in range(2):
                    for c in range(2):
                        yield ns/2*h[i][a]*t[a][b]*k[c][b]*t[j][c]
                        yield ns/2*t[i][b]*k[c][b]*t[a][c]*h[a][j]
                        yield -ng/2*f[i][a]*t[a][b]*g[c][b]*t[j][c]
                        yield -ng/2*t[i][b]*g[c][b]*t[a][c]*f[a][j]
        return entries(2,2,terms)
    m,gm=calc(f1,f2,t);n,gn=calc(f2,f1,[list(row) for row in zip(*t)])
    delta=s.get('constants',canonical())['delta_s_ev']*EV;e1=delta*p['y'];e2=delta*(1-p['y']);ww=d86(p['y']);mw=ww*3/(64*math.pi**2);aw=mw/2
    vals={'screen_overlap':[a for row in t for x in row for a in [x,0.]],'m12':m,'m21':n,'c1':[x*mw/(AG*e1*e1*delta) for x in m],'c2':[x*mw/(AG*e2*e2*delta) for x in n],
          'energy_j':[delta,e1,e2],'event_rate_density':[aw*trace(m,2)],'w':[ww],'weights':[aw,mw],'pair_factors':[.5,2.]}
    gs={'screen_overlap':2.,'m12':gm,'m21':gn,'c1':gm*mw/(AG*e1*e1*delta),'c2':gn*mw/(AG*e2*e2*delta),'energy_j':delta,'event_rate_density':2*gm*aw,'w':ww,'weights':mw,'pair_factors':2.}
    return record(case['id'],values=vals,scales=gs,tags={'density_measure':'PairDyDOmega1DOmega2','marginal_measure':'PartnerSolidAngleAtFixedMaterialEnergy'})


def bfgrid(case):
    s=case['state'];co=s.get('constants',canonical());vals={'rates':[0.,0.],'atomic_p':[0.]*18,'atomic_s':[0.],'photon_number':[0.],'photon_power_j':[0.],'photon_momentum':[0.]*3,'removed_power_j':[0.],'internal_power_j':[0.],'heat_power_j':[0.],'coverage_counts':[0.,0.]};gs={k:0. for k in vals}
    for node in case['nodes']:
        st=copy.deepcopy(s);st.update(f=node['f'],v=node['v']);r=bf(dict(node,id=case['id'],state=st));v,g=r['values'],r['scales'];idx=0 if node['channel']=='P' else 1
        w=node['weight_energy_j']*node['weight_omega_sr'];en=node['energy_ev']*EV;chi=co['chi_'+node['channel'].lower()+'_ev']*EV
        event=v['event_rate_density'][0]*w;eg=g['event_rate_density']*abs(w)
        vals['rates'][idx]+=event;gs['rates']+=eg
        name='atomic_p' if idx==0 else 'atomic_s';vals[name]=[a+w*b for a,b in zip(vals[name],v['atomic'])];gs[name]+=abs(w)*g['atomic']
        photon=AG*en*en*trace(v['photon_c'],2)*w;ngross=AG*en*en*2*g['photon_c']*abs(w)
        for k,x,scale in [('photon_number',photon,ngross),('photon_power_j',en*photon,en*ngross),('removed_power_j',en*event,en*eg),('internal_power_j',chi*event,chi*eg),('heat_power_j',(node['energy_ev']-co['chi_'+node['channel'].lower()+'_ev'])*EV*event,abs(en-chi)*eg)]:vals[k][0]+=x;gs[k]+=scale
        for j in range(3):vals['photon_momentum'][j]+=en/C*node['direction'][j]*photon
        gs['photon_momentum']+=en/C*ngross
        vals['coverage_counts'][1 if r['tags']['coverage']=='PhysicalZeroBelowThreshold' else 0]+=1
    gs['coverage_counts']=float(len(case['nodes']))
    return record(case['id'],values=vals,scales=gs)


def pairgrid(case):
    vals={'event_rate':[0.],'photon_number':[0.,0.],'photon_power_j':[0.,0.],'weight_sum':[0.],'node_count':[float(len(case['nodes']))]};gs={k:0. for k in vals};gs['node_count']=vals['node_count'][0]
    for node in case['nodes']:
        r=pair(dict(id=case['id'],state=case['state'],input=node['input']));v,g=r['values'],r['scales'];w=node['weight_dy']*node['weight_omega1_sr']*node['weight_omega2_sr'];delta=v['energy_j'][0]
        vals['event_rate'][0]+=w*v['event_rate_density'][0];gs['event_rate']+=abs(w)*g['event_rate_density'];vals['weight_sum'][0]+=w;gs['weight_sum']+=abs(w)
        for i in range(2):
            en=v['energy_j'][i+1];key='c'+str(i+1);n=AG*en*en*trace(v[key],2)*delta*w;ng=AG*en*en*2*g[key]*delta*abs(w)
            vals['photon_number'][i]+=n;vals['photon_power_j'][i]+=en*n;gs['photon_number']+=ng;gs['photon_power_j']+=en*ng
    return record(case['id'],values=vals,scales=gs,tags={'convention':'FullOrderedExchangeClosed'})


def ledger(case):
    co=canonical();r=case['rates'];es=[co['delta_p_ev'],co['epsilon_ir_ev'],co['chi_p_ev'],co['chi_s_ev'],co['delta_s_ev']]
    species=[math.fsum(a*b for a,b in zip(row,r)) for row in EVENT]
    internal=math.fsum(s*e*EV*q for s,e,q in zip([-1,-1,1,1,-1],es,r))
    photon=math.fsum(es[i]*EV*r[i] for i in [0,1,4])-case['bf_power_j']
    gross=math.fsum(abs(e*EV*q) for e,q in zip(es,r))+abs(case['bf_power_j'])+abs(case['heat_j'])
    return record(case['id'],values={'species_source':species,'internal_power_j':[internal],'photon_power_j':[photon],'heat_power_j':[case['heat_j']]},scales={'species_source':2*sum(abs(x) for x in r),'internal_power_j':gross,'photon_power_j':gross,'heat_power_j':abs(case['heat_j'])})


def selected(case):
    b=bfgrid(dict(id=case['id'],state=case['state'],nodes=case['bf']));v,g=b['values'],b['scales'];s=case['state']
    rates=[0.,0.,*v['rates'],0.];rg=[0.,0.,g['rates'],g['rates'],0.];ap=v['atomic_p'][:];asp=v['atomic_s'][0];apg=g['atomic_p'];asg=g['atomic_s'];n=v['photon_number'][0];pow=v['photon_power_j'][0];mom=v['photon_momentum'][:];ng=g['photon_number'];pg=g['photon_power_j'];mg=g['photon_momentum']
    for index,ch,nodes,lower in [(0,'He584',case['bb584'],s['ng']),(1,'IrPToS',case['ir'],s['ns'])]:
        for node in nodes:
            vv,gg=bb_node(ch,lower,s['wp'],node);w=node['weight_sr'];en=vv['energy_j'][0]
            rates[index]+=w*vv['event_rate'][0];rg[index]+=abs(w)*gg['event_rate'];ap=[a+w*z for a,z in zip(ap,vv['atomic_b'])];apg+=abs(w)*gg['atomic_b']
            if index==1:asp-=w*trace(vv['atomic_b'],3);asg+=abs(w)*3*gg['atomic_b']
            ph=AG*en*en*trace(vv['occupation_c'],2)*w;gr=AG*en*en*2*gg['occupation_c']*abs(w)
            n+=ph;pow+=en*ph;ng+=gr;pg+=en*gr;mg+=en/C*gr
            for j in range(3):mom[j]+=en/C*node['direction'][j]*ph
    if case['pairs']:
        pp=pairgrid(dict(id=case['id'],state=s,nodes=case['pairs']));rates[4]=pp['values']['event_rate'][0];rg[4]=pp['scales']['event_rate'];asp-=rates[4];asg+=rg[4]
        for node in case['pairs']:
            pp=pair(dict(id=case['id'],state=s,input=node['input']));pv,ps=pp['values'],pp['scales'];en=pv['energy_j'][1];w=node['weight_dy']*node['weight_omega1_sr']*node['weight_omega2_sr']*pv['energy_j'][0]
            ph=AG*en*en*trace(pv['c1'],2)*w;gr=AG*en*en*2*ps['c1']*abs(w)
            n+=ph;pow+=en*ph;ng+=gr;pg+=en*gr;mg+=en/C*gr
            for j in range(3):mom[j]+=en/C*node['direction1'][j]*ph
    le=ledger(dict(id=case['id'],rates=rates,bf_power_j=v['removed_power_j'][0],heat_j=v['heat_power_j'][0]))
    q=[pow/C,*mom]
    vals={'rates':rates,'species_source':le['values']['species_source'],'atomic_p':ap,'atomic_s':[asp],'photon_number':[n],'photon_power_j':[pow],'internal_power_j':le['values']['internal_power_j'],'heat_power_j':v['heat_power_j'],'q_photon':q,'q_matter':[-x for x in q]}
    co=canonical();ig=sum(rg[i]*co[k]*EV for i,k in enumerate(['delta_p_ev','epsilon_ir_ev','chi_p_ev','chi_s_ev','delta_s_ev']))
    gs={'rates':sum(rg),'species_source':2*sum(rg),'atomic_p':apg,'atomic_s':asg,'photon_number':ng,'photon_power_j':pg,'internal_power_j':ig,'heat_power_j':g['heat_power_j'],'q_photon':max(pg/C,mg),'q_matter':max(pg/C,mg)}
    return record(case['id'],values=vals,scales=gs,tags={'frame':'material_tetrad','metric':'-+++','pair_tag_policy':'first_full_tag_only'})


def evaluate(case):
    if 'expected_error' in case:return record(case['id'],status=case['expected_error'])
    op=case['op']
    if op=='domain':
        d=case['source_case'];st=d['expected_domain']
        if st not in ['ACCEPTED_NUMERICAL_GUARD','Represented','PhysicalZeroBelowThreshold']:return record(case['id'],status=st)
        if d['kind']=='energy':return record(case['id'],tags={'coverage':st})
        if d['kind']=='width_ev':
            val=d['value']*EV;return record(case['id'],values={'width_j':[val]},scales={'width_j':abs(val)})
        return record(case['id'])
    if op=='d86':
        w=d86(case['y']);return record(case['id'],values={'w':[w]},scales={'w':abs(w)})
    return {'bb':bb,'bb_jvp':bb,'bf':bf,'pair':pair,'bfgrid':bfgrid,'pairgrid':pairgrid,'ledger':ledger,'selected':selected}[op](case)


def build(inputs):
    return {'schema':SCHEMA,'meaning':'REFERENCE_CALCULATION_NOT_RUST_OUTPUT','records':[evaluate(c) for c in inputs['cases']]}


if __name__=='__main__':
    import sys
    if len(sys.argv)!=3:raise SystemExit('Usage: reference_v2.py INPUT_JSON OUTPUT_JSON (never Rust output)')
    obj=build(json.loads(Path(sys.argv[1]).read_text()))
    Path(sys.argv[2]).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
