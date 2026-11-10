# VST3 host adapter contract

The engine owns discovery, stable class identity, activation, processing,
parameter changes, native editor sessions, state capture/restoration, crash
reporting, and shutdown around the pinned `vst3-host` dependency.

Plugin construction and lifecycle transitions are serialized host-wide where
required by thread-unsafe plugins and never occur in the realtime callback.
Prepared processing is bounded to declared block/channel limits. State files
carry plugin identity and integrity metadata; legacy raw component state may be
accepted only through the documented compatibility path.

The adapter does not promise the vendored crate's complete API, plugin-specific
parameter semantics, plugin availability, or portable native state across
different plugin identities/versions. Failures must not leave active notes,
editors, processes, or audio resources silently orphaned.
