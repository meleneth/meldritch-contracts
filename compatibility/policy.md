# Compatibility policy

The Lua host API and Web protocol use independent semantic versions. Neither is
tied to the Rust crate or executable version.

## Compatible changes

A minor release may add optional fields, optional capabilities, safely
ignorable events, new command variants, or new functions that do not change
existing behavior. Consumers must ignore unknown optional response fields and
events unless their declared capability makes the event mandatory.

A patch release may clarify documentation, add fixtures, or correct an
implementation without changing the set or meaning of valid API interactions.

## Breaking changes

Removing or renaming public fields, changing field types or command semantics,
changing state ownership, strengthening required behavior, removing a
capability, or making an incompatible persistence change requires a new major
version.

Deprecation is additive. A deprecated element names its replacement and the
earliest major in which it may be removed.

## Negotiation and upgrade order

Web peers negotiate before authentication or application commands. A server
selects a version in the intersection of client and server ranges, or returns a
structured incompatibility error and closes the connection.

Lua applications declare an API range and required capabilities in their
manifest. The engine rejects an incompatible application before executing its
entry script, mutating application state, or starting audio.

For breaking changes, publish an engine that supports old and new contracts
when safe, migrate consumers, and remove the old contract only in the next
major. When dual support is unsafe, the coordinated release order and expected
compatibility failure must be explicit.

## Pinning

Release builds pin an immutable contracts Git revision, semantic versions, and
artifact SHA-256 digests. Floating branches are forbidden. Local overrides are
development-only and must not alter committed release pins.
