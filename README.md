<div align="center">
  <h1><a href="https://pypi.org/project/doclify/">Doclify</a></h1>
  <p><i>A hands-on exploration of advanced context engineering — built as an open source AI agent for documentation.</i></p>

  [![PyPI Version](https://img.shields.io/pypi/v/doclify?style=flat&color=blue)](https://pypi.org/project/doclify/)
  [![PyPI Downloads](https://img.shields.io/pypi/dm/doclify?style=flat&color=blue)](https://pypi.org/project/doclify/)
  [![GitHub Stars](https://img.shields.io/github/stars/KalyanM45/Doclify?style=flat&color=ffd700)](https://github.com/KalyanM45/Doclify/stargazers)
  [![GitHub Issues](https://img.shields.io/github/issues/KalyanM45/Doclify?style=flat&color=red)](https://github.com/KalyanM45/Doclify/issues)
  [![GitHub Forks](https://img.shields.io/github/forks/KalyanM45/Doclify?style=flat&color=green)](https://github.com/KalyanM45/Doclify/network/members)
  [![GitHub Discussions](https://img.shields.io/github/discussions/KalyanM45/Doclify?style=flat&color=purple)](https://github.com/KalyanM45/Doclify/discussions)
  [![GitHub License](https://img.shields.io/github/license/KalyanM45/Doclify?style=flat&color=blue)](https://github.com/KalyanM45/Doclify/blob/main/LICENSE)
</div>

---

**Doclify** is an AI agent that documents your software projects. It scans your codebase, builds structured context for each file using a multi-stage agentic pipeline, and generates a comprehensive, professional `README.md` — all from the command line.

But the tool itself is secondary. The real purpose of this project is described below.

---

## 🧠 Why This Project Exists — Advanced Context Engineering

This project is a **deliberate, hands-on laboratory for learning and practising advanced context engineering for AI agents**.

The core inspiration comes from **Dex Horthy** (founder of [HumanLayer](https://humanlayer.dev)) and his write-up on **[Advanced Context Engineering for Coding Agents](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md)** — one of the most concrete, practitioner-level treatments of what it actually takes to make AI agents work in real production codebases, not just toy examples.

> *"The contents of your context window are the ONLY lever you have to affect the quality of your output."*
> — Dex Horthy, HumanLayer

The thesis is direct: **AI agent failures in complex codebases are almost never model failures. They are context failures.** The agent hallucinated because a crucial fact was missing. It chose the wrong approach because it received ambiguous information. It produced low-quality output because it had no reference for what "good" looks like in this specific domain.

Picking a smarter model does not fix this. Structuring better context does.

Doclify is built as a real, non-trivial environment for testing, breaking, and improving context engineering techniques — with open source feedback loops that private experiments cannot replicate.

---

## 📖 The ACE Framework — What Dex Horthy's Research Actually Says

Read the full piece here: **[Advanced Context Engineering for Coding Agents](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md)**

Below is a detailed breakdown of the core principles and how Doclify's agentic pipeline is built around each of them.

---

### 1. LLMs Are Stateless Functions — Input Quality Is Everything

The 12-factor agents framework makes this point explicitly: LLMs have no persistent state. Every inference call starts from zero. The only thing that changes between a good result and a bad result — without retraining the model — is the quality of the input you construct.

This is not a minor observation. It reframes the entire problem. Asking "how do I get a better AI agent?" becomes the same question as "how do I build better inputs?"

**How Doclify applies this:**

Doclify treats every stage of its pipeline as an input construction problem. The two prompts in `prompts/batch_summary.txt` and `prompts/final_summary.txt` are not convenience wrappers — they are the primary engineering artefacts. The model is a fixed function; the input is what we control and optimise.

---

### 2. Frequent Intentional Compaction (FIC)

This is the central technique from the ACE document. The core idea: as an AI agent works through a complex problem, its context window fills with noisy intermediate state — file search results, tool call outputs, build logs, dead ends, partial reasoning. If you let this accumulate, the quality of the agent's output degrades. The agent starts to lose the thread.

**Intentional compaction** means pausing at strategic points and asking the agent to distil everything it has learned into a structured, compact document — capturing the end goal, the approach taken, what has been completed, and what the current blocker is. Then starting a fresh context window from that compact document rather than from the full noisy history.

Dex's recommended cadence: keep context window utilisation in the **40–60% range**. Never let the window fill. Compact before you need to.

The hierarchy of what makes a context window bad, in order of severity:

| Priority | Problem | Why It's Worse |
|----------|---------|----------------|
| 1 (worst) | Incorrect information | Agent makes confident wrong decisions |
| 2 | Missing information | Agent hallucinates to fill the gap |
| 3 | Too much noise | Agent loses signal, degrades on complex reasoning |

**How Doclify applies this:**

The two-stage pipeline is intentional compaction in code. Stage 1 forces each file through a compression step — a 500-line source file becomes 3–4 sentences of dense, structured signal. That summary is cached. Stage 2 assembles only the summaries (not the raw files) as input to the final agent call. The raw code never touches the final context window.

The cache in `.doclify/cache.json` is the compaction artefact. It stores the already-distilled state so the agent can resume from a clean, compact foundation on subsequent runs rather than re-processing everything from scratch.

---

### 3. Research → Plan → Implement

Dex's workflow splits agentic work into three distinct phases, each with a deliberately separate context window:

**Research** — the agent's only job is to understand the codebase: find relevant files, trace information flow, identify where the relevant logic lives. The output is a structured research document. Nothing is changed.

**Plan** — using the research document as input (not the raw codebase), the agent produces a step-by-step implementation plan: exact files to edit, precise testing strategy, verification steps per phase. The output is a plan document. Still nothing is changed.

**Implement** — the agent executes the plan phase by phase. After each verified phase, the current status is compacted back into the plan document before proceeding. Only this phase requires a working branch.

The key insight: **a bad line in the research document can produce thousands of bad lines of code**. A bad line in the plan can produce hundreds. A bad line of code is just a bad line of code. Human review effort should be concentrated at the highest-leverage point — research and planning — not at the code review stage after the damage is already done.

> *"I can't read 2000 lines of Go daily. But I can read 200 lines of a well-written implementation plan."*
> — Dex Horthy

**How Doclify applies this:**

`doclify init` is the research phase — the agent scans the repository, identifies all relevant files, and compiles its findings into `doclify.yaml`. No inference happens here; this is pure discovery.

`doclify run` is the plan-and-implement phase — it reads the structured output of init, processes each file in sequence, and builds toward the final README.

`doclify update <path>` is targeted re-planning — when a specific file changes, only that slice of the plan is invalidated and recomputed. The rest of the cached context remains valid.

---

### 4. Subagents for Context Isolation

From the ACE document: subagents are not about role-playing. They are a **context management tool**. When an agent needs to search a codebase, understand a dependency, or summarise a file, that discovery process generates a large volume of noisy intermediate output. If the parent agent does this work itself, that noise pollutes its context window for the rest of the task.

The solution: delegate discovery tasks to a subagent with a fresh context window. The subagent does the noisy work, distils the result into a compact summary, and returns only the summary to the parent. The parent's context window stays clean.

**How Doclify applies this:**

Each file summary call in the pipeline is effectively a subagent invocation — a fresh, bounded inference call whose only job is to distil one file into a dense paragraph. The parent pipeline never sees the raw file content again after handing it to the summariser. It only receives the compacted output.

This is why the two-stage architecture exists. A single-shot "summarise the entire codebase at once" approach would be both token-expensive and context-polluting. The subagent-per-file pattern keeps each call bounded and focused.

---

### 5. Specs Are the New Code — Prompts as Source Artefacts

Sean Grove's framing from AI Engineer 2025, cited in the ACE document: developers who vibe-code for two hours, discard their prompts, and commit only the final output are doing the equivalent of a Java developer committing a compiled JAR while throwing away the source.

**The prompt is the source. The generated output is the compiled artefact.**

This means prompts deserve the same rigour as code — version control, peer review, iteration, and documentation of why specific constraints exist.

**How Doclify applies this:**

The two prompt files in `doclify/prompts/` are version-controlled and treated as the primary engineering artefacts of the project. Every constraint in those prompts — negative examples ("do not write X"), explicit delimiters, output format rules — exists because removing it produced measurably worse output. The prompts have a changelog, not just the Python code.

When a generated README is poor quality, the first question is not "which model should we use?" — it is "what is missing or incorrect in the prompt that caused this context failure?"

---

### 6. Mental Alignment — The Hidden Cost of High-Volume AI Output

The ACE document identifies an underappreciated problem with productive AI agents: as code volume increases dramatically, a larger proportion of the codebase becomes unfamiliar to every engineer at any given time. Mental alignment — everyone on the team understanding how the code is changing and why — starts to break down.

Code review was designed to solve this. But it was designed for human-pace code production. At AI-agent pace (2000-line PRs every few days), code review can no longer carry the full mental-alignment load. The artefacts that maintain alignment need to move upstream — into research documents and implementation plans that engineers can actually read and evaluate before the code is written.

**How Doclify applies this:**

Documentation generated by Doclify is itself a mental alignment artefact. A well-structured README keeps the entire team oriented to what the project is, how it is structured, and how the key components relate. When the README is generated by an agent with good context, it is a side effect of the agent genuinely understanding the codebase — not a description of file names.

The quality of the README is a proxy for the quality of the agent's context. If the README is vague, the context was vague.

---

## 🎯 What Doclify Is Really Practising

| Context Engineering Concept | How Doclify Implements It |
|-----------------------------|---------------------------|
| Stateless LLM — input is everything | Prompts treated as primary engineering artefacts, not boilerplate |
| Frequent Intentional Compaction | Two-stage pipeline: raw files → dense summaries → final synthesis |
| Compaction artefact persistence | `cache.json` stores distilled state; runs resume from compact context |
| Subagent context isolation | Per-file summariser calls keep raw content out of the synthesis context window |
| Research → Plan → Implement | `init` (discover) → `run` (synthesise) → `update` (selective replan) |
| Minimise context window utilisation | Each inference call is bounded; raw files never enter the final context |
| Prompts as source code | `prompts/` are version-controlled; constraints are documented and reviewed |
| High-leverage human review | Every generated README is a reviewable artefact; failures trace back to prompt gaps |

---

## 🚀 Getting Started

### 1. Installation

```bash
pip install doclify
```

### 2. Configure Your API Key

Doclify runs its agentic pipeline against a fast LLM inference API. Set your API key as an environment variable or place it in a `.env` file at your project root.

| Platform | Command |
| :--- | :--- |
| **Windows (CMD)** | `set GROQ_API_KEY=your_api_key_here` |
| **Windows (PS)** | `$env:GROQ_API_KEY="your_api_key_here"` |
| **Linux / macOS** | `export GROQ_API_KEY=your_api_key_here` |
| **.env File** | `GROQ_API_KEY=your_api_key_here` |

*(Get a free API key at [console.groq.com](https://console.groq.com/))*

---

## 📖 CLI Reference

Doclify exposes four commands that map directly to the Research → Plan → Implement workflow.

### `doclify init` — Research Phase

Scan the repository and build the context manifest.

- Walks your project folder respecting all `.gitignore` rules
- Produces `doclify.yaml` — the structured list of files the agent will process
- Creates `.doclify/` for cache and log storage
- Safe to re-run: updates the file manifest while preserving your model configuration

```bash
doclify init
```

Run this first whenever you start documenting a new project, or when the project structure has changed significantly.

### `doclify models` — Discover Available Models

List all AI models available to the agent.

- Fetches a real-time table of available models with context window sizes and output limits
- Use this to select a model appropriate for your codebase size

```bash
doclify models
```

### `doclify set default <model_id>` — Configure the Agent

Set the default model for all future pipeline runs.

```bash
doclify set default llama-3.3-70b-versatile
```

This updates `doclify.yaml`. You can override it per-run with `--model`.

### `doclify run` — Plan and Implement Phase

Execute the full agentic documentation pipeline.

- Reads the file manifest from `doclify.yaml`
- Runs Stage 1: each file is processed by a bounded summariser agent → dense summary cached to `.doclify/cache.json`
- Runs Stage 2: all summaries are assembled into the final context window → README synthesised
- Backs up any existing `README.md` before overwriting

```bash
doclify run
```

Override the model for a single run without changing config:

```bash
doclify run --model qwen/qwen3-32b
```

### `doclify update <path>` — Selective Context Refresh

Recompute only the cache entries that are stale, then optionally regenerate the README.

- Targeted update: invalidates and recomputes the summary for a specific file or directory
- Full regeneration from existing cache: use `.` as the path

```bash
# Update a specific file's summary in the cache
doclify update src/database/connection.py

# Regenerate README from the current cache without re-running all summaries
doclify update .
```

This is the selective context refresh operation — the equivalent of re-running only the relevant slice of the compaction pipeline.

---

## ⚙️ Configuration (`doclify.yaml`)

```yaml
project: My Awesome Project
structure:
  - src/main.py
  - src/utils/helpers.py
llm:
  model: llama-3.3-70b-versatile
```

The `structure` list is the agent's context manifest — the explicit, curated set of files that will be processed. Keeping this list intentional (rather than letting the agent process every file blindly) is itself a context engineering decision: what does the agent actually need to understand this codebase, and what is noise?

Re-run `doclify init` to update the manifest when the project structure changes. Existing model configuration is preserved.

---

## 💬 Feedback, Issues, and Discussions

- **Found a bug?** Open an issue with your `doclify.yaml`, the command you ran, and the terminal output.
- **Generated README was wrong or off-tone?** That is a context engineering failure worth diagnosing. Share the output in [Discussions](https://github.com/KalyanM45/Doclify/discussions) — it helps improve the pipeline for everyone.
- **Ideas or experiments?** The [Discussions](https://github.com/KalyanM45/Doclify/discussions) tab is the right place. What context engineering techniques have you tried? What changed the output quality?

---

## 🤝 Contributing & License

Contributions make this a better learning environment. If you want to contribute, the most valuable areas are:

- **Prompt engineering** — if the README output was vague or off, the root cause is almost always in `prompts/`. Open an issue with the output and let's diagnose the context failure together.
- **Context pipeline experiments** — cross-file context injection, retrieval-augmented summarisation, structured intermediate outputs, subagent strategies.
- **Reliability improvements** — retry logic, atomic cache writes, async parallel summarisation.
- **New language support** — extending the agent beyond Python to JavaScript, Go, Rust, and other ecosystems.

Please open an issue before starting large changes so we can align on direction first. Feel free to fork, branch, and submit Pull Requests.

This project is licensed under the **GNU AGPLv3 License**. See the [LICENSE](LICENSE) file for details.
