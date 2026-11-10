# Consumer pinning

Each consumer stores:

- the immutable contracts commit;
- the relevant semantic contract version;
- the SHA-256 of the packaged contract artifact.

CI unpacks that artifact, runs the repository's conformance suite, and rejects
version-range mismatches. Coordinated local work may pass an explicit path to a
contracts checkout. Source code must not assume an adjacent directory.

The standard public change order is contract, independent validation, immutable
pin/artifact, implementation updates, conformance tests, then integration.
