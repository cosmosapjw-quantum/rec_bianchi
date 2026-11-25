//! Standalone calibrated scalar angular-frequency graph executable.
use rec_microphysics::{
    angular_line::{AngularNetwork, Edge},
    live_line::Hat,
};
use std::{
    env, fs,
    io::{BufReader, BufWriter, Read, Write},
};
fn u32r(r: &mut impl Read) -> Result<usize, String> {
    let mut b = [0; 4];
    r.read_exact(&mut b).map_err(|e| e.to_string())?;
    Ok(u32::from_le_bytes(b) as usize)
}
fn f64r(r: &mut impl Read) -> Result<f64, String> {
    let mut b = [0; 8];
    r.read_exact(&mut b).map_err(|e| e.to_string())?;
    Ok(f64::from_le_bytes(b))
}
fn vec_r(r: &mut impl Read, n: usize) -> Result<Vec<f64>, String> {
    (0..n).map(|_| f64r(r)).collect()
}
fn load(path: &str) -> Result<AngularNetwork, String> {
    let mut r = BufReader::new(fs::File::open(path).map_err(|e| e.to_string())?);
    let mut magic = [0; 8];
    r.read_exact(&mut magic).map_err(|e| e.to_string())?;
    if &magic != b"RECAWG01" {
        return Err("graph magic".into());
    }
    let n = u32r(&mut r)?;
    let ne = u32r(&mut r)?;
    let nu0 = f64r(&mut r)?;
    let dnu = f64r(&mut r)?;
    if n == 0 || n > 8192 || ne > 12_000_000 {
        return Err("graph bounds".into());
    }
    let mut x = Vec::with_capacity(n);
    let mut hats = Vec::with_capacity(n);
    let mut dirs = Vec::with_capacity(n);
    for _ in 0..n {
        let v = f64r(&mut r)?;
        let g = f64r(&mut r)?;
        let d = [f64r(&mut r)?, f64r(&mut r)?, f64r(&mut r)?];
        let nq = u32r(&mut r)?;
        if nq == 0 || nq > 256 {
            return Err("quadrature cap".into());
        }
        hats.push(Hat::new(g, vec_r(&mut r, nq)?, vec_r(&mut r, nq)?)?);
        x.push(v);
        dirs.push(d);
    }
    let mut edges = Vec::with_capacity(ne);
    for _ in 0..ne {
        edges.push(Edge {
            i: u32r(&mut r)?,
            j: u32r(&mut r)?,
            k: f64r(&mut r)?,
        });
    }
    let mut b = [0];
    if r.read(&mut b).map_err(|e| e.to_string())? != 0 {
        return Err("trailing graph bytes".into());
    }
    AngularNetwork::new(hats, x, dirs, edges, nu0, dnu)
}
fn run() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = env::args().skip(1).collect();
    if args.len() != 3 {
        return Err("usage rec_angular_line GRAPH CASE NEW_OUT".into());
    }
    let n = load(&args[0])?;
    let text = fs::read_to_string(&args[1])?;
    let mut t = text.split_whitespace();
    if t.next() != Some("rec_angular_line_case_v1") {
        return Err("case schema".into());
    }
    let dt: f64 = t.next().ok_or("dt")?.parse()?;
    let steps: usize = t.next().ok_or("steps")?.parse()?;
    if !dt.is_finite() || dt < 0. || steps > 1024 || (dt > 0. && steps == 0) {
        return Err("invalid time grid".into());
    }
    let init = t.map(str::parse::<f64>).collect::<Result<Vec<_>, _>>()?;
    if init.len() != n.hats.len() {
        return Err("case shape".into());
    }
    let action = n.action(&init)?;
    let mut f = init.clone();
    let (mut rs, mut nd, mut xd, mut pd, mut fr) = (0_f64, 0_f64, 0_f64, 0_f64, 0_f64);
    let (mut it, mut k) = (0, 0);
    let mut xc = 0.;
    let mut pc = [0.; 3];
    let start = std::time::Instant::now();
    for _ in 0..steps {
        let s = n.step(&f, dt / steps as f64)?;
        rs = rs.max(s.residual);
        nd = nd.max(s.number_defect);
        xd = xd.max(s.centered_defect);
        pd = pd.max(s.momentum_defect);
        fr = fr.max(s.free_change);
        it = it.max(s.iterations);
        k = k.max(s.krylov);
        xc += s.centered_exchange;
        for i in 0..3 {
            pc[i] += s.momentum_exchange[i]
        }
        f = s.f;
    }
    let sec = start.elapsed().as_secs_f64();
    let out = std::path::Path::new(&args[2]);
    fs::create_dir(out)?;
    let mut q = BufWriter::new(fs::File::create(out.join("state.tsv"))?);
    writeln!(
        q,
        "node\tx\tg\tex\tey\tez\tinitial_f\tfinal_f\tinitial_rate"
    )?;
    for i in 0..f.len() {
        let [x, y, z] = n.directions[i];
        writeln!(
            q,
            "{i}\t{:.17e}\t{:.17e}\t{x:.17e}\t{y:.17e}\t{z:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            n.x[i], n.hats[i].g, init[i], f[i], action.rate[i]
        )?;
    }
    q.flush()?;
    let mut file = BufWriter::new(fs::File::create(out.join("run.txt"))?);
    let norm = n.number(&init).max(f64::MIN_POSITIVE);
    writeln!(
        file,
        "scope=frozen_material_scalar_angular_frequency\nnodes={}\nedges={}\nsteps={steps}\nwall_s={sec:.17e}\ninitial_X_rate={:.17e}\ninitial_P_rate_x={:.17e}\ninitial_P_rate_y={:.17e}\ninitial_P_rate_z={:.17e}\ninitial_number_defect={:.17e}\ninitial_force_defect={:.17e}\ninitial_entropy_rate={}\ninitial_gross_X={:.17e}\ninitial_gross_P={:.17e}\ncollision_X={xc:.17e}\ncollision_P_x={:.17e}\ncollision_P_y={:.17e}\ncollision_P_z={:.17e}\ncollision_energy_j_m3={:.17e}\nnumber_defect={:.17e}\nmax_be_residual={rs:.17e}\nmax_be_number_defect={nd:.17e}\nmax_centered_defect={xd:.17e}\nmax_momentum_defect={pd:.17e}\nmax_free_increase={fr:.17e}\nmax_iterations={it}\nmax_krylov={k}\nminimum_f={:.17e}",
        n.hats.len(),
        n.edges.len(),
        action.centered,
        action.momentum[0],
        action.momentum[1],
        action.momentum[2],
        action.number_defect,
        action.force_defect,
        action.entropy_rate,
        action.gross_centered,
        action.gross_momentum,
        pc[0],
        pc[1],
        pc[2],
        xc * 6.62607015e-34 * n.dnu,
        (n.number(&f) - n.number(&init)).abs() / norm,
        f.iter().copied().fold(f64::INFINITY, f64::min)
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
