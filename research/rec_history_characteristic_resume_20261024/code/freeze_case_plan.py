"""Serialize explicit finite cases; no adapter calls or scientific evaluation."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
geometries=[('FLRW',[.6,.8,0],[0,0,0]),('axis_x',[1,0,0],[.2,-.1,-.1]),('axis_z',[0,0,-1],[-.2,-.2,.4]),('zero_x',[0,.6,.8],[-.2,-.2,.4]),('LRS',[.36,.48,.8],[-.2,-.2,.4]),('triaxial',[.36,.48,.8],[.35,-.1,-.25]),('near_positive',[.6,0,.8],[-.999999,.399999,.6]),('negative_axis',[0,-1,0],[.25,-.5,.25])]
ratios=[0.,1e-10,.17,.6931471805599453,8.,1000.]
cases=[]
for name,n,b in geometries:
 for j,L in enumerate(ratios):cases.append({'id':f'root_{name}_{j}','group':'root','n':n,'b':b,'lam':L,'eta_t':1.3})
for i in range(12):
 kind=i%4;n=[.36,.48,.8];dn=[.48,-.36,0] if kind in [0,3] else [0,0,0];db=[.07,-.02,-.05] if kind in [1,3] else [0,0,0]
 cases.append({'id':f'tangent_{i:02}','group':'tangent','n':n,'b':[-.2,-.2,.4] if i<6 else [.35,-.1,-.25],'lam':.15+.11*i,'eta_t':1.3,'dn':dn,'db':db,'dlam':.13 if kind in [2,3] else 0.,'deta_t':.04,'fd_step':'1e-25'})
cases[48].update(n=[1.,0.,0.],dn=[0.,.1,0.])
cases[49]['lam']=0.
for i,(x,L,D) in enumerate([(0,0,0),(0,1000,1),(1,0,0),(1,1,1),(1,1,1+1e-12),(1,1+1e-12,1),(.001,.4,.2),(.001,.2,.4),(10,.8,.2),(10,.2,.8),(700,1,.2),(700,.2,1),(1000,1,.2),(1,1000,1),(1e-300,700,0),(1e300,0,700)]):
 cases.append({'id':f'wien_{i:02}','group':'wien','xt':x,'lam':L,'delta':D,'dlnxt':.2,'dlam':.1,'ddelta':-.03,'extreme':True,'relative_gate':8e-12,'absolute_floor':5e-324})
base=[.12,.01,-.02,.015,.004,.005,-.003,.002,-.001,.003];slopes=[.003,-.001,.0015,.0004,.0002,-.0003,.0001,.0001,.0002,-.0001]
for i in range(12):
 cases.append({'id':f'composite_{i:02}','group':'composite','n':[.36,.48,.8],'b':[.2,-.1,-.1],'lam':.18+.013*i,'eta_t':.73+.03*i,'xt':.4+.1*i,'eta0':-2.,'h':.25,'iz':24,'coefficient_base':base,'coefficient_slopes':slopes,'coefficient_data_tangent':[.001*(j+1)*(1 if i%2 else -1) for j in range(10)],'dn':[.048,-.036,0],'db':[.007,-.002,-.005],'dlam':.03,'deta_t':.02,'dlnxt':.04,'xr_p':.03,'x1s':.6,'tau':.1+.08*i,'nH_cm3':200.,'H_t':1e-13,'dxr_p':.002,'dx1s':-.001,'dtau':.003,'fd_step':'1e-25'})
for i,(ch,k,alpha) in enumerate([(0,0,.25),(50,2,.5),(139,5,.75),(140,8,.375),(270,11,.625),(310,15,.25),(311,18,.5),(313,21,.75)]):cases.append({'id':f'actual_{i:02}','group':'actual','channel':ch,'cell':k,'alpha':alpha,'iz':24,'g0':72892,'h':2.1225e-5,'eta0_formula':'-log(8001)+g0*h','calibration':'INPUT_DEPENDENT_UNCALIBRATED','ADM01_fixed_face_coverage':'0/313'})
guards=['direction_shape','direction_unit','direction_nonfinite','shear_trace','rate_nonpositive','negative_lambda','lambda_nonfinite','nontangent','tangent_trace','tangent_overflow','before_prefix','short_prefix','exclusive_endpoint','negative_absolute','knot_tangent','missing_bound']
for i,g in enumerate(guards):cases.append({'id':f'guard_{i:02}','group':'guard','guard':g})
for i in range(12):cases.append({'id':f'envelope_{i:02}','group':'envelope','n':[.36,.48,.8],'b':[.2,-.1,-.1],'lam':.2+.02*i,'xt':.8,'eps_F':1e-7*(i+1),'e_H':1e-8,'K_eta':.03,'K_n':.02,'e_arithmetic':2e-13,'root_perturbation_fraction':(-.4 if i%2 else .4),'qt':.93888,'tau':.3,'H_t':1e-13})
for name in ['FLRW_delay_in_shear','omit_Wien_offset','photon_clock_plus_one']:cases.append({'id':'defect_'+name,'group':'defect','defect':name})
counts={g:sum(c['group']==g for c in cases) for g in ['root','tangent','wien','composite','actual','guard','envelope','defect']}
assert counts==dict(root=48,tangent=12,wien=16,composite=12,actual=8,guard=16,envelope=12,defect=3)
p={'schema':1,'unit':'REC-HISTORY-02R','mp_dps':80,'root_bisection_iterations':300,'fd_step':'1e-25','value_scaled_gate':5e-12,'jvp_scaled_gate':5e-9,'actual_scaled_gate':'64*float64_eps','wien_relative_gate':8e-12,'wien_underflow_absolute_floor':5e-324,'first_failure':'PRESERVE_AND_STOP_NO_AUTOREPAIR','case_counts':counts,'case_count':len(cases),'case_rows':cases,'independent_review_probes_in_primary':0,'execution_budget':{'cpu':16,'wall':45},'actual_angular_inference':False}
(R/'inputs/CASE_PLAN.json').write_text(json.dumps(p,indent=2,allow_nan=False)+'\n')
print('Serialized 127 predeclared cases; scientific execution 0.')
