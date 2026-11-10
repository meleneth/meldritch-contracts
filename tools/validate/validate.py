#!/usr/bin/env python3
"""Dependency-free contract and fixture validation."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def load(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class Invalid(ValueError):
    pass


def resolve(root: dict[str, Any], reference: str) -> dict[str, Any]:
    if not reference.startswith("#/"):
        raise Invalid(f"external reference is forbidden: {reference}")
    value: Any = root
    for component in reference[2:].split("/"):
        value = value[component.replace("~1", "/").replace("~0", "~")]
    return value


def type_matches(value: Any, expected: str) -> bool:
    return {
        "null": value is None,
        "boolean": isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "string": isinstance(value, str),
        "array": isinstance(value, list),
        "object": isinstance(value, dict),
    }.get(expected, False)


def validate(value: Any, schema: dict[str, Any], root: dict[str, Any], where: str = "$") -> None:
    if "$ref" in schema:
        validate(value, resolve(root, schema["$ref"]), root, where)
        return
    if "oneOf" in schema:
        matches = 0
        for candidate in schema["oneOf"]:
            try:
                validate(value, candidate, root, where)
                matches += 1
            except Invalid:
                pass
        if matches != 1:
            raise Invalid(f"{where}: expected exactly one schema match, got {matches}")
        return
    if "const" in schema and value != schema["const"]:
        raise Invalid(f"{where}: expected constant {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise Invalid(f"{where}: {value!r} is not in {schema['enum']!r}")
    expected = schema.get("type")
    if expected:
        expected_types = expected if isinstance(expected, list) else [expected]
        if not any(type_matches(value, item) for item in expected_types):
            raise Invalid(f"{where}: expected {expected_types}, got {type(value).__name__}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise Invalid(f"{where}: string is too short")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            raise Invalid(f"{where}: string does not match {schema['pattern']!r}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise Invalid(f"{where}: value is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            raise Invalid(f"{where}: value is above maximum")
    if isinstance(value, list):
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True) for item in value]
            if len(set(encoded)) != len(encoded):
                raise Invalid(f"{where}: array entries must be unique")
        if "items" in schema:
            for index, item in enumerate(value):
                validate(item, schema["items"], root, f"{where}[{index}]")
    if isinstance(value, dict):
        for name in schema.get("required", []):
            if name not in value:
                raise Invalid(f"{where}: missing required property {name!r}")
        properties = schema.get("properties", {})
        for name, item in value.items():
            if name in properties:
                validate(item, properties[name], root, f"{where}.{name}")
            elif schema.get("additionalProperties") is False:
                raise Invalid(f"{where}: unknown property {name!r}")


def validate_lua() -> int:
    api = load(ROOT / "lua/api.yaml")
    versions = load(ROOT / "compatibility/versions.yaml")
    if api["version"] != versions["lua_host_api"]["current"]:
        raise Invalid("Lua API version differs from compatibility/versions.yaml")
    capability_ids = [item["id"] for item in api["capabilities"]]
    if len(capability_ids) != len(set(capability_ids)):
        raise Invalid("duplicate Lua capability ID")
    namespace_names: set[str] = set()
    for namespace in api["namespaces"]:
        name = namespace["name"]
        if name in namespace_names:
            raise Invalid(f"duplicate Lua namespace {name}")
        namespace_names.add(name)
        operation_names: set[str] = set()
        for operation in namespace["operations"]:
            opname = operation["name"]
            if opname.startswith("_"):
                raise Invalid(f"private Lua operation published: {name}.{opname}")
            if opname in operation_names:
                raise Invalid(f"duplicate Lua operation {name}.{opname}")
            operation_names.add(opname)
            capability = operation.get("capability", namespace.get("capability"))
            if capability and capability not in capability_ids:
                raise Invalid(f"unknown capability {capability} on {name}.{opname}")

    app_schema = load(ROOT / "lua/schemas/application.schema.json")
    for path in sorted((ROOT / "fixtures/lua/valid").glob("*.json")):
        manifest = load(path)
        validate(manifest, app_schema, app_schema, path.name)
        unknown = set(manifest["capabilities"]) - set(capability_ids)
        if unknown:
            raise Invalid(f"{path.name}: unknown capabilities {sorted(unknown)}")
    for path in sorted((ROOT / "fixtures/lua/invalid").glob("*.json")):
        manifest = load(path)
        try:
            validate(manifest, app_schema, app_schema, path.name)
            unknown = set(manifest.get("capabilities", [])) - set(capability_ids)
            if unknown:
                raise Invalid(f"unknown capabilities {sorted(unknown)}")
        except Invalid:
            continue
        raise Invalid(f"invalid Lua fixture unexpectedly passed: {path.name}")
    return len(capability_ids)


def validate_web() -> int:
    protocol = load(ROOT / "web/protocol.yaml")
    versions = load(ROOT / "compatibility/versions.yaml")
    schema = load(ROOT / "web/schemas/protocol.schema.json")
    if protocol["version"] != versions["web_protocol"]["current"]:
        raise Invalid("Web protocol version differs from compatibility/versions.yaml")
    if protocol["wire_schema_version"] != versions["web_protocol"]["wire_schema_version"]:
        raise Invalid("wire schema version differs from compatibility/versions.yaml")
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise Invalid("Web schema must use JSON Schema Draft 2020-12")
    message_schema = schema["$defs"]["Message"]
    count = 0
    for path in sorted((ROOT / "fixtures/web/valid").glob("*.json")):
        fixture = load(path)
        messages = fixture if isinstance(fixture, list) else [fixture]
        for index, message in enumerate(messages):
            validate(message, message_schema, schema, f"{path.name}[{index}]")
            count += 1
    for path in sorted((ROOT / "fixtures/web/invalid").glob("*.json")):
        fixture = load(path)
        if "sequence" in fixture:
            if fixture.get("expected") != "hello_required" or fixture["sequence"][0].get("type") == "hello":
                raise Invalid(f"invalid lifecycle fixture is malformed: {path.name}")
            continue
        try:
            validate(fixture, message_schema, schema, path.name)
        except Invalid:
            continue
        raise Invalid(f"invalid Web fixture unexpectedly passed: {path.name}")
    return count


def validate_integration_lock() -> None:
    lock = load(ROOT / "integration.lock.json")
    versions = load(ROOT / "compatibility/versions.yaml")
    expected_components = {
        "meldritch",
        "meldritch-contracts",
        "meldritch-lua",
        "meldritch-ui",
    }
    if set(lock.get("components", {})) != expected_components:
        raise Invalid("integration lock must name exactly the four repositories")
    if not isinstance(lock.get("integration"), str) or not lock["integration"]:
        raise Invalid("integration lock requires a nonempty integration identifier")
    for name, component in lock["components"].items():
        revision = component.get("revision", "")
        if not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise Invalid(f"{name}: revision must be a full lowercase Git hash")
    contract = lock["components"]["meldritch-contracts"]
    if contract.get("lua_host_api") != versions["lua_host_api"]["current"]:
        raise Invalid("integration lock Lua API version is not current")
    if contract.get("web_protocol") != versions["web_protocol"]["current"]:
        raise Invalid("integration lock Web protocol version is not current")
    expected_artifacts = {
        f"meldritch-lua-contract-{contract['lua_host_api']}.tar.gz",
        f"meldritch-web-contract-{contract['web_protocol']}.tar.gz",
    }
    if set(lock.get("artifacts", {})) != expected_artifacts:
        raise Invalid("integration lock must pin both published contract artifacts")
    for artifact, digest in lock["artifacts"].items():
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise Invalid(f"{artifact}: checksum must be lowercase SHA-256")


def main() -> int:
    try:
        lua_count = validate_lua()
        web_count = validate_web()
        validate_integration_lock()
    except (Invalid, KeyError, json.JSONDecodeError) as error:
        print(f"contract validation failed: {error}", file=sys.stderr)
        return 1
    print(f"contracts valid: {lua_count} Lua capabilities, {web_count} Web messages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
