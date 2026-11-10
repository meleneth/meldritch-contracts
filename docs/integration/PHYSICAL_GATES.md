# Physical release gates

Automated and simulated checks do not constitute physical verification. The
following gates remain release blockers until executed on the designated Linux
audio workstation and recorded against `integration.lock.json`:

- PipeWire playback under representative load with no callback xruns.
- Physical MIDI input/output and Arturia MicroLab mapping.
- APC mini input, RGB feedback, page switching, and shutdown LED reset.
- Stream Deck input, feedback, disconnect, and shutdown reset.
- Native VST3 instrument load, editor attach/detach, state restoration, and
  host-wide serialized lifecycle construction.
- Parallel DSP throughput and dependency-level scheduler regression baseline.
- Full startup/shutdown with no stale audio, MIDI, APC, or Stream Deck state.

The VST3 integration suite is intentionally feature-gated in the engine and is
barred from default test/CI commands. It may be invoked only as part of an
explicit plugin-host validation session.
