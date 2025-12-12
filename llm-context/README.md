# LLM Context Files for Strata

This folder contains documentation artifacts designed to help local LLM models (Qwen, Ollama, DeepSeek, etc.) understand the Strata codebase without needing to scan all source files.

## For Claude Code Users

**Claude should ignore this folder unless explicitly asked.** These files are optimized for local LLMs with limited context windows. Claude Code can read the actual source files directly for more accurate responses.

## Files in This Folder

| File | Purpose |
|------|---------|
| `CODEBASE.md` | Project overview, directory structure, tech stack, development commands |
| `API.md` | Key functions, signatures, parameters, and usage patterns |
| `DATA_FORMATS.md` | YAML recipe schema, source URIs, and data structures |
| `ARCHITECTURE.md` | System design, data flow, and module relationships |

## How to Use with Local LLMs

### Basic Context Loading

Copy the relevant file(s) into your prompt. For most tasks, start with `CODEBASE.md`:

```
<context>
[Contents of CODEBASE.md]
</context>

Your question here...
```

### Task-Specific Context

| Task Type | Files to Include |
|-----------|-----------------|
| Understanding the project | `CODEBASE.md` |
| Writing new features | `CODEBASE.md` + `API.md` + `ARCHITECTURE.md` |
| Debugging build issues | `API.md` + `DATA_FORMATS.md` |
| Creating/editing recipes | `DATA_FORMATS.md` |
| Adding new data sources | `API.md` (thoreau section) |
| SVG/output issues | `API.md` (kelley section) |

### Example Prompts

**"How do I add a new layer to my recipe?"**
```
<context>
[Contents of DATA_FORMATS.md]
</context>

How do I add a new layer to my strata recipe that shows only roads with RTTYP="I" (interstates)?
```

**"How does the build pipeline work?"**
```
<context>
[Contents of ARCHITECTURE.md]
</context>

Explain how strata processes a recipe from YAML to SVG output.
```

**"I need to add support for a new data source"**
```
<context>
[Contents of API.md - thoreau section]
</context>

I want to add support for fetching data from OpenStreetMap. What functions do I need to implement?
```

## Context Size Estimates

| File | Approximate Tokens |
|------|-------------------|
| `README.md` (this file) | ~500 |
| `CODEBASE.md` | ~1,500 |
| `API.md` | ~3,000 |
| `DATA_FORMATS.md` | ~2,500 |
| `ARCHITECTURE.md` | ~1,500 |
| **Total** | **~9,000** |

All files combined fit comfortably in most local LLM context windows (8K-32K tokens), leaving room for your questions and responses.

## Keeping Context Updated

These files should be updated when:
- New modules or major functions are added
- The YAML recipe schema changes
- New data source providers are added
- The CLI interface changes significantly

The source of truth is always the actual code in `src/strata/`.
