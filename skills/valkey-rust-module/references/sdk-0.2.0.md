# valkey-module 0.2.0: patterns that work

Verified on 2026-11-19 by building a module against `valkey-module = "=0.2.0"` (features `min-valkey-compatibility-version-8-0`, default features off) and running it in Valkey 8.0.6. Recheck if you pin a different version.

## Read the examples locally

After the first `cargo build`, the crate source is on disk at
`~/.cargo/registry/src/*/valkey-module-0.2.0/`. Read whole example files there instead of grepping `src/` a few lines at a time:

| Example | Use it for |
| --- | --- |
| `examples/hello.rs` | `valkey_module!` registration, `ValkeyAlloc`, arity checks, `parse_integer`, unit tests with `test_shims` (test builds only) |
| `examples/keys_pos.rs` | Key metadata. Fixed positions use the first/last/step numbers; `getkeys-api` is only for variable key layouts |
| `examples/lists.rs` | `key_type()` checks that return `WRONGTYPE`. Its list calls need a writable key |
| `examples/call.rs` | `ctx.call` versus `ctx.call_ext` and `CallOptionsBuilder` |
| `examples/response.rs` | Reply types |

## Facts that change the design

1. **Registration, and read-only keys.** In `valkey_module!`, `["demo.cmd", handler, "readonly", 1, 1, 1]` is flags, first key, last key, step. But the server derives a key spec from that triple flagged `RW access update`, even with the `readonly` command flag. A user limited to read-only key access (ACL `%R~*`) then gets `NOPERM` on your read-only command, while `LLEN` on the same key works. For a command that only reads, register it with the `#[command]` attribute and an explicit read-only key spec instead (see below). Add `fast` only for constant-time commands.
2. **Read-only keys cannot read lists.** `ctx.open_key()` returns a `ValkeyKey` with only `key_type()` and `is_null()`. The list functions (`list_push_*`, `list_pop_*`) are on `ValkeyKeyWritable`. A read-only command reads a list by checking the type with `open_key`, then calling `LLEN` and `LRANGE`.
3. **Never read user data with `ctx.call`.** It converts every string reply with `to_string().unwrap()`. A list element that is not valid UTF-8 panics inside the server, and the server aborts (signal 6). Use `ctx.call_ext::<_, CallResult>` and read `as_bytes()`.
4. **`parse_integer` is the server's strict parser.** It rejects `007`, `-0`, `+5`, leading or trailing spaces, and `1e3`. It accepts the i64 range only, so it rejects unsigned values above 9223372036854775807. If your spec allows leading zeros or needs the u64 range, parse the bytes yourself.
5. **Errors.** `ValkeyError::WrongArity` and `ValkeyError::WrongType` produce the standard replies. `ValkeyError::Str` sends its text as the error message, so start it with an error code such as `ERR`.

## Registering a read-only command

Verified 2026-11-19: with this registration, `COMMAND INFO` shows the key spec as `RO access`, and a user with `%R~*` can run the command. Add `valkey-module-macros = "=0.2.0"` and `linkme = "=0.3.38"` to `[dependencies]`: the macro's generated code names `linkme` directly, so the build fails without it.

```rust
use valkey_module_macros::command;

#[command(
    {
        name: "demo.haspair",
        flags: [ReadOnly],
        arity: 2,
        key_spec: [
            {
                flags: [ReadOnly, Access],
                begin_search: Index({ index: 1 }),
                find_keys: Range({ last_key: 0, steps: 1, limit: 0 }),
            }
        ]
    }
)]
fn haspair(ctx: &Context, args: Vec<ValkeyString>) -> ValkeyResult {
    // ...
}

valkey_module! {
    name: "twosum",
    version: 1,
    allocator: (ValkeyAlloc, ValkeyAlloc),
    data_types: [],
    commands: [],   // registered by #[command] above
}
```

Test it: `ACL SETUSER ro on >pw %R~* +@all`, then run the command as `ro`. It must answer, not return `NOPERM`.

## Reading a list safely

This compiled and ran against Valkey 8.0.6. It returned 0 for a missing key, `WRONGTYPE` for a string key, and handled a list with a `\xff\xfe` element without crashing.

```rust
use valkey_module::raw::KeyType;
use valkey_module::{CallOptionsBuilder, CallReply, CallResult, Context, ValkeyError, ValkeyResult, ValkeyString, ValkeyValue};

fn read_list(ctx: &Context, args: Vec<ValkeyString>) -> ValkeyResult {
    if args.len() != 2 {
        return Err(ValkeyError::WrongArity);
    }
    let key = &args[1];
    match ctx.open_key(key).key_type() {
        KeyType::Empty => return Ok(ValkeyValue::Integer(0)),
        KeyType::List => {}
        _ => return Err(ValkeyError::WrongType),
    }
    let opts = CallOptionsBuilder::new().errors_as_replies().build();
    let len = match ctx.call_ext::<_, CallResult>("LLEN", &opts, &[key]) {
        Ok(CallReply::I64(n)) => n.to_i64(),
        _ => return Err(ValkeyError::Str("ERR LLEN failed")),
    };
    if len > 10_000 {
        return Err(ValkeyError::Str("ERR list too long"));
    }
    let reply: CallResult = ctx.call_ext("LRANGE", &opts, &[key.as_slice(), b"0", b"-1"]);
    let Ok(CallReply::Array(items)) = reply else {
        return Err(ValkeyError::Str("ERR LRANGE failed"));
    };
    for item in items.iter() {
        let Ok(CallReply::String(s)) = item else {
            return Err(ValkeyError::Str("ERR unexpected list element"));
        };
        let bytes: &[u8] = s.as_bytes();
        // Parse and use `bytes` here. Never convert with unwrap().
        let _ = bytes;
    }
    Ok(ValkeyValue::Integer(len))
}
```

Commands called this way show up in `SLOWLOG` and count toward keyspace hits. Mention that in the handoff if it matters to the user.

## Test the crash case

Add a real-server test that pushes a non-UTF-8 element (for example with `printf 'RPUSH k "\\xff\\xfe" 5\n' | valkey-cli -p <port>`), runs the command, and then checks `PING`. A module that panics fails this test by taking the server down.
