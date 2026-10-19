//! The only unsafe boundary. All fixed-size buffers are owned and live across
//! each synchronous call. C pointers never escape. A process-local mutex guards
//! the original static rates/cosmology, including initialization. The CLI starts
//! no worker threads and never exposes global C state to Python callbacks.
use std::{os::raw::{c_double,c_int,c_long}, sync::Mutex};
use rodas5p_core::{CoreError,CoreResult};
use crate::contracts::{Checkpoint,invalid,H,END};
static C_LOCK: Mutex<()> = Mutex::new(());
unsafe extern "C" {
    fn rec_r3o_lowz_init() -> c_int;
    fn rec_r3o_lowz_dlna() -> c_double;
    fn rec_r3o_lowz_nz() -> c_long;
    fn rec_r3o_lowz_z(iz:c_long) -> c_double;
    fn rec_r3o_lowz_guard(z:c_double,tm:c_double) -> c_int;
    fn rec_r3o_lowz_rhs(iz:c_long,peebles:c_int,xe:c_double,tm:c_double,out:*mut c_double) -> c_int;
    fn rec_r3o_lowz_step(iz:c_long,peebles:c_int,state:*mut c_double) -> c_int;
    fn rec_r3o_rust_continuous(t:c_double,span:c_double,xe:c_double,tm:c_double,out:*mut c_double) -> c_int;
    fn rec_r3o_rust_thermal_coefficients(xe:c_double,tm:c_double,out:*mut c_double) -> c_int;
}
fn lock() -> CoreResult<std::sync::MutexGuard<'static,()>> {
    C_LOCK.lock().map_err(|_| invalid("R3O_C_MUTEX_POISONED"))
}
pub fn initialize() -> CoreResult<()> {
    let _guard=lock()?;
    // SAFETY: serialized initialization, source-rate working directory set by launcher.
    let (status,h,n)=unsafe {(rec_r3o_lowz_init(),rec_r3o_lowz_dlna(),rec_r3o_lowz_nz())};
    if status!=0 || h.to_bits()!=H.to_bits() || n!=END+1 {return Err(invalid(format!("R3O_C_INIT:{status}:{h}:{n}")));}
    Ok(())
}
pub fn redshift(iz:i64) -> CoreResult<f64> {
    let _guard=lock()?;
    // SAFETY: scalar-only C function; supported target uses 64-bit c_long.
    Ok(unsafe{rec_r3o_lowz_z(iz as c_long)})
}
pub fn guard(iz:i64,tm:f64) -> CoreResult<i32> {
    let _guard=lock()?;
    // SAFETY: scalar-only functions under the C lock.
    let result=unsafe{rec_r3o_lowz_guard(rec_r3o_lowz_z(iz as c_long),tm)};
    if result<0 {Err(invalid(format!("R3O_C_GUARD:{result}")))} else {Ok(result)}
}
pub fn rhs(c:&Checkpoint) -> CoreResult<(i32,[f64;2])> {
    let _guard=lock()?;let mut out=[0.;2];
    // SAFETY: two-double C output contract; initialized source and no aliasing.
    let m=unsafe{rec_r3o_lowz_rhs(c.iz as c_long,c.peebles_event_iz.is_some() as i32,c.xe,c.tm,out.as_mut_ptr())};
    if ![0,2].contains(&m) || !out.iter().all(|x|x.is_finite()) {return Err(invalid(format!("R3O_C_RHS:{m}")));}
    Ok((m,out))
}
pub fn oracle_step(c:&Checkpoint) -> CoreResult<Checkpoint> {
    c.validate()?;let (model,event,reason)=c.input_stage()?;
    let _guard=lock()?;let mut a=c.values();
    // SAFETY: independent six-double C state copy, original rec_get_xe_next2_HTm.
    let m=unsafe{rec_r3o_lowz_step(c.iz as c_long,c.peebles_event_iz.is_some() as i32,a.as_mut_ptr())};
    if m!=model || !a.iter().all(|x|x.is_finite()) {return Err(invalid(format!("R3O_C_ORACLE:{m}")));}
    let mut result=c.with_values(a);result.iz+=1;result.peebles_event_iz=event;result.peebles_event_reason=reason;
    drop(_guard);result.validate()?;Ok(result)
}
pub fn continuous(t:f64,span:f64,y:[f64;2]) -> CoreResult<[f64;2]> {
    let _guard=lock()?;let mut out=[0.;2];
    // SAFETY: output has exactly two doubles; C rejects time/stage/physical-domain errors.
    let m=unsafe{rec_r3o_rust_continuous(t,span,y[0],y[1],out.as_mut_ptr())};
    if m!=2 {return Err(CoreError::NonlinearSolve(format!("R3O_C_EMLA_CALLBACK:{m};t={t:.17e};xe={:.17e};Tm={:.17e}",y[0],y[1])));}
    if !out.iter().all(|v|v.is_finite()) {return Err(CoreError::NonFinite("R3O_C_CONTINUOUS".into()));}
    Ok(out)
}
pub fn thermal_coefficients(c:&Checkpoint) -> CoreResult<[f64;4]> {
    let _guard=lock()?;let mut out=[0.;4];
    // SAFETY: four-double coefficient output contract, read-only original C parameters.
    let m=unsafe{rec_r3o_rust_thermal_coefficients(c.xe,c.tm,out.as_mut_ptr())};
    if m!=0 || !out.iter().all(|v|v.is_finite()) {return Err(invalid(format!("R3O_THERMAL_COEFFICIENTS:{m}")));}
    Ok(out)
}
