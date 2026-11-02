# IoT code case design decisions

Recorded November 2, 2026, from the student's architecture approval and realism requirements. This is a design record; no application code or verified vulnerability cases have been produced by this documentation step.

## Accepted application direction

Build a small room temperature monitoring and fan-control system in Python, retaining Streamlit for the dashboard, Flask for the API, and PostgreSQL for storage. A device program will simulate the temperature sensor and fan instead of requiring physical hardware.

The device program sends readings and reported fan state to Flask through network requests. The dashboard obtains data through Flask and lets a user request fan changes. Flask handles access checks, storage, and command delivery; the device retrieves commands, changes its simulated fan state, and reports the outcome. Readings and actuator behavior are simulated; communication and application processing should actually execute once implemented.

Describe the study as an IoT application with simulated devices. It does not evaluate actual hardware or establish results about physical sensors, radio behavior, or deployed firmware.

## Realistic, localized vulnerabilities

- Build coherent application behavior first, preserving a baseline intended to lack the selected weaknesses. Insert controlled defects into plausible application paths.
- Do not repeat a selected weakness across every endpoint or many endpoints just to make detection easy. Prefer a localized mistake within otherwise consistent handling where that fits the weakness.
- For example, a single route might omit a required authentication check while comparable protected routes retain it, or one code path might call an inappropriate method. These illustrate realistic mistakes; they do not select authentication as a study target or establish an endpoint count.
- Do not force every vulnerability into a one-line change. Choose the smallest plausible change that produces the intended behavior and document its full effect, including shared callers if relevant.
- Use ordinary names, comments, and structure. Do not put vulnerability labels, CWE IDs, hints such as "authentication intentionally missing," or answer-key information into detector inputs.
- Aim for representative developer mistakes, not code obfuscation or artificial difficulty. Do not change scored cases in response to which weaknesses a detector catches or misses.
- Preserve target-absent controls and independently verify each selected presence and absence. Localized code can still produce a widespread effect; record the actual affected behavior.

## Realistic device behavior and interfaces

- Structure the device program like a normal device client: acquire a sensor reading, read actuator state, construct a message, authenticate, communicate with the API, process commands, and report outcomes.
- Obtain temperature through a dedicated sensor interface, such as a method for reading the current room temperature. Keep the simulated measurement implementation behind that interface so the communication code has the same responsibilities it would have with a physical sensor.
- Keep fan control behind an actuator interface that changes and reports state. A requested command and the device's reported outcome are distinct steps.
- Avoid scattering hardcoded sample temperatures or arbitrary random values through request-building code. The simulated sensor should produce a coherent sequence of readings with documented, reproducible behavior; its exact model remains to be designed.
- Include plausible device identity, measurement units, timing, command handling, and communication failure behavior as the implementation is designed. Exact message fields, routes, and retry policies remain open.
- Keep simulation provenance explicit in study documentation and setup. The goal is realistic device-facing code and interfaces, not disguising synthetic readings as physical measurements. All detectors must receive the same agreed project context.

## Next step and pending choices

Before generating application code, select and document the exact weaknesses, CWE mappings, and intended placements within the accepted credential and communication/data-handling focus areas. For each proposed placement, identify the component, intended route/function or operation, baseline behavior, controlled change, realism rationale, and verification plan. Record final file/function locations and line ranges against the preserved code version once implementation exists.

The student accepted ten weakness types on November 2; see the [complete selection](../app-idea/selected-vulnerabilities.md#november-2-selection-update). These include predictable generated credentials, disabled certificate verification, and insufficient restriction of repeated authentication attempts in addition to the original seven choices. Exact defects, CWE mappings, placements, instance count, project versions, endpoint count, database schema/library confirmation, sensor model, and file structure remain to be finalized. Keep placements within the agreed focus areas.

Keep this design record and later injection notes separate from the source packages supplied to detectors. No application code is authorized by this documentation-only request.
