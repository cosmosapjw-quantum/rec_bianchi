//! Exploratory continuous EMLA integration in tau=ln(a/a_boundary), u=y/S.
//! S=[xe_boundary,Tm_boundary] is constant. Thus du/dtau=F(tau,S*u)/S,
//! J_u[i,j]=S[j]/S[i]*dF_i/dy_j, partial_t=partial_tau F/S at FIXED u.
//! No multistep memories enter this different algorithm and no dense output is used.
use std::{sync::{Arc,Mutex},time::Instant};
use rodas5p_core::{CoreError,CoreResult,DenseMatrix,LuFactorization,WorkCounters,error_scale,wrms};
use rodas5p_integrators::{OdeProblem,AdaptiveStepConfig,OutputSchedule,integrate_rodas5p_fast_observed};
use serde::Serialize;
use serde_json::{Value,json};
use crate::{contracts::{Request,H,invalid},ffi};

#[derive(Default,Serialize)]
struct Trace {
    evaluations_attempted: usize,
    source_work: WorkCounters,
    failed_callbacks: Vec<Value>,
    last_callback: Option<Value>,
}
#[derive(Clone)]
struct Context {
    scale:[f64;2],span:f64,limit:usize,trace:Arc<Mutex<Trace>>,started:Instant,
}
impl Context {
    fn new(scale:[f64;2],span:f64,limit:usize)->Self {
        Self{scale,span,limit,trace:Arc::new(Mutex::new(Trace::default())),started:Instant::now()}
    }
    fn eval(&self,t:f64,y:&[f64],out:&mut[f64])->CoreResult<()> {
        if y.len()!=2 || out.len()!=2 {return Err(CoreError::Dimension("R3O_CALLBACK_REQUIRES_TWO_STATES".into()));}
        let p=[self.scale[0]*y[0],self.scale[1]*y[1]];
        let mut trace=self.trace.lock().map_err(|_|invalid("R3O_TRACE_MUTEX"))?;
        trace.evaluations_attempted+=1;
        let ordinal=trace.evaluations_attempted;
        let result=if ordinal>self.limit || self.started.elapsed().as_secs_f64()>45. {
            Err(CoreError::NonlinearSolve("R3O_CALLBACK_BUDGET_EXHAUSTED".into()))
        } else {
            trace.source_work.rhs_calls+=1;trace.source_work.rhs_evaluations+=1;
            ffi::continuous(t,self.span,p)
        };
        let entry=json!({"ordinal":ordinal,"tau":if t.is_finite(){Some(t)}else{None},
            "physical_state":if p.iter().all(|v|v.is_finite()){Some(p)}else{None},
            "physical_state_bits":[format!("{:016x}",p[0].to_bits()),format!("{:016x}",p[1].to_bits())],
            "error":result.as_ref().err().map(ToString::to_string)});
        trace.last_callback=Some(entry.clone());
        if result.is_err(){trace.failed_callbacks.push(entry);}
        let f=result?;
        out[0]=f[0]/self.scale[0];out[1]=f[1]/self.scale[1];
        if !out.iter().all(|v|v.is_finite()) {return Err(CoreError::NonFinite("R3O_SCALED_RHS".into()));}
        Ok(())
    }
    fn jac(&self,t:f64,y:&[f64])->CoreResult<DenseMatrix> {
        if y.len()!=2{return Err(CoreError::Dimension("R3O_JACOBIAN_SHAPE".into()));}
        self.trace.lock().map_err(|_|invalid("R3O_TRACE_MUTEX"))?.source_work.jacobian_builds+=1;
        let mut a=DenseMatrix::zeros(2,2);
        for j in 0..2 {
            let d=f64::EPSILON.cbrt()*y[j].abs().max(1.);
            let mut plus=[y[0],y[1]];let mut minus=plus;
            plus[j]+=d;minus[j]-=d;
            let mut fp=[0.;2];let mut fm=[0.;2];
            self.eval(t,&plus,&mut fp)?;self.eval(t,&minus,&mut fm)?;
            for i in 0..2 {a[(i,j)]=(fp[i]-fm[i])/(plus[j]-minus[j]);}
        }
        if !a.as_slice().iter().all(|v|v.is_finite()) {return Err(CoreError::NonFinite("R3O_FD_JACOBIAN".into()));}
        Ok(a)
    }
    fn ft_with_delta(&self,t:f64,y:&[f64],out:&mut[f64],d:f64)->CoreResult<()> {
        if y.len()!=2 || out.len()!=2 {return Err(CoreError::Dimension("R3O_PARTIAL_T_SHAPE".into()));}
        let mut a=[0.;2];let mut b=[0.;2];let mut c=[0.;2];
        // One-sided second-order differences keep every sample in the EMLA span.
        if t<d {
            self.eval(t,y,&mut a)?;self.eval(t+d,y,&mut b)?;self.eval(t+2.*d,y,&mut c)?;
            for i in 0..2 {out[i]=(-3.*a[i]+4.*b[i]-c[i])/(2.*d);}
        } else if t+d>self.span {
            self.eval(t,y,&mut a)?;self.eval(t-d,y,&mut b)?;self.eval(t-2.*d,y,&mut c)?;
            for i in 0..2 {out[i]=(3.*a[i]-4.*b[i]+c[i])/(2.*d);}
        } else {
            self.eval(t+d,y,&mut a)?;self.eval(t-d,y,&mut b)?;
            for i in 0..2 {out[i]=(a[i]-b[i])/(2.*d);}
        }
        if !out.iter().all(|v|v.is_finite()) {return Err(CoreError::NonFinite("R3O_PARTIAL_T".into()));}
        Ok(())
    }
    fn ft(&self,t:f64,y:&[f64],out:&mut[f64])->CoreResult<()> {
        self.trace.lock().map_err(|_|invalid("R3O_TRACE_MUTEX"))?.source_work.ft_calls+=1;
        self.ft_with_delta(t,y,out,1e-7)
    }
    fn problem(&self)->CoreResult<OdeProblem> {
        let rhs=self.clone();let jac=self.clone();let ft=self.clone();
        OdeProblem::new("original-HyRec-2012-short-EMLA-nonautonomous",2,
            Arc::new(move|t,y,f|rhs.eval(t,y,f)),None,
            Some(Arc::new(move|t,y|jac.jac(t,y))),None,
            Some(Arc::new(move|t,y,f|ft.ft(t,y,f))),false,None,None)
    }
}

pub fn run(req:&Request,max_attempts:usize,callback_limit:usize)->CoreResult<Value> {
    if !(1..=32).contains(&max_attempts) || !(1..=2048).contains(&callback_limit) {
        return Err(invalid("R3O_DIAGNOSTIC_CAP"));
    }
    let s=[req.native.xe,req.native.tm];let span=H*req.steps as f64;
    let grid=(0..=req.steps).map(|i|H*i as f64).collect::<Vec<_>>();
    let schedule=OutputSchedule::new(grid.clone())?;
    let probe=Context::new(s,span,2048);
    let jac=probe.jac(0.,&[1.,1.])?;
    let mut ft=[0.;2];let mut ft_half=[0.;2];
    probe.ft(0.,&[1.,1.],&mut ft)?;
    probe.ft_with_delta(0.,&[1.,1.],&mut ft_half,5e-8)?;
    let ft_consistency=(0..2).map(|i|(ft[i]-ft_half[i]).abs()/ft[i].abs().max(1.)).fold(0.,f64::max);
    let coeff=ffi::thermal_coefficients(&req.native)?;
    let thermal_jacobian_relative=(jac[(1,1)]+coeff[2]).abs()/coeff[2];
    let (_,discrete)=ffi::rhs(&req.native)?;
    let continuous=ffi::continuous(0.,span,s)?;
    let common_rhs_bits=(0..2).all(|i|discrete[i].to_bits()==continuous[i].to_bits());

    // Actual-Jacobian 2x2 linear algebra check using VigilODE's faer-backed LU.
    // W=I-hJ is only a residual diagnostic; it is not an alternate stepper.
    let w=DenseMatrix::identity(2).sub(&jac.scale(H))?;
    let b=[continuous[0]/s[0],continuous[1]/s[1]];
    let x=LuFactorization::new(&w)?.solve(&b)?;
    let wx=w.matvec(&x)?;
    let det=w[(0,0)]*w[(1,1)]-w[(0,1)]*w[(1,0)];
    if !det.is_finite() || det==0. {return Err(CoreError::LinearSolve("R3O_2X2_DETERMINANT".into()));}
    let analytic=[(w[(1,1)]*b[0]-w[(0,1)]*b[1])/det,
                  (w[(0,0)]*b[1]-w[(1,0)]*b[0])/det];
    let linear_residual=(0..2).map(|i|(wx[i]-b[i]).abs()/b[i].abs().max(1.)).fold(0.,f64::max);
    let linear_crosscheck=(0..2).map(|i|(x[i]-analytic[i]).abs()/analytic[i].abs().max(1.)).fold(0.,f64::max);
    let probe_pass=common_rhs_bits && thermal_jacobian_relative<1e-6 && ft_consistency<5e-4
        && linear_residual<1e-12 && linear_crosscheck<1e-12;

    let ctx=Context::new(s,span,callback_limit);
    let problem=ctx.problem()?;
    // Scalar tolerances apply to u. Their physical meaning is recorded below;
    // the fixed-owner comparison continues to use the original frozen gates.
    let cfg=AdaptiveStepConfig{atol:1e-12,rtol:1e-9,initial_step:H,
        min_step:1e-12,max_step:2.*H,max_attempts,..Default::default()};
    let result=integrate_rodas5p_fast_observed(&problem,(0.,span),&[1.,1.],&cfg,&schedule);
    let probes=json!({"jacobian_normalized":jac.as_slice(),"partial_t_normalized":ft,
        "partial_t_half_delta":ft_half,"partial_t_relative_consistency":ft_consistency,
        "thermal_coefficients_Tr_A_lambda_Teq":coeff,"thermal_jacobian_relative":thermal_jacobian_relative,
        "initial_fixed_and_continuous_rhs_byte_identity":common_rhs_bits,
        "faer_0_24_4_linear_residual":linear_residual,"faer_vs_analytic_2x2":linear_crosscheck,
        "faer_solution":x,"analytic_2x2_solution":analytic,"matrix_I_minus_hJ":w.as_slice(),
        "success":probe_pass,"source_callbacks":*probe.trace.lock().map_err(|_|invalid("R3O_TRACE_MUTEX"))?});
    let callbacks=serde_json::to_value(&*ctx.trace.lock().map_err(|_|invalid("R3O_TRACE_MUTEX"))?)
        .map_err(|e|invalid(e.to_string()))?;
    match result {
        Err(error)=>Ok(json!({"status":"ERROR","success":false,"classification":"EXPLORATORY_METHOD_COMPARISON",
            "error":error.to_string(),"initial_actual_state":s,"callbacks":callbacks,"probes":probes,
            "last_committed_output":null,"note":"driver returned CoreError; callback states are retained and not relabelled as accepted states"})),
        Ok(result)=>{
            let o=&result.observed;
            if o.t.len()!=o.y.len() || o.t.is_empty() || o.t.len()>grid.len()
                || result.attempts>max_attempts || o.internal_steps>32
                || o.y.iter().any(|y|y.len()!=2 || !y.iter().all(|v|v.is_finite()))
                || (o.success && o.t.len()!=grid.len()) {
                return Err(invalid("R3O_VIGILODE_OUTPUT_SHAPE_COUNT_OR_CAP"));
            }
            for i in 0..o.t.len() {
                if o.t[i].to_bits()!=grid[i].to_bits(){return Err(invalid("R3O_DIRECT_OUTPUT_TIME_IDENTITY"));}
            }
            let physical=o.y.iter().map(|y|[s[0]*y[0],s[1]*y[1]]).collect::<Vec<_>>();
            let mut comparisons=Vec::new();
            for i in 0..physical.len() {
                let py=[req.python_states[i].xe,req.python_states[i].tm];
                let budgets=[5e-9*py[0].abs().max(1e-8),5e-10*py[1].abs().max(1.)];
                let scales=error_scale(&py,&physical[i],&budgets,0.)?;
                comparisons.push(json!({"tau":o.t[i],"scaled_state_residual":[(physical[i][0]-py[0]).abs()/budgets[0],
                    (physical[i][1]-py[1]).abs()/budgets[1]],"wrms":wrms(&[physical[i][0]-py[0],physical[i][1]-py[1]],&scales)?,
                    "admission_test":false}));
            }
            let n=physical.len();
            Ok(json!({"status":if o.success&&probe_pass {"EXPLORATORY_DIAGNOSTIC_COMPLETE"} else if !o.success {"PARTIAL_BOUNDED_FAILURE"} else {"PROBE_FAILURE"},
                "success":o.success&&probe_pass,"classification":"EXPLORATORY_METHOD_COMPARISON",
                "algorithm":"integrate_rodas5p_fast_observed","driver":result.driver,"autonomous":false,
                "model":"EMLA2s2p","time":"tau = ln(a/a_native_U6_boundary)","normalizers":s,
                "config":cfg,"physical_atol":[cfg.atol*s[0],cfg.atol*s[1]],"physical_rtol":cfg.rtol,
                "requested_times":grid,"times":o.t,"normalized_states":o.y,"physical_states":physical,
                "last_committed_output":{"tau":o.t[n-1],"state":physical[n-1]},
                "last_internal_accepted_state_exposed_by_api":false,
                "same_algorithm_parity":false,"production_admission":false,"dense_interpolation":false,
                "attempts":result.attempts,"accepted_steps":result.accepted_steps,"rejected_steps":result.rejected_steps,
                "work":o.counters,"internal_steps":o.internal_steps,"message":o.message,
                "jacobian_reuses":result.jacobian_reuses,"lu_backend":format!("{:?}",result.lu),
                "callbacks":callbacks,"probes":probes,"comparisons_with_python_fixed_h2":comparisons}))
        }
    }
}
