//! Input on stdin, one comma-separated point per line (blank/# lines ignored).
//! source: T_K,nH_m3,H_s,xp,x2
//! frozen: nH_m3,alphaB_m3_s,betaP_s,Lambda_s,Ralpha_s,b_Lya,xp,x2
use rec_microphysics::hydrogen_peebles::*;
use std::io::{self, BufRead};
fn run() -> Result<(), String> {
    let mode = std::env::args().nth(1).ok_or("mode required: source or frozen")?;
    if mode != "source" && mode != "frozen" { return Err("unknown mode".into()); }
    println!("row,alpha_b_m3_s,r_alpha_s,beta_p_s,beta_shell_s,d_ground_s,b_lya,c_factor,x1,continuum_flux,ground_flux,dxp_dt,dx2_dt,dx1_dt,peebles_dt,qss_fixed_ground,defect_direct,defect_lag,defect_depletion,defect_reconstructed");
    for (idx, line) in io::stdin().lock().lines().enumerate() {
        let line = line.map_err(|e| e.to_string())?;
        if line.trim().is_empty() || line.trim_start().starts_with('#') { continue; }
        let nums: Vec<f64> = line.split(',').map(|s| s.trim().parse::<f64>())
            .collect::<Result<_, _>>().map_err(|e| format!("row {}: {e}", idx+1))?;
        let (n, alpha, r_alpha, rates, state) = if mode == "source" {
            if nums.len()!=5 { return Err(format!("row {}: source needs 5 fields",idx+1)); }
            let state=RetainedState{xp:nums[3],x2:nums[4]};
            let p=hyrec2_one_temperature_source(nums[0],nums[0],nums[1],nums[2],state)
                .map_err(|e|format!("row {}: {e:?}",idx+1))?;
            (nums[1],p.alpha_b_m3_s,p.r_alpha_s,p.rates,state)
        } else {
            if nums.len()!=8 { return Err(format!("row {}: frozen needs 8 fields",idx+1)); }
            let rates=ShellRates::new(nums[2],nums[3],nums[4],nums[5])
                .map_err(|e|format!("row {}: {e:?}",idx+1))?;
            (nums[0],nums[1],nums[4],rates,RetainedState{xp:nums[6],x2:nums[7]})
        };
        let (rhs,peebles,qss,defect,x1)=(|| -> Result<_,HydrogenError>{
            let rhs=retained_rhs(n,alpha,rates,state)?;
            let peebles=peebles_rhs(n,alpha,rates,state.xp)?;
            let x1=state.ground()?;
            Ok((rhs,peebles,qss_at_fixed_ground(n,alpha,rates,state.xp,x1)?,
                closure_defect(n,alpha,rates,state)?,x1))
        })().map_err(|e|format!("row {}: {e:?}",idx+1))?;
        print!("{}",idx+1);
        for v in [alpha,r_alpha,rates.beta_p_s(),rates.beta_shell_s(),rates.d_ground_s(),
                  rates.boltzmann_lya(),rates.c_factor(),x1,rhs.continuum_flux,
                  rhs.ground_flux,rhs.dxp_dt,rhs.dx2_dt,rhs.dx1_dt,peebles,qss,
                  defect.direct,defect.shell_lag,defect.ground_depletion,defect.reconstructed] {
            print!(",{v:.17e}");
        }
        println!();
    }
    Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("{e}");std::process::exit(2)}}
