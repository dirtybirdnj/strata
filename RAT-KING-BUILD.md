# Rat-King Build & Distribution

## Goal

Build rat-king as a **standalone static binary** that can be distributed with strata. The binary should have zero runtime dependencies and work on any modern system without requiring users to install Rust or compile anything.

## Current State

- Rat-king source lives in `crates/` but is a separate project
- Python code references an external binary path (needs fixing)
- Binary is dynamically linked (has glibc dependencies)

## Solution: Static Binary Distribution

Rat-king should be built as a fully static binary in the **rat-king repo**, then distributed to strata users via:
1. GitHub releases (downloadable binaries)
2. Vendored in strata's `bin/` directory
3. Or installed via package manager (future)

### Why Static Linking?

- **Zero dependencies**: No glibc, no shared libraries needed
- **Portable**: Same binary works on any Linux distro
- **Simple distribution**: Single file to download/include
- **No Rust required**: Users don't need rustc/cargo installed

## Implementation in Rat-King Repo

### For Linux (using musl)

```bash
# Add the musl target
rustup target add x86_64-unknown-linux-musl

# Build static binary
cargo build --target x86_64-unknown-linux-musl --release

# Binary at: target/x86_64-unknown-linux-musl/release/rat-king
```

For ARM Linux:
```bash
rustup target add aarch64-unknown-linux-musl
cargo build --target aarch64-unknown-linux-musl --release
```

### For macOS

macOS binaries are already mostly static. Build with:
```bash
# Intel
cargo build --target x86_64-apple-darwin --release

# Apple Silicon
cargo build --target aarch64-apple-darwin --release
```

### For Windows

```bash
# Static link the C runtime
RUSTFLAGS='-C target-feature=+crt-static' cargo build --target x86_64-pc-windows-msvc --release
```

### Cargo Configuration

Add to `crates/.cargo/config.toml`:
```toml
[target.x86_64-unknown-linux-musl]
rustflags = ["-C", "target-feature=+crt-static", "-C", "link-self-contained=yes"]

[target.x86_64-pc-windows-msvc]
rustflags = ["-C", "target-feature=+crt-static"]
```

## Strata Integration Changes

Once rat-king publishes static binaries:

1. **Update default path** in `src/strata/kelley/plotter_fill.py`:
   - Look for binary in strata's `bin/` directory first
   - Fall back to system PATH
   - Fall back to `RAT_KING_BIN` env var

2. **Add binary discovery**:
   ```python
   def find_rat_king_binary():
       # 1. User override
       if user_specified:
           return user_specified
       # 2. Bundled with strata
       bundled = Path(__file__).parent.parent.parent.parent / "bin" / "rat-king"
       if bundled.exists():
           return bundled
       # 3. System PATH
       if shutil.which("rat-king"):
           return "rat-king"
       # 4. Environment variable
       if os.environ.get("RAT_KING_BIN"):
           return os.environ["RAT_KING_BIN"]
       raise RuntimeError("rat-king binary not found")
   ```

3. **Add download script** or document installation

---

## Prompt for Rat-King Agent

```
# Add Static Binary Build Support to Rat-King

## Goal
Enable building rat-king as a fully static, distributable binary with zero runtime dependencies.

## Tasks

### 1. Add Cargo configuration for static builds
Create `.cargo/config.toml` with targets:
- x86_64-unknown-linux-musl (Linux static)
- aarch64-unknown-linux-musl (Linux ARM static)
- x86_64-apple-darwin (macOS Intel)
- aarch64-apple-darwin (macOS Apple Silicon)
- x86_64-pc-windows-msvc (Windows static CRT)

### 2. Add build script
Create `scripts/build-release.sh` that:
- Builds for all available targets
- Strips binaries for smaller size
- Outputs to `dist/` directory with platform-specific names:
  - rat-king-linux-x86_64
  - rat-king-linux-aarch64
  - rat-king-macos-x86_64
  - rat-king-macos-aarch64
  - rat-king-windows-x86_64.exe

### 3. Add GitHub Actions workflow
Create `.github/workflows/release.yml` that:
- Triggers on version tags (v*)
- Builds static binaries for all platforms
- Creates GitHub release with binaries attached
- Uses cross-compilation where needed (cross-rs or native runners)

### 4. Verify no C dependencies
Check that all dependencies (usvg, svgtypes, lyon_geom, ratatui, crossterm, image, resvg, tiny-skia) support static linking without external C libraries.

### 5. Test static binaries
- Verify binary runs on fresh system (no Rust installed)
- Check with `ldd` that binary has no dynamic dependencies (Linux)
- Test on different distros (Ubuntu, Alpine, etc.)

## Reference
- musl target: https://doc.rust-lang.org/edition-guide/rust-2018/platform-and-target-support/musl-support-for-fully-static-binaries.html
- cross-rs for cross-compilation: https://github.com/cross-rs/cross
- Static CRT on Windows: RUSTFLAGS='-C target-feature=+crt-static'

## Expected Output
Static binaries that can be downloaded and run immediately without any dependencies.
```

---

## Sources

- [Rust Linkage Reference](https://doc.rust-lang.org/reference/linkage.html)
- [MUSL Support for Static Binaries](https://doc.rust-lang.org/edition-guide/rust-2018/platform-and-target-support/musl-support-for-fully-static-binaries.html)
- [rust-musl-builder](https://github.com/emk/rust-musl-builder) - Docker images for static builds
- [rust-musl-cross](https://github.com/rust-cross/rust-musl-cross) - Cross-compilation support
- [Building Statically Linked Rust Binaries](https://shivjm.blog/statically-linked-rust-binaries/)
