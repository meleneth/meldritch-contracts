# Meldritch Web protocol

`protocol.yaml` defines lifecycle, authority, and ordering. The Draft 2020-12
schema in `schemas/protocol.schema.json` defines wire messages and the semantic
control projection.

Protocol `1.0.0` preserves wire schema version 3 behavior and adds a mandatory
`hello`/`hello.accepted` negotiation before authentication or commands. State
updates remain complete authoritative value projections, not patches.

`generated/protocol.ts` is deterministic output. Run `make check` to detect
stale generated bindings and validate positive/negative fixtures.
