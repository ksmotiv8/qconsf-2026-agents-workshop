# Exercise: from slop to signal, Slack track

Not into LinkedIn posts? Same exercise, different audience: a Slack
message to your favorite teammate about QConSF. Every step matches the
[LinkedIn track](SLOP-TO-SIGNAL.md), so you can follow along with the room.

A good DM to a teammate is short, says why it matters to your shared
work, and asks for something. Only you know those things, so the agent
interviews you first, you approve a brief, and every draft sticks to it.

We will save each version as `msg-1.md`, `msg-2.md` and so on, so you can
compare them as you go.

The most important part is reading what comes back after every step. If
something is off, tell the agent in your next prompt. For example: "Way
too long for Slack," "I never said that," or "Skip the keynote, they care
about our caching work." You are the one deciding what goes out with your
name on it.

For tools, see [What you need](SLOP-TO-SIGNAL.md#what-you-need) in the
LinkedIn track. For step 5, put 2 or 3 messages you wrote to teammates in
`samples/`. Pick ones you wrote, not announcements, and remove anything
confidential. No samples? Skip step 5.

## 1. Just ask

Pick a real teammate. Use their first name in place of `[name]`.

> Write a Slack message to my teammate [name] summarizing the highlights
> from QConSF. http://qconsf.com. Save it as msg-1.md.

Read it. Would [name] read past the first line? What did it make up, or
leave blank? Don't fix anything yet. This is our baseline.

## 2. Research the talks

QConSF has almost 90 sessions. Let the agent read all of them and find the
ones that matter to your shared work:

> Research QConSF 2026 for a message to my teammate [name]. First ask me
> what [name] and I work on and which sessions I went to. Then go through
> every session on https://qconsf.com/schedule/nov2026 and read its
> abstract. Save the 3 most relevant to our work in talks.md, with title,
> speaker, link, and one line on why. Only use what's on the site.

Open the links. Is each talk real, and does the reason hold up?

## 3. Get interviewed

> Interview me for a short Slack message to my teammate [name] about
> QConSF. Read talks.md first. Ask up to 3 questions, one at a time,
> about what you need to know to write a message only I could send. Wait
> for each answer. Then write my answers to brief.md, show it to me, and
> wait for my approval. Don't write the message yet.

Answer in your own words. Then read `brief.md` closely. Is every line
true? Is the ask clear, including when? Ask it to fix anything that is
off. When the brief is right, send step 4: that is your approval.

## 4. Write from the brief

> Using only brief.md, write the Slack message to [name], under 80 words.
> Lead with what it means for our work and end with what I want [name] to
> do. Save it as msg-2.md.

Put `msg-1.md` and `msg-2.md` side by side. What changed?

## 5. Add your voice

> Read the messages in samples/. Show me up to 3 habits of my writing,
> each with a short quote, and wait for my edits. Then save the habits I
> approve as a skill called my-voice in this project. It should change
> phrasing and structure only, never add facts.

Delete any habit that isn't you before you approve. To find the skill:

- Claude Code: `.claude/skills/my-voice/SKILL.md`
- Codex: `.agents/skills/my-voice/SKILL.md`
- mo: any of those, or `.mo/skills/my-voice/SKILL.md`

Start a new session in the same folder, so the skill loads, and check it:
run `/skills` in Claude Code or Codex, or `/skill` in mo. Then:

> Using only brief.md, write the Slack message to [name], under 80 words.
> Use my-voice. Save it as msg-3.md.

Does it sound more like you? Did it add anything that isn't in your
brief?

## 6. Edit it

> Install the humanizer skill from github.com/blader/humanizer in this
> project.

Check it loaded with `/skills` (`/skill` in mo). Not listed? In Claude
Code, run `/reload-skills`. In Codex or mo, start a new session in the
same folder.

> Read msg-3.md. Quote up to 3 lines that sound stock or repeat a point,
> and suggest a cut or a small edit for each. Use the humanizer skill.
> Suggestions only. Don't write any files.

Skipped step 5? Use `msg-2.md`. Now edit it yourself: read it out loud,
take the suggestions you agree with, and save it as `msg-final.md`.

## 7. Cold read

Start a new session, ideally on a different model. Same commands as
[step 7 of the LinkedIn track](SLOP-TO-SIGNAL.md#7-cold-read).

> Read msg-final.md as [name], between meetings. In one sentence, what
> would you do after reading it? Then check it against brief.md and quote
> up to 3 places where the point is unclear, a detail isn't backed by the
> brief, or the ask feels unearned. Comments only, don't rewrite it.

Is that what you want [name] to do? Fix what you agree with, by hand.

## 8. Make it stick

You corrected the same things all workshop. Save them so you don't have to
type them again:

> Read brief.md, and compare msg-3.md with msg-final.md, my own edit.
> Propose up to 5 lines for my memory: facts about me, and rules my
> edits show. Nothing about this one message. Show me before saving.

Skipped step 5? Use `msg-2.md`. Delete any line that isn't true of
everything you write. Then:

> Save them to this folder's instruction file: CLAUDE.md for Claude Code,
> AGENTS.md for Codex or mo.

Start a fresh session in the same folder (`/clear` in Claude Code and mo,
`/new` in Codex) and type only:

> Write a LinkedIn post about one talk in talks.md. Save it as post.md.

Put it next to `msg-1.md`. What did it do that you didn't ask for?

Memory is loaded in every session, so keep it short: who you are and the
rules you keep repeating. How you phrase things stays in your my-voice
skill, which loads only when needed. Want the lines in every project?
Move them to `~/.claude/CLAUDE.md` (Claude Code) or `~/.codex/AGENTS.md`
(Codex).

The agents also keep memory of their own. Claude Code's auto memory is on
by default and saves notes from your corrections; see or turn it off with
`/memory`. Codex memories are off by default; turn them on with
`/memories`. Codex doesn't see what ChatGPT remembers about you. Both
vendors say the same thing: rules that must always apply go in the file
you write. See the [Claude Code](https://code.claude.com/docs/en/memory)
and [Codex](https://learn.chatgpt.com/docs/customization/memories?surface=cli)
memory docs.

## 9. See them side by side, then design it

Build one page with every version next to the prompt that made it, then
redesign it with the frontend-design skill. Both are in
[DESIGN.md](DESIGN.md).

## Done?

Read `msg-final.md` one more time. Would you send it to [name] as is? If
so, send it.
