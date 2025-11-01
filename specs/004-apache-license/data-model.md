# Data Model: Apache 2.0 License

**Feature**: 004-apache-license | **Date**: 2025-11-01 | **Phase**: 1 (Design)

## Overview

This feature introduces **static text metadata** only - no runtime data structures or persistent storage. The data model describes the **structure and placement** of license information across the codebase for documentation and compliance purposes.

---

## Entity Definitions

### Entity 1: LICENSE File

**Purpose**: Primary legal document granting Apache 2.0 permissions to users

**Location**: Repository root (`/LICENSE`)

**Attributes**:

| Property | Type | Value | Constraints |
|----------|------|-------|-------------|
| `filename` | String | `LICENSE` | MUST be exact (case-sensitive on Unix) |
| `content` | Text | Apache License 2.0 full text | MUST be unmodified official text |
| `line_count` | Integer | 361 | Exact line count for verification |
| `encoding` | String | UTF-8 | Standard text encoding |
| `copyright_notice` | Text | "Copyright 2025 fotoview contributors" | Prepended before license text |

**Invariants**:
- File MUST be plain text (no PDF, no HTML)
- Content MUST match official Apache 2.0 text from https://www.apache.org/licenses/LICENSE-2.0.txt
- Copyright notice MUST appear at top (before license text proper)
- No modifications to license text allowed (violates Apache 2.0 terms)

**Structure**:
```text
Copyright 2025 fotoview contributors

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
   ...
   [359 lines of license text]
   ...
   END OF TERMS AND CONDITIONS
```

**Testing**:
- Verify file exists: `test -f LICENSE`
- Verify line count: `wc -l LICENSE` == 361
- Verify copyright: `head -1 LICENSE` matches expected
- Verify official text: Compare hash or key phrases

---

### Entity 2: License Header

**Purpose**: File-level license declaration using SPDX short-form

**Location**: Top of source files (Python, JavaScript, CSS)

**Attributes**:

| Property | Type | Value | Constraints |
|----------|------|-------|-------------|
| `copyright_line` | String | "Copyright 2025 fotoview contributors" | Year + holder |
| `spdx_identifier` | String | "SPDX-License-Identifier: Apache-2.0" | Exact SPDX format |
| `comment_syntax` | String | Language-dependent | `#` for Python, `/* */` for JS/CSS |
| `placement` | Integer | Line 1-3 | After shebang/encoding if present |

**Invariants**:
- MUST appear before any code (after shebang/encoding only)
- MUST use exact SPDX identifier "Apache-2.0" (case-sensitive)
- Copyright year MUST match LICENSE file (consistency)
- Comment syntax MUST be valid for file language

**Format by Language**:

**Python** (`.py`):
```python
# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0
```

**JavaScript** (`.js`):
```javascript
/*
 * Copyright 2025 fotoview contributors
 * SPDX-License-Identifier: Apache-2.0
 */
```

**CSS** (`.css`):
```css
/*
 * Copyright 2025 fotoview contributors
 * SPDX-License-Identifier: Apache-2.0
 */
```

**Placement Rules**:
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2025 fotoview contributors  <-- After shebang/encoding
# SPDX-License-Identifier: Apache-2.0

"""Module docstring comes after license header."""

import sys  # Code starts here
```

**Testing**:
- Verify presence: `grep -l "SPDX-License-Identifier: Apache-2.0" src/**/*.py`
- Verify format: Regex pattern match
- Verify placement: Header in first 5 lines (allowing shebang/encoding)

---

### Entity 3: License Metadata (pyproject.toml)

**Purpose**: Machine-readable license declaration for Python packaging

**Location**: `/pyproject.toml` in `[project]` section

**Attributes**:

| Property | Type | Value | Constraints |
|----------|------|-------|-------------|
| `license` | String | "Apache-2.0" | SPDX identifier (PEP 621) |
| `classifiers` | List[String] | `["License :: OSI Approved :: Apache Software License"]` | PyPI classifier (optional) |

**Format**:
```toml
[project]
name = "fotoview"
license = "Apache-2.0"
classifiers = [
    "License :: OSI Approved :: Apache Software License",
]
```

**Invariants**:
- `license` field MUST use SPDX identifier (not free text)
- Classifier is optional but recommended for PyPI compatibility
- Value MUST match LICENSE file content (Apache-2.0)

**Testing**:
- Verify field: `grep 'license = "Apache-2.0"' pyproject.toml`
- Validate TOML syntax: `python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"`

---

### Entity 4: License Documentation (README.md)

**Purpose**: Human-readable license reference for repository visitors

**Location**: `/README.md` in "License" section

**Attributes**:

| Property | Type | Value | Constraints |
|----------|------|-------|-------------|
| `section_heading` | String | "## License" | Markdown H2 heading |
| `description` | Text | "This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details." | Link to LICENSE file |
| `badge` | String (optional) | `[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)` | shields.io badge |

**Format**:
```markdown
## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
```

**Invariants**:
- Section MUST appear in README (placement flexible, typically near end)
- Link to LICENSE file MUST be valid relative path
- Badge is optional enhancement

**Testing**:
- Verify section exists: `grep "## License" README.md`
- Verify link: `grep "\[LICENSE\](LICENSE)" README.md`

---

### Entity 5: File Exclusion Rules

**Purpose**: Define which files do NOT require license headers

**Location**: Implementation decision (documented, not stored)

**Attributes**:

| File Type | Pattern | Exclusion Reason |
|-----------|---------|------------------|
| Configuration | `*.yaml`, `*.toml`, `*.json`, `.gitignore` | Structural data, comments can break parsers |
| Documentation | `*.md`, `docs/**` | Documentation, not source code |
| User Content | `content/**`, `gallery.yaml` | User-owned content, not project code |
| Generated | `output/**`, `dist/**`, `__pycache__/**` | Build artifacts, derived from source |
| Templates | `*.html.tpl` | Consider excluding (edge case) |

**Invariants**:
- Exclusion list MUST be documented in quickstart.md
- All Python/JS/CSS source MUST have headers (no exceptions)
- Test files treated as source (headers required)

---

## Entity Relationships

```
LICENSE File (1)
    ├── Referenced by → README.md (Entity 4)
    ├── Referenced by → pyproject.toml metadata (Entity 3)
    └── Matches → License Headers (Entity 2) [same copyright, same license]

License Header (many)
    ├── Applied to → Source Files (~25 files)
    ├── Format variant → Language-specific comment syntax
    └── Excluded from → File Exclusion Rules (Entity 5)

License Metadata (1)
    └── Declares → Apache-2.0 (references LICENSE file)

License Documentation (1)
    └── Links to → LICENSE file

File Exclusion Rules (1)
    └── Determines → Which files skip License Header
```

---

## Data Flow

```
Phase 1: Create LICENSE File
  1. Download official Apache 2.0 text
  2. Add copyright notice at top
  3. Save as LICENSE in repository root
  4. Verify: line count == 361, contains "Apache License"

Phase 2: Add License Headers
  1. For each source file in src/**/*.py, src/**/*.js, src/**/*.css, tests/**/*.py:
     a. Check if excluded (Entity 5 rules)
     b. Determine comment syntax (Entity 2)
     c. Insert header after shebang/encoding (if present)
     d. Verify placement (first 5 lines)
  2. Total files: ~25

Phase 3: Update Metadata
  1. Edit pyproject.toml:
     Add license = "Apache-2.0" in [project]
  2. Edit README.md:
     Add ## License section
  3. Commit all changes

Phase 4: Verification
  1. GitHub license detection (automatic within 24h)
  2. Manual check: All headers present
  3. Optional: Run licensee/FOSSA scanner
```

---

## Size Impact Analysis

| Entity | File Count | Lines Added | Total Impact |
|--------|-----------|-------------|--------------|
| LICENSE File | 1 new file | 361 lines | 361 lines |
| License Headers (Python) | ~17 files | 2 lines each | ~34 lines |
| License Headers (JS/CSS) | ~8 files | 4 lines each | ~32 lines |
| pyproject.toml | 1 modified | +1 line | 1 line |
| README.md | 1 modified | +3 lines | 3 lines |
| **Total** | **28 files** | **~431 lines** | **431 lines** |

**Repository Impact**:
- Files modified: 28 (1 new, 27 modified)
- Lines added: ~431 (comments, no runtime code)
- Size increase: ~15KB (text files compress well)
- Performance impact: Zero (comments ignored at runtime)

---

## Validation Rules

### LICENSE File Validation
- **Existence Check**: `test -f LICENSE` returns 0
- **Content Check**: Contains "Apache License" and "Version 2.0, January 2004"
- **Copyright Check**: First line matches "Copyright 2025 fotoview contributors"
- **Line Count**: Exactly 361 lines (`wc -l LICENSE`)

### License Header Validation
- **Presence Check**: All source files contain "SPDX-License-Identifier: Apache-2.0"
- **Format Check**: Copyright line precedes SPDX line
- **Placement Check**: Header in first 5 lines (allowing shebang/encoding)
- **Syntax Check**: Comment syntax matches file language

### Metadata Validation
- **pyproject.toml**: Contains `license = "Apache-2.0"`
- **README.md**: Contains "## License" section
- **README.md**: Link to LICENSE file is valid

### Exclusion Validation
- **No headers in**: `config/`, `content/`, `docs/`, `specs/`, `output/`, `__pycache__/`
- **Headers present in**: All `.py`, `.js`, `.css` files in `src/` and `tests/`

---

## Migration Path

**From**: Unlicensed repository (no LICENSE file, no headers)
**To**: Apache 2.0 licensed with full compliance

**Steps**:
1. **Download LICENSE**: `curl https://www.apache.org/licenses/LICENSE-2.0.txt > LICENSE`
2. **Add copyright notice**: Prepend "Copyright 2025 fotoview contributors" to LICENSE
3. **Add headers**: Insert SPDX headers in all source files (see Entity 2 format)
4. **Update metadata**: Edit pyproject.toml and README.md
5. **Commit**: `git add LICENSE src/ tests/ pyproject.toml README.md && git commit -m "Add Apache 2.0 license"`
6. **Push**: Changes pushed to GitHub trigger automatic license detection

**Rollback**: Remove LICENSE file and headers (unlikely needed - licensing is permanent decision)

---

## Testing Contract

### Automated Tests (Optional Enhancement)
```python
def test_license_file_exists():
    assert Path("LICENSE").exists()

def test_license_file_content():
    content = Path("LICENSE").read_text()
    assert "Apache License" in content
    assert "Version 2.0, January 2004" in content
    assert content.startswith("Copyright 2025 fotoview contributors")

def test_source_files_have_headers():
    source_files = [
        *Path("src").rglob("*.py"),
        *Path("src").rglob("*.js"),
        *Path("src").rglob("*.css"),
        *Path("tests").rglob("*.py"),
    ]
    for f in source_files:
        content = f.read_text()
        assert "SPDX-License-Identifier: Apache-2.0" in content

def test_pyproject_toml_license():
    import tomllib
    config = tomllib.load(open("pyproject.toml", "rb"))
    assert config["project"]["license"] == "Apache-2.0"
```

### Manual Tests
1. Visual inspection of LICENSE file
2. Review license headers in sample files (one per language)
3. Check GitHub repository sidebar shows "License: Apache-2.0"
4. Verify README License section is visible

---

## References

- [Apache License 2.0 Full Text](https://www.apache.org/licenses/LICENSE-2.0.txt)
- [SPDX License Identifier Spec](https://spdx.dev/ids/)
- [PEP 621 - Python Project Metadata](https://peps.python.org/pep-0621/)
- [GitHub License Detection](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
