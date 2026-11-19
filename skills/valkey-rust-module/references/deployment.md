# Verify and deploy

## Minimum acceptance for a new module

Build a production release artifact, load it into a fresh isolated Valkey instance, and inspect startup logs and `MODULE LIST`. Verify the registered commands and assert actual responses, including error replies. CLI process exit status alone may not distinguish server error replies from success; inspect replies or use a client that raises command errors.

Cover valid input, wrong arity, malformed values, overflow/boundaries, and the feature's key/TTL/wrong-type behavior. For a command that only reads keys, also run it as an ACL user with read-only key access (`%R~*`); it must not return `NOPERM`. A failed load must fail the test even if another process responds to `PING`. Keep the exact artifact used for these checks as the release candidate; rebuilding afterward requires rechecking it.

Add only the applicable cases:

- Persistent writes: create data, save/restart from RDB, and separately test AOF replay and AOF rewrite/restart. Wait for background save/rewrite success and inspect persistence status. Verify content, TTL semantics, and native type decoding after restart.
- Native types with an AOF rewrite callback: include a separate disposable instance with `--appendonly yes --aof-use-rdb-preamble no`. Wait for `BGREWRITEAOF` to finish successfully, restart with the same data directory and configuration, and assert the restored values. The default hybrid AOF can serialize a type through its RDB callbacks, so passing that test alone does not exercise the native type's AOF rewrite callback. Retain coverage of the intended production AOF configuration too.
- Replicated writes: use a dedicated primary/replica pair with compatible module builds loaded on both. Wait for synchronization, verify data, and exercise promotion/reconnection when failover is in scope.
- Cluster commands: run a disposable multi-node cluster, test key discovery, same-slot and cross-slot inputs, and behavior during routing changes appropriate to the feature.
- Background work: timeout, client disconnect, queue saturation, worker errors, and shutdown cleanup.
- Upgrades: exercise data created by the old module with the new one. Test backward readability before describing binary rollback as safe.

For stateful modules, simple smoke tests are not sufficient to declare production readiness. Report any untested persistence, replication, failover, or upgrade behavior explicitly.

## Package for the actual runtime

Build on a compatible target or in a pinned builder matching the deployment architecture and runtime libc. Inspect dynamic dependencies and minimum GLIBC requirements on Linux; do not ship a host-built macOS library into Linux. A Rust target flag alone does not supply a compatible C toolchain or sysroot.

Package the tested library, checksum, SDK revision, Rust version, Cargo.lock, feature set, target triple, server compatibility range actually tested, and module configuration. Use a versioned immutable artifact path. For container deployment, copy the library into a pinned Valkey runtime image and test the final image. Keep persistent data in a separate volume and make the module readable by the runtime user. Do not bake credentials into the image.

## Load and deploy

For an authorized self-managed server, place the artifact at a stable absolute path and configure startup loading:

```text
loadmodule /opt/valkey/modules/<release>/lib<module>.so
```

Resolve placeholders and optional module arguments for the actual target. Ensure directory traversal permissions and the service's sandbox allow reading the file. Inspect the effective service command/config rather than assuming a distro config location. Keep existing authentication, TLS, bind, persistence, and service-user settings.

Runtime `MODULE LOAD` loads a file on the server filesystem, not the CLI machine. It does not itself guarantee loading after restart. Prefer persistent startup configuration unless the user specifically needs a supported runtime-loading workflow. Do not globally enable module-management commands to bypass an ACL or service restriction.

Managed services may not support arbitrary customer modules. Verify provider support before attempting deployment; if unsupported, explain the concrete constraint and offer a self-managed test target without silently moving the workload.

## Upgrade and rollback

Use the target's existing maintenance or rolling deployment process. Ensure every replica and cluster node that can receive module data has a compatible module before sending new data or commands. Mixed versions must have a proven compatibility contract. Follow the topology's failover procedure instead of prescribing a universal restart order.

Before rollout, preserve the old artifact/configuration and a verified recovery path for persistent data. Module unloading is not a general hot-upgrade mechanism: native data types or outstanding activity can prevent it. Prefer a planned process restart with the new library. Never force unload or overwrite a mapped library in place.

After rollout, verify loaded identity, command semantics, startup logs, persistence health, and replication state on the affected nodes. If validation fails, stop rollout. Restore the previous artifact/config only when it can read the resulting data; otherwise use the tested recovery procedure. Never delete live data to make an older module start.

## Sources

- [Module loading and lifecycle](https://valkey.io/topics/modules-intro/)
- [Persistence](https://valkey.io/topics/persistence/)
- [Replication](https://valkey.io/topics/replication/)
- [Cluster specification](https://valkey.io/topics/cluster-spec/)
- [Module native types](https://valkey.io/topics/modules-native-types/)
