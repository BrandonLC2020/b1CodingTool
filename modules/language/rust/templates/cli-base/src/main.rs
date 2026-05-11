use anyhow::{Context, Result};
use clap::Parser;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// Name of the person to greet
    #[arg(short, long)]
    name: String,
}

fn main() -> Result<()> {
    tracing_subscriber::fmt::init();

    let args = Args::parse();
    
    // Example of context usage
    run(&args.name).context("Failed to execute run logic")?;

    Ok(())
}

fn run(name: &str) -> Result<()> {
    tracing::info!("Hello, {}!", name);
    Ok(())
}
