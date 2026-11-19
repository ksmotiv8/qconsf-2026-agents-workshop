# Exercise: Build a Rust Valkey module with a skill

Can two numbers in a list add up to 10? Small problem. Real server module.

Use your coding agent to build it, load it into Valkey, and benchmark it.
Then turn something you learned into guidance another session can use.
The point is not to memorize Two Sum. It is to see what a skill changes
about the way an agent builds and verifies software.

## Setup

- Start your agent at the root of this workshop repository.
- Use a machine where you can run Rust and a disposable local Valkey server.
  The agent should inspect existing tools and explain missing dependencies
  before installing anything.
- The bundled [Valkey Rust module skill](../skills/valkey-rust-module/SKILL.md)
  includes references for installation, development, testing, and deployment.

No global skill installation is required. Tell the agent to read that file
and follow its reference links. This works even if your harness does not
automatically discover skills in this repository's `skills/` directory.

## 1. Give the agent a precise prompt

Paste this prompt:

> Read skills/valkey-rust-module/SKILL.md and its relevant references.
> Build a Rust Valkey server module in work/valkey-two-sum.
> Implement DEMO.HASPAIR key, where key is a Valkey list of unsigned 64-bit
> integers.
>
> Return integer 1 if two distinct list positions sum to 10, otherwise 0.
> Duplicate values are allowed: [5, 5] matches 10, but [5] does not.
> A missing key returns 0. A non-list key returns a wrong-type error.
> Wrong arity, malformed integers, negative numbers, and integers above
> 18446744073709551615 return errors. Accept ASCII digits only, with no
> sign or whitespace. Leading zeros are allowed.
> Validate the entire list even if an early pair matches.
> Treat sums mathematically: overflow must never wrap or crash the server.
> Reject lists longer than 10,000 elements before fetching their contents.
> The command must not change the list or its TTL.
>
> Keep the algorithm separate from the module adapter so it can be unit
> tested.
> Register the command as read-only with correct single-key metadata.
> Pin the SDK dependency, preserve Cargo.lock, and record the actual
> Rust, SDK, and Valkey versions and build features used.
>
> Build a release library and load it into a disposable loopback-only Valkey
> process on an unused port, with its own data directory. Do not touch an
> existing server, configure a system service, or deploy to a cloud account.
> Verify MODULE LIST, command metadata, actual command replies, and errors.
> Add automated unit and real-server integration tests. Document how to
> reproduce the build, load, tests, and cleanup. Report what actually ran
> and any blockers. Do not claim success based only on compilation or PING.

Example interaction, using the host and port of your disposable instance:

```text
RPUSH demo:numbers 3 8 7
DEMO.HASPAIR demo:numbers
→ 1
RPUSH demo:other 1 2 4
DEMO.HASPAIR demo:other
→ 0
```

The 10,000-element cap is an exercise limit, not a production safety claim.
Element byte lengths also affect parsing cost. A stretch task is to define
and enforce a byte budget without first copying an unbounded payload.

## 2. Review the behavior, not just the code

Ask the agent to review its work before fixing anything. Use a second
reviewer if available, or follow the [dual-review exercise](DUAL-REVIEW.md).
Confirm suspected defects against the prompt, then fix and add regression
tests for the ones that hold up.

At minimum, check:

| List or condition | Expected |
| --- | --- |
| Missing key | 0 |
| `[5]` | 0 |
| `[5, 5]` | 1 |
| `[0, 10]` | 1 |
| `[-3, 13]` | Error: negative numbers are not allowed |
| `[1, 2, 3]` | 0 |
| `[3, 7, "bad"]` | Error, not an early 1 |
| `[18446744073709551615, 11]` | 0: the real sum is 2^64 + 10, which wraps to 10 in 64-bit arithmetic |
| `[18446744073709551616, 1]` | Out-of-range error |
| String key instead of a list | Wrong-type error |
| More than 10,000 elements | Size-limit error |

Also test wrong arity, malformed and out-of-range elements, and that
list contents and expiration are unchanged. Allow for elapsed time when
checking TTL. Ensure test failures include server error replies, not just
nonzero CLI exit codes.

## 3. Optimize it

> Explain the algorithm DEMO.HASPAIR uses and what it costs in time and
> memory. Then try a different approach as a test helper, and check that
> both give the same answers on small generated inputs. Time both in a
> release build on lists of 10, 1,000, and 10,000 elements, each with an
> early match, a late match, and no match. Keep the whole benchmark under
> one minute. Report the numbers you measured in one table and save it to
> bench.md. Keep the faster approach only where the numbers show it. Do not
> invent results.

For no-match inputs, a list of integers that are all greater than 10 is
simple and reproducible. The second approach stays a test helper; you do
not need a second public command.

Stretch: benchmark the full `DEMO.HASPAIR` command against your local
Valkey. Prepare data outside the timed region, record client concurrency,
connection reuse, request count, and pipelining, and report latency and
throughput separately from the algorithm-only numbers. Do not compare one
algorithm's in-process time with another's network round-trip time.

Want to see it? Render your results as a page: [bonus in DESIGN.md](DESIGN.md#bonus-render-your-benchmark).

### Share your algorithm

> Describe the algorithm DEMO.HASPAIR uses, in plain English and five
> sentences or fewer: how it decides, what it costs in time and memory,
> how it handles duplicates and overflow, and what the benchmark showed.

Bring the answer to the room. We will compare approaches: which algorithm
each agent picked first, what it tried next, and which one won where.

## 4. Turn a finding into experience

Ask:

> What did review or testing teach us that a fresh agent should know?
> Propose one concise addition to the skill or a supporting reference.
> Include the failure mode, when the guidance applies, evidence from the
> test or code, and how to verify it. Do not invent a mistake if none occurred.
> Show me the proposed lesson before changing the skill.

Approve a useful lesson. Then clone the workshop repo again into a new
folder, copy your revised `skills/valkey-rust-module/` over the one in the
new clone, and start a fresh session there. Give it the same prompt,
without the previous implementation or conversation. See whether it applies the lesson without
being reminded. A single successful rerun is an observation, not proof
that the skill always improves results.

Optional comparison: run the same task in isolated folders with and without
the skill. Keep model, task, environment, and test criteria the same and
record human interventions. If a harness automatically loads the skill,
that is not a no-skill baseline.

## Done means

- A release module actually loaded and answered commands in local Valkey.
- Automated checks passed for every case in the prompt, including invalid inputs.
- The benchmark table reports measured results, or says why it could not run.
- A reviewed lesson is captured, or you explain why no addition was justified.
- A fresh-session attempt is recorded separately from the original run.
- The owned test process is stopped without disturbing other servers.

Keep source, Cargo.lock, tests, benchmark instructions, and your short
findings together. Do not commit generated libraries, data directories,
credentials, or benchmark claims you did not measure.
