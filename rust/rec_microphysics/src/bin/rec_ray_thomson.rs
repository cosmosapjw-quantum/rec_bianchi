//! Native REC cold-electron ray-history consumer. One photon ray per input file.
use rec_microphysics::thomson_history::{RaySample, integrate};
use std::error::Error;
use std::fs::File;
use std::io::{self, BufRead, BufReader, Write};

const HEADER: &str =
    "normal_t_s n_reference_rest_m3 electrons_per_reference beta_x beta_y beta_z dir_x dir_y dir_z";

fn main() -> Result<(), Box<dyn Error>> {
    let args: Vec<_> = std::env::args_os().collect();
    if args.len() != 2 {
        return Err("usage: rec_ray_thomson INPUT.tsv".into());
    }
    let mut lines = BufReader::new(File::open(&args[1])?).lines();
    let header = lines.next().ok_or("empty ray history")??;
    let names: Vec<_> = header.split_whitespace().collect();
    if !(names.len() == 9 || (names.len() == 11 && names[9..] == ["N", "b"]))
        || names[..9] != HEADER.split_whitespace().collect::<Vec<_>>()
    {
        return Err(format!("expected columns {HEADER} with optional trailing N b").into());
    }
    let mut samples = Vec::new();
    for (i, line) in lines.enumerate() {
        let line = line?;
        let fields = line
            .split_whitespace()
            .map(str::parse::<f64>)
            .collect::<Result<Vec<_>, _>>()?;
        if fields.len() != names.len() || fields.iter().any(|v| !v.is_finite()) {
            return Err(format!("invalid row {}", i + 2).into());
        }
        samples.push(
            RaySample::new(
                fields[0],
                fields[1],
                fields[2],
                [fields[3], fields[4], fields[5]],
                [fields[6], fields[7], fields[8]],
            )
            .map_err(|e| format!("row {}: {e}", i + 2))?,
        );
    }
    let bins = integrate(&samples)?;
    let mut output = io::BufWriter::new(io::stdout().lock());
    writeln!(
        output,
        "near_t_s\tfar_t_s\tdelta_tau\ttau_near\ttau_far\tsurvival_near\tvisibility_mass"
    )?;
    for b in bins {
        writeln!(
            output,
            "{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            b.near_t_s,
            b.far_t_s,
            b.delta_tau,
            b.tau_near,
            b.tau_far,
            b.survival_near,
            b.visibility_mass
        )?;
    }
    output.flush()?;
    Ok(())
}
