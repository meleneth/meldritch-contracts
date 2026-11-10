# Lua host API

`api.yaml` is the authoritative supported author API. It is JSON-compatible
YAML so validation and generation need only Python's standard library.

The engine implements the API and reports `meldritch.host_api_version()` plus
`meldritch.host_capabilities()`. Applications declare a compatible range and
required capability IDs in an `application.json` validated by
`schemas/application.schema.json`.

## Application libraries

The optional `libraries` array contains exact public library identifiers, not
filesystem paths. Before executing an application's entry script, the host
must resolve every declared identifier from a configured catalog validated by
`schemas/library-catalog.schema.json`. The catalog path is deployment
configuration and is never inferred from the Rust checkout or application
directory.

Each catalog entry names one catalog-relative Lua file, its library version,
compatible Lua host API range, and SHA-256 digest. The host must reject a
missing identifier, incompatible host range, duplicate identifier, escaping
path, unreadable file, or digest mismatch before application code executes.
Only explicitly declared libraries are evaluated. Each library returns the
table installed at the dot-separated public namespace named by its identifier;
for example `meldritch.musical` installs the returned table as
`meldritch.musical`. Undeclared catalog entries are neither read nor evaluated.

Applications with no `libraries` field require no catalog. Standalone entry
files have no implicit author libraries. Library resolution and evaluation are
control-thread startup work and must never occur in an audio callback.

Private bootstrap names beginning with `_` are intentionally absent. The
engine-owned prelude may use them, but applications must not.

Run `make generate` at the repository root to reproduce LuaLS annotations in
`types/meldritch.lua`. The generated file is consumer developer support; this
manifest remains authoritative.
