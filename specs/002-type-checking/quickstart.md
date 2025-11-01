# Quickstart: Type Checking with ty

This guide helps developers quickly start using type checking with **ty** from Astral in the fotoview project.

**⚠️ Note**: ty is a new tool from Astral. This guide uses expected command patterns based on Astral's other tools (ruff, uv). Commands will be validated during implementation.

## Prerequisites

- Python 3.11+ installed
- Project dependencies installed: `uv sync --dev`
- ty installed as dev dependency

## 5-Minute Setup

### 1. Verify Installation

```bash
# Check ty is installed
uv run ty --version
# Expected: ty version info
```

### 2. Run Type Checker

```bash
# Check all source files
uv run ty check src/

# Expected output (when types are complete):
# All checks passed! ✓
```

### 3. Interpret Results

**Success** (exit code 0):
```
All checks passed! ✓
```
✅ All type checks passed. You're good to commit!

**Errors** (exit code 1):
```
src/generator/scan.py:42:5: error: Function is missing a return type annotation
Found 1 error in 1 file
```
❌ Fix the errors before committing. See "Fixing Common Errors" below.

## Common Development Tasks

### Check a Single File

```bash
# Faster feedback during development
uv run ty check src/generator/model.py
```

### Check Before Commit

```bash
# Run full check
uv run ty check src/

# If successful (exit 0), commit
git add .
git commit -m "Add feature X with type annotations"
```

### Integration with Editor

**VS Code**: ty integration expected via Python extension or dedicated extension
- Install: Python extension (already recommended for project)
- Type errors expected to appear as red squiggles (once ty support added)
- Hover for error details

**Configuration** (TBD): ty integration settings will be added when available.

**Note**: Early ty adoption may mean editor integration is limited initially. Type checking via CLI (`uv run ty check`) provides full functionality.

## Fixing Common Errors

### Error: Missing Return Type Annotation

```
src/generator/scan.py:16: error: Function is missing a return type annotation
```

**Fix**: Add return type after function parameters:

```python
# Before
def discover_images(content_dir: Path):
    ...

# After
def discover_images(content_dir: Path) -> list[Path]:
    ...
```

### Error: Missing Parameter Type Annotation

```
src/generator/yaml_sync.py:10: error: Function is missing a type annotation for one or more arguments
```

**Fix**: Add types to all parameters (except self/cls):

```python
# Before
def load_gallery_yaml(yaml_path):
    ...

# After
def load_gallery_yaml(yaml_path: Path) -> tuple[list[str], list[YamlEntry]]:
    ...
```

### Error: Incompatible Type

```
src/generator/yaml_sync.py:42: error: Argument 1 has incompatible type "str"; expected "Path"
```

**Fix**: Convert string to Path:

```python
# Before
load_gallery_yaml("config/gallery.yaml")

# After
from pathlib import Path
load_gallery_yaml(Path("config/gallery.yaml"))
```

### Error: Optional Type Not Handled

```
src/generator/scan.py:70: error: Incompatible return value type (got "tuple[int, int] | None", expected "tuple[int, int]")
```

**Fix**: Update return type to allow None:

```python
# Before
def get_image_dimensions(image_path: Path) -> tuple[int, int]:
    ...
    return None  # This caused the error

# After
def get_image_dimensions(image_path: Path) -> tuple[int, int] | None:
    ...
    return None  # Now allowed
```

### Error: Unused Type Ignore

```
src/generator/model.py:28: error: Unused "type: ignore" comment
```

**Fix**: Remove the unnecessary comment:

```python
# Before
PILImage = None  # type: ignore

# After (if the ignore isn't needed)
PILImage = None
```

## Type Annotation Quick Reference

### Basic Types

```python
# Primitives
def count_images(num: int) -> bool:
    ...

# Strings
def get_title(filename: str) -> str:
    ...

# Path objects
from pathlib import Path
def load_file(path: Path) -> str:
    ...
```

### Collections (Python 3.11+ Syntax)

```python
# Lists
def get_filenames() -> list[str]:
    ...

# Dictionaries
def get_entry_map() -> dict[str, YamlEntry]:
    ...

# Tuples (fixed size)
def get_dimensions() -> tuple[int, int]:
    ...

# Tuples (variable size)
def get_values() -> tuple[str, ...]:
    ...
```

### Optional Types

```python
# Use X | None instead of Optional[X]
def find_image(name: str) -> Image | None:
    ...

# Multiple alternatives
def parse_value(text: str) -> int | float | str:
    ...
```

### Functions

```python
# No return value (use -> None)
def save_file(path: Path, content: str) -> None:
    ...

# Multiple parameters
def create_image(
    filename: str,
    category: str,
    title: str | None = None
) -> Image:
    ...
```

## Working with Tests

Test files have relaxed type checking rules:

```python
# tests/unit/test_model.py

# Fixture parameter types are optional
def test_image_creation(tmp_path):  # tmp_path: Path annotation optional
    """Test docstring."""
    # But return type is still required
    img = Image(filename="test.jpg", file_path=tmp_path / "test.jpg", category="Test")
    assert img.filename == "test.jpg"  # Type checker validates this
```

**What's relaxed in tests**:
- Fixture parameters don't need annotations
- Decorator types aren't enforced
- Test functions can omit `-> None` if obvious

**What's still enforced**:
- Type consistency in test bodies
- Correct types when calling source functions
- Return values from helper functions

## Performance Tips

### Rust Speed (Built-in)

ty is built in Rust, making it inherently fast:

```bash
# Expected performance: ~1-2 seconds for full check
uv run ty check src/

# Subsequent runs: Even faster with caching
uv run ty check src/
```

### Clear Cache if Needed

```bash
# After dependency updates or strange errors
# Cache location TBD (likely .ty_cache/ or similar)
rm -rf .ty_cache/  # Adjust based on actual cache directory
uv run ty check src/
```

### Check Only What Changed

```bash
# Single file for quick feedback
uv run ty check src/generator/model.py

# Then full check before commit
uv run ty check src/
```

**Performance Expectation**: ty's Rust implementation should significantly outperform Python-based type checkers, easily meeting the <5 second feedback requirement.

## CI Integration

Type checking runs automatically in CI:

```yaml
# .github/workflows/ci.yml
- name: Type check with mypy
  run: uv run mypy src/
```

**If CI fails**:
1. Pull latest changes: `git pull`
2. Run locally: `uv run mypy src/`
3. Fix errors shown
4. Commit and push

## Troubleshooting

### Problem: ty not found

```bash
$ uv run ty check src/
Command not found: ty
```

**Solution**: Install dev dependencies
```bash
uv sync --dev
```

### Problem: Type stubs missing

```
src/generator/yaml_sync.py:6: error: Library stubs not installed for "yaml"
```

**Solution**: Verify type stubs are installed
```bash
# Check pyproject.toml has:
# types-PyYAML>=6.0
# types-Pillow>=10.0

# Reinstall
uv sync --dev
```

### Problem: Cache issues

```
Internal error: ty cache is inconsistent
```

**Solution**: Clear cache
```bash
rm -rf .ty_cache/  # Adjust based on actual cache directory
uv run ty check src/
```

### Problem: Unexpected behavior

**ty is experimental**: If you encounter issues:
1. Check [ty GitHub repository](https://github.com/astral-sh/ty) for known issues
2. Verify you're using latest ty version: `uv sync --dev`
3. Report issues to Astral (they're very responsive)
4. Fallback option: Type annotations are standard Python, can switch to mypy if needed

### Problem: False positive errors

**Check**:
1. Is your code actually correct?
2. Are you using Python 3.11+ syntax?
3. Are type stubs installed?

**Last Resort**: Add `# type: ignore` comment (but file an issue first!)
```python
result = complex_function()  # type: ignore[error-code]
```

## Getting Help

### Error Messages

All mypy errors include:
- **File and line**: Where the issue is
- **Error code**: Type of issue (in brackets)
- **Message**: What's wrong

Example:
```
src/generator/scan.py:42: error: Function is missing a return type annotation  [no-untyped-def]
^file             ^line  ^severity  ^message                                    ^code
```

### Documentation

- **mypy docs**: https://mypy.readthedocs.io/
- **Python typing**: https://docs.python.org/3/library/typing.html
- **PEP 484**: https://www.python.org/dev/peps/pep-0484/ (Type hints spec)

### Project-Specific

- **Configuration**: See `contracts/mypy-config.md`
- **CLI details**: See `contracts/cli-interface.md`
- **Data model**: See `data-model.md`
- **Research decisions**: See `research.md`

## Next Steps

Once type checking is set up:

1. **Write new code**: Always add type annotations
2. **Modify existing code**: Ensure types remain correct
3. **Run checks**: `uv run mypy src/` before committing
4. **Fix errors**: Use this guide to resolve issues
5. **CI will enforce**: Type checking gates in pull requests

**Remember**: Type checking catches bugs at development time, not runtime. Invest a few seconds adding types to save minutes debugging later!
