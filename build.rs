use sha2::Digest;
use std::{
    env,
    io::{self, Write},
};
use std::{
    fs::{self, File},
    path::PathBuf,
};
use walkdir::WalkDir;

fn main() -> Result<(), io::Error> {
    let mut file =
        File::create(PathBuf::from(env::var("OUT_DIR").unwrap()).join("source_hashes.rs")).unwrap();

    writeln!(file, "lazy_static::lazy_static! {{")?;
    writeln!(
        file,
        "    pub(crate) static ref SOURCE_HASHES: std::collections::HashMap<&'static str, &'static str> = {{"
    )?;
    writeln!(
        file,
        "        let mut m = std::collections::HashMap::new();"
    )?;

    for entry in WalkDir::new(format!("{}/src", env!("CARGO_MANIFEST_DIR")))
        .into_iter()
        .filter_map(Result::ok)
        .filter(|e| e.file_type().is_file())
    {
        writeln!(
            file,
            "        m.insert(\"{}\", \"{}\");",
            entry.path().to_string_lossy(),
            hex::encode(sha2::Sha256::digest(&fs::read(entry.path()).unwrap()).as_slice())
        )?;
        println!("cargo:rerun-if-changed={}", entry.path().display());
    }
    writeln!(file, "        m")?;
    writeln!(file, "    }};")?;
    writeln!(file, "}}")?;

    println!("cargo:rerun-if-changed=build.rs");

    Ok(())
}
