//! No cc crate: the host verifier authenticates the isolated original source.
use std::{env, path::PathBuf, process::Command};

fn run(cmd: &mut Command) {
    let rendered = format!("{cmd:?}");
    assert!(cmd.status().expect("start native compiler").success(), "{rendered}");
}

fn main() {
    let root = PathBuf::from(env::var_os("CARGO_MANIFEST_DIR").unwrap());
    let source = PathBuf::from(env::var_os("REC_HYREC2012_SRC")
        .expect("use scripts/build_r3o_rust.py to prepare/authenticate REC_HYREC2012_SRC"));
    let out = PathBuf::from(env::var_os("OUT_DIR").unwrap());
    let bridge = root.join("../../scripts/c_harness/original_hyrec_r3o_rust_bridge.c");
    let cc = env::var("CC").unwrap_or_else(|_| "cc".into());
    let ar = env::var("AR").unwrap_or_else(|_| "ar".into());
    let mut objects = Vec::new();
    for (name, path) in [("history", source.join("history.c")),
        ("hydrogen", source.join("hydrogen.c")), ("helium", source.join("helium.c")),
        ("hyrectools", source.join("hyrectools.c")), ("bridge", bridge.clone())] {
        let object = out.join(format!("{name}.o"));
        run(Command::new(&cc).args(["-std=gnu99", "-O2", "-fno-fast-math", "-ffp-contract=off", "-fPIC", "-I"])
            .arg(&source).arg("-c").arg(&path).arg("-o").arg(&object));
        println!("cargo:rerun-if-changed={}", path.display());
        objects.push(object);
    }
    run(Command::new(ar).arg("crs").arg(out.join("librec_hyrec2012.a")).args(objects));
    println!("cargo:rustc-link-search=native={}", out.display());
    println!("cargo:rustc-link-lib=static=rec_hyrec2012");
    println!("cargo:rustc-link-lib=m");
    println!("cargo:rerun-if-env-changed=REC_HYREC2012_SRC");
    println!("cargo:rerun-if-changed={}", source.join("hyrec_params.h").display());
    println!("cargo:rerun-if-changed={}", root.join("../../scripts/c_harness/original_hyrec_r3o_lowz_harness.c").display());
}
