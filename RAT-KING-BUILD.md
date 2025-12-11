# Rat-King Build & Packaging

## Current State

The rat-king Rust code lives inside strata at `crates/`, but the Python integration still references an **external binary path**:

```python
RAT_KING_DEFAULT = "/Users/mgilbert/Code/rat-king/crates/target/release/rat-king"
```

This is hardcoded in `src/strata/kelley/plotter_fill.py:28`.

## Problem

When strata is cloned to a new machine or by a different user, the rat-king binary path doesn't exist, breaking the `plotter-fill` functionality.

## Required Changes

### 1. Fix the default binary path (HIGH PRIORITY)

In `src/strata/kelley/plotter_fill.py:28`, change the hardcoded path to a relative path within the strata project:

```python
RAT_KING_DEFAULT = Path(__file__).parent.parent.parent.parent / "crates" / "target" / "release" / "rat-king"
```

### 2. Add rat-king build to the strata build/install process

Options (pick one):

a) **Add a build script** - Add `scripts/build_rat_king.sh` that runs `cargo build --release` in `crates/`

b) **Add pyproject.toml build hook** - Use `hatch` or `maturin` build hooks to compile Rust during `pip install`

c) **Include pre-built binary** - Ship the compiled binary in a `bin/` directory (not recommended for cross-platform)

### 3. Add strata CLI command to build rat-king

Add a `strata build-tools` or `strata setup` command that:

- Checks if Rust/Cargo is installed
- Runs `cargo build --release` in `crates/`
- Verifies the binary is working

### 4. Improve binary discovery logic

In `plotter_fill.py`, implement a search order:

1. User-specified path (via `--rat-king` flag or YAML config)
2. `RAT_KING_BIN` environment variable
3. Built binary in strata's `crates/target/release/`
4. System PATH (`which rat-king`)
5. Fail with helpful error message

### 5. Documentation updates needed

- `docs/` should explain that rat-king needs to be built
- Add to README or installation docs: `cd crates && cargo build --release`

### 6. Consider PyPI packaging (long-term)

Use `maturin` to publish rat-king as a Python package with embedded Rust binary, so `pip install strata` would also install rat-king automatically.

## Files to Modify

| File | Change |
|------|--------|
| `src/strata/kelley/plotter_fill.py` | Fix default path, improve discovery |
| `src/strata/cli.py` | Add build command |
| `pyproject.toml` | Add build hooks or scripts |
| `README.md` or `docs/` | Document build requirements |

## Current Architecture

```
strata/
├── src/strata/           # Python package
│   └── kelley/
│       └── plotter_fill.py  # Calls rat-king binary via subprocess
├── crates/               # Rust workspace (rat-king source)
│   ├── rat-king/         # Core library
│   └── rat-king-cli/     # CLI binary
└── RAT-KING-BUILD.md     # This file
```

## Quick Fix (Manual)

Until the above changes are implemented, build rat-king manually:

```bash
cd crates
cargo build --release
```

The binary will be at `crates/target/release/rat-king`.
