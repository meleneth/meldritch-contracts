#!/usr/bin/env python3
"""Verify, build, test, or run an exact four-repository integration."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "integration.lock.json").read_text(encoding="utf-8"))


def command(arguments: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    print(f"[{cwd.name}] {' '.join(arguments)}", flush=True)
    return subprocess.run(arguments, cwd=cwd, check=check)


def revision(path: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=path, text=True
    ).strip()


def tracked_changes(path: Path) -> str:
    return subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=path,
        text=True,
    ).strip()


def load_pin(path: Path) -> dict:
    return json.loads((path / "contracts.lock").read_text(encoding="utf-8"))


def paths(arguments: argparse.Namespace) -> dict[str, Path]:
    result = {
        "meldritch": arguments.engine.resolve(),
        "meldritch-contracts": ROOT,
        "meldritch-lua": arguments.lua.resolve(),
        "meldritch-ui": arguments.ui.resolve(),
    }
    for name, path in result.items():
        if not (path / ".git").exists():
            raise SystemExit(f"{name} is not a Git checkout: {path}")
    return result


def verify(checkouts: dict[str, Path]) -> None:
    expected = LOCK["components"]
    failures = []
    for name, path in checkouts.items():
        actual = revision(path)
        # The contracts checkout may contain integration-tool commits after the
        # immutable API release; consumer pins must still name the locked API revision.
        if name != "meldritch-contracts" and actual != expected[name]["revision"]:
            failures.append(f"{name}: expected {expected[name]['revision']}, found {actual}")
        if tracked_changes(path):
            failures.append(f"{name}: tracked working-tree changes are not reproducible")
    contract_revision = expected["meldritch-contracts"]["revision"]
    for name in ("meldritch", "meldritch-lua", "meldritch-ui"):
        pin = load_pin(checkouts[name])
        if pin["revision"] != contract_revision:
            failures.append(f"{name}: contract pin {pin['revision']} != {contract_revision}")
        for artifact, digest in LOCK["artifacts"].items():
            if artifact in pin.get("artifacts", {}) and pin["artifacts"][artifact] != digest:
                failures.append(f"{name}: artifact digest mismatch for {artifact}")
    if failures:
        raise SystemExit("incompatible integration:\n  " + "\n  ".join(failures))
    print(f"compatible integration {LOCK['integration']}")


def build(checkouts: dict[str, Path]) -> None:
    command(["cargo", "build", "--release", "-p", "meldritch2"], checkouts["meldritch"])
    command(["npm", "ci"], checkouts["meldritch-ui"])
    command(["npm", "run", "build"], checkouts["meldritch-ui"])


def test(checkouts: dict[str, Path]) -> None:
    command(["make", "check"], checkouts["meldritch-contracts"])
    command(["python3", "tools/validate-test-policy.py"], checkouts["meldritch"])
    command(["cargo", "check", "--workspace", "--all-targets"], checkouts["meldritch"])
    command(
        ["cargo", "test", "-p", "meldritch-interface", "-p", "meldritch-arp", "-p", "meldritch-midi-utils"],
        checkouts["meldritch"],
    )
    command(["cargo", "test", "-p", "meldritch2", "--lib", "--tests"], checkouts["meldritch"])
    command(["make", "check"], checkouts["meldritch-lua"])
    command(["npm", "run", "check"], checkouts["meldritch-ui"])


def run_system(checkouts: dict[str, Path], application: str) -> None:
    binary = checkouts["meldritch"] / "target/release/meldritch2"
    ui_dist = checkouts["meldritch-ui"] / "dist"
    app = Path(application)
    if not app.is_absolute():
        app = checkouts["meldritch-lua"] / "applications" / app
    if not binary.is_file() or not ui_dist.is_dir():
        raise SystemExit("release engine or UI build missing; run the build action first")
    if not app.exists():
        raise SystemExit(f"application does not exist: {app}")
    environment = os.environ.copy()
    environment["MELDRITCH_UI_DIST"] = str(ui_dist)
    environment["MELDRITCH_LUA_CATALOG"] = str(
        checkouts["meldritch-lua"] / "libraries/catalog.json"
    )
    process = subprocess.Popen([str(binary), "perform", str(app)], env=environment)

    def stop(_signum=None, _frame=None):
        if process.poll() is None:
            process.send_signal(signal.SIGINT)
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=4)

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    try:
        while process.poll() is None:
            time.sleep(0.2)
    finally:
        stop()
    if process.returncode:
        raise SystemExit(process.returncode)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("verify", "build", "test", "run"))
    parser.add_argument("--engine", type=Path, required=True)
    parser.add_argument("--lua", type=Path, required=True)
    parser.add_argument("--ui", type=Path, required=True)
    parser.add_argument("--application", default="network-performance")
    arguments = parser.parse_args()
    checkouts = paths(arguments)
    verify(checkouts)
    if arguments.action == "build":
        build(checkouts)
    elif arguments.action == "test":
        test(checkouts)
    elif arguments.action == "run":
        run_system(checkouts, arguments.application)
    return 0


if __name__ == "__main__":
    sys.exit(main())
