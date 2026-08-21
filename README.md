# Simulation Runner Workbench

A PyQt6 desktop application that launches a compiled OpenModelica
`TwoConnectedTanks` simulation executable with user-specified start and
stop times, streams its output live, and validates inputs before launch.

## What problem does this solve?

Running an OpenModelica-compiled simulation normally requires using the
terminal and remembering the correct command-line flags (`-startTime`,
`-stopTime`, etc.). This app wraps that executable in a simple desktop GUI
so a user can pick the executable, enter start/stop times, and run it with
one click — with input validation so invalid runs are caught before they
launch, rather than failing inside the simulation.

## What exact versions and OS were tested?

- **OS:** Ubuntu 24.04 (Linux)
- **OpenModelica:** 1.27.0
- **Python:** 3.13
- **PyQt6:** latest available via pip at time of writing

## How do I install and run it?

\`\`\`bash
git clone https://github.com/pragadaramanababu/openmodelica-pyqt-runner.git
cd openmodelica-pyqt-runner
pip install PyQt6 --break-system-packages
cd app
python3 main.py
\`\`\`

The GUI window will open. Click **Browse**, select the executable in
\`model/artifacts/\`, enter a start time and stop time, and click **Run**.

## How do I obtain/compile the model executable?

The original Modelica source package (\`NonInteractingTanks\`, containing
the \`TwoConnectedTanks\` model) was provided as part of the task. It was
compiled using OpenModelica's \`omc\` compiler:

\`\`\`bash
omc run_sim.mos
\`\`\`

where \`run_sim.mos\` is a small script that loads \`package.mo\` and calls
\`simulate(NonInteractingTanks.TwoConnectedTanks, ...)\`. This produces the
executable and its dependent files (\`_init.xml\`, \`_info.json\`, \`_JacA.bin\`,
\`_external_functions.json\`), all of which are included in
\`model/artifacts/\` in this repository.

**Note:** the original \`Tank2.mo\` model contained a bug — a residence-time
diagnostic variable \`T = V/Q1\` that divided by zero at initialization
(since flow \`Q1\` starts at 0 before the system reaches steady state). This
variable was unused elsewhere in the model, so it was removed rather than
guarded, since a guard clause did not resolve the compiler's own
division-safety assertion during equation flattening. See "Limitations"
below.

## What command/arguments are generated?

The app builds and passes exactly:

\`\`\`
<executable_path> -startTime=<start> -stopTime=<stop>
\`\`\`

For example: \`./NonInteractingTanks.TwoConnectedTanks -startTime=0 -stopTime=4\`

## What does a successful run produce?

The log panel streams the executable's stdout/stderr live, ending with:

\`\`\`
LOG_SUCCESS | info | The initialization finished successfully without homotopy method.
LOG_SUCCESS | info | The simulation finished successfully.
\`\`\`

The status bar shows **"Finished successfully (exit code 0)"**, and a
\`.mat\` result file is written next to the executable.

## How are invalid inputs and process errors handled?

Input is validated **before** launching, per this matrix:

| Input | Behavior |
|---|---|
| start < 0 | Rejected: "Start time must be at least 0." |
| stop >= 5 | Rejected: "Stop time must be less than 5." |
| start >= stop | Rejected: "Start time must be less than stop time." |
| non-integer / blank | Rejected with a field-specific message |
| missing/invalid executable | Rejected: "Please choose an executable." |
| valid input | Launches; Run button disables, Stop enables, output streams live |

If the process itself fails (nonzero exit code), the status bar reports
the exit code and the full stderr is visible in the log panel.

## What limitations remain?

- The \`NonInteractingTanks\` package contains two harmless, unrelated
  Modelica warnings ("connector \`flowConnect\` is not balanced") from the
  original model design — these do not affect simulation correctness and
  were left as-is, since fixing them would mean redesigning the provided
  model rather than wrapping it.
- The app currently only supports overriding start/stop time, per the task
  spec — step size and other simulation flags are not exposed in the UI.
- Tested only on Linux; Windows paths/executables are not yet verified.

## Repository layout

\`\`\`
openmodelica-pyqt-runner/
├── app/
│   ├── main.py           # entry point
│   ├── main_window.py    # GUI layout and event wiring
│   ├── models.py         # SimulationConfig data class
│   ├── validation.py     # InputValidator, validation matrix
│   └── runner.py         # QProcess wrapper for async execution
├── model/
│   └── artifacts/        # compiled executable + dependent files
├── tests/                # unit tests for validation logic
└── README.md
\`\`\`
