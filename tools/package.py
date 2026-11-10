#!/usr/bin/env python3
"""Create deterministic contract release archives and SHA-256 checksums."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def load(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def package(name: str, paths: list[str]) -> Path:
    output = DIST / f"{name}.tar.gz"
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for relative in sorted(paths):
            path = ROOT / relative
            candidates = sorted(path.rglob("*")) if path.is_dir() else [path]
            for candidate in candidates:
                if not candidate.is_file() or "__pycache__" in candidate.parts:
                    continue
                data = candidate.read_bytes()
                info = tarfile.TarInfo(candidate.relative_to(ROOT).as_posix())
                info.size = len(data)
                info.mode = 0o644
                info.mtime = 0
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                archive.addfile(info, io.BytesIO(data))
    with output.open("wb") as handle:
        with gzip.GzipFile(filename="", mode="wb", fileobj=handle, mtime=0) as zipped:
            zipped.write(raw.getvalue())
    return output


def main() -> None:
    versions = load(ROOT / "compatibility/versions.yaml")
    DIST.mkdir(exist_ok=True)
    outputs = [
        package(f"meldritch-lua-contract-{versions['lua_host_api']['current']}", ["lua", "fixtures/lua", "compatibility"]),
        package(f"meldritch-web-contract-{versions['web_protocol']['current']}", ["web", "fixtures/web", "compatibility"]),
    ]
    checksums = "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in outputs)
    (DIST / "SHA256SUMS").write_text(checksums, encoding="utf-8")
    print(checksums, end="")


if __name__ == "__main__":
    main()
