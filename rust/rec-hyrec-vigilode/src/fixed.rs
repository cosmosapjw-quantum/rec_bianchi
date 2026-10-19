use rodas5p_core::{CoreResult,WorkCounters,error_scale,wrms};
use serde_json::{Value,json};
use crate::{contracts::{Checkpoint,Request,H,invalid},ffi};

/// Rust owns this recurrence and all four predictor memories. No mul_add or
/// reassociation: match history.c's expression and update ordering exactly.
pub fn step(c:&Checkpoint,work:&mut WorkCounters) -> CoreResult<Checkpoint> {
    c.validate()?;
    let (model,event,reason)=c.input_stage()?;
    work.rhs_calls+=1;work.rhs_evaluations+=1;
    let (actual,f)=ffi::rhs(c)?;
    if actual!=model {return Err(invalid("R3O_RUST_INPUT_STAGE"));}
    let a=[c.xe+H*(1.25*f[0]-0.25*c.hydrogen_prev2),
        c.tm+H*(1.25*f[1]-0.25*c.thermal_prev2),
        f[0],c.hydrogen_prev,f[1],c.thermal_prev];
    let mut n=c.with_values(a);n.iz+=1;n.peebles_event_iz=event;n.peebles_event_reason=reason;
    n.validate()?;work.accepted_steps+=1;Ok(n)
}

pub fn run(req:&Request) -> CoreResult<Value> {
    // Bounded stage contract checks are separate from the 16 physical steps.
    let mut cold=req.native.clone();cold.tm=0.09*2.7255*(1.+ffi::redshift(cold.iz)?);
    let cold_stage=cold.input_stage()?;
    let mut restored=req.native.clone();restored.iz+=1;
    restored.peebles_event_iz=cold_stage.1;restored.peebles_event_reason=cold_stage.2.clone();
    let absorbed=restored.input_stage()?;
    let stage_checks=cold_stage.0==0 && cold_stage.2.as_deref()==Some("TM_TR_MIN")
        && ffi::guard(restored.iz,restored.tm)?==0 && absorbed.0==0
        && absorbed.1==cold_stage.1 && absorbed.2==cold_stage.2;
    let mut rust=req.native.clone();let mut native=req.native.clone();
    let mut work=WorkCounters::default();let mut rows=Vec::new();
    let mut state_max=[0.0_f64;6];let mut rhs_max=[0.0_f64;2];
    let mut failure=None;
    for i in 0..=req.steps {
        let py=&req.python_states[i];
        let rv=rust.values();let cv=native.values();let pv=py.values();
        let bits_match=(0..6).all(|k|rv[k].to_bits()==cv[k].to_bits());
        let stage_match=rust.iz==native.iz && rust.iz==py.iz
            && rust.peebles_event_iz==native.peebles_event_iz && rust.peebles_event_iz==py.peebles_event_iz
            && rust.peebles_event_reason==native.peebles_event_reason && rust.peebles_event_reason==py.peebles_event_reason;
        let state_scale=[5e-9*cv[0].abs().max(1e-8),5e-10*cv[1].abs().max(1.)];
        // Core WRMS uses the frozen per-component absolute budgets and zero rtol;
        // admission still requires each component, never just their mean.
        let scale=error_scale(&cv[..2],&pv[..2],&state_scale,0.)?;
        let w=wrms(&[pv[0]-cv[0],pv[1]-cv[1]],&scale)?;
        let mut common=None;
        for k in 0..6 {
            let floor=if k==0 {1e-8} else {1.};
            let residual=(pv[k]-cv[k]).abs()/cv[k].abs().max(floor);
            state_max[k]=state_max[k].max(residual);
            let limit=if k==0 {5e-9} else if k==1 {5e-10} else {2e-8};
            if !residual.is_finite() || residual>limit {failure=Some(format!("R3O_PYTHON_STATE:{i}:{k}:{residual}"));}
        }
        if i<req.steps {
            let (m,f)=ffi::rhs(py)?;let p=req.python_rhs[i];
            let residual=[(p[0]-f[0]).abs()/p[0].abs().max(f[0].abs()).max(1e-13),
                          (p[1]-f[1]).abs()/f[1].abs().max(1.)];
            for k in 0..2 {rhs_max[k]=rhs_max[k].max(residual[k]);}
            if !residual.iter().all(|v|v.is_finite()) || residual[0]>3e-10 || residual[1]>2e-10 {failure=Some(format!("R3O_PYTHON_COMMON_RHS:{i}"));}
            common=Some(json!({"model":m,"c_rhs":f,"python_rhs":p,"scaled_residual":residual}));
        }
        rows.push(json!({"rust":rust,"original_c":native,"python":py,
            "rust_bits":rust.bits(),"original_c_bits":native.bits(),
            "state_and_four_memory_byte_identity":bits_match,"stage_identity":stage_match,
            "python_state_wrms":w,"common_input_rhs":common}));
        if !bits_match || !stage_match {failure=Some(format!("R3O_BYTE_OR_STAGE_IDENTITY:{i}"));}
        if failure.is_some() || i==req.steps {break;}
        // C advances its own state; the Rust result never seeds the C oracle.
        match (step(&rust,&mut work),ffi::oracle_step(&native)) {
            (Ok(r),Ok(c)) => {rust=r;native=c;},
            (r,c) => {failure=Some(format!("R3O_STEP_FAILURE:rust={:?};c={:?}",r.err(),c.err()));break;}
        }
    }
    let completed=rows.len()==req.steps+1 && failure.is_none() && stage_checks;
    Ok(json!({"status":if completed {"FIXED_H2_16_OR_BOUNDED_PARITY_PASS"} else {"FAILED"},
        "success":completed,"rows":rows,"failure":failure,"last_rust_state":rust,
        "last_original_c_state":native,"work":work,"max_state_scaled_residual":state_max,
        "max_common_rhs_scaled_residual":rhs_max,"algorithm":"Y+h*(1.25*Fnow-.25*Fprev2)",
        "absorbing_input_stage_contract":{"success":stage_checks,"first_guard_reason":cold_stage.2,"retained_event":absorbed.1},
        "state_tolerances":[5e-9,5e-10],"memory_tolerance":2e-8,"rhs_tolerances":[3e-10,2e-10],
        "production_admission":false}))
}
