//! REC-owned standalone scalar live-line executable. No BASS or HyRec
//! executable, C library or recombination history. Graph compiled from
//! explicit material bath and atomic source. Prescribed local drift only.
use rec_microphysics::{
    dual_transport::{Cell, DualTransport},
    live_line::{Hat, Network},
};
use std::{
    env, fs,
    io::{BufWriter, Write},
    path::Path,
};
const H: f64 = 6.62607015e-34;
const C: f64 = 299792458.;
struct Tokens<'a>(std::str::SplitWhitespace<'a>);
impl Tokens<'_> {
    fn word(&mut self) -> Result<&str, String> {
        self.0.next().ok_or("missing token".into())
    }
    fn num<T: std::str::FromStr>(&mut self) -> Result<T, String> {
        self.word()?.parse().map_err(|_| "invalid number".into())
    }
    fn vec(&mut self, n: usize) -> Result<Vec<f64>, String> {
        (0..n).map(|_| self.num()).collect()
    }
    fn end(&mut self) -> Result<(), String> {
        if self.0.next().is_some() {
            Err("trailing input".into())
        } else {
            Ok(())
        }
    }
}
struct Mesh {
    tr: DualTransport,
    indices: Vec<[usize; 2]>,
    shares: Vec<[f64; 2]>,
    ext: usize,
}
impl Mesh {
    fn new(
        net: &Network,
        sub: usize,
        nu: f64,
        dnu: f64,
        ext: usize,
        extent: f64,
    ) -> Result<Self, String> {
        let n = net.x.len();
        let p = sub + 1;
        if ext == 0 || ext > 128 || extent <= 21.25 || sub == 0 || n != 35 * p {
            return Err("invalid scalar source transport grid".into());
        }
        let mut order = (0..35).collect::<Vec<_>>();
        order.sort_by(|i, j| net.x[i * p].total_cmp(&net.x[j * p]));
        if net.x[order[0] * p] != -21.25 || net.x[order[34] * p + sub] != 21.25 {
            return Err("invalid source faces".into());
        }
        let mut edges = (0..ext)
            .map(|i| -extent + (extent - 21.25) * i as f64 / ext as f64)
            .collect::<Vec<_>>();
        let mut indices = vec![];
        let mut shares = vec![];
        let mut vg = vec![0.; n];
        for &i in &order {
            for j in 0..sub {
                let a = i * p + j;
                let b = a + 1;
                edges.push(net.x[a]);
                indices.push([a, b]);
                let v = Self::hat(nu, dnu, net.x[a], net.x[b]);
                vg[a] += v[0];
                vg[b] += v[1];
                shares.push(v);
            }
        }
        edges.push(21.25);
        edges.extend((1..=ext).map(|i| 21.25 + (extent - 21.25) * i as f64 / ext as f64));
        for (g, h) in vg.iter().zip(&net.hats) {
            if (*g / h.g - 1.).abs() > 2e-12 {
                return Err("node phase measure mismatch".into());
            }
        }
        for (q, [a, b]) in shares.iter_mut().zip(&indices) {
            q[0] /= vg[*a];
            q[1] /= vg[*b];
        }
        Ok(Self {
            tr: DualTransport::new(edges, nu, dnu, -21.25, 21.25)?,
            indices,
            shares,
            ext,
        })
    }
    fn hat(nu: f64, dnu: f64, l: f64, r: f64) -> [f64; 2] {
        let b = dnu / nu;
        let x = 1. + b * l;
        let y = 1. + b * r;
        let scale = 8. * std::f64::consts::PI * nu * nu * dnu / C.powi(3) * (r - l) / 12.;
        [
            scale * (3. * x * x + 2. * x * y + y * y),
            scale * (x * x + 2. * x * y + 3. * y * y),
        ]
    }
    fn put(&self, net: &Network, f: &[f64], m: &mut [Cell]) {
        for (k, ([a, b], s)) in self.indices.iter().zip(&self.shares).enumerate() {
            m[self.ext + k] = Cell {
                left: net.hats[*a].g * f[*a] * s[0],
                right: net.hats[*b].g * f[*b] * s[1],
            };
        }
    }
    fn get(&self, net: &Network, m: &[Cell]) -> Vec<f64> {
        let mut f = vec![0.; net.x.len()];
        for (k, [a, b]) in self.indices.iter().enumerate() {
            let q = m[self.ext + k];
            f[*a] += q.left;
            f[*b] += q.right;
        }
        for (x, h) in f.iter_mut().zip(&net.hats) {
            *x /= h.g
        }
        f
    }
}
#[derive(Default)]
struct Ledger {
    esc: f64,
    escx: f64,
    work: f64,
    collision: f64,
    pc: f64,
    pe: f64,
    face: f64,
    ri: f64,
    ro: f64,
    bi: f64,
    bo: f64,
    nd: f64,
    xd: f64,
    zd: f64,
    zone_n: f64,
    be: f64,
    be_n: f64,
    be_x: f64,
    be_abs: f64,
    free: f64,
    it: usize,
    partition_n: f64,
    partition_x: f64,
}
fn run() -> Result<(), Box<dyn std::error::Error>> {
    let args = env::args().skip(1).collect::<Vec<_>>();
    if args.len() != 3 {
        return Err("usage rec_live_line GRAPH CASE NEW_OUT".into());
    }
    let data = fs::read_to_string(&args[0])?;
    let mut t = Tokens(data.split_whitespace());
    if t.word()? != "rec_calibrated_line_v1" {
        return Err("bad graph schema".into());
    }
    let n: usize = t.num()?;
    let sub: usize = t.num()?;
    let nu: f64 = t.num()?;
    let dnu: f64 = t.num()?;
    let tm: f64 = t.num()?;
    let n1s: f64 = t.num()?;
    if n > 512
        || n != 35 * (sub + 1)
        || !nu.is_finite()
        || !dnu.is_finite()
        || nu <= 0.
        || dnu <= 0.
        || !tm.is_finite()
        || tm <= 0.
        || !n1s.is_finite()
        || n1s < 0.
    {
        return Err("invalid calibrated graph metadata".into());
    }
    let mut hats = vec![];
    let mut x = vec![];
    for _ in 0..n {
        let v: f64 = t.num()?;
        let g: f64 = t.num()?;
        let nq: usize = t.num()?;
        if nq == 0 || nq > 256 {
            return Err("hat quadrature cap".into());
        }
        x.push(v);
        hats.push(Hat::new(g, t.vec(nq)?, t.vec(nq)?)?);
    }
    let net = Network::new(hats, x, t.vec(n * n)?)?;
    t.end()?;
    let case = fs::read_to_string(&args[1])?;
    let mut t = Tokens(case.split_whitespace());
    if t.word()? != "rec_live_line_case_v1" {
        return Err("bad case schema".into());
    }
    let dt: f64 = t.num()?;
    let steps: usize = t.num()?;
    let mut f = t.vec(n)?;
    let initial = f.clone();
    if dt < 0.
        || !dt.is_finite()
        || steps > 8192
        || steps == 0 && dt > 0.
        || f.iter().any(|v| !v.is_finite() || *v < 0.)
    {
        return Err("invalid initial state/time".into());
    }
    let flag: usize = t.num()?;
    let mut mesh = None;
    let mut cells = vec![];
    let (mut dz1, mut dz2) = (0., 0.);
    if flag != 0 {
        if steps == 0 || steps % 2 != 0 {
            return Err("live transport needs positive even step count".into());
        }
        let ext: usize = t.num()?;
        let extent: f64 = t.num()?;
        dz1 = t.num()?;
        dz2 = t.num()?;
        let m = Mesh::new(&net, sub, nu, dnu, ext, extent)?;
        let nc = m.tr.edges.len() - 1;
        cells = vec![Cell::default(); nc];
        let outside = t.vec(2 * ext)?;
        for j in 0..ext {
            for (i, o) in [(j, outside[j]), (nc - ext + j, outside[ext + j])] {
                if !o.is_finite() || o < 0. {
                    return Err("invalid exterior occupation".into());
                }
                let v = Mesh::hat(nu, dnu, m.tr.edges[i], m.tr.edges[i + 1]);
                cells[i] = Cell {
                    left: o * v[0],
                    right: o * v[1],
                };
            }
        }
        m.put(&net, &f, &mut cells);
        mesh = Some(m);
    }
    t.end()?;
    let initial_action = net.action(&f)?;
    let state = |f: &[f64], cells: &[Cell]| {
        if let Some(m) = &mesh {
            (m.tr.number(cells), m.tr.detuning(cells))
        } else {
            (net.number(f), net.centered(f))
        }
    };
    let (n0, x0) = state(&f, &cells);
    let mut l = Ledger::default();
    let mut hist = vec![(0., n0, x0, 0., 0., 0., 0.)];
    for k in 0..steps {
        let dz = if k < steps / 2 { dz1 } else { dz2 };
        let drift = |cells: &mut Vec<Cell>, l: &mut Ledger| -> Result<(), String> {
            if let Some(m) = &mesh {
                let q = m.tr.shift(cells, dz / steps as f64)?;
                l.esc += q.escaped_mass;
                l.escx += q.escaped_x;
                l.work += q.work_x;
                l.pc += q.projection_core_x;
                l.pe += q.projection_exterior_x;
                l.face += q.face_x;
                l.ri += q.red_in;
                l.ro += q.red_out;
                l.bi += q.blue_in;
                l.bo += q.blue_out;
                l.nd = l.nd.max(q.number_defect);
                l.xd = l.xd.max(q.centered_defect);
                l.zd =
                    l.zd.max(q.core_centered_defect.max(q.exterior_centered_defect));
                l.zone_n = l
                    .zone_n
                    .max(q.core_number_defect.max(q.exterior_number_defect));
                *cells = q.cells;
            }
            Ok(())
        };
        if let Some(m) = &mesh {
            drift(&mut cells, &mut l)?;
            f = m.get(&net, &cells);
        }
        let q = net.step(&f, dt / steps as f64)?;
        l.collision += q.centered_exchange;
        l.be = l.be.max(q.residual);
        l.be_n = l.be_n.max(q.number_defect);
        l.be_x = l.be_x.max(q.centered_defect);
        l.be_abs = l.be_abs.max(q.centered_absolute_defect);
        l.free = l.free.max(q.free_change);
        l.it = l.it.max(q.iterations);
        f = q.f;
        if let Some(m) = &mesh {
            let got = m.get(&net, &cells);
            let mut a = cells.clone();
            m.put(&net, &got, &mut a);
            // Repartition at shared nodes must preserve both number and X.
            let denom = m.tr.number(&cells).max(f64::MIN_POSITIVE);
            l.partition_n = l
                .partition_n
                .max((m.tr.number(&a) - m.tr.number(&cells)).abs() / denom);
            l.partition_x = l
                .partition_x
                .max((m.tr.detuning(&a) - m.tr.detuning(&cells)).abs() / (denom * 21.25));
            m.put(&net, &f, &mut cells);
            drift(&mut cells, &mut l)?;
            f = m.get(&net, &cells);
        }
        let (n, x) = state(&f, &cells);
        hist.push((
            (k + 1) as f64 * dt / steps as f64,
            n,
            x,
            l.esc,
            l.escx,
            l.work,
            l.collision,
        ));
    }
    let out = Path::new(&args[2]);
    fs::create_dir(out)?;
    let mut file = BufWriter::new(fs::File::create(out.join("state.tsv"))?);
    writeln!(file, "node\tx\tg\tinitial_f\tfinal_f\tinitial_rate")?;
    for i in 0..n {
        writeln!(
            file,
            "{i}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            net.x[i], net.hats[i].g, initial[i], f[i], initial_action.rate[i]
        )?;
    }
    file.flush()?;
    let mut file = BufWriter::new(fs::File::create(out.join("history.tsv"))?);
    writeln!(
        file,
        "time_s\tN_m3\tX_m3\tescape_N_m3\tescape_X_m3\twork_X_m3\tcollision_X_m3"
    )?;
    for q in &hist {
        writeln!(
            file,
            "{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            q.0, q.1, q.2, q.3, q.4, q.5, q.6
        )?;
    }
    file.flush()?;
    if let Some(m) = &mesh {
        let mut file = BufWriter::new(fs::File::create(out.join("full.tsv"))?);
        writeln!(file, "lo\thi\tleft_mass\tright_mass")?;
        for (i, q) in cells.iter().enumerate() {
            writeln!(
                file,
                "{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
                m.tr.edges[i],
                m.tr.edges[i + 1],
                q.left,
                q.right
            )?;
        }
        file.flush()?;
    }
    let (_, nn, xx, _, _, _, _) = *hist.last().unwrap();
    let denom = n0.max(f64::MIN_POSITIVE);
    let mut file = BufWriter::new(fs::File::create(out.join("run.txt"))?);
    writeln!(
        file,
        "scope=rec_owned_scalar_fixed_calibrated_bath_local_live_exterior\nT_m_K={tm:.17e}\nn_1s_m3={n1s:.17e}\nsteps={steps}\nnumber_defect={:.17e}\ncentered_balance_defect={:.17e}\ncentered_absolute_defect={:.17e}\ncollision_X={:.17e}\ncollision_energy_j_m3={:.17e}\ninitial_X_rate={:.17e}\ninitial_number_defect={:.17e}\ninitial_entropy_rate={}\nmax_be_residual={:.17e}\nmax_be_number_defect={:.17e}\nmax_be_centered_defect={:.17e}\nmax_be_centered_absolute_defect={:.17e}\nmax_iterations={}\nmax_free_increase={:.17e}\nmin_occupation={:.17e}\nmax_drift_number={:.17e}\nmax_drift_centered={:.17e}\nmax_zone_centered={:.17e}\nmax_zone_number={:.17e}\ncore_projection_X={:.17e}\nexterior_projection_X={:.17e}\npartition_number={:.17e}\npartition_X={:.17e}\nred_in={:.17e}\nred_out={:.17e}\nblue_in={:.17e}\nblue_out={:.17e}\nface_X={:.17e}\ninterface_atom_heat=0",
        (nn + l.esc - n0).abs() / denom,
        (xx + l.escx - x0 - l.work - l.collision).abs() / (denom * 80. + l.work.abs()),
        (xx + l.escx - x0 - l.work - l.collision).abs(),
        l.collision,
        l.collision * H * dnu,
        initial_action.centered,
        initial_action.number_defect,
        initial_action.entropy_rate,
        l.be,
        l.be_n,
        l.be_x,
        l.be_abs,
        l.it,
        l.free,
        f.iter().copied().fold(f64::INFINITY, f64::min),
        l.nd,
        l.xd,
        l.zd,
        l.zone_n,
        l.pc,
        l.pe,
        l.partition_n,
        l.partition_x,
        l.ri,
        l.ro,
        l.bi,
        l.bo,
        l.face
    )?;
    file.flush()?;
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("{e}");
        std::process::exit(1)
    }
}
