#[macro_use]
extern crate lazy_static;

use std::process::Command;

use exonum::runtime::Runtime;

mod errors;
mod pending_deployment;
mod python_interface;
mod runtime;
mod types;

use runtime::PythonRuntime;

pub use python_interface::init_python_side;

// TODO return result
pub fn initialize_python_backend(python_config_path: &str) -> Option<Box<dyn Runtime>> {
    let python_run_command = Command::new("python")
        .arg("-m runtime")
        .arg(python_config_path)
        .spawn();

    let python_process = match python_run_command {
        Ok(handle) => handle,
        Err(_) => return None,
    };

    let python_runtime = PythonRuntime::new(python_process);

    Some(Box::new(python_runtime))
}
