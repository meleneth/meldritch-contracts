# `meldritch-arp`

Host-independent realtime MIDI arpeggiation over `meldritch-interface`.

Supported API: `CONTRACT`, `Mode`, `Config`, `Arpeggiator`, its validated
constructor, and its `MidiProcessor`/`MidiModule` implementations. It owns held
notes, cursor/direction, deterministic PRNG, scheduled gate-off, and transport
pause state. The host owns time, tempo, routing, and output consumption.

Construction rejects invalid octaves, rate, gate, and channel. Processing is
allocation-free, bounded to MIDI's 128 notes, nonblocking, and deterministic
for a configuration/event stream. `reset` releases active notes and clears held
state. Transport stop releases sounding notes; resume restarts scheduling from
the supplied frame. It does not own devices, threads, persistence, Lua
bindings, or audio rendering and must not know neighboring graph nodes.

Configuration meaning and named ports are compatibility commitments. No
serialized internal state is public.
