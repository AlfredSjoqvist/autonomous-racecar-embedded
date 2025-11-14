#![deny(clippy::pedantic)]

use clap::Parser;
use serial::SerialPort;
use std::io::{self, prelude::*};

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /** The port to open and write to. */
    #[arg(short, long)]
    port: String,

    /** The speed with which should be set. */
    #[arg(short, long)]
    velocity: u8,

    /** The steering angle which should be set. */
    #[arg(short, long)]
    angle: u8,

    #[arg(short, long)]
    direction: u8,
}

fn main() -> io::Result<()> {
    let args = Args::parse();
    let mut port = serial::open(&args.port)?;
    port.reconfigure(&|x| {
        x.set_baud_rate(serial::BaudRate::Baud9600)?;
        x.set_char_size(serial::CharSize::Bits8);
        x.set_parity(serial::Parity::ParityNone);
        x.set_stop_bits(serial::StopBits::Stop2);
        Ok(())
    })?;
    port.write_all(&[0, args.velocity, args.angle, args.direction])?;
    Ok(())
}
