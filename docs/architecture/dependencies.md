# Contract architecture

This repository defines public cross-repository behavior. It does not derive
contracts from an implementation and does not import implementation source.

The engine implements the Lua and Web contracts. Lua applications consume the
Lua contract. The Vue/Phaser UI consumes the Web contract. Shared fixtures are
black-box expectations usable by every implementation.

Rust crate documents describe supported in-process boundaries but Rust types
and the compiler remain authoritative for binary/type compatibility inside the
engine workspace.
