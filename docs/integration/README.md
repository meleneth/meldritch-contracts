# Four-repository integration

`integration.lock.json` records an exact compatible engine, contract release,
Lua application, and UI revision plus immutable contract artifact hashes. An
adjacent checkout is convenient but never required.

## Daily commands

With the four repositories under the same `~/code` directory, run these from
any directory:

```sh
~/code/meldritch-contracts/bin/verify
~/code/meldritch-contracts/bin/build
~/code/meldritch-contracts/bin/test
~/code/meldritch-contracts/bin/full-check
~/code/meldritch-contracts/bin/run
~/code/meldritch-contracts/bin/run self-reproducing-playground
```

The wrappers use Bash strict mode, quote every repository path, perform no
deletion, and reject missing Git checkouts. `run` accepts zero or one
application name and defaults to `network-performance`. `build` always creates
the release engine, and `run` refuses to use a debug binary because the debug
DSP path can underrun under representative workloads. `run` also supplies the
pinned Lua repository's explicit `libraries/catalog.json`; the engine has no
embedded author-library fallback. To use a non-adjacent layout, set
`MELDRITCH_ENGINE_REPO`, `MELDRITCH_LUA_REPO`, and `MELDRITCH_UI_REPO` to
absolute checkout paths.

## Direct orchestrator use

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
artifact digest is incompatible. `build` uses repository-local toolchains,
builds the engine in release mode, and never downloads source at engine
startup. `run` requires that release binary, passes absolute application and UI
artifact paths to it, and forwards termination so the engine performs its
normal MIDI, APC, Stream Deck, audio, and plugin shutdown.

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
