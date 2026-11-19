# Supercharge Your Work With Claude Code and Codex

QCon SF · Thursday, November 19, 9:00 AM · Seacliff C · 3-hour training workshop · Beginner
Khawaja Shams and Ruth Linehan, Momento

Working outline. We edit this first, then build slides one at a time.
Status per section: `draft` → `agreed` → `slides started` → `slides done`.

## Promise to the room (from the listing)

By the end, attendees have used agents for writing, publishing, a Rust Valkey module, benchmarking,
and agent-to-agent loops, and leave with reusable workflows and project memory they can keep.

## Source material

Proven exercises from the face recognition workshop
([ksmotiv8/momento-face-workshop](https://github.com/ksmotiv8/momento-face-workshop)),
copied into `exercises/` as-is. Each section below names what it reuses.

| File | What it is | Used in |
|---|---|---|
| `exercises/SLOP-TO-SIGNAL.md` | One LinkedIn post, six passes; builds a `my-voice` skill from 5 of your own posts | 2 |
| `exercises/DEVILS-ADVOCATE.md` | Three-pass hostile review: argument, voice, machine tells | 2 |
| `exercises/DUAL-REVIEW.md` | Claude Code runs Codex as an independent second reviewer, then reconciles | 5 |
| `exercises/LOOPS-WORKFLOWS-GOALS.md` | `/loop` vs workflows vs Codex `/goal`, and when to use each | 5 |
| face workshop `SYLLABUS.md` modules 1-3, 5 | Rust face pipeline, Valkey vector index, live video, enrollment | 0, 3, 4 |
| face workshop module 6 | Blog post from this session's real numbers, fact-checked against the transcript | 2 |
| face workshop module 7 | "Interrogate what you built": quiz me, explain decisions I didn't ask for | 1, 6 |

## Timing (180 min)

| Time | Section | Min | Status |
|---|---|---|---|
| 0:00 | 0. Welcome and setup check | 10 | draft |
| 0:10 | 1. A better working relationship with your agent | 30 | draft |
| 0:40 | 2. Write, publish, and style with agents | 35 | draft |
| 1:15 | Break | 10 | |
| 1:25 | 3. Technical fearlessness: Rust and Valkey vector search | 40 | draft |
| 2:05 | 4. Performance tests without living in Unix commands | 25 | draft |
| 2:30 | 5. Agent loops and agent-to-agent workflows | 20 | draft |
| 2:50 | 6. Wrap: the workflows you take home | 10 | draft |

## 0. Welcome and setup check (10 min)

- Who we are and why we work this way (Momento: we build with agents daily)
- What you'll have built by noon
- Setup check: Claude Code, Codex, GitHub, AWS. Fallback for anyone without subscriptions

Reuse: open with the face workshop finale as a live demo. Someone walks up to the
camera, the terminal prints their name, the laptop says "Welcome, <name>" (module 3d).
Then: "you'll build the pieces of this today."

Candidate slides: title · who we are · live demo · what you'll build today · setup check

## 1. A better working relationship with your agent (30 min)

- What happens to a prompt: context window, tools, what the agent can and can't see
- Memory: CLAUDE.md / AGENTS.md, what belongs there and what doesn't
- Steering: plan first, give it a way to check its work, say what "done" means
- Exercise: write a project memory file for your own repo, then watch behavior change

Reuse:
- Skills lesson from the face workshop: without the four skills registered, each module took
  2-3x longer with more wrong turns. A concrete case for memory and skills.
- "Hold the agent to checks it can run, not promises it can make" (the thread through every
  face workshop prompt: "verify on one portrait before building the rest").
- Module 7 prompts as the habit of asking the agent to explain, not just do.

Candidate slides: the agent loop · what's in context · memory files · plan, check, done · exercise

## 2. Write, publish, and style with agents (35 min)

- Research → draft → revise, with one agent writing and another reviewing
- Voice and style rules as reusable instructions
- From draft to a live page
- Exercise: write a short piece, have the second agent critique it, publish it

Reuse:
- SLOP-TO-SIGNAL: attendees build their own `my-voice` skill (bring 5 LinkedIn posts) inside the six-pass exercise.
- DEVILS-ADVOCATE: run it on their draft; second run should lead with a different finding.
- Module 6 rule: every number from your own session, then fact-check against the transcript.

Candidate slides: house style vs your voice · my-voice skill · devil's advocate · draft to deploy · exercise

## 3. Technical fearlessness: Rust and Valkey vector search (40 min)

- Point: unfamiliar language and codebase, still productive
- Explore the repo with the agent before writing code
- Build the face pipeline, index embeddings in Valkey, recognize faces
- Exercise: face workshop modules 1-2 (and 5, enrollment) on an EC2 box

Decided: reuse the face pipeline. A Rust workspace (`facecore` + CLI) that uses Valkey's
search module (FT.CREATE / FT.SEARCH KNN). Proven prompts, test faces, known gotchas
(distance vs similarity, pinned `redis` crate, detector's 20 px floor). The listing says
"a Valkey module in Rust"; address that in the intro (we build in Rust on top of a Valkey module).
Distance-vs-similarity is the "trust but verify" story.

Candidate slides: why unfamiliar on purpose · explore before you write · the build · exercise

## 4. Performance tests without living in Unix commands (25 min)

- The agent runs the benchmark, reads the output, proposes the next run
- Asking for an analysis you can trust: baselines, repeats, what changed
- Exercise: benchmark your module against a baseline

Reuse:
- Face workshop module 3: per-frame latency distribution (measured 12/104/141 ms for
  0/1/2 faces) and the native vs serverless comparison (~30 ms vs ~360 ms per face).
- Possibly the large-object Valkey benchmarks from `~/v-lab` as the "real" example.

Candidate slides: the benchmark loop · results you can trust · exercise

## 5. Agent loops and agent-to-agent workflows (20 min)

- Give a goal and a check, let it loop
- Claude builds, Codex reviews (or the reverse)
- Exercise: run a build/review loop on your module

Reuse:
- LOOPS-WORKFLOWS-GOALS: the three primitives and the "which one, when" table.
- DUAL-REVIEW: Claude reviews first, then runs Codex, then reconciles. Agreement is
  correlation, not proof.
- Story: the face workshop syllabus was hardened by a workflow that ran it autonomously,
  fixed what broke, and voted on whether to run again.

Candidate slides: goal + check = loop · two agents, two roles · how we hardened the face workshop · exercise

## 6. Wrap (10 min)

- The reusable workflows, one line each
- Module 7 "quiz me" as the closing habit: interrogate what you built
- Where to go next

## Open questions

1. Exercise environment: does each attendee bring their own EC2 box, or do we hand out pre-built ones?
2. Do we share a starter repo with exercises? (Likely yes, and the GitHub repo can hold it.)
3. Hands-on vs talking ratio: target about 50/50?
4. Opening demo: do we run the live "Welcome, <name>" face demo? Needs a webcam and a rehearsal.
