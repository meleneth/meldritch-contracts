# Physical release gates

## 2026-11-10 fracture checkpoint

Automated integration passed for the revisions in `integration.lock.json`:

- Contract validation, negative fixtures, generated-file freshness, and two
  consecutive deterministic package builds passed.
- Rust workspace checking and tests passed: 234 engine library tests, the
  retained crate suites, and every non-VST3 integration target. The one real
  upstream sample-download check remained intentionally ignored.
- All 15 Lua application manifests, syntax checks, and mock-host tests passed.
- UI contract validation, typechecking, formatting, 36 unit tests, and the
  independent production build passed.
- `network-performance` started from the independent Lua checkout with the
  independent UI bundle, opened the default 48 kHz audio device, served HTTP
  on localhost, and shut down without a remaining process or listener.

Attached-device inventory found an Arturia MicroLab mk3, APC mini mk2, and
Stream Deck XL. `self-reproducing-playground` opened the MicroLab input and
ran its real hardware-enabled application path. A debug build reported two
audio buffer underrun/overrun events, which is why the integration wrappers now
require a release build. The same bounded startup and shutdown through the
release-only `bin/run` wrapper completed with no reported xruns and exit code
zero. Visual LED reset, physical gestures, disconnect/reconnect, sustained-load
listening, and latency checks were not observed by a human and remain
unverified. No VST3 integration test or plugin lifecycle session was run.

Automated and simulated checks do not constitute physical verification. The
following gates remain release blockers until they pass on the designated
Linux audio workstation and are recorded against `integration.lock.json`:

- PipeWire playback under representative load with no callback xruns.
- Physical MIDI input/output and Arturia MicroLab mapping.
- APC mini input, RGB feedback, page switching, and shutdown LED reset.
- Stream Deck input, feedback, disconnect, and shutdown reset.
- Native VST3 instrument load, editor attach/detach, state restoration, and
  host-wide serialized lifecycle construction.
- Parallel DSP throughput and dependency-level scheduler regression baseline.
- Sustained representative-load operation with no xruns or stale audio, MIDI,
  APC, or Stream Deck state. Bounded release startup/shutdown passed; the debug
  binary is deliberately unsupported by the integration runner.

The VST3 integration suite is intentionally feature-gated in the engine and is
barred from default test/CI commands. It may be invoked only as part of an
explicit plugin-host validation session.
