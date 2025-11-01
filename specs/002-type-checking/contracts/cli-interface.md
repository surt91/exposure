# CLI Interface Contract

This contract defines the command-line interface for running type checking with ty in the fotoview project.

**⚠️ PROVISIONAL**: Command syntax based on expected Astral patterns. Actual commands will be validated against ty documentation.

## Commands

### Primary Command: Type Check All Source Files

```bash
uv run ty check src/
```

**Purpose**: Type check all Python files in the src/ directory

**Note**: Command assumed to be `ty check` following ruff pattern. May be just `ty src/` or similar.

**Exit Codes**:
- `0`: Success - no type errors found
- `1`: Type errors found
- `2`: Fatal error (configuration issue, crash)

**Output Format**:
```
<file>:<line>: <severity>: <message>  [<error-code>]
```

**Example Success** (expected format):
```
$ uv run ty check src/
All checks passed! ✓
$ echo $?
0
```

**Example Failure** (expected format):
```
$ uv run ty check src/
src/generator/scan.py:42:5: error: Function is missing a return type annotation
src/generator/yaml_sync.py:18:10: error: Argument 1 has incompatible type "str"; expected "Path"
Found 2 errors in 2 files
$ echo $?
1
```

**Note**: Exact output format will match ty's implementation. Expected to follow Astral's excellent error formatting seen in ruff.

---

### Quick Check: Single File

```bash
uv run ty check src/generator/<filename>.py
```

**Purpose**: Type check a specific file (faster feedback during development)

**Example** (expected):
```bash
$ uv run ty check src/generator/model.py
All checks passed! ✓
```

---

### Verbose Mode: Show Context

```bash
uv run mypy --show-error-context src/
```

**Purpose**: Display additional context around errors

**Output Includes**:
- Source code line with error
- Error column pointer (^)
- Additional notes about error

**Example**:
```
src/generator/scan.py:42: error: Function is missing a return type annotation
def discover_images(content_dir: Path):
                                       ^
Note: Use -> list[Path] to annotate return type
```

---

### Show Error Codes: For Selective Ignoring

```bash
uv run mypy --show-error-codes src/
```

**Purpose**: Display error codes for selective suppression (use sparingly)

**Output**:
```
src/generator/scan.py:42: error: Function is missing a return type annotation  [no-untyped-def]
```

**Note**: Error codes should not be suppressed except for known limitations. Prefer fixing the code.

---

### Performance: Show Stats

```bash
uv run mypy --verbose src/
```

**Purpose**: Show performance statistics and cache hits

**Output Includes**:
- Files analyzed
- Cache hits/misses
- Time taken per module

---

### CI Mode: Summary Only

```bash
uv run mypy src/ --no-error-summary
```

**Purpose**: Cleaner output for CI logs (errors only, no summary line)

**Use Case**: CI pipelines that count lines or parse output

---

## Integration Commands

### Pre-commit Hook (optional future)

```bash
# .pre-commit-config.yaml
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.7.0
  hooks:
    - id: mypy
      args: [src/]
      additional_dependencies: [types-PyYAML, types-Pillow]
```

**Purpose**: Run type checking before commit

**Behavior**:
- Runs on staged Python files
- Blocks commit if errors found
- Fast due to incremental checking

---

### CI Pipeline Integration

```yaml
# .github/workflows/ci.yml
- name: Type check with mypy
  run: uv run mypy src/
```

**Purpose**: Enforce type checking in continuous integration

**Exit Code Handling**:
- Success (0): CI continues
- Failure (1): CI fails, blocks merge
- Fatal (2): CI fails with configuration error

---

## Error Output Format

### Standard Error Format

```
<file_path>:<line>: <severity>: <message>  [<error_code>]
```

**Components**:
- `file_path`: Relative path from project root
- `line`: Line number (1-indexed)
- `severity`: "error", "warning", or "note"
- `message`: Human-readable description
- `error_code`: mypy error classification (optional)

### Example Errors

#### Missing Return Type
```
src/generator/scan.py:16: error: Function is missing a return type annotation  [no-untyped-def]
```

#### Incompatible Types
```
src/generator/yaml_sync.py:42: error: Argument 1 to "load_gallery_yaml" has incompatible type "str"; expected "Path"  [arg-type]
```

#### Unused Type Ignore
```
src/generator/model.py:28: error: Unused "type: ignore" comment  [unused-ignore]
```

#### Any Unimported
```
src/generator/scan.py:7: error: Untyped import of "some_module"  [import]
```

---

## Performance Characteristics

### Incremental Mode (Default)

**First Run**:
- Analyzes all files: ~2-5 seconds
- Builds cache: .mypy_cache/
- No cache benefit

**Subsequent Runs**:
- Modified files only: ~1-2 seconds
- Uses cached type information
- Fast developer feedback

**Cache Invalidation**:
- Dependency version change
- Configuration change
- Manual: `rm -rf .mypy_cache/`

### Full Analysis (CI)

**CI First Build**:
- No cache: ~2-5 seconds
- Cache stored in GitHub Actions cache

**CI Subsequent Builds**:
- Cache hit: ~1-2 seconds
- Cache miss: ~2-5 seconds (rebuild)

---

## Configuration Flags

### Commonly Used Flags

#### --install-types (interactive)

```bash
uv run mypy --install-types src/
```

**Purpose**: Automatically install missing type stubs (requires confirmation)

**Not Recommended**: Use explicit type stub dependencies in pyproject.toml instead

#### --ignore-missing-imports (not recommended)

```bash
uv run mypy --ignore-missing-imports src/
```

**Purpose**: Suppress errors about missing type information

**Why Not**: Weakens type safety; prefer installing type stubs

#### --strict (redundant if in config)

```bash
uv run mypy --strict src/
```

**Purpose**: Enable strict mode from command line

**Note**: Already configured in pyproject.toml, no need to specify

---

## Help and Documentation

### Show All Options

```bash
uv run mypy --help
```

**Output**: Complete list of mypy command-line options

### Check Version

```bash
uv run mypy --version
```

**Expected**: `mypy 1.7.0` or higher

---

## Troubleshooting Commands

### Clear Cache

```bash
rm -rf .mypy_cache/
uv run mypy src/
```

**When**: After dependency updates, configuration changes, or mysterious errors

### Check Configuration

```bash
uv run mypy --config-file pyproject.toml --warn-unused-configs src/
```

**Purpose**: Verify configuration is valid and used

### Show Imported Modules

```bash
uv run mypy --verbose src/ 2>&1 | grep "Parsing"
```

**Purpose**: See which modules are being analyzed

---

## Expected Workflow

### Local Development

1. **Make code changes**
2. **Quick check**: `uv run mypy src/generator/build_html.py`
3. **See errors**: Fix type annotations or logic
4. **Full check**: `uv run mypy src/`
5. **Commit**: Changes should pass

### CI Pipeline

1. **Install dependencies**: `uv sync --dev`
2. **Run type check**: `uv run mypy src/`
3. **Exit code 0**: Continue to tests
4. **Exit code 1**: Fail build, show errors

---

## See Also

- [mypy Command Line Documentation](https://mypy.readthedocs.io/en/stable/command_line.html)
- Project: [pyproject.toml](../../../pyproject.toml) - Configuration
- Contract: [mypy-config.md](./mypy-config.md) - Configuration schema
