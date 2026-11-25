//! Positive reciprocal frequency graph with quadrature-averaged BE activity.
//! Fixed bath, scalar material frame. Backward Euler with analytic Jacobian,
//! positivity line search and explicit number / centered energy checks.
//! K = W/z0 (integrated source conductance). No HyRec FFI or history.
#[derive(Clone, Debug)]
pub struct Hat {
    pub g: f64,
    w: Vec<f64>,
    z: Vec<f64>,
    upper: f64,
    mean: f64,
}
impl Hat {
    pub fn new(g: f64, w: Vec<f64>, z: Vec<f64>) -> Result<Self, String> {
        if !g.is_finite()
            || g <= 0.
            || w.is_empty()
            || w.len() != z.len()
            || w.iter().any(|x| !x.is_finite() || *x <= 0.)
            || z.iter().any(|x| !x.is_finite() || *x <= 0.)
            || (w.iter().sum::<f64>() - 1.).abs() > 2e-12
        {
            return Err("invalid positive hat quadrature".into());
        }
        let upper = 1. / z.iter().copied().fold(0., f64::max);
        let mean = w.iter().zip(&z).map(|(w, z)| w * z).sum();
        Ok(Self {
            g,
            w,
            z,
            upper,
            mean,
        })
    }
    pub fn value(&self, a: f64) -> Result<(f64, f64), String> {
        if !a.is_finite() || a < 0. || a >= self.upper {
            return Err("outside discrete Bose activity domain".into());
        }
        let (mut f, mut df) = (0., 0.);
        for (w, z) in self.w.iter().zip(&self.z) {
            let y = a * z;
            let d = 1. - y;
            if d <= 0. {
                return Err("Bose pole".into());
            }
            f += w * y / d;
            df += w * z / (d * d);
        }
        Ok((f, df))
    }
    pub fn inverse(&self, f: f64) -> Result<f64, String> {
        if !f.is_finite() || f < 0. {
            return Err("invalid occupation".into());
        }
        if f == 0. {
            return Ok(0.);
        }
        // The finite quadrature is monotone onto [0,infinity) in
        // exact arithmetic; fail closed if the pole is unresolvable.
        let (mut lo, mut hi) = (0., self.upper);
        let mut a = f / (1. + f) / self.mean;
        if a >= hi {
            a = 0.5 * hi
        }
        for _ in 0..90 {
            let (v, d) = self.value(a)?;
            let r = v - f;
            if r.abs() <= 8. * f64::EPSILON * f {
                return Ok(a);
            }
            if r > 0. {
                hi = a
            } else {
                lo = a
            }
            let next = a - r / d;
            let b = if next > lo && next < hi {
                next
            } else {
                0.5 * (lo + hi)
            };
            if b == a || b >= self.upper {
                break;
            }
            a = b;
        }
        let (v, _) = self.value(a)?;
        if (v - f).abs() <= 8e-14 * f {
            return Ok(a);
        }
        Err("Bose activity inverse not converged".into())
    }
}
#[derive(Clone, Debug)]
pub struct Network {
    pub hats: Vec<Hat>,
    pub x: Vec<f64>,
    pub k: Vec<f64>,
}
#[derive(Clone, Debug)]
pub struct Action {
    pub rate: Vec<f64>,
    pub jac: Vec<f64>,
    pub centered: f64,
    pub gross_centered: f64,
    pub number_defect: f64,
    pub entropy_rate: f64,
}
#[derive(Clone, Debug)]
pub struct Step {
    pub f: Vec<f64>,
    pub residual: f64,
    pub number_defect: f64,
    pub centered_exchange: f64,
    pub centered_defect: f64,
    pub centered_absolute_defect: f64,
    pub iterations: usize,
    pub free_change: f64,
}
fn ksum(it: impl Iterator<Item = f64>) -> f64 {
    let (mut s, mut c) = (0., 0.);
    for v in it {
        let y = v - c;
        let t = s + y;
        c = (t - s) - y;
        s = t;
    }
    s
}
fn maxabs(v: &[f64]) -> f64 {
    v.iter().map(|x| x.abs()).fold(0., f64::max)
}
fn solve(mut a: Vec<f64>, mut b: Vec<f64>, n: usize) -> Result<Vec<f64>, String> {
    for i in 0..n {
        let j = (i..n)
            .max_by(|&j, &k| a[j * n + i].abs().total_cmp(&a[k * n + i].abs()))
            .unwrap();
        for k in i..n {
            a.swap(i * n + k, j * n + k)
        }
        b.swap(i, j);
        let pivot = a[i * n + i];
        if !pivot.is_finite() || pivot.abs() < 1e-300 {
            return Err("singular BE Jacobian".into());
        }
        for j in i + 1..n {
            let t = a[j * n + i] / pivot;
            if t == 0. {
                continue;
            }
            for k in i + 1..n {
                a[j * n + k] -= t * a[i * n + k]
            }
            b[j] -= t * b[i];
        }
    }
    for i in (0..n).rev() {
        b[i] = (b[i] - (i + 1..n).map(|j| a[i * n + j] * b[j]).sum::<f64>()) / a[i * n + i];
    }
    if b.iter().all(|v| v.is_finite()) {
        Ok(b)
    } else {
        Err("nonfinite BE correction".into())
    }
}
impl Network {
    pub fn new(hats: Vec<Hat>, x: Vec<f64>, k: Vec<f64>) -> Result<Self, String> {
        let n = hats.len();
        if n == 0
            || n > 512
            || x.len() != n
            || k.len() != n * n
            || x.iter().any(|v| !v.is_finite())
            || k.iter().any(|v| !v.is_finite() || *v < 0.)
        {
            return Err("invalid line graph".into());
        }
        for i in 0..n {
            if k[i * n + i] != 0. {
                return Err("nonzero self edge".into());
            }
            for j in i + 1..n {
                if k[i * n + j] != k[j * n + i] {
                    return Err("nonreciprocal line graph".into());
                }
            }
        }
        Ok(Self { hats, x, k })
    }
    pub fn number(&self, f: &[f64]) -> f64 {
        ksum(self.hats.iter().zip(f).map(|(a, f)| a.g * f))
    }
    pub fn centered(&self, f: &[f64]) -> f64 {
        ksum(
            self.hats
                .iter()
                .zip(f)
                .zip(&self.x)
                .map(|((a, f), x)| a.g * f * x),
        )
    }
    pub fn equilibrium(&self, a: f64) -> Result<Vec<f64>, String> {
        self.hats.iter().map(|q| q.value(a).map(|v| v.0)).collect()
    }
    pub fn action(&self, f: &[f64]) -> Result<Action, String> {
        let n = self.hats.len();
        if f.len() != n {
            return Err("line field shape".into());
        }
        let mut aa = vec![];
        let mut da = vec![];
        for (q, v) in self.hats.iter().zip(f) {
            let a = q.inverse(*v)?;
            aa.push(a);
            da.push(1. / q.value(a)?.1);
        }
        let (mut rate, mut jac) = (vec![0.; n], vec![0.; n * n]);
        let (mut centered, mut corr, mut gross, mut ngross, mut ent) = (0., 0., 0., 0., 0.);
        for i in 0..n {
            for j in i + 1..n {
                let k = self.k[i * n + j];
                if k == 0. {
                    continue;
                }
                let d = aa[j] - aa[i];
                let ai = 1. + f[i];
                let aj = 1. + f[j];
                let v = k * ai * aj * d;
                let di = k * aj * (d - ai * da[i]);
                let dj = k * ai * (d + aj * da[j]);
                let gi = self.hats[i].g;
                let gj = self.hats[j].g;
                rate[i] += v / gi;
                rate[j] -= v / gj;
                jac[i * n + i] += di / gi;
                jac[i * n + j] += dj / gi;
                jac[j * n + i] -= di / gj;
                jac[j * n + j] -= dj / gj;
                let e = v * (self.x[i] - self.x[j]);
                let y = e - corr;
                let t = centered + y;
                corr = (t - centered) - y;
                centered = t;
                gross += e.abs();
                ngross += 2. * v.abs();
                if v != 0. {
                    ent += if aa[i] == 0. || aa[j] == 0. {
                        f64::NEG_INFINITY
                    } else {
                        v * (aa[i].ln() - aa[j].ln())
                    }
                }
            }
        }
        let nd = self.number(&rate).abs() / ngross.max(f64::MIN_POSITIVE);
        if rate.iter().chain(&jac).any(|v| !v.is_finite()) || !centered.is_finite() {
            return Err("nonfinite line action".into());
        }
        Ok(Action {
            rate,
            jac,
            centered,
            gross_centered: gross,
            number_defect: nd,
            entropy_rate: ent,
        })
    }
    // F'(f)=ln(activity(f)); integrate the single-node free energy
    // in activity coordinate analytically using each quadrature state.
    pub fn free(&self, f: &[f64]) -> Result<f64, String> {
        let mut v = 0.;
        for (q, occ) in self.hats.iter().zip(f) {
            let a = q.inverse(*occ)?;
            if a == 0. {
                continue;
            }
            let term = ksum(q.w.iter().zip(&q.z).map(|(w, z)| w * (-a * z).ln_1p()));
            v += q.g * (occ * a.ln() + term);
        }
        Ok(v)
    }
    pub fn step(&self, old: &[f64], dt: f64) -> Result<Step, String> {
        if !dt.is_finite()
            || dt < 0.
            || old.len() != self.hats.len()
            || old.iter().any(|v| !v.is_finite() || *v < 0.)
        {
            return Err("invalid line time step".into());
        }
        let n = old.len();
        let scale = maxabs(old).max(f64::MIN_POSITIVE);
        let n0 = self.number(old);
        let free0 = self.free(old)?;
        let mut f = old.to_vec();
        for iter in 0..=30 {
            let a = self.action(&f)?;
            let r: Vec<_> = (0..n).map(|i| (f[i] - old[i]) - dt * a.rate[i]).collect();
            let res = maxabs(&r) / scale;
            let nd = (self.number(&f) - n0).abs() / n0.max(f64::MIN_POSITIVE);
            if res <= 2e-11 && nd <= 2e-11 {
                let de = ksum((0..n).map(|i| self.hats[i].g * (f[i] - old[i]) * self.x[i]));
                let ex = dt * a.centered;
                let diff = (de - ex).abs();
                let denom = (dt * a.gross_centered)
                    .max(n0 * self.x.iter().map(|v| v.abs()).fold(1., f64::max) * f64::EPSILON)
                    .max(f64::MIN_POSITIVE);
                return Ok(Step {
                    free_change: self.free(&f)? - free0,
                    f,
                    residual: res,
                    number_defect: nd,
                    centered_exchange: ex,
                    centered_defect: diff / denom,
                    centered_absolute_defect: diff,
                    iterations: iter,
                });
            }
            if iter == 30 {
                break;
            }
            let mut jac = a.jac;
            for i in 0..n {
                for j in 0..n {
                    jac[i * n + j] *= -dt
                }
                jac[i * n + i] += 1.
            }
            let delta = solve(jac, r.iter().map(|v| -v).collect(), n)?;
            let mut lambda = 1.;
            let mut accepted = None;
            for _ in 0..40 {
                let q: Vec<_> = f.iter().zip(&delta).map(|(v, d)| v + lambda * d).collect();
                if q.iter().all(|v| v.is_finite() && *v >= 0.) {
                    if let Ok(b) = self.action(&q) {
                        let nr = (0..n)
                            .map(|i| ((q[i] - old[i]) - dt * b.rate[i]).abs())
                            .fold(0., f64::max)
                            / scale;
                        if nr < res * (1. - 1e-4 * lambda) {
                            accepted = Some(q);
                            break;
                        }
                    }
                }
                lambda *= 0.5;
            }
            f = accepted
                .ok_or_else(|| format!("positive BE line search failed residual {res:e}"))?;
        }
        Err("positive BE not converged".into())
    }
}
