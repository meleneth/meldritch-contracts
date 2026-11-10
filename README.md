# Meldritch Contracts

Authoritative, implementation-independent public contracts for the Meldritch
engine, Lua applications, and Web UI.

Contract streams are versioned independently from engine releases:

- `lua-host-api`: the public Lua authoring/runtime API.
- `web-protocol`: the HTTP/WebSocket protocol and projected UI model.

The repository has no dependency on Rust, Vue, Phaser, or Meldritch application
source. Python 3 is sufficient to validate contracts, reproduce generated
bindings, and package release artifacts.

```sh
make check
make package
```

`make check` validates manifests and schemas, checks positive and negative
fixtures, and fails if generated TypeScript or LuaLS bindings are stale.

The dependency direction is strictly:

```text
meldritch-contracts -> described/consumed by meldritch, meldritch-lua, meldritch-ui
```

Implementation repositories pin an immutable contracts commit and declared API
versions. They may use an explicit local override during coordinated work, but
release validation always uses the pin.

See [compatibility/policy.md](compatibility/policy.md) for evolution rules and
[docs/integration/consumer-pinning.md](docs/integration/consumer-pinning.md) for
consumer integration.
