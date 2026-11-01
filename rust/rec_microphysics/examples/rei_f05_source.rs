//! Source-authentic original REI F05 accepted 0->160 Rust material science.
use rec_microphysics::rei_f05_material::{
    ORIGINAL_F05_CELLS, SourceCell, aggregate_original_material, evaluate_source_cell,
};
use std::error::Error;
use std::fs::{self, File};
use std::io::{BufWriter, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
type R<T> = Result<T, Box<dyn Error>>;
const TAR_SHA: &str = "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b";
const INIT_SHA: &str = "7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d";
const FORCE_SHA: &str = "9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268";
const STATE_SHA: [&str; 3] = [
    "74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6",
    "a93c9a5f3cf95521322dc033d14a24a0ed8d4ed44a823ccb39720b0434c73b0a",
    "3aaff7b8cc4be8664c2d81d617d205f85f6ff974b62460a69e3839760c2fcf9c",
];
const ARRAY_SHA: &str = "cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01";
const LANES: [&str; 3] = [
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
];

fn run_cmd(program: &str, args: &[&str]) -> R<Vec<u8>> {
    let output = Command::new(program).args(args).output()?;
    if !output.status.success() {
        return Err(format!("{} failed with {:?}", program, output.status.code()).into());
    }
    Ok(output.stdout)
}
fn hash_bytes(src: &[u8]) -> R<String> {
    let mut child = Command::new("sha256sum")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()?;
    child
        .stdin
        .take()
        .ok_or("hash pipe unavailable")?
        .write_all(src)?;
    let out = child.wait_with_output()?;
    if !out.status.success() {
        return Err("hash stdin failed".into());
    }
    Ok(String::from_utf8(out.stdout)?
        .split_whitespace()
        .next()
        .ok_or("empty hash")?
        .to_owned())
}
fn check_hash(path: &Path, expected: &str) -> R<()> {
    let bytes = run_cmd("sha256sum", &[path.to_str().ok_or("nonutf8 path")?])?;
    if String::from_utf8(bytes)?.split_whitespace().next() != Some(expected) {
        return Err(format!("BYTE_SOURCE_SHA_DRIFT at {}", path.display()).into());
    }
    Ok(())
}
fn num(bytes: &[u8]) -> R<f64> {
    let raw: [u8; 8] = bytes.try_into()?;
    let value = f64::from_le_bytes(raw);
    if !value.is_finite() {
        return Err("nonfinite original IEEE state".into());
    }
    Ok(value)
}
fn npy(npz: &Path, key: &str) -> R<Vec<f64>> {
    let entry = format!("{}.npy", key);
    let raw = run_cmd("unzip", &["-p", npz.to_str().ok_or("npz path")?, &entry])?;
    if raw.len() < 16 || &raw[..6] != b"\x93NUMPY" {
        return Err("original npy magic drift".into());
    }
    let (hlen, start) = match raw[6] {
        1 => (u16::from_le_bytes(raw[8..10].try_into()?) as usize, 10usize),
        2 | 3 => (u32::from_le_bytes(raw[8..12].try_into()?) as usize, 12usize),
        _ => return Err("unsupported original npy version".into()),
    };
    let end = start + hlen;
    if end > raw.len() {
        return Err("original npy header truncated".into());
    }
    let hdr = std::str::from_utf8(&raw[start..end])?;
    if !hdr.contains("'descr': '<f8'")
        || !hdr.contains("'fortran_order': False")
        || !hdr.contains("'shape': (46080,)")
        || raw.len() != end + 8 * ORIGINAL_F05_CELLS
    {
        return Err(format!("npy contract mismatch {}", key).into());
    }
    raw[end..].chunks_exact(8).map(num).collect()
}
fn member(tar: &Path, name: &str) -> R<Vec<u8>> {
    run_cmd(
        "tar",
        &["-xOf", tar.to_str().ok_or("source tar path")?, name],
    )
}
fn state(tar: &Path) -> R<(Vec<[f64; 5]>, Vec<[f64; 5]>)> {
    let mut reference = Vec::new();
    for (index, lane) in LANES.iter().enumerate() {
        let key = format!(
            "checkpoints/generations/g-00000003-tick-000160/{}.state",
            lane
        );
        let raw = member(tar, &key)?;
        if hash_bytes(&raw)? != STATE_SHA[index] {
            return Err("accepted source lane SHA mismatch".into());
        }
        if raw.len() < 16 || &raw[..8] != b"REIADP1\0" {
            return Err("original REI state format invalid".into());
        }
        let hlen = u64::from_le_bytes(raw[8..16].try_into()?) as usize;
        let off = 16 + hlen;
        if off >= raw.len() || raw.len() - off != ORIGINAL_F05_CELLS * 12 * 8 {
            return Err("original accepted state population shape invalid".into());
        }
        let head = std::str::from_utf8(&raw[16..off])?;
        if !head.contains("\"accepted_index\":3")
            || !head.contains("\"endpoint_tick\":160")
            || !head.contains(&format!("\"lane\":\"{}\"", lane))
            || !head.contains("\"population_shape\":[46080,5]")
        {
            return Err("original accepted state provenance mismatch".into());
        }
        let data = &raw[off..];
        if hash_bytes(data)? != ARRAY_SHA {
            return Err("original numeric-state array SHA drift".into());
        }
        if index == 0 {
            reference = data.to_vec()
        } else if reference != data {
            return Err("three original lanes differ in source physical arrays".into());
        }
    }
    let mut lo = Vec::with_capacity(ORIGINAL_F05_CELLS);
    let mut hi = Vec::with_capacity(ORIGINAL_F05_CELLS);
    let offset = ORIGINAL_F05_CELLS * 5;
    for i in 0..ORIGINAL_F05_CELLS {
        let mut a = [0.0; 5];
        let mut b = [0.0; 5];
        for j in 0..5 {
            let x = (i * 5 + j) * 8;
            let y = (offset + i * 5 + j) * 8;
            a[j] = num(&reference[x..x + 8])?;
            b[j] = num(&reference[y..y + 8])?;
        }
        lo.push(a);
        hi.push(b);
    }
    Ok((lo, hi))
}
fn check_history(tar: &Path) -> R<()> {
    for (i, left, right) in [(1, 0, 64), (2, 64, 128), (3, 128, 160)] {
        let name = format!("history/accepted_{:08}.json", i);
        let raw = member(tar, &name)?;
        let s = std::str::from_utf8(&raw)?;
        if !s.contains(&format!("\"left_tick\":{}", left))
            || !s.contains(&format!("\"right_tick\":{}", right))
            || !s.contains("\"scientific_accept\":true")
        {
            return Err("original accepted 0-160 receipt chain mismatch".into());
        }
    }
    let s = String::from_utf8(member(tar, "data/results.json")?)?;
    if !s.contains("\"accepted_tick\":160") || !s.contains("\"status\":\"BLOCKED_MINIMUM_STEP\"") {
        return Err("original F05 first history owner terminal status drift".into());
    }
    Ok(())
}
fn check_clock(force: &Path) -> R<f64> {
    let csv = fs::read_to_string(force)?;
    let mut it = csv.lines();
    let header: Vec<&str> = it
        .next()
        .ok_or("missing original forcing")?
        .split(',')
        .collect();
    let index = |name: &str| {
        header
            .iter()
            .position(|x| *x == name)
            .ok_or("missing forcing field")
    };
    let ii = index("interval_index")?;
    let ni = index("node_index")?;
    let zi = index("z_mid")?;
    let ti = index("time_s")?;
    let mut n = 0;
    let mut lines = 0;
    let mut first = 0.0;
    let mut last = 0.0;
    for line in it {
        lines += 1;
        let values: Vec<&str> = line.split(',').collect();
        if values.len() != header.len() {
            return Err("forcing CSV shape drift".into());
        }
        if values[ii] != "0" {
            continue;
        }
        let t: f64 = values[ti].parse()?;
        if values[ni].parse::<usize>()? != n
            || values[zi].parse::<f64>()? != 5.95
            || !t.is_finite()
            || (n > 0 && t <= last)
        {
            return Err("first interval source redshift/clock drift".into());
        }
        if n == 0 {
            first = t
        }
        last = t;
        n += 1;
    }
    if n != 17 || lines != 85 || first != 0.0 {
        return Err("first interval forcing incomplete".into());
    }
    let t160 = (last - first) * (160.0 / 131072.0);
    if t160 != 779_495_799_866.924_8_f64 {
        return Err("original accepted tick clock mismatch".into());
    }
    Ok(t160)
}
fn write_csv(path: &Path, rows: &[rec_microphysics::rei_f05_material::MaterialWitness]) -> R<()> {
    let mut f = BufWriter::new(File::create_new(path)?);
    writeln!(
        f,
        "node,source_proper_volume_cm3,initial_tick0_n_e_cm3,accepted_tick160_n_e_lower_cm3,accepted_tick160_n_e_upper_cm3,accepted_tick0_Thomson_rate_s_inv,accepted_tick160_Thomson_rate_lower_s_inv,accepted_tick160_Thomson_rate_upper_s_inv,accepted_0_to_160_DeltaThomson_rate_lower_s_inv,accepted_0_to_160_DeltaThomson_rate_upper_s_inv,accepted_initial_H_electron_N,accepted_initial_He_electron_N,accepted_0_to_160_DeltaH_electron_lower_N,accepted_0_to_160_DeltaH_electron_upper_N,accepted_0_to_160_DeltaHe_electron_lower_N,accepted_0_to_160_DeltaHe_electron_upper_N,accepted_electron_change_sign_class"
    )?;
    for (i, x) in rows.iter().enumerate() {
        writeln!(
            f,
            "{i},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{}",
            x.volume_cm3,
            x.initial_electron / x.volume_cm3,
            x.accepted_electron_lower / x.volume_cm3,
            x.accepted_electron_upper / x.volume_cm3,
            x.gamma_initial_s,
            x.gamma_accepted_lower_s,
            x.gamma_accepted_upper_s,
            x.delta_gamma_lower_s,
            x.delta_gamma_upper_s,
            x.initial_electron_h,
            x.initial_electron_he,
            x.delta_h_lower,
            x.delta_h_upper,
            x.delta_he_lower,
            x.delta_he_upper,
            x.sign.as_str()
        )?;
    }
    f.flush()?;
    Ok(())
}
fn main() -> R<()> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 3 {
        return Err("USAGE: rei_f05_source REPO_ROOT NEW_OUTPUT_DIR".into());
    }
    let root = PathBuf::from(&args[1]);
    let out = PathBuf::from(&args[2]);
    if out.exists() {
        return Err("SCIENCE_OUTPUT_ALREADY_EXISTS_NO_OVERWRITE".into());
    }
    let src = root.join("research/rec_rei_f05_native_thomson_medium_20261101/source_inputs");
    let init = src.join("ORIGINAL_REI_F05_initial_material_state_z6.npz");
    let force = src.join("ORIGINAL_REI_F05_canonical_time_resolved_forcing_nodes.csv");
    let tar=root.join("research/rec_rei_f05_accepted_history_thomson_20261101/source_inputs/ORIGINAL_REI_F05_FIRST_INTERVAL_ACCEPTED160.tar.gz");
    check_hash(&init, INIT_SHA)?;
    check_hash(&force, FORCE_SHA)?;
    check_hash(&tar, TAR_SHA)?;
    let t160 = check_clock(&force)?;
    check_history(&tar)?;
    let (lo, hi) = state(&tar)?;
    let weights = npy(&init, "W_node")?;
    let nhi = npy(&init, "N_HI")?;
    let nhii = npy(&init, "N_HII")?;
    let nhei = npy(&init, "N_HeI")?;
    let nheii = npy(&init, "N_HeII")?;
    let nheiii = npy(&init, "N_HeIII")?;
    let mut rows = Vec::with_capacity(ORIGINAL_F05_CELLS);
    for i in 0..ORIGINAL_F05_CELLS {
        rows.push(evaluate_source_cell(SourceCell {
            weight: weights[i],
            initial: [nhi[i], nhii[i], nhei[i], nheii[i], nheiii[i]],
            accepted_lower: lo[i],
            accepted_upper: hi[i],
        })?);
    }
    let a = aggregate_original_material(&rows)?;
    if a.count != ORIGINAL_F05_CELLS || a.delta_gamma_upper_s >= 0.0 {
        return Err("accepted original physical material aggregate did not close".into());
    }
    fs::create_dir(&out)?;
    write_csv(&out.join("RUST_ACCEPTED_F05_MATERIAL_46080.csv"), &rows)?;
    let result = format!(
        concat!(
            "{{\n  \"schema\":\"REC_ORIGINAL_F05_RUST_HHE_ACCEPTED_MATERIAL_V1\",\n",
            "  \"source_tar_sha256\":\"{TAR_SHA}\",\n",
            "  \"source_initial_npz_sha256\":\"{INIT_SHA}\",\n",
            "  \"source_forcing_sha256\":\"{FORCE_SHA}\",\n",
            "  \"source_accepted_numeric_array_sha256\":\"{ARRAY_SHA}\",\n",
            "  \"source_physical_cells\":{count},\"independent_source_populations\":1,\n",
            "  \"official_accepted_tick\":160,\"total_ticks\":131072,\n",
            "  \"original_elapsed_seconds\":{time:.17e},\n",
            "  \"total_volume_cm3\":{vol:.17e},\n",
            "  \"initial_total_electron\":{e0:.17e},\n",
            "  \"accepted_lower_total_electron\":{elo:.17e},\n",
            "  \"accepted_upper_total_electron\":{ehi:.17e},\n",
            "  \"initial_mean_Thomson_rate_s_inv\":{g0:.17e},\n",
            "  \"accepted_lower_mean_Thomson_rate_s_inv\":{gl:.17e},\n",
            "  \"accepted_upper_mean_Thomson_rate_s_inv\":{gu:.17e},\n",
            "  \"accepted_lower_delta_mean_Thomson_rate_s_inv\":{dl:.17e},\n",
            "  \"accepted_upper_delta_mean_Thomson_rate_s_inv\":{du:.17e},\n",
            "  \"initial_electron_clumping\":{c0:.17e},\n",
            "  \"accepted_lower_electron_clumping\":{cl:.17e},\n",
            "  \"accepted_upper_electron_clumping\":{cu:.17e},\n",
            "  \"definite_gain_cells\":{gain},\"definite_loss_cells\":{loss},\"ambiguous_cells\":{amb},\n",
            "  \"source_status\":\"ACCEPTED_0_TO_160_MATERIAL_ONLY_NO_TICK161_NO_LOS\",\n",
            "  \"REI_canonical_DAG\":\"28/88\",\"REC_H5_physical_DAG\":\"0/313\",\n",
            "  \"production\":\"HOLD\",\"auto_next\":false}}\n"
        ),
        count = a.count,
        time = t160,
        vol = a.volume_cm3,
        e0 = a.initial_electron,
        elo = a.accepted_lower_electron,
        ehi = a.accepted_upper_electron,
        g0 = a.initial_gamma_s,
        gl = a.accepted_lower_gamma_s,
        gu = a.accepted_upper_gamma_s,
        dl = a.delta_gamma_lower_s,
        du = a.delta_gamma_upper_s,
        c0 = a.initial_clumping,
        cl = a.accepted_lower_clumping,
        cu = a.accepted_upper_clumping,
        gain = a.counts[0],
        loss = a.counts[1],
        amb = a.counts[2],
        TAR_SHA = TAR_SHA,
        INIT_SHA = INIT_SHA,
        FORCE_SHA = FORCE_SHA,
        ARRAY_SHA = ARRAY_SHA
    );
    fs::write(out.join("RUST_SCIENCE_RESULT.json"), result)?;
    println!(
        "RUST_SOURCE_PHYSICS_OK N={} accepted160_gamma={:.17e} delta_gamma={:.17e} clump_init={:.17e} sign={:?}",
        a.count, a.accepted_lower_gamma_s, a.delta_gamma_lower_s, a.initial_clumping, a.counts
    );
    Ok(())
}
