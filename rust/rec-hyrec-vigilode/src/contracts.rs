use rodas5p_core::{CoreError, CoreResult};
use serde::{Deserialize, Serialize};
use crate::ffi;

pub const H: f64 = 4.245e-5;
pub const START: i64 = 58389;
pub const END: i64 = 211716;
pub const VIGILODE_COMMIT: &str = "a21d573980f66fe02891bd216153443b5352f921";

pub fn invalid(message: impl Into<String>) -> CoreError { CoreError::InvalidInput(message.into()) }

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Checkpoint {
    pub iz: i64,
    pub xe: f64,
    #[serde(rename = "Tm_K")]
    pub tm: f64,
    pub hydrogen_prev: f64,
    pub hydrogen_prev2: f64,
    pub thermal_prev: f64,
    pub thermal_prev2: f64,
    pub peebles_event_iz: Option<i64>,
    pub peebles_event_reason: Option<String>,
}

impl Checkpoint {
    pub fn values(&self) -> [f64; 6] {
        [self.xe,self.tm,self.hydrogen_prev,self.hydrogen_prev2,self.thermal_prev,self.thermal_prev2]
    }
    pub fn bits(&self) -> Vec<String> {
        self.values().iter().map(|x| format!("{:016x}", x.to_bits())).collect()
    }
    pub fn validate(&self) -> CoreResult<()> {
        if !(START..=END).contains(&self.iz) || !self.values().iter().all(|v| v.is_finite())
            || !(self.xe > 0. && self.xe < 1. && self.tm > 0.
                 && self.tm <= 2.7255*(1.+ffi::redshift(self.iz)?)) {
            return Err(invalid("R3O_CHECKPOINT_DOMAIN"));
        }
        match (&self.peebles_event_iz,&self.peebles_event_reason) {
            (None,None) => (),
            (Some(iz),Some(reason)) if *iz >= START && *iz < self.iz
                && (reason == "TR_MIN" || reason == "TM_TR_MIN") => (),
            _ => return Err(invalid("R3O_ABSORBING_EVENT_PAIR")),
        }
        Ok(())
    }
    pub fn with_values(&self, a: [f64;6]) -> Self {
        let mut c=self.clone();
        c.xe=a[0];c.tm=a[1];c.hydrogen_prev=a[2];c.hydrogen_prev2=a[3];
        c.thermal_prev=a[4];c.thermal_prev2=a[5];c
    }
    pub fn input_stage(&self) -> CoreResult<(i32,Option<i64>,Option<String>)> {
        let reason=ffi::guard(self.iz,self.tm)?;
        if self.peebles_event_iz.is_some() {
            return Ok((0,self.peebles_event_iz,self.peebles_event_reason.clone()));
        }
        match reason {
            0 => Ok((2,None,None)),
            1 => Ok((0,Some(self.iz),Some("TR_MIN".into()))),
            2 => Ok((0,Some(self.iz),Some("TM_TR_MIN".into()))),
            _ => Err(invalid("R3O_GUARD_RESULT")),
        }
    }
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Request {
    pub schema: String,
    pub h2: f64,
    pub start_iz: i64,
    pub end_iz: i64,
    pub steps: usize,
    pub native: Checkpoint,
    pub python_states: Vec<Checkpoint>,
    pub python_rhs: Vec<[f64;2]>,
    pub input_hashes: serde_json::Value,
}
impl Request {
    pub fn validate(&self) -> CoreResult<()> {
        if self.schema != "rec.r3o.rust-input.v1" || self.h2.to_bits() != H.to_bits()
            || self.start_iz != START || self.end_iz != END || !(1..=32).contains(&self.steps)
            || self.native.iz != START || self.native.peebles_event_iz.is_some()
            || self.python_states.len() != self.steps+1 || self.python_rhs.len() != self.steps {
            return Err(invalid("R3O_INPUT_SHAPE_GRID_OR_CAP"));
        }
        self.native.validate()?;
        for i in 0..self.python_states.len() {
            self.python_states[i].validate()?;
            if self.python_states[i].iz != START+i as i64 {
                return Err(invalid("R3O_PYTHON_TIME_COUNT_ORDER"));
            }
        }
        if !self.python_rhs.iter().flatten().all(|v|v.is_finite()) {
            return Err(CoreError::NonFinite("R3O_PYTHON_RHS".into()));
        }
        Ok(())
    }
}
