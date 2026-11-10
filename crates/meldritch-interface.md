# `meldritch-interface`

## Purpose and supported API

The allocation-free base contract for graph DSP descriptors and timestamped
MIDI processors. Supported items are `Domain`, `FanIn`, `Role`, `InputPort`,
`OutputPort`, `Param`, `ProcessFn`, `Contract`, `MidiMessage`, `MidiEvent`,
`MidiPort`, `MidiModuleContract`, `Tempo`, `MidiModuleContext`, `MidiProcessor`,
and `MidiModule`.

It owns value semantics and processing traits, but no device, graph, transport,
allocation, thread, or persistence state. It depends on no other Meldritch
crate. Host-agnostic processors depend on it; the engine adapts them.

## Lifecycle, threading, and realtime behavior

Descriptors are immutable `'static` data. MIDI modules are constructed and
owned by the host, receive ordered timestamped events, may be reset explicitly,
and are `Send`. Implementations must not allocate, block, access files/network,
or panic during processing. A process function receives host-validated buffers
and must remain bounded by their lengths.

Errors belong to construction/validation; realtime traits report through
bounded host diagnostics rather than unwinding. No serialization format is
promised. Additive enum variants or required trait methods are breaking unless
made non-exhaustive/defaulted in a compatible major design.

## Non-responsibilities

No graph compilation, audio device, scheduling policy, Lua/Web API, MIDI device
I/O, plugin hosting, or application behavior.
