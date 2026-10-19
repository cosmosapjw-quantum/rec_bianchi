mod contracts;
mod diagnostic;
mod ffi;
mod fixed;
use std::{env,fs::{self,OpenOptions},io::Write,path::PathBuf};
use serde_json::{Value,json};
use contracts::{Request,H,START,END,VIGILODE_COMMIT};

fn main() {
    let args:Vec<String>=env::args().skip(1).collect();
    let mut input=None;let mut output=None;let mut mode="all".to_string();
    let mut attempts=32usize;let mut callback_limit=2048usize;
    let mut parse_error=None;
    if args.len()%2!=0 {parse_error=Some("arguments require flag/value pairs".to_string());}
    else {
        let mut seen=std::collections::BTreeSet::new();
        for i in (0..args.len()).step_by(2) {
            if !seen.insert(args[i].clone()) {parse_error=Some("duplicate flag".into());}
            match args[i].as_str() {
                "--input"=>input=Some(PathBuf::from(&args[i+1])),
                "--output"=>output=Some(PathBuf::from(&args[i+1])),
                "--mode"=>mode=args[i+1].clone(),
                "--max-attempts"=>match args[i+1].parse(){Ok(v)=>attempts=v,Err(_)=>parse_error=Some("invalid attempt cap".into())},
                "--callback-limit"=>match args[i+1].parse(){Ok(v)=>callback_limit=v,Err(_)=>parse_error=Some("invalid callback cap".into())},
                _=>parse_error=Some(format!("unknown flag {}",args[i])),
            }
        }
    }
    let Some(out)=output else {eprintln!("usage: rec-hyrec-vigilode --input REQUEST.json --output NEW.json [--mode all|fixed|diagnostic] [--max-attempts 1..32] [--callback-limit 1..2048]");std::process::exit(2);};
    // Reserve before numerical work. Existing evidence is never overwritten.
    let mut stream=match OpenOptions::new().write(true).create_new(true).open(&out) {
        Ok(s)=>s,Err(e)=>{eprintln!("R3O_OUTPUT_CREATE_ONLY:{}:{e}",out.display());std::process::exit(2);}
    };
    let mut report=json!({"schema":"rec.r3o.rust-output.v1","status":"ERROR","h2":H,"start_iz":START,"end_iz":END,
        "vigilode_commit":VIGILODE_COMMIT,"command":env::args().collect::<Vec<_>>(),
        "historical_status":{"u5_original_h":"HOLD_9_FAIL","u5_h2":"HOLD_8_FAIL","budget":"CLOSED_HOLD_NOT_RESET","REI_activation":false},
        "full_153327_steps":"NOT_RUN","global_convergence":"NOT_RUN","speedup":"NOT_RUN","production_admission":false});
    let result=(|| -> Result<bool,String> {
        if let Some(e)=parse_error {return Err(e);}
        if !["all","fixed","diagnostic"].contains(&mode.as_str()) || !(1..=32).contains(&attempts)
            || !(1..=2048).contains(&callback_limit) {return Err("R3O_CLI_MODE_OR_CAP".into());}
        let p=input.ok_or("input required")?;
        if fs::metadata(&p).map_err(|e|e.to_string())?.len()>1024*1024 {return Err("input exceeds 1 MiB bound".into());}
        let text=fs::read_to_string(&p).map_err(|e|e.to_string())?;
        let raw:Value=serde_json::from_str(&text).map_err(|e|e.to_string())?;
        report["input"]=raw;
        let req:Request=serde_json::from_str(&text).map_err(|e|e.to_string())?;
        ffi::initialize().map_err(|e|e.to_string())?;
        req.validate().map_err(|e|e.to_string())?;
        report["input_hashes"]=req.input_hashes.clone();
        let mut success=true;
        if mode=="all" || mode=="fixed" {
            let r=fixed::run(&req).map_err(|e|e.to_string())?;
            success &= r["success"]==true;report["fixed"]=r;
        }
        if mode=="all" || mode=="diagnostic" {
            let r=diagnostic::run(&req,attempts,callback_limit).map_err(|e|e.to_string())?;
            success &= r["success"]==true;report["diagnostic"]=r;
        }
        Ok(success)
    })();
    let exit_code=match result {Ok(true)=>{report["status"]=json!("BOUNDED_PASS");0},
        Ok(false)=>{report["status"]=json!("BOUNDED_FAILURE");3},
        Err(e)=>{report["error"]=json!(e);2}};
    report["exit_code"]=json!(exit_code);
    if let Err(e)=serde_json::to_writer_pretty(&mut stream,&report).map_err(std::io::Error::other)
        .and_then(|_|stream.write_all(b"\n")).and_then(|_|stream.sync_all()) {
        eprintln!("R3O_EVIDENCE_WRITE_FAILURE:{e}");std::process::exit(2);
    }
    eprintln!("R3O_RESULT:{}:{}",report["status"],out.display());
    std::process::exit(exit_code);
}
