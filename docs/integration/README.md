# Four-repository integration

`integration.lock.json` records an exact compatible engine, contract release,
Lua application, and UI revision plus immutable contract artifact hashes. An
adjacent checkout is convenient but never required.

```sh
python3 tools/integrate.py verify \
  --engine /work/engine \
  --lua /other/location/apps \
  --ui /tmp/frontend

python3 tools/integrate.py build --engine /work/engine --lua /other/location/apps --ui /tmp/frontend
python3 tools/integrate.py test  --engine /work/engine --lua /other/location/apps --ui /tmp/frontend
python3 tools/integrate.py run   --engine /work/engine --lua /other/location/apps --ui /tmp/frontend --application network-performance
```

`verify` fails before mutation if a component revision, contract pin, or
artifact digest is incompatible. `build` uses repository-local toolchains and
never downloads source at engine startup. `run` passes absolute application and
UI artifact paths to an already-built engine and forwards termination so the
engine performs its normal MIDI, APC, Stream Deck, audio, and plugin shutdown.

## Coordinated changes

1. Change and independently validate the authoritative contract.
2. Commit/publish its immutable revision and artifacts.
3. Update implementation and consumer pins on matching feature branches.
4. Run repository-local checks, then this integration test action.
5. Record the four accepted revisions in a new integration lock.
6. Promote consumers in additive-compatible order; for breaking changes,
   upgrade implementations before enabling the new negotiated major version.

Ordinary UI or Lua work stays within its repository and published contract.
No consumer uses a floating branch, Rust source path, or adjacent-checkout
relative dependency.
