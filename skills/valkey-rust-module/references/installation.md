# Install and isolate Valkey

## Choose one installation path

Inspect `valkey-server --version`, `valkey-cli --version`, `rustc --version`, `cargo --version`, and the host architecture first. Do not replace an existing server installation just to develop a module.

- macOS: `brew install valkey` is the official documented Homebrew route. Start a foreground test process, not a login service, unless a service is requested.
- Linux: verify the distribution's package name and available version first. Official examples use `apt install valkey` or `dnf install valkey`; availability varies by release and configured repositories. Package installation may auto-start a service; inspect that behavior before installing on a shared host. Prefer a container or user-owned source build when isolation matters.
- Source: download a specific official release or check out an exact release commit, verify the release checksum when provided, and follow that release's README for dependencies and build flags. Use `src/valkey-server` and `src/valkey-cli` directly for development; system-wide installation is unnecessary.
- Containers: pin a verified Valkey image tag or digest and build the module for its OS, architecture, and libc. A macOS `.dylib` cannot be loaded into a Linux container. Publish ports only to loopback for development. Mount only the module artifact and a dedicated data directory, not the whole home directory.
- Windows: use WSL or a Linux container. Do not assume native Windows server/module support.

Rust builds may need a C compiler, linker, and Clang/libclang because the SDK uses C bindings. Diagnose missing build tools from the selected SDK's build output and documentation. Do not install arbitrary collections of packages. Record a Rust toolchain that actually builds the selected dependency graph; do not infer MSRV from the crate edition.

## Disposable development instance

Use absolute paths to the server and built artifact. Create a dedicated directory with `mktemp -d`, select an unused loopback port, and record both. Example, after resolving `valkey_server`, `module_path`, and `module_test_port`:

```sh
module_test_dir=$(mktemp -d)
"$valkey_server" --bind 127.0.0.1 --protected-mode yes \
  --port "$module_test_port" --dir "$module_test_dir" \
  --save "" --appendonly no --loadmodule "$module_path"
```

Run in a retained foreground process and capture startup logs. This configuration is only for disposable smoke tests. Persistence testing needs a separate instance with RDB/AOF enabled. Pass the explicit host and port to every CLI call. If startup fails because of a collision, choose another port; never stop an unrelated service.

From a second terminal, run `valkey-cli -h 127.0.0.1 -p <chosen-port> PING`, `MODULE LIST`, and an actual module command. Use explicit paths for the CLI when several installations exist. For cleanup, stop the owned process using its recorded process/session handle. Do not use broad `pkill` commands or shut down a default-port server.

Test harnesses that start a server must stop it on every exit path, including failures and panics (for example, a guard whose `Drop` kills the child). Before reporting done, confirm each server you started is gone: `valkey-cli -h 127.0.0.1 -p <port> PING` must fail to connect.

Prefer startup `--loadmodule` for local tests. Runtime `MODULE LOAD` may be disabled by `enable-module-command` or restricted by ACLs. Do not weaken an existing server's configuration to bypass that restriction. Inspect the target version's configuration if runtime loading is explicitly required.

## Sources

- [Official installation](https://valkey.io/topics/installation/)
- [Valkey releases](https://github.com/valkey-io/valkey/releases)
- [SDK build instructions](https://github.com/valkey-io/valkeymodule-rs)
- [Module loading](https://valkey.io/topics/modules-intro/)

Verified against these sources on 2026-11-19. Recheck package availability and release-specific requirements when executing the skill.
