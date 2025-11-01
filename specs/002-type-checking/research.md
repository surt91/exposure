# Research: Type Checking and Type Annotations

**Feature**: 002-type-checking
**Date**: 2025-11-01
**Status**: Complete

## Overview

This document captures research decisions for introducing static type checking to the fotoview Python codebase. All technical unknowns from the planning phase are resolved here.

## Key Decisions

### Decision 1: Type Checker Tool Selection

**Decision**: Use **ty** from Astral as the static type checker

**Rationale**:
- **Astral ecosystem bet**: Built by Astral (creators of uv, ruff), proven track record with Python tooling
- **Performance-first design**: Rust-based implementation promises faster checking than Python-based tools
- **Modern Python support**: Native Python 3.11+ syntax support (list[str], X | Y unions)
- **Unified tooling**: Part of Astral's vision for integrated Python development tools
- **uv integration**: Seamless integration with uv (already used in project)
- **Future-ready**: Investing in the emerging standard as Astral demonstrates with ruff adoption
- **Experimental advantage**: Early adoption allows learning and feedback while tool matures
- **Simplified configuration**: Designed with modern Python workflows in mind

**Alternatives Considered**:
- **mypy**: Industry standard, mature ecosystem
  - Considered but rejected: Slower (Python-based), separate ecosystem from uv/ruff
  - Note: More mature but doesn't align with Astral ecosystem bet
- **pyright**: Microsoft's type checker, fast and modern
  - Rejected: Different ecosystem, less integrated with uv workflow
- **pyre**: Facebook's type checker
  - Rejected: Less community adoption, more focused on large codebases
- **pytype**: Google's type checker with inference
  - Rejected: Slower, less strict mode options, overkill for small project

**Strategic Rationale**:
This is partly an experiment to evaluate ty and partly a strategic bet on Astral's future dominance in Python tooling. Astral has proven excellence with:
- **uv**: Revolutionary Python package/project management (already adopted)
- **ruff**: Fastest Python linter/formatter (industry standard in <2 years)
- Track record suggests ty will become the preferred type checker

**Implementation Notes**:
- Install via: `ty` in dev dependencies (no version pin needed initially)
- Configuration likely in `pyproject.toml` (ty follows ruff/uv patterns)
- Exit code 0 = success, non-zero = errors (CI-friendly)
- Early adoption risk mitigated by small codebase (easy to migrate if needed)

---

### Decision 2: Type Stub Packages

**Decision**: Install official type stubs for third-party dependencies

**Rationale**:
- PyYAML lacks inline type hints; requires `types-PyYAML` stub package
- Pillow has some stubs but `types-Pillow` provides complete coverage
- Stubs are maintained by typeshed project (official Python typing effort)
- Enables full type checking of library calls without modifying dependencies
- ty should support standard typeshed stubs (following Python typing standards)

**Implementation**:
```toml
[project.optional-dependencies]
dev = [
    "ty",
    "types-PyYAML>=6.0",
    "types-Pillow>=10.0",
    # ... existing dev deps
]
```

**Alternatives Considered**:
- Ignore missing library types: Rejected - weakens type safety at API boundaries
- Inline stub files: Rejected - harder to maintain, duplicate effort from typeshed

**Note**: ty's stub handling will be validated during implementation. If ty has different requirements, this will be updated.

---

### Decision 3: Strictness Configuration

**Decision**: Enable strict mode for src/, relaxed for tests/

**Rationale**:
- Strict mode enforces maximum type safety in production code
- Test files use pytest fixtures and decorators with complex types
- Pragmatic approach: strict where it matters most
- Allows incremental adoption if needed
- ty should follow similar configuration patterns to ruff (TOML-based)

**Configuration Strategy** (provisional, subject to ty's actual configuration format):
```toml
[tool.ty]
python-version = "3.11"
strict = true

# Per-module overrides (if supported)
[tool.ty.per-file-ignores]
"tests/*" = ["untyped-def", "untyped-decorator"]
```

**Note**: Exact configuration format will be determined by ty's documentation. Expected to follow ruff's configuration patterns (Astral consistency).

**Strict Mode Expected to Include**:
- No implicit Optional
- All functions must have type annotations
- No dynamic typing (Any) without explicit annotation
- Return types required
- Unused ignores flagged

---

### Decision 4: Handling Optional PIL Import

**Decision**: Use `TYPE_CHECKING` conditional import for PIL types

**Rationale**:
- PIL is optional dependency (project works without it)
- Runtime code uses `try/except ImportError` pattern
- Type checker needs to know PIL types exist
- Python's `typing.TYPE_CHECKING` constant is False at runtime, True during type checking

**Implementation Pattern**:
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image as PILImage
else:
    try:
        from PIL import Image as PILImage
    except ImportError:
        PILImage = None  # type: ignore
```

**Alternatives Considered**:
- Make PIL required: Rejected - violates existing design (lightweight by default)
- Ignore PIL types: Rejected - loses type safety where PIL is used
- Stub out PIL locally: Rejected - duplicate effort, maintenance burden

---

### Decision 5: CI/CD Integration

**Decision**: Add ty step to existing GitHub Actions workflow

**Rationale**:
- Existing CI already runs pytest, ruff (both from Astral)
- Adding ty completes the Astral tooling suite
- Fast fail strategy: type check before expensive tests
- ty's Rust implementation should be faster than Python-based checkers
- Unified Astral tooling simplifies CI configuration

**CI Workflow Addition**:
```yaml
- name: Type check with ty
  run: uv run ty check src/
```

**Placement**: After dependency installation, before pytest (fast feedback)

**Cache Strategy**: ty will likely follow ruff's caching patterns (handled automatically by uv/ty)

---

### Decision 6: Incremental Adoption Strategy

**Decision**: Fix all type errors in one pass (feasible for small codebase)

**Rationale**:
- Codebase is small (~500-1000 LOC)
- Most functions already have return type hints
- Parameters need type annotations added
- Dataclasses in model.py already typed
- Estimated effort: 2-4 hours to annotate fully

**Approach**:
1. Run mypy to identify all missing annotations
2. Add parameter types to all functions
3. Fix any type inconsistencies revealed
4. Enable strict mode from start (no gradual migration needed)

**Alternatives Considered**:
- Gradual adoption with `# type: ignore`: Rejected - technical debt accumulation
- Module-by-module enablement: Rejected - unnecessary for small codebase

---

### Decision 7: Performance Optimization

**Decision**: Rely on ty's Rust-based performance and built-in caching

**Rationale**:
- ty is built in Rust, inherently faster than Python-based type checkers
- Astral tools (ruff, uv) demonstrate exceptional performance
- Expected to meet <5 second feedback requirement for developers
- Expected <10 second full codebase check requirement
- Caching likely handled automatically (following ruff patterns)

**Configuration** (provisional):
```toml
[tool.ty]
# Performance configuration likely minimal or automatic
# Following Astral's "fast by default" philosophy
```

**Cache Management**:
- Cache directory likely `.ty_cache/` or similar (to be added to `.gitignore`)
- CI will handle caching automatically via uv
- Developers benefit from fast Rust implementation without manual tuning

---

### Decision 8: Error Message Handling

**Decision**: Use ty's default error format (expected to follow ruff patterns)

**Rationale**:
- Astral tools (ruff) have excellent error formatting with clear messages
- Expected format: `file.py:line:col: error: message`
- Parseable by IDEs and CI tools
- Color output in terminal, plain in CI
- Likely includes helpful context and suggestions (ruff-style)
- No need for custom formatters

**Expected Output** (based on Astral patterns):
```
src/generator/scan.py:42:5: error: Function is missing a return type annotation
src/generator/yaml_sync.py:18:10: error: Argument 1 has incompatible type "str"; expected "Path"
```

**Note**: Actual format will be confirmed during implementation. Astral's track record suggests excellent error UX.

---

## Integration Patterns

### Pattern 1: Type Checking in Development Workflow

**Local Development**:
```bash
# Quick check current file
uv run ty check src/generator/build_html.py

# Full codebase check
uv run ty check src/

# With watch mode (if supported, following ruff --watch pattern)
uv run ty check --watch src/
```

**Pre-commit Hook** (optional future enhancement):
```yaml
# .pre-commit-config.yaml
- repo: https://github.com/astral-sh/ty
  rev: v0.1.0  # Or latest version
  hooks:
    - id: ty
      additional_dependencies: [types-PyYAML, types-Pillow]
```

**Note**: Pre-commit configuration subject to ty's release and hook availability.

### Pattern 2: Handling Type Errors in Tests

**Strategy**: Allow test-specific patterns while maintaining safety

**Common Test Patterns**:
- Fixtures without annotations: Allowed in tests/
- Mock objects: Use `unittest.mock` with proper typing
- Parametrize decorators: Types inferred from values

**Example**:
```python
# tests/unit/test_model.py
import pytest
from pathlib import Path

def test_image_creation(tmp_path: Path) -> None:  # tmp_path annotated
    """Test docstring."""
    img = Image(filename="test.jpg", file_path=tmp_path / "test.jpg", category="Test")
    assert img.filename == "test.jpg"
```

### Pattern 3: Union Types and Optional

**Modern Python 3.11+ Syntax**:
```python
# Use X | Y instead of Union[X, Y]
def get_dimensions(path: Path) -> tuple[int, int] | None:
    ...

# Use X | None instead of Optional[X]
def find_image(name: str) -> Image | None:
    ...
```

## Open Questions (Resolved with Provisos)

Technical unknowns from planning phase are resolved with implementation validation needed:

- ✅ Type checker tool: **ty** selected (Astral bet)
- ✅ Type stub packages: types-PyYAML, types-Pillow (standard typeshed)
- ⚠️ Configuration approach: pyproject.toml [tool.ty] section (format TBD)
- ⚠️ Strictness levels: Strict for src/, relaxed for tests/ (exact flags TBD)
- ✅ Optional dependencies: TYPE_CHECKING pattern (Python standard)
- ✅ CI integration: GitHub Actions `uv run ty check` step
- ⚠️ Performance: Rust-based, expected fast (benchmarks TBD)
- ✅ Adoption strategy: Full annotation in single pass

**Implementation Notes**:
- ⚠️ Indicates provisional decisions that will be validated during implementation
- ty is new/experimental; documentation will guide final configuration
- Fallback to mypy possible if ty blockers discovered (migration easy with standard annotations)

## References

- [Astral](https://astral.sh/) - Creator of uv, ruff, and ty
- [ty repository](https://github.com/astral-sh/ty) - Type checker source
- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [PEP 604 - Union Syntax](https://www.python.org/dev/peps/pep-0604/)
- [Python typing module](https://docs.python.org/3/library/typing.html)
- [typeshed repository](https://github.com/python/typeshed)
- [ruff documentation](https://docs.astral.sh/ruff/) - Reference for Astral tool patterns

## Next Steps

Proceed to Phase 1:
- Create data-model.md (type checking entities)
- Create contracts/ (configuration schemas)
- Create quickstart.md (developer commands)
- Update agent context
