# No Claude Code or Codex? Use Momento

If you don't have a Claude or ChatGPT plan, you can do the writing, design, and Valkey exercises with
open models on the Momento inference gateway. Use the coupon
code `qcon2026`.

## 1. Get credits

1. Sign in to the Momento console at https://app.gomomento.ai/.
2. Redeem the coupon code `qcon2026` on the Overview page.

You only need an API key if you set up Claude Code by hand (below). mo
logs in through your browser.

## 2. Pick a harness

### mo

mo is Momento's coding harness. It runs open models by default.

```bash
# macOS
brew install momentohq/tap/mo

# Linux
curl -fsSL https://packages.gomomento.ai/install.sh | sh
```

Log in once. `mo login` opens your browser; sign in with the same account
you redeemed the coupon on. Then check it worked:

```bash
mo login
mo auth status
```

Start it in an empty folder and ask for the repo, as on the setup slide:

```bash
mkdir qcon && cd qcon
mo
```

### Claude Code on open models

With mo and Claude Code both installed, `mo cc` starts Claude Code on the
gateway for you. `mo cc --model <route>` picks the model.

Without mo, create an API key in the console (API keys, then create one)
and point Claude Code at the gateway yourself:

```bash
export ANTHROPIC_BASE_URL="https://api.gomomento.ai"
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=500000
export CLAUDE_CODE_AUTO_COMPACT_WINDOW=400000
export ANTHROPIC_AUTH_TOKEN="REPLACE_ME" # your key from the console
export ANTHROPIC_MODEL="momento/zai-org/GLM-5.3-Flash-Fast"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="momento/zai-org/GLM-5.3-Flash-Fast"
export CLAUDE_CODE_AUTO_MODE_SERVER=0
export CLAUDE_CODE_AUTO_MODE_MODEL="momento/zai-org/GLM-5.3-Flash-Fast"
unset ANTHROPIC_API_KEY
claude
```

## 3. Switch models

`mo list momento` shows the open models. In a session, `/clear` starts
fresh and `/model <route>` switches, for example
`/model momento/moonshotai/Kimi-K3`. You can also start with
`mo --model <route>`.

Everything else in the exercises works the same: the prompts, the skills
and the cold read.
