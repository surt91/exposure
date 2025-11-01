# Contract: CLI Entry Point

**Feature**: 006-tool-rename-cli
**Type**: Console Script Entry Point
**Status**: Proposed

## Purpose

Define the contract for the `exposure` command-line interface entry point that users invoke to build static galleries.

## Entry Point Definition

**Package**: `pyproject.toml`
**Section**: `[project.scripts]`
**Entry**: `exposure = "src.generator.build_html:main"`

This creates an executable command `exposure` that can be invoked via:
- `uv run exposure` (recommended - uses project environment)
- `exposure` (if package installed globally)

## Command Interface

### Invocation

```bash
exposure [CONFIG_PATH]
```

### Arguments

- `CONFIG_PATH` (optional): Path to settings.yaml file
  - Default: `config/settings.yaml`
  - Type: File path (absolute or relative to current directory)
  - Example: `exposure /path/to/custom/settings.yaml`

### Environment Variables

Configuration can be overridden via environment variables with `EXPOSURE_` prefix:

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `EXPOSURE_CONTENT_DIR` | Path | Source images directory | `EXPOSURE_CONTENT_DIR=photos/` |
| `EXPOSURE_GALLERY_YAML_PATH` | Path | Metadata YAML file | `EXPOSURE_GALLERY_YAML_PATH=meta.yaml` |
| `EXPOSURE_DEFAULT_CATEGORY` | String | Default category name | `EXPOSURE_DEFAULT_CATEGORY=Misc` |
| `EXPOSURE_ENABLE_THUMBNAILS` | Boolean | Enable image metadata | `EXPOSURE_ENABLE_THUMBNAILS=true` |
| `EXPOSURE_OUTPUT_DIR` | Path | Output directory | `EXPOSURE_OUTPUT_DIR=build` |
| `EXPOSURE_LOCALE` | String | UI language (en, de) | `EXPOSURE_LOCALE=de` |
| `EXPOSURE_LOG_LEVEL` | String | Log verbosity | `EXPOSURE_LOG_LEVEL=DEBUG` |

### Exit Codes

| Code | Meaning | When Returned |
|------|---------|---------------|
| 0 | Success | Gallery built successfully |
| 1 | Error | Any error during build (missing files, invalid config, etc.) |

### Output

**Standard Output (stdout)**:
- Log messages at configured level (INFO by default)
- Progress indicators (scanning, generating, etc.)
- Success confirmation with output path

**Standard Error (stderr)**:
- Error messages
- Warning messages
- Exception tracebacks (DEBUG level only)

**File System**:
- Generates static HTML gallery in configured output directory
- Default: `dist/`
- Structure:
  ```
  dist/
  ├── index.html           # Main gallery page
  ├── gallery-{hash}.css   # Stylesheet (content-hashed)
  ├── gallery-{hash}.js    # JavaScript (content-hashed)
  └── images/              # Copied images (content-hashed)
      ├── image1-{hash}.jpg
      └── image2-{hash}.jpg
  ```

## Entry Point Function

**Module**: `src.generator.build_html`
**Function**: `main()`

### Function Signature

```python
def main() -> None:
    """CLI entry point for exposure command."""
```

### Responsibilities

1. Setup logging via `setup_logging()` from `src.generator`
2. Parse command-line arguments (config path)
3. Call `build_gallery(config_path)`
4. Handle exceptions and exit with appropriate code
5. Report success/failure to stdout/stderr

### Error Handling

- **FileNotFoundError**: Missing config/content files → exit 1, clear error message
- **ValidationError**: Invalid config → exit 1, show validation errors
- **ValueError**: Duplicate filenames, invalid data → exit 1, describe issue
- **Exception**: Unexpected errors → exit 1, show traceback if DEBUG level

## Backward Compatibility

### Old Command Support

The legacy command continues to work:

```bash
uv run python -m src.generator.build_html
```

**Rationale**: Python module execution is a language feature, not controllable by the package.

**Recommendation**: All documentation should promote `uv run exposure` as the primary method.

### Environment Variables

No backward compatibility for environment variables:
- Old `FOTOVIEW_*` prefix will **not** work after rename
- Only `EXPOSURE_*` prefix supported
- Justification: No existing users yet - clean break opportunity

## Examples

### Basic Usage

```bash
# Build gallery with default settings
uv run exposure

# Build with custom config
uv run exposure config/production.yaml
```

### Environment Override

```bash
# Build with German locale
EXPOSURE_LOCALE=de uv run exposure

# Build to custom output directory
EXPOSURE_OUTPUT_DIR=public uv run exposure

# Debug mode
EXPOSURE_LOG_LEVEL=DEBUG uv run exposure
```

### CI/CD Integration

```bash
# GitHub Actions example
- name: Build gallery
  run: |
    EXPOSURE_OUTPUT_DIR=docs \
    EXPOSURE_LOG_LEVEL=INFO \
    uv run exposure
```

## Validation

After implementation, verify:

1. **Command resolves**: `uv run exposure --help` (once --help added) or `uv run exposure` runs without error
2. **Arguments work**: `uv run exposure config/settings.yaml` uses specified config
3. **Env vars work**: `EXPOSURE_LOCALE=de uv run exposure` applies override
4. **Exit codes correct**: Success returns 0, errors return 1
5. **Output readable**: Log messages clear and informative
6. **Error messages helpful**: Missing files show which file and where to place it

## Non-Goals

This contract does **not** include:
- Additional command-line flags (--version, --help, --verbose) - may be added in future
- Subcommands (exposure init, exposure serve) - out of scope for rename
- Interactive mode - tool remains fully scriptable
- Configuration file generation - users create config/settings.yaml manually

## References

- Python Packaging User Guide: [Entry Points](https://packaging.python.org/en/latest/specifications/entry-points/)
- PEP 621: [Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- Feature Spec: [spec.md](../spec.md)
- Data Model: [data-model.md](../data-model.md)
