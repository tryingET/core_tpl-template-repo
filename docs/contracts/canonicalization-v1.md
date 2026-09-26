# Canonicalization and tree identity v1

## Rules

- strict UTF-8; BOM rejected; invalid bytes and unpaired surrogates rejected;
- NFC for JSON strings/keys, text content, and logical paths;
- JSON duplicate keys after NFC rejected; keys ordered by UTF-8 bytes;
- only interoperable integers in ±(2^53−1); floats, exponents, and negative zero rejected;
- no insignificant whitespace in canonical JSON;
- logical paths use `/`; absolute paths, `~`, backslashes, empty/dot/dot-dot segments, traversal, symlinks, devices, sockets, and other special files rejected;
- case-fold and Unicode-normalization path collisions rejected;
- only file modes `0644` and `0755` participate; text newlines normalize to LF; binary is exact;
- empty directories are excluded; aggregate tree identity is SHA-256 of the canonical manifest;
- every digest is algorithm-tagged; source revision, content digest, tree digest, and executable artifact identity remain distinct.

`contracts/canonicalization-v1-vectors.json` is normative only after L0 acceptance. Python and TypeScript references must produce identical results for every vector. Fixture changes require a new fixture version and compatibility note; silently changing a vector is forbidden.
