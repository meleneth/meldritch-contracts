# `meldritch2`

The engine facade implements graph validation/lowering, bounded DSP execution,
audio and MIDI runtime services, sequencing, persistence, Lua hosting, Web
projection, VST3 lifecycle, and hardware adapters.

The supported cross-repository API is not every Rust `pub` module. It is:

- the executable/application loading interface documented by the Lua contract;
- Lua host behavior in `lua/api.yaml`;
- HTTP/WebSocket behavior in `web/protocol.yaml` and schemas;
- persisted formats explicitly identified in those contracts;
- selected Rust integration entry points documented in engine rustdoc.

Compiler/model/runtime modules may be deliberately coupled in-process to keep
prepared data direct and realtime-safe. Their implementation-public types are
not cross-repository promises.

The control side owns Lua, filesystem/network work, validation, plugin
construction, device sessions, and publication. The audio callback consumes
prepared bounded state: no Lua, network, filesystem, contract validation,
plugin construction, unbounded allocation, or unexpected blocking locks are
permitted. Shutdown releases MIDI notes, device sessions, APC/Stream Deck LED
state, Web tasks, audio streams, and plugins in bounded host order.

Errors from authoring/loading are descriptive and occur before audio startup
where possible. Invalid network/application input must not panic. Audio-path
failures use bounded diagnostics and safe output. Serialization commitments are
limited to declared sequencer persistence, VST3 state documents, Lua manifests,
and public wire messages.
