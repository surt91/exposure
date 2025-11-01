# Data Model: Type Checking Configuration

**Feature**: 002-type-checking
**Date**: 2025-11-01
**Status**: Provisional (ty configuration format TBD)

## Overview

This document defines the configuration entities and structures for the type checking system using **ty** from Astral. Unlike runtime data models, these represent development-time configuration and metadata used by the type checker.

**Note**: Configuration format is provisional and will be validated against ty's actual documentation during implementation. Expected to follow Astral patterns (similar to ruff configuration).

## Configuration Entities

### Entity 1: Type Checker Configuration

**Description**: Main configuration for ty type checker behavior

**Location**: `pyproject.toml` under `[tool.ty]` section (provisional)

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| python_version | string | Yes | Target Python version (e.g., "3.11") |
| strict | boolean | Yes | Enable all strict checks |
| warn_return_any | boolean | Yes | Warn when returning Any from typed function |
| warn_unused_configs | boolean | Yes | Warn about unused configuration options |
| disallow_untyped_defs | boolean | Yes | Require type annotations on all functions |
| disallow_any_unimported | boolean | Yes | Disallow Any from untyped imports |
| incremental | boolean | Yes | Enable incremental type checking |
| cache_dir | string | Yes | Directory for caching (.mypy_cache) |

**Validation Rules**:
- python_version must match project requirement (3.11+)
- cache_dir must be writable by developer
- strict=true implies multiple sub-settings

**Example** (provisional format):
```toml
[tool.ty]
python-version = "3.11"
strict = true
# Additional settings TBD based on ty documentation
# Expected to follow ruff-style configuration patterns
```

**Note**: Exact configuration keys will be determined by ty's documentation.

---

### Entity 2: Per-Module Override Configuration

**Description**: Module-specific type checking rules that override global settings

**Location**: `pyproject.toml` under `[[tool.mypy.overrides]]` (array of tables)

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| module | string | Yes | Module pattern (e.g., "tests.*") |
| disallow_untyped_defs | boolean | No | Override for untyped function definitions |
| disallow_untyped_decorators | boolean | No | Override for untyped decorators |
| ignore_errors | boolean | No | Suppress all errors in module |
| follow_imports | string | No | How to handle imports ("normal", "silent", "skip") |

**Validation Rules**:
- module pattern must be valid Python module glob
- At least one override setting must be specified
- Cannot have conflicting overrides for same module

**Relationships**:
- Belongs to TypeCheckerConfiguration (one-to-many)
- Overrides global strict mode settings for specific modules

**Example**:
```toml
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
disallow_untyped_decorators = false
```

---

### Entity 3: Type Stub Dependency

**Description**: External type information packages for third-party libraries

**Location**: `pyproject.toml` under `[project.optional-dependencies]` dev section

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| package_name | string | Yes | Name of type stub package (e.g., "types-PyYAML") |
| version_constraint | string | Yes | Version specification (e.g., ">=6.0") |

**Validation Rules**:
- package_name must start with "types-" prefix
- version_constraint must be valid PEP 440 version specifier
- Stub package must correspond to an actual dependency

**Relationships**:
- One TypeStubDependency per third-party library requiring stubs
- Must match corresponding runtime dependency

**Example**:
```toml
[project.optional-dependencies]
dev = [
    "mypy>=1.7",
    "types-PyYAML>=6.0",
    "types-Pillow>=10.0",
]
```

---

### Entity 4: Type Annotation

**Description**: Type hint metadata attached to function parameters and return values (conceptual entity, not configuration)

**Location**: Python source code inline

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| target | string | Yes | What is annotated (parameter, return, attribute) |
| type_expression | string | Yes | Type specification (e.g., "Path", "list[str]") |
| optional | boolean | No | Whether None is allowed (X \| None) |

**Validation Rules**:
- type_expression must be valid Python type syntax
- Must use Python 3.11+ union syntax (X \| Y, not Union[X, Y])
- No bare "Any" without justification comment

**Examples**:
```python
# Parameter annotation
def load_config(settings_path: Path) -> GalleryConfig:
    ...

# Return type with optional
def get_image_dimensions(image_path: Path) -> tuple[int, int] | None:
    ...

# Multiple parameters
def append_stub_entries(
    yaml_path: Path,
    new_filenames: list[str],
    default_category: str
) -> int:
    ...
```

---

### Entity 5: Type Error Report

**Description**: Output from mypy when type checking fails (runtime entity)

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| file_path | string | Yes | Source file with error |
| line_number | integer | Yes | Line where error occurs |
| column_number | integer | No | Column position (if available) |
| error_code | string | Yes | mypy error code (e.g., "arg-type", "return-value") |
| message | string | Yes | Human-readable error description |
| severity | string | Yes | "error", "warning", "note" |

**Validation Rules**:
- line_number must be positive integer
- file_path must exist in project
- error_code must be valid mypy error code

**State Transitions**:
1. Type check triggered → errors generated
2. Developer fixes code → errors resolved
3. CI runs check → reports errors if present

**Example Output**:
```
src/generator/scan.py:42: error: Function is missing a return type annotation  [no-untyped-def]
src/generator/yaml_sync.py:18: error: Argument 1 to "load_gallery_yaml" has incompatible type "str"; expected "Path"  [arg-type]
Found 2 errors in 2 files (checked 6 source files)
```

---

## Configuration Schema Relationships

```
TypeCheckerConfiguration (1)
  ├─→ (1..N) PerModuleOverride
  └─→ (1..N) TypeStubDependency

SourceFile (N)
  ├─→ (N) TypeAnnotation
  └─→ (0..N) TypeErrorReport
```

**Key Relationships**:
1. **One configuration per project**: Single `[tool.mypy]` section
2. **Multiple overrides**: Tests, generated code, third-party code
3. **Multiple stubs**: One per typed third-party dependency
4. **Annotations per function**: Parameters + return type
5. **Errors per file**: Zero when code is correctly typed

---

## Validation Summary

**Configuration Validation** (at parse time):
- TOML syntax must be valid
- All required mypy options must be present
- Module override patterns must be valid glob syntax
- Type stub versions must match dependency versions

**Runtime Validation** (at type check time):
- All function definitions have return type annotations
- All parameters (except self/cls) have type annotations
- Type annotations use Python 3.11+ syntax
- No implicit Any types in strict mode
- Imported types are available (stubs installed)

---

## Configuration Files

### Primary Configuration: pyproject.toml

```toml
[tool.mypy]
# Global strict settings
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_unimported = true
incremental = true
cache_dir = ".mypy_cache"

# Relaxed rules for tests
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
disallow_untyped_decorators = false
```

### Supporting Configuration: .gitignore

```
# Type checking cache
.mypy_cache/
```

### CI Configuration: .github/workflows/ci.yml

```yaml
- name: Type check with mypy
  run: |
    uv run mypy src/
```

---

## Migration Path

Since this is a new feature with no existing configuration:

1. **Initial State**: No type checker configuration
2. **Add Configuration**: Create [tool.mypy] section in pyproject.toml
3. **Install Dependencies**: Add mypy and type stubs to dev dependencies
4. **Fix Annotations**: Add missing type hints to source code
5. **Enable CI Gate**: Add mypy step to GitHub Actions
6. **Final State**: 100% type coverage with CI enforcement

No data migration needed - purely additive configuration.

---

## Next Steps

Proceed to:
- Create contracts/ (configuration file schemas)
- Create quickstart.md (developer commands)
