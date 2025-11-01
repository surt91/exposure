# ty Configuration Schema

This contract defines the structure of the `[tool.ty]` configuration section in `pyproject.toml`.

**⚠️ PROVISIONAL**: This schema is based on expected patterns from Astral tools (ruff, uv). Actual configuration format will be validated against ty documentation during implementation.

## Schema Version

- **Version**: 0.1.0 (Provisional)
- **ty Version**: Latest from Astral
- **Format**: TOML

## Configuration Structure (Provisional)

```toml
[tool.ty]
# Expected settings (format TBD)
python-version = "3.11"           # string: Python version to target (ruff-style kebab-case)
strict = true                      # boolean: Enable all strict checks (assumed)

# Per-file/module ignores (following ruff pattern)
[tool.ty.per-file-ignores]
"tests/*" = ["untyped-def", "untyped-decorator"]

# Alternative: explicit excludes
exclude = [
    "tests/accessibility/*",  # If needed for specific exemptions
]
```

**Configuration Philosophy**: Expected to follow Astral patterns:
- Kebab-case for keys (`python-version` not `python_version`)
- Simple, flat structure where possible
- Per-file ignores similar to ruff
- Sensible defaults requiring minimal configuration

## Field Specifications

### Global Settings

#### python_version (required)

- **Type**: string
- **Format**: "MAJOR.MINOR" (e.g., "3.11")
- **Constraints**: Must be >= 3.11 for this project
- **Purpose**: Defines which Python syntax features are valid

#### strict (required)

- **Type**: boolean
- **Default**: false (but required true for this project)
- **Purpose**: Enables all strict checking options at once
- **Implies**: Multiple sub-settings are enabled

#### warn_return_any (required)

- **Type**: boolean
- **Default**: false (but required true for this project)
- **Purpose**: Warn when a typed function returns Any

#### warn_unused_configs (required)

- **Type**: boolean
- **Default**: false (but required true for this project)
- **Purpose**: Detect typos or outdated configuration options

#### disallow_untyped_defs (required)

- **Type**: boolean
- **Default**: false (but required true for this project)
- **Purpose**: Enforce that all functions have type annotations

#### disallow_any_unimported (required)

- **Type**: boolean
- **Default**: false (but required true for this project)
- **Purpose**: Prevent implicit Any from missing type stubs

#### incremental (required)

- **Type**: boolean
- **Default**: true
- **Purpose**: Cache type information for faster subsequent checks

#### cache_dir (required)

- **Type**: string
- **Format**: Relative or absolute path
- **Default**: ".mypy_cache"
- **Constraints**: Must be writable, should be in .gitignore
- **Purpose**: Directory to store incremental cache

### Per-Module Overrides

Array of override configurations using `[[tool.mypy.overrides]]` syntax.

#### module (required in override)

- **Type**: string
- **Format**: Python module glob pattern
- **Examples**: "tests.*", "tests.unit.*", "scripts.*"
- **Purpose**: Identifies which modules this override applies to

#### disallow_untyped_defs (optional in override)

- **Type**: boolean
- **Purpose**: Override global setting for specific modules
- **Common Use**: Set to false for test modules

#### disallow_untyped_decorators (optional in override)

- **Type**: boolean
- **Purpose**: Override global setting for specific modules
- **Common Use**: Set to false for test modules with pytest decorators

## Validation Rules

1. **Required Fields**: All global settings listed as "required" must be present
2. **Type Correctness**: All fields must match specified types
3. **Version Compatibility**: python_version must be valid Python version string
4. **Path Validity**: cache_dir must be valid path syntax
5. **Override Completeness**: Each override must have at least one overridden setting
6. **No Conflicts**: Cannot have duplicate overrides for same module pattern

## Error Handling

If configuration is invalid, mypy will:

1. **Parse Error**: Exit with error if TOML syntax is invalid
2. **Unknown Option**: Warn if warn_unused_configs=true
3. **Invalid Value**: Exit with error explaining invalid setting
4. **Missing Required**: Use defaults (but we enforce required settings)

## Example Valid Configuration

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_unimported = true
incremental = true
cache_dir = ".mypy_cache"

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
disallow_untyped_decorators = false

[[tool.mypy.overrides]]
module = "tests.accessibility.*"
ignore_errors = false  # Still check accessibility tests
```

## Configuration Inheritance

Settings follow this priority order (highest to lowest):

1. Command-line flags (e.g., `mypy --strict`)
2. Per-module overrides in `[[tool.mypy.overrides]]`
3. Global settings in `[tool.mypy]`
4. mypy built-in defaults

## See Also

- [mypy Configuration File Documentation](https://mypy.readthedocs.io/en/stable/config_file.html)
- [TOML Specification](https://toml.io/en/)
- Project: [pyproject.toml](../../../pyproject.toml)
