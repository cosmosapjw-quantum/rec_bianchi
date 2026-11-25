//! REC-owned nonseparable scalar angular-frequency collision graph.
//! Positive symmetric source events; equilibrium-aware BE, matrix-free
//! analytic JVP and restarted GMRES. Frozen material clock/bath.
//! Angular projection is a finite quadrature closure, not exact continuum.
use crate::live_line::Hat;
#[derive(Clone, Copy, Debug)]
pub struct Edge {
    pub i: usize,
    pub j: usize,
    pub k: f64,
}
#[derive(Clone, Debug)]
pub struct AngularNetwork {
    pub hats: Vec<Hat>,
    pub x: Vec<f64>,
    pub directions: Vec<[f64; 3]>,
    pub edges: Vec<Edge>,
    pub nu0: f64,
    pub dnu: f64,
}
#[derive(Clone, Debug)]
pub struct Action {
    pub rate: Vec<f64>,
    pub centered: f64,
    pub momentum: [f64; 3],
    pub gross_centered: f64,
    pub gross_momentum: f64,
    pub number_defect: f64,
    pub force_defect: f64,
    pub entropy_rate: f64,
}
#[derive(Clone, Debug)]
pub struct AngularStep {
    pub f: Vec<f64>,
    pub residual: f64,
    pub number_defect: f64,
    pub centered_exchange: f64,
    pub momentum_exchange: [f64; 3],
    pub centered_defect: f64,
    pub momentum_defect: f64,
    pub iterations: usize,
    pub krylov: usize,
    pub free_change: f64,
}
#[derive(Clone, Copy, Default)]
struct Kahan(f64, f64);
impl Kahan {
    fn add(&mut self, x: f64) {
        let y = x - self.1;
        let t = self.0 + y;
        self.1 = (t - self.0) - y;
        self.0 = t;
    }
}
fn sum(it: impl Iterator<Item = f64>) -> f64 {
    let mut s = Kahan::default();
    for x in it {
        s.add(x)
    }
    s.0
}
fn dot(a: &[f64], b: &[f64]) -> f64 {
    sum(a.iter().zip(b).map(|(x, y)| x * y))
}
fn norm(v: &[f64]) -> f64 {
    dot(v, v).sqrt()
}
fn maxabs(v: &[f64]) -> f64 {
    v.iter().map(|x| x.abs()).fold(0., f64::max)
}
struct Lin {
    di: Vec<f64>,
    dj: Vec<f64>,
    diag: Vec<f64>,
}
impl AngularNetwork {
    pub fn new(
        hats: Vec<Hat>,
        x: Vec<f64>,
        directions: Vec<[f64; 3]>,
        edges: Vec<Edge>,
        nu0: f64,
        dnu: f64,
    ) -> Result<Self, String> {
        let n = hats.len();
        if n == 0
            || n > 8192
            || x.len() != n
            || directions.len() != n
            || edges.len() > 12_000_000
            || !nu0.is_finite()
            || !dnu.is_finite()
            || nu0 <= 0.
            || dnu <= 0.
            || x.iter().any(|x| !x.is_finite() || nu0 + dnu * x <= 0.)
            || directions
                .iter()
                .any(|v| (dot(v, v) - 1.).abs() > 2e-12 || v.iter().any(|x| !x.is_finite()))
        {
            return Err("invalid angular network dimensions".into());
        }
        if edges
            .iter()
            .any(|e| e.i >= e.j || e.j >= n || !e.k.is_finite() || e.k <= 0.)
            || edges
                .windows(2)
                .any(|e| (e[0].i, e[0].j) >= (e[1].i, e[1].j))
        {
            return Err("invalid or duplicate angular event edge".into());
        }
        Ok(Self {
            hats,
            x,
            directions,
            edges,
            nu0,
            dnu,
        })
    }
    fn p(&self, i: usize) -> [f64; 3] {
        self.directions[i].map(|e| e * (1. + self.dnu / self.nu0 * self.x[i]))
    }
    pub fn number(&self, f: &[f64]) -> f64 {
        sum(self.hats.iter().zip(f).map(|(h, v)| h.g * v))
    }
    pub fn free(&self, f: &[f64]) -> Result<f64, String> {
        let mut s = Kahan::default();
        for (h, v) in self.hats.iter().zip(f) {
            s.add(h.g * h.free_primitive(*v)?)
        }
        Ok(s.0)
    }
    fn evaluate(&self, f: &[f64], linear: bool) -> Result<(Action, Option<Lin>), String> {
        let n = self.hats.len();
        if f.len() != n {
            return Err("angular field shape".into());
        }
        let mut a = Vec::with_capacity(n);
        let mut da = Vec::with_capacity(n);
        for (h, v) in self.hats.iter().zip(f) {
            let x = h.inverse(*v)?;
            a.push(x);
            da.push(1. / h.value(x)?.1);
        }
        let logs: Vec<_> = a.iter().map(|x| x.ln()).collect();
        let p: Vec<_> = (0..n).map(|i| self.p(i)).collect();
        let mut rate = vec![0.; n];
        let mut xc = Kahan::default();
        let mut pc = [Kahan::default(); 3];
        let (mut gx, mut gp, mut gn, mut ent) = (0., 0., 0., 0.);
        let mut lin = if linear {
            Some(Lin {
                di: Vec::with_capacity(self.edges.len()),
                dj: Vec::with_capacity(self.edges.len()),
                diag: vec![0.; n],
            })
        } else {
            None
        };
        for e in &self.edges {
            let i = e.i;
            let j = e.j;
            let ai = 1. + f[i];
            let aj = 1. + f[j];
            let d = a[j] - a[i];
            let v = e.k * ai * aj * d;
            rate[i] += v;
            rate[j] -= v;
            let dx = v * (self.x[i] - self.x[j]);
            xc.add(dx);
            gx += dx.abs();
            gn += 2. * v.abs();
            for k in 0..3 {
                let dp = v * (p[i][k] - p[j][k]);
                pc[k].add(dp);
                gp += dp.abs();
            }
            if v != 0. {
                ent += if a[i] == 0. || a[j] == 0. {
                    f64::NEG_INFINITY
                } else {
                    v * (logs[i] - logs[j])
                }
            }
            if let Some(l) = &mut lin {
                let di = e.k * aj * (d - ai * da[i]);
                let dj = e.k * ai * (d + aj * da[j]);
                l.di.push(di);
                l.dj.push(dj);
                l.diag[i] += di / self.hats[i].g;
                l.diag[j] -= dj / self.hats[j].g;
            }
        }
        let nd = sum(rate.iter().copied()).abs() / gn.max(f64::MIN_POSITIVE);
        let xd = (sum(rate.iter().zip(&self.x).map(|(r, x)| r * x)) - xc.0).abs()
            / gx.max(f64::MIN_POSITIVE);
        let pd = (0..3)
            .map(|k| {
                (sum(rate.iter().zip(&p).map(|(r, p)| r * p[k])) - pc[k].0).abs()
                    / gp.max(f64::MIN_POSITIVE)
            })
            .fold(0., f64::max);
        for (r, h) in rate.iter_mut().zip(&self.hats) {
            *r /= h.g
        }
        if rate.iter().any(|v| !v.is_finite())
            || !xc.0.is_finite()
            || pc.iter().any(|x| !x.0.is_finite())
        {
            return Err("nonfinite angular action".into());
        }
        Ok((
            Action {
                rate,
                centered: xc.0,
                momentum: pc.map(|s| s.0),
                gross_centered: gx,
                gross_momentum: gp,
                number_defect: nd,
                force_defect: xd.max(pd),
                entropy_rate: ent,
            },
            lin,
        ))
    }
    pub fn action(&self, f: &[f64]) -> Result<Action, String> {
        Ok(self.evaluate(f, false)?.0)
    }
    fn jvp(&self, l: &Lin, v: &[f64]) -> Vec<f64> {
        let mut r = vec![0.; v.len()];
        for (e, (&di, &dj)) in self.edges.iter().zip(l.di.iter().zip(&l.dj)) {
            let q = di * v[e.i] + dj * v[e.j];
            r[e.i] += q;
            r[e.j] -= q;
        }
        for (x, h) in r.iter_mut().zip(&self.hats) {
            *x /= h.g
        }
        r
    }
    pub fn step(&self, old: &[f64], dt: f64) -> Result<AngularStep, String> {
        if old.len() != self.hats.len()
            || !dt.is_finite()
            || dt < 0.
            || old.iter().any(|v| !v.is_finite() || *v < 0.)
        {
            return Err("invalid angular step".into());
        }
        let scale = maxabs(old).max(f64::MIN_POSITIVE);
        let n0 = self.number(old);
        let free0 = self.free(old)?;
        let mut f = old.to_vec();
        let mut krylov = 0;
        for it in 0..=24 {
            let (a, l) = self.evaluate(&f, true)?;
            let l = l.unwrap();
            let r: Vec<_> = (0..f.len())
                .map(|i| (f[i] - old[i] - dt * a.rate[i]) / scale)
                .collect();
            let res = maxabs(&r);
            let nd = (self.number(&f) - n0).abs() / n0.max(f64::MIN_POSITIVE);
            if res <= 2e-11 && nd <= 2e-11 {
                let de = sum((0..f.len()).map(|i| self.hats[i].g * (f[i] - old[i]) * self.x[i]));
                let ex = dt * a.centered;
                let md = a.momentum.map(|v| dt * v);
                let den = (dt * a.gross_centered)
                    .max(n0 * maxabs(&self.x).max(1.) * f64::EPSILON)
                    .max(f64::MIN_POSITIVE);
                let pden = (dt * a.gross_momentum)
                    .max(n0 * f64::EPSILON)
                    .max(f64::MIN_POSITIVE);
                let pd = (0..3)
                    .map(|k| {
                        (sum((0..f.len()).map(|i| self.hats[i].g * (f[i] - old[i]) * self.p(i)[k]))
                            - md[k])
                            .abs()
                            / pden
                    })
                    .fold(0., f64::max);
                return Ok(AngularStep {
                    free_change: self.free(&f)? - free0,
                    f,
                    residual: res,
                    number_defect: nd,
                    centered_exchange: ex,
                    momentum_exchange: md,
                    centered_defect: (de - ex).abs() / den,
                    momentum_defect: pd,
                    iterations: it,
                    krylov,
                });
            }
            if it == 24 {
                break;
            }
            let diag: Vec<_> = l.diag.iter().map(|v| 1. - dt * v).collect();
            if diag.iter().any(|v| !v.is_finite() || v.abs() < 1e-30) {
                return Err("invalid BE preconditioner".into());
            }
            let b: Vec<_> = r.iter().zip(&diag).map(|(r, d)| -r / d).collect();
            let (delta, k) = gmres(&b, |v| {
                let j = self.jvp(&l, v);
                (0..v.len()).map(|i| (v[i] - dt * j[i]) / diag[i]).collect()
            })?;
            krylov += k;
            let mut lambda = 1.;
            let mut found = None;
            for _ in 0..40 {
                let q: Vec<_> = f
                    .iter()
                    .zip(&delta)
                    .map(|(v, d)| v + lambda * scale * d)
                    .collect();
                if q.iter().all(|v| v.is_finite() && *v >= 0.) {
                    if let Ok(b) = self.action(&q) {
                        let nr = (0..q.len())
                            .map(|i| ((q[i] - old[i]) - dt * b.rate[i]).abs() / scale)
                            .fold(0., f64::max);
                        if nr < res * (1. - 1e-4 * lambda) {
                            found = Some(q);
                            break;
                        }
                    }
                }
                lambda *= 0.5;
            }
            f = found
                .ok_or_else(|| format!("angular positivity line search failed residual={res:e}"))?;
        }
        Err("angular BE did not converge".into())
    }
}
/// Left-preconditioned restarted GMRES with two MGS passes. No dense
/// N^2 Jacobian, O(edges) matvec, bounded 32-vector Krylov storage.
fn gmres<F: Fn(&[f64]) -> Vec<f64>>(b: &[f64], op: F) -> Result<(Vec<f64>, usize), String> {
    let n = b.len();
    let bn = norm(b);
    let mut x = vec![0.; n];
    let mut count = 0;
    if bn == 0. {
        return Ok((x, 0));
    }
    let tol = 2e-11 * bn;
    let m = 32.min(n);
    for _ in 0..12 {
        let ax = op(&x);
        let r: Vec<_> = b.iter().zip(ax).map(|(b, a)| b - a).collect();
        let beta = norm(&r);
        if beta <= tol {
            return Ok((x, count));
        }
        let mut basis = vec![r.iter().map(|v| v / beta).collect::<Vec<_>>()];
        let mut h = vec![vec![0.; m]; m + 1];
        let mut cs = vec![0.; m];
        let mut sn = vec![0.; m];
        let mut rhs = vec![0.; m + 1];
        rhs[0] = beta;
        let mut used = 0;
        for j in 0..m {
            let mut v = op(&basis[j]);
            count += 1;
            for _ in 0..2 {
                for i in 0..=j {
                    let a = dot(&v, &basis[i]);
                    h[i][j] += a;
                    for (k, vk) in v.iter_mut().enumerate() {
                        *vk -= a * basis[i][k]
                    }
                }
            }
            let next = norm(&v);
            h[j + 1][j] = next;
            for i in 0..j {
                let a = h[i][j];
                let b = h[i + 1][j];
                h[i][j] = cs[i] * a + sn[i] * b;
                h[i + 1][j] = -sn[i] * a + cs[i] * b;
            }
            let d = h[j][j].hypot(h[j + 1][j]);
            if !d.is_finite() || d == 0. {
                return Err("angular GMRES breakdown".into());
            }
            cs[j] = h[j][j] / d;
            sn[j] = h[j + 1][j] / d;
            h[j][j] = d;
            h[j + 1][j] = 0.;
            rhs[j + 1] = -sn[j] * rhs[j];
            rhs[j] *= cs[j];
            used = j + 1;
            if rhs[j + 1].abs() <= tol || next <= 1e-15 * d {
                break;
            }
            basis.push(v.iter().map(|v| v / next).collect());
        }
        let mut y = vec![0.; used];
        for i in (0..used).rev() {
            y[i] = (rhs[i] - (i + 1..used).map(|j| h[i][j] * y[j]).sum::<f64>()) / h[i][i]
        }
        for i in 0..used {
            for (k, xk) in x.iter_mut().enumerate() {
                *xk += y[i] * basis[i][k]
            }
        }
    }
    let ax = op(&x);
    let r: Vec<_> = b.iter().zip(ax).map(|(b, a)| b - a).collect();
    if norm(&r) <= tol {
        Ok((x, count))
    } else {
        Err(format!(
            "angular GMRES not converged ratio={:e}",
            norm(&r) / bn
        ))
    }
}
