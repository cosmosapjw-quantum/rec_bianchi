//! Persistent, source-qualified point-feedback driver of the unchanged F08
//! paired runtime. Build as src/main.rs beside its byte-exact paired_runtime.rs.
//!
//! Protocol: STEP|dt, FEEDBACK|dt|photons|guard_n|guard_u, QUIT.
//! Arrays are comma-separated in original direction-major, energy-minor order.
//! Feedback conserves every energy-group total and guard N/U totals to the
//! declared floating-point summation tolerance. It resets only photon and guard
//! boxes to point intervals; this invalidates cumulative photon-interval claims.
#![forbid(unsafe_code)]

pub use rei_microphysics::*;
mod paired_runtime;

use paired_runtime::{energy_nodes, paired_initial, paired_trial, qhat, PairedConfig, PairedState};
use std::fmt::Write as FmtWrite;
use std::io::{self, BufRead, Write as IoWrite};

const CHI: [f64; 3] = [13.598_434_599_702, 24.587_389_011, 54.417_76];
const FHE: f64 = 0.083;
const CONSERVATION_ULPS: f64 = 128.0;
const MIN_TOTAL: f64 = 1e-300;

fn jstr(s: &str) -> String {
    let mut out = String::from("\"");
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if c < '\u{20}' => { let _ = write!(out, "\\u{:04x}", c as u32); }
            c => out.push(c),
        }
    }
    out.push('"');
    out
}

fn num(x: f64) -> Result<String, String> {
    if !x.is_finite() { return Err("BRIDGE_NONFINITE_OUTPUT".into()); }
    Ok(format!("{x:.17e}"))
}

fn array(values: &[f64]) -> Result<String, String> {
    let v = values.iter().map(|&x| num(x)).collect::<Result<Vec<_>, _>>()?;
    Ok(format!("[{}]", v.join(",")))
}

fn intervals(values: &[Interval]) -> Result<String, String> {
    let v = values.iter().map(|b| array(&[b.lo, b.hi])).collect::<Result<Vec<_>, _>>()?;
    Ok(format!("[{}]", v.join(",")))
}

// Match the runtime's compensated summation for photon and energy inventories.
fn sum(values: impl IntoIterator<Item = f64>) -> f64 {
    let (mut result, mut correction) = (0.0, 0.0);
    for x in values {
        let y = x - correction;
        let next = result + y;
        correction = (next - result) - y;
        result = next;
    }
    result
}

fn photon_n(s: &PairedState) -> f64 {
    sum(s.photons.iter().chain(&s.lower_guard_n).copied())
}

fn photon_u(s: &PairedState, energies: &[f64]) -> f64 {
    sum(s.photons.iter().enumerate().map(|(i, x)| x * energies[i % energies.len()])
        .chain(s.lower_guard_u.iter().copied()))
}

fn matter_u(s: &PairedState) -> f64 {
    let g = &s.gas;
    g.w_ev_per_h + CHI[0] * g.fractions[0]
        + FHE * (CHI[1] * g.fractions[1] + (CHI[1] + CHI[2]) * g.fractions[2])
        + g.escape_ev_per_h
}

fn gas_temperature(s: &PairedState) -> f64 {
    let x = s.gas.fractions;
    let particles = 1.0 + FHE + x[0] + FHE * (x[1] + 2.0 * x[2]);
    2.0 * s.gas.w_ev_per_h * 1.602176634e-12 / (3.0 * 1.380649e-16 * particles)
}

#[derive(Clone, Copy, Default)]
struct Widths { max: f64, sum: f64, nonzero: usize }

impl Widths {
    fn of(boxes: &[Interval]) -> Result<Self, String> {
        let mut widths = Vec::with_capacity(boxes.len());
        for b in boxes {
            if !b.lo.is_finite() || !b.hi.is_finite() || b.hi < b.lo {
                return Err("BRIDGE_INTERVAL_WIDTH_DOMAIN".into());
            }
            widths.push(b.hi - b.lo);
        }
        Ok(Self {
            max: widths.iter().copied().fold(0.0, f64::max),
            sum: sum(widths.iter().copied()),
            nonzero: widths.iter().filter(|&&w| w > 0.0).count(),
        })
    }
    fn json(self) -> Result<String, String> {
        Ok(format!("{{\"max\":{},\"sum\":{},\"nonzero_count\":{}}}",
            num(self.max)?, num(self.sum)?, self.nonzero))
    }
}

#[derive(Default)]
struct Feedback {
    photon: Widths,
    guard_n: Widths,
    guard_u: Widths,
    max_group_abs_delta: f64,
    max_group_relative_delta: f64,
    guard_n_delta: f64,
    guard_u_delta: f64,
}

impl Feedback {
    fn json(&self) -> Result<String, String> {
        Ok(format!(concat!(
            "{{\"discarded_photon_widths\":{},\"discarded_guard_n_widths\":{},",
            "\"discarded_guard_u_widths\":{},\"max_group_abs_delta\":{},",
            "\"max_group_relative_delta\":{},\"guard_n_delta\":{},\"guard_u_delta\":{}}}"),
            self.photon.json()?, self.guard_n.json()?, self.guard_u.json()?,
            num(self.max_group_abs_delta)?, num(self.max_group_relative_delta)?,
            num(self.guard_n_delta)?, num(self.guard_u_delta)?))
    }
}

fn parse_dt(s: &str) -> Result<f64, String> {
    let dt = s.parse::<f64>().map_err(|_| "BRIDGE_DT_PARSE".to_owned())?;
    if !dt.is_finite() || dt <= 0.0 { return Err("BRIDGE_DT_DOMAIN".into()); }
    Ok(dt)
}

fn parse_array(s: &str, length: usize, name: &str) -> Result<Vec<f64>, String> {
    let v = s.split(',').map(|word| {
        let x = word.parse::<f64>().map_err(|_| format!("BRIDGE_{name}_PARSE"))?;
        if !x.is_finite() || x < 0.0 { return Err(format!("BRIDGE_{name}_DOMAIN")); }
        Ok(x)
    }).collect::<Result<Vec<_>, String>>()?;
    if v.len() != length {
        return Err(format!("BRIDGE_{name}_LENGTH:expected={length},actual={}", v.len()));
    }
    Ok(v)
}

fn conserved(before: f64, after: f64, name: &str) -> Result<(), String> {
    let tolerance = CONSERVATION_ULPS * f64::EPSILON * before.max(MIN_TOTAL);
    if !before.is_finite() || !after.is_finite() || (after - before).abs() > tolerance {
        return Err(format!("BRIDGE_FEEDBACK_{name}_NOT_CONSERVED:before={before:.17e},after={after:.17e},tolerance={tolerance:.17e}"));
    }
    Ok(())
}

fn point_boxes(values: &[f64]) -> Result<Vec<Interval>, String> {
    values.iter().map(|&x| Interval::point(x).map_err(|_| "BRIDGE_POINT_INTERVAL".into())).collect()
}

fn apply_feedback(s: &mut PairedState, nk: usize, photons: Vec<f64>, gn: Vec<f64>, gu: Vec<f64>)
    -> Result<Feedback, String>
{
    // Complete every scientific precheck before changing the state.
    let mut report = Feedback {
        photon: Widths::of(&s.photon_boxes)?,
        guard_n: Widths::of(&s.lower_guard_n_box)?,
        guard_u: Widths::of(&s.lower_guard_u_box)?,
        ..Feedback::default()
    };
    for k in 0..nk {
        let before = sum(s.photons.iter().skip(k).step_by(nk).copied());
        let after = sum(photons.iter().skip(k).step_by(nk).copied());
        conserved(before, after, &format!("GROUP_{k}"))?;
        let delta = (after - before).abs();
        report.max_group_abs_delta = report.max_group_abs_delta.max(delta);
        report.max_group_relative_delta = report.max_group_relative_delta.max(delta / before.max(MIN_TOTAL));
    }
    for (d, (&n, &u)) in gn.iter().zip(&gu).enumerate() {
        if (n == 0.0 && u != 0.0) || (n > 0.0 && u >= 10.0 * n) {
            return Err(format!("BRIDGE_FEEDBACK_GUARD_DOMAIN:direction={d}"));
        }
    }
    let old_gn = sum(s.lower_guard_n.iter().copied());
    let old_gu = sum(s.lower_guard_u.iter().copied());
    let new_gn = sum(gn.iter().copied());
    let new_gu = sum(gu.iter().copied());
    conserved(old_gn, new_gn, "GUARD_N")?;
    conserved(old_gu, new_gu, "GUARD_U")?;
    report.guard_n_delta = new_gn - old_gn;
    report.guard_u_delta = new_gu - old_gu;
    let pb = point_boxes(&photons)?;
    let nb = point_boxes(&gn)?;
    let ub = point_boxes(&gu)?;
    s.photons = photons;
    s.lower_guard_n = gn;
    s.lower_guard_u = gu;
    s.photon_boxes = pb;
    s.lower_guard_n_box = nb;
    s.lower_guard_u_box = ub;
    // gas/gas_box, all cumulative ledgers, ledger_comp, and energy_comp remain
    // untouched. The original endpoint constructs gas packets from photons.
    Ok(report)
}

struct Driver {
    cfg: PairedConfig,
    geometry: String,
    h: [f64; 3],
    energies: Vec<f64>,
    state: PairedState,
    initial_n: f64,
    initial_total_u: f64,
    reset_count: usize,
    accepted_steps: usize,
}

impl Driver {
    fn new(geometry: &str) -> Result<Self, String> {
        let h = match geometry {
            "S0_BI" => [1.01e-14, 0.99e-14, 1.0e-14],
            "S0_FLRW" => [1.0e-14; 3],
            _ => return Err("BRIDGE_GEOMETRY_EXPECTED_S0_BI_OR_S0_FLRW".into()),
        };
        let cfg = PairedConfig { spectral_subdivisions: 4, n_mu: 8, n_phi: 16 };
        let energies = energy_nodes(&cfg).map_err(|e| e.code().to_owned())?;
        let state = paired_initial(&cfg).map_err(|e| e.code().to_owned())?;
        let initial_n = photon_n(&state);
        let initial_total_u = matter_u(&state) + photon_u(&state, &energies);
        Ok(Self { cfg, geometry: geometry.to_owned(), h, energies, state,
            initial_n, initial_total_u, reset_count: 0, accepted_steps: 0 })
    }

    fn record(&self, gates: Option<[f64; 3]>, audits: &[String], feedback: Option<&Feedback>)
        -> Result<String, String>
    {
        let s = &self.state;
        let photon_n_value = photon_n(s);
        let photon_u_value = photon_u(s, &self.energies);
        let nres = photon_n_value + s.absorbed_photons_per_h - self.initial_n - s.source_photons_per_h;
        let eres = matter_u(s) + photon_u_value + s.redshift_work_ev_per_h
            + s.thermal_work_ev_per_h - self.initial_total_u - s.source_energy_ev_per_h;
        let x = s.gas.fractions;
        let gas = [x[0], x[1], x[2], s.gas.w_ev_per_h, s.gas.escape_ev_per_h];
        let n_h = 1e-4 * (-self.h.iter().sum::<f64>() * s.time_s).exp();
        let n_e = n_h * (x[0] + FHE * (x[1] + 2.0 * x[2]));
        let mut fields = vec![
            "\"status\":\"OK\"".to_owned(),
            format!("\"geometry\":{}", jstr(&self.geometry)),
            format!("\"accepted_steps\":{}", self.accepted_steps),
            format!("\"time_s\":{}", num(s.time_s)?),
            format!("\"gas\":{}", array(&gas)?),
            format!("\"gas_box\":{}", intervals(&s.gas_box)?),
            format!("\"photons\":{}", array(&s.photons)?),
            format!("\"lower_guard_n\":{}", array(&s.lower_guard_n)?),
            format!("\"lower_guard_u\":{}", array(&s.lower_guard_u)?),
            format!("\"source_n\":{}", num(s.source_photons_per_h)?),
            format!("\"source_u\":{}", num(s.source_energy_ev_per_h)?),
            format!("\"absorbed_n\":{}", num(s.absorbed_photons_per_h)?),
            format!("\"redshift_work\":{}", num(s.redshift_work_ev_per_h)?),
            format!("\"thermal_work\":{}", num(s.thermal_work_ev_per_h)?),
            format!("\"photon_N\":{}", num(photon_n_value)?),
            format!("\"photon_U\":{}", num(photon_u_value)?),
            format!("\"temperature\":{}", num(gas_temperature(s))?),
            format!("\"n_h_cm3\":{}", num(n_h)?),
            format!("\"n_e_cm3\":{}", num(n_e)?),
            format!("\"global_N_residual\":{}", num(nres)?),
            format!("\"global_E_residual\":{}", num(eres)?),
            format!("\"ledger_comp\":{}", array(&s.ledger_comp)?),
            format!("\"energy_comp\":{}", num(s.energy_comp)?),
            format!("\"photon_interval_chain_reset\":{}", self.reset_count > 0),
            format!("\"photon_interval_reset_count\":{}", self.reset_count),
            format!("\"reset_this_step\":{}", feedback.is_some()),
            format!("\"photon_interval_widths\":{}", Widths::of(&s.photon_boxes)?.json()?),
            format!("\"guard_n_interval_widths\":{}", Widths::of(&s.lower_guard_n_box)?.json()?),
            format!("\"guard_u_interval_widths\":{}", Widths::of(&s.lower_guard_u_box)?.json()?),
            "\"cumulative_photon_interval_certificate\":false".to_owned(),
            format!("\"feedback\":{}", match feedback { Some(f) => f.json()?, None => "null".into() }),
            format!("\"audits\":[{}]", audits.join(",")),
        ];
        if let Some([local, public, ledger]) = gates {
            fields.push(format!("\"local_bound\":{}", num(local)?));
            fields.push(format!("\"public_width\":{}", num(public)?));
            fields.push(format!("\"max_ledger\":{}", num(ledger)?));
        } else {
            fields.push("\"local_bound\":null,\"public_width\":null,\"max_ledger\":null".into());
            let qs = (0..self.cfg.n_mu * self.cfg.n_phi).map(|d| array(&qhat(&self.cfg, d)))
                .collect::<Result<Vec<_>, _>>()?;
            fields.push(format!("\"energy_nodes\":{}", array(&self.energies)?));
            fields.push(format!("\"q128\":[{}]", qs.join(",")));
            fields.push(format!("\"h_per_s\":{}", array(&self.h)?));
            fields.push("\"config\":{\"spectral_subdivisions\":4,\"n_mu\":8,\"n_phi\":16}".into());
            fields.push(format!("\"initial_photon_N\":{}", num(self.initial_n)?));
            fields.push(format!("\"initial_total_U\":{}", num(self.initial_total_u)?));
            fields.push(format!("\"feedback_conservation_relative_tolerance\":{}", num(CONSERVATION_ULPS * f64::EPSILON)?));
            fields.push("\"normalization\":\"N per H; U eV per H; gas proper seconds\"".into());
            fields.push("\"audit_order\":[\"full\",\"half1\",\"half2\"]".into());
        }
        Ok(format!("{{{}}}", fields.join(",")))
    }

    fn advance(&mut self, command: &str) -> Result<String, String> {
        let parts: Vec<_> = command.split('|').collect();
        let mut feedback = None;
        let dt = match parts.first().copied() {
            Some("STEP") if parts.len() == 2 => parse_dt(parts[1])?,
            Some("FEEDBACK") if parts.len() == 5 => {
                let dt = parse_dt(parts[1])?;
                let nd = self.cfg.n_mu * self.cfg.n_phi;
                let nk = self.energies.len();
                let photons = parse_array(parts[2], nd * nk, "PHOTONS")?;
                let gn = parse_array(parts[3], nd, "GUARD_N")?;
                let gu = parse_array(parts[4], nd, "GUARD_U")?;
                feedback = Some(apply_feedback(&mut self.state, nk, photons, gn, gu)?);
                self.reset_count += 1;
                dt
            }
            _ => return Err("BRIDGE_COMMAND_EXPECTED_STEP_OR_FEEDBACK".into()),
        };
        let trial = paired_trial(&self.cfg, self.h, &self.state, dt)
            .map_err(|e| format!("{}:time_s={:.17e},dt_s={dt:.17e},reset_count={}",
                e.code(), self.state.time_s, self.reset_count))?;
        let gates = [trial.local_bound, trial.public_width, trial.max_ledger];
        self.state = trial.state;
        self.accepted_steps += 1;
        self.record(Some(gates), &trial.audits, feedback.as_ref())
    }
}

fn emit(out: &mut impl IoWrite, line: &str) -> Result<(), String> {
    writeln!(out, "{line}").map_err(|e| format!("BRIDGE_STDOUT_WRITE:{e}"))?;
    out.flush().map_err(|e| format!("BRIDGE_STDOUT_FLUSH:{e}"))
}

fn run() -> Result<(), String> {
    let args: Vec<_> = std::env::args().collect();
    if args.len() != 2 { return Err("BRIDGE_USAGE:paired_bridge S0_BI|S0_FLRW".into()); }
    let mut driver = Driver::new(&args[1])?;
    let stdout = io::stdout();
    let mut out = io::BufWriter::new(stdout.lock());
    emit(&mut out, &driver.record(None, &[], None)?)?;
    let stdin = io::stdin();
    for (index, line) in stdin.lock().lines().enumerate() {
        let line = line.map_err(|e| format!("BRIDGE_STDIN_READ:{e}"))?;
        let command = line.trim();
        if command == "QUIT" { return Ok(()); }
        let record = driver.advance(command).map_err(|e| format!("command={}:{}", index + 1, e))?;
        emit(&mut out, &record)?;
    }
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        // Emit the first failure and exit: no retry, clipping, or hidden reset.
        let line = format!("{{\"status\":\"ERROR\",\"error\":{}}}", jstr(&error));
        let _ = writeln!(io::stdout(), "{line}");
        let _ = io::stdout().flush();
        eprintln!("{error}");
        std::process::exit(1);
    }
}
