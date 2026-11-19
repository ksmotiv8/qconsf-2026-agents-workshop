# Loops, workflows, and goals

One prompt, one answer is the default shape of a coding agent. It is the
wrong shape for plenty of real work. Claude Code and Codex each have ways
past it, and they answer three different questions.

## /goal: "keep going until this is true"

Claude Code and Codex both have `/goal`. You state a completion condition,
and the agent keeps taking turns until it holds. In Claude Code, after
every turn a separate model checks the condition against what the agent
has shown in the conversation. The goal ends when the condition is met,
when that model judges it impossible, or when you run `/goal clear`. Codex
adds `/goal pause` and `/goal resume`.

For the [Valkey module](VALKEY-MODULE.md) exercise:

```
/goal every case in the section 2 table passes against the release module
on a disposable Valkey, cargo test and cargo clippy pass, and git status
shows no files outside work/valkey-two-sum changed. Or stop after 20 turns.
```

Reach for it when the end state is testable and the path is not. Write
each part as something the agent proves by running a command, and add a
limit.

## /loop: "do this again, over time"

`/loop` in Claude Code reruns a prompt on an interval, or lets the model
pick the interval each time. It runs while the session stays open.

```
/loop 5m check the deploy; if it failed, diagnose it and tell me
```

Reach for it when the work is watching: a CI run, a migration, a queue.
The prompt does not change; the world does.

## Workflows: "do these all at once, in order"

A workflow in Claude Code is a small script that fans work out to many
agents, with control flow the model cannot forget or reorder: run five
reviewers in parallel, check every finding, then merge what survives. The
order lives in the script; the judgment lives in the agents.

Reach for it when you need coverage (many files, many angles) or
confidence (independent reviewers) that one session cannot hold.

## Which one, when

| You are really asking | Use |
|---|---|
| Converge on this provable end state | `/goal` (Claude Code, Codex) |
| Watch this and act when it changes | `/loop` (Claude Code) |
| Cover this from many angles at once | A workflow (Claude Code) |

All three work for the same reason the exercises keep repeating: the agent
is held to checks it can run, not to promises it can make.

## Docs

- Claude Code: [/goal](https://code.claude.com/docs/en/goal),
  [/loop and scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks),
  [workflows](https://code.claude.com/docs/en/workflows),
  [best practices](https://code.claude.com/docs/en/best-practices)
- Codex: [Using goals in Codex](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex),
  [best practices](https://developers.openai.com/codex/learn/best-practices)
