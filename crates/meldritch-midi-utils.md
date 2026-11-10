# `meldritch-midi-utils`

Small allocation-free MIDI stream processors over `meldritch-interface`.

The initial supported processor is `KeyLock`, with `KEY_LOCK_CONTRACT`, `Scale`,
`WrongNotePolicy`, `TieBreak`, `KeyLockConfig`, construction, policy mutation,
key/note inputs, reset, and its `MidiModule` implementation. It owns scale root,
held-source reference counts, and mapped-output reference counts. The host owns
routing and timestamps.

Processing and remapping are bounded, allocation-free, nonblocking, and must
emit balanced note edges. Reset releases every referenced output. Invalid
construction returns an error and processing must not panic on untrusted MIDI.
The crate owns no device, transport, Lua/Web, audio, or persistence behavior.
Named ports and configuration semantics are compatibility commitments; internal
state has no serialization commitment.
