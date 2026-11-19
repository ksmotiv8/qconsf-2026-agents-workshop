# Develop a Rust server module

## Select the SDK deliberately

Use the project's existing `valkey-module` dependency when present. For new projects, inspect the published crate and its matching source; pin a released version or an exact Git revision if an unreleased fix is necessary. Commit Cargo.lock for reproducible module builds. Build with `--locked` after creating or updating the lockfile intentionally.

Inspect the selected revision's Cargo features rather than assuming the defaults. The upstream README and manifest can disagree about defaults. Choose the minimum supported server API feature explicitly where the SDK supports that choice, and use identical settings for module builds and integration tests. Feature names containing `redis` can describe API compatibility floors and do not by themselves mean the artifact targets Redis. `use-redismodule-api` is a distinct choice. Do not claim Redis compatibility unless requested and tested.

For `valkey-module` 0.2.0, [sdk-0.2.0.md](sdk-0.2.0.md) has verified patterns for registration, reading a list from a read-only command, strict integer parsing, and errors, plus which local example file answers which question.

Set `[lib] crate-type = ["cdylib"]`. Use the chosen revision's `examples/hello.rs` for macro syntax and allocator registration, adapting the behavior instead of blindly copying it. Typical entry points include `valkey_module!`, `Context`, `ValkeyString`, `ValkeyResult`, and `ValkeyError`. An example manifest or source on main is not evidence it compiles with a released dependency.

For an empty project, start with `cargo new --lib <project>` and add the verified SDK dependency, `cdylib` target, and explicit compatibility features. For an existing repository, edit its manifest instead of initializing over it. Implement a small command in `src/lib.rs`, generate the lockfile, then run `cargo build --release --locked` using the chosen production features. Preserve the build command in the project's normal build instructions. Treat upstream examples as references, not a requirement to clone and ship the entire SDK repository.

The main branch hello example uses unchecked integer multiplication. Replace it with checked arithmetic when adapting it. Test release builds too, where overflow behavior can differ.

## Commands and memory

- Namespace commands and module names to avoid collisions. Validate exact/minimum arity including the command name in the SDK argument vector. Use binary-safe parsing when keys or values may contain arbitrary bytes.
- Declare read/write flags truthfully. For fixed-position keys, supply accurate first/last/step metadata; use the version-supported key discovery API for dynamic layouts. Zero key positions are appropriate only for commands that do not access keys. Test `COMMAND INFO` and key discovery for key-bearing commands.
- Use existing key types unless the feature needs a native module type. Preserve TTL and wrong-type semantics intentionally, and cover both in integration tests when modifying keys.
- Use the SDK's intended production allocator configuration. Do not ship `test-shims` or `enable-system-alloc` merely to make tests pass. Keep test feature activation in a distinct invocation, then produce the release artifact with the production feature set and inspect `cargo tree -e features` for unification surprises.
- Keep the core algorithm in a pure function or crate with no SDK types. Then unit tests and release-mode benchmarks run without Valkey. In SDK 0.2.0, `test-shims` fails to compile in release builds, and the production allocator aborts outside a server; use `enable-system-alloc` only for standalone test or benchmark builds, never for the loadable artifact.
- Avoid `unwrap`, indexing panics, or unbounded allocation on client-controlled input. Bound expensive work and payload sizes according to the command's contract. `panic=abort` kills the server; it is not a substitute for error handling.
- Keep key handles and borrowed server values within their valid lifetime. In particular, do not call a command that deletes or replaces a key while retaining handles that refer to its old value.

## Stateful operations

Choose a propagation strategy for each write command: replicate a deterministic invocation, or propagate the concrete resulting operations. Consult the selected SDK's `Context`/call APIs and the underlying module API for their exact replication semantics. Do not both propagate individual writes and replicate the whole command, which can apply changes twice. Nondeterministic results must replay consistently. Test replica contents and AOF recovery, not just primary replies.

For native module data types, implement and test ownership/freeing, memory accounting, RDB encoding and decoding, and AOF rewrite behavior appropriate to the type. Keep the type identifier stable; version the encoding and reject unsupported or malformed encodings cleanly. Memory usage reporting does not by itself make every external allocation obey eviction limits. Do not rely on ordinary process globals for durable, replicated user data.

Native type names must be exactly nine ASCII characters from letters, digits, underscore, or hyphen and unique to the type. Check the current API contract rather than copying an illustrative name from prose. This persisted type identifier is distinct from the module name and its release version.

## Background work

Use the chosen SDK's blocking and thread examples as the starting point. Move only owned, thread-safe data to workers. Access server state through supported thread-safe contexts with the required lock. Perform external I/O outside the server lock. Handle timeout, disconnect, cancellation, worker startup failure, and completion exactly once. Bound worker counts and queues. Arrange cleanup even when the normal reply callback never runs. Do not unload a module while workers, callbacks, or native values can still refer to its code.

## Build and test

Run formatting and compiler/lint checks appropriate to the project. Separate pure algorithm tests from server integration tests; SDK context mocks are only usable where supported by the pinned SDK. Compile the production release artifact with production features, inspect it with `file`, and verify its initialization symbol with platform-appropriate tooling. The Rust SDK's `valkey_module!` macro exports `RedisModule_OnLoad` (checked in 0.2.0 and on main as of 2026-11-19), whatever compatibility features you select. Valkey 8 and 9 load it through their legacy Redis module path and log `Legacy Redis Module ... found`; that is expected, not an error. Only C modules built against `valkeymodule.h` export `ValkeyModule_OnLoad`. Do not hand-write a second entry point to change the symbol. Confirm the exported symbol with `nm -D` and confirm loading on every server version you claim to support.

On Linux the artifact is normally `target/release/lib<crate_name>.so`, on macOS `.dylib`; Cargo target names convert hyphens to underscores. Cross-target builds have an additional target-triple directory. Locate the actual Cargo output rather than guessing paths or renaming binaries to change platforms.

Read [deployment.md](deployment.md) for required real-server checks.

## Source routes

- [SDK examples](https://github.com/valkey-io/valkeymodule-rs/tree/main/examples): `hello`, `keys_pos`, `data_type`, `block`, `threads`, `load_unload`. Read equivalents at the selected revision.
- [Published SDK API](https://docs.rs/valkey-module/): select the actual version.
- [Module API reference](https://valkey.io/topics/modules-api-ref/)
- [Native types](https://valkey.io/topics/modules-native-types/)
- [Blocking operations](https://valkey.io/topics/modules-blocking-ops/)

Source review: 2026-11-19. API names, feature availability, and test helpers must be verified at the selected revision.
