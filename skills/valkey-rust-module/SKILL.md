---
name: valkey-rust-module
description: Build, test, install, and deploy Valkey server modules written in Rust using valkeymodule-rs. Covers local Valkey setup, module commands, persistence, replication, and release compatibility. Use for server extensions, not ordinary Rust clients that connect to Valkey.
---

# Valkey modules in Rust

Deliver a module that builds for the selected server and platform, loads successfully, and passes command-level checks. Match the requested scope: a request for a skill or deployment plan does not authorize installing a server or changing production.

## Establish the target

Inspect the existing repository, Cargo manifest and lockfile, server configuration, and deployment scripts. Preserve established conventions. Identify the server version, CPU architecture, OS/libc, module SDK revision, command semantics, persistence requirements, and whether the target is disposable local development or an existing deployment. Infer these from the project before asking.

For a new local prototype, prefer an isolated loopback-only server with its own data directory. If production details are missing, build and test locally while leaving deployment as a concrete plan.

## Route the work

- Installing Valkey, preparing Rust dependencies, or starting a development server: read [installation.md](references/installation.md).
- Creating or changing Rust module code: read [development.md](references/development.md). With `valkey-module` 0.2.0, also read [sdk-0.2.0.md](references/sdk-0.2.0.md): verified patterns, the local example files, and the `ctx.call` crash to avoid.
- Testing server behavior, shipping artifacts, upgrading, or rolling back: read [deployment.md](references/deployment.md).

Read the relevant references before acting. Use official documentation and the exact SDK revision selected by the project to resolve API details. Do not mix examples from SDK main with an older published crate.

## Essential workflow

1. Establish a working server/SDK/platform combination and record it. The SDK repository is `valkey-io/valkeymodule-rs`; the crate is `valkey-module`, imported as `valkey_module`.
2. Build a `cdylib` with one namespaced command first. Prove that the release artifact loads before implementing complex state or concurrency.
3. Implement the requested behavior with correct argument validation, command flags and key metadata. Scope native types, background work, replication, and persistence to the actual feature.
4. Verify release behavior in a real isolated Valkey process. Pure Rust tests alone cannot prove module loading or server interactions.
5. Deploy only to the authorized target using an artifact built for that target. Verify loaded module identity, command output, logs, and any persistence or replication behavior the feature requires.

## Non-negotiable correctness points

- Module code runs inside the server process. Unhandled panics, invalid FFI lifetimes, and blocking I/O can compromise the entire server. Return command errors for malformed input and checked-arithmetic failures.
- An ordinary callback context and open key handles are not transferable worker-thread state. Use SDK-supported blocked-client and thread-safe-context patterns when needed.
- Writing to keys is not proof of replication or AOF propagation. Define and test the propagation strategy explicitly.
- Module data must be readable on restart, replicas, and any planned rollback version. Do not promise downgrade compatibility without testing it.
- Test-only allocator/shim features must not enter the shipped module artifact.

## Handoff

Provide the artifact location and checksum, exact server/SDK versions and build features, build/load commands, tests actually run, and remaining limitations. Distinguish planned deployment from completed deployment. Never report successful loading solely from compilation or `PING`.

Before handing off, stop every server you started and confirm its port no longer answers. A leftover test server is a defect.
