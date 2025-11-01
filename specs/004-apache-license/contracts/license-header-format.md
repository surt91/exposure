# License Header Format Contract

**Feature**: 004-apache-license | **Date**: 2025-11-01 | **Type**: Format Specification

## Overview

This contract defines the exact format and placement of SPDX license headers in source files. All source files (Python, JavaScript, CSS) MUST include these headers for legal clarity and machine-readable license detection.

---

## Header Components

### Required Elements

1. **Copyright Line**: `Copyright {YEAR} {HOLDER}`
   - YEAR: 4-digit year (2025 for initial addition)
   - HOLDER: "fotoview contributors" (collective authorship)

2. **SPDX Identifier Line**: `SPDX-License-Identifier: Apache-2.0`
   - Exact format (case-sensitive)
   - Official SPDX short identifier for Apache License 2.0

### Optional Elements

- Blank line after header (for readability, not required)
- Additional attribution (rare, avoid unless necessary)

---

## Format by Language

### Python Files (`.py`)

**Standard Format**:
```python
# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0
```

**With Shebang**:
```python
#!/usr/bin/env python3
# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0
```

**With Encoding Declaration**:
```python
# -*- coding: utf-8 -*-
# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0
```

**With Both Shebang and Encoding**:
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0
```

**Placement Rules**:
- Line 1: Shebang (if present)
- Line 2: Encoding (if present)
- Next 2 lines: License header
- Then: Blank line, module docstring, imports, code

**Example Complete File**:
```python
#!/usr/bin/env python3
# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0

"""Module for building HTML from gallery data."""

import sys
from pathlib import Path

def build_gallery():
    pass
```

---

### JavaScript Files (`.js`)

**Standard Format**:
```javascript
/*
 * Copyright 2025 fotoview contributors
 * SPDX-License-Identifier: Apache-2.0
 */
```

**Placement Rules**:
- Lines 1-4: License header (block comment)
- Line 5: Blank line (optional)
- Line 6+: Code starts

**Example Complete File**:
```javascript
/*
 * Copyright 2025 fotoview contributors
 * SPDX-License-Identifier: Apache-2.0
 */

'use strict';

/**
 * Gallery initialization
 */
function initGallery() {
    // Implementation
}
```

**Alternative Single-Line Format** (discouraged but valid):
```javascript
// Copyright 2025 fotoview contributors
// SPDX-License-Identifier: Apache-2.0
```

**Rationale for Block Comment**:
- More visually distinct
- Consistent with CSS format
- Common practice for JS license headers

---

### CSS Files (`.css`)

**Standard Format**:
```css
/*
 * Copyright 2025 fotoview contributors
 * SPDX-License-Identifier: Apache-2.0
 */
```

**Placement Rules**:
- Lines 1-4: License header (block comment)
- Line 5: Blank line (optional)
- Line 6+: CSS rules start

**Example Complete File**:
```css
/*
 * Copyright 2025 fotoview contributors
 * SPDX-License-Identifier: Apache-2.0
 */

/* Gallery Styles */
:root {
    --color-primary: #333;
}

body {
    font-family: sans-serif;
}
```

---

## Validation Rules

### Format Validation

**Copyright Line**:
- MUST start with comment character(s) appropriate to language
- MUST contain "Copyright"
- MUST contain 4-digit year (2025)
- MUST contain "fotoview contributors"

**SPDX Line**:
- MUST start with comment character(s)
- MUST contain exact string "SPDX-License-Identifier: Apache-2.0"
- Case-sensitive (Apache-2.0, not apache-2.0 or APACHE-2.0)
- No extra whitespace around identifier

### Placement Validation

**Python**:
- Header MUST be in first 5 lines (allowing shebang/encoding)
- MUST come before any imports or code
- MUST come before module docstring

**JavaScript/CSS**:
- Header MUST be in first 5 lines
- MUST come before any code/rules
- MUST use block comment (`/* */`)

### Common Errors to Avoid

❌ **Wrong identifier**:
```python
# SPDX-License-Identifier: Apache 2.0  # Missing hyphen
# SPDX-License-Identifier: apache-2.0  # Wrong case
# SPDX-License-Identifier: Apache License 2.0  # Not SPDX format
```

✅ **Correct**:
```python
# SPDX-License-Identifier: Apache-2.0
```

❌ **Missing copyright**:
```python
# SPDX-License-Identifier: Apache-2.0  # Missing copyright line
```

✅ **Correct**:
```python
# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0
```

❌ **Wrong comment syntax**:
```css
// Copyright 2025 fotoview contributors  /* Wrong: single-line comment in CSS */
// SPDX-License-Identifier: Apache-2.0
```

✅ **Correct**:
```css
/*
 * Copyright 2025 fotoview contributors
 * SPDX-License-Identifier: Apache-2.0
 */
```

---

## Regex Patterns for Validation

### Python Header Detection
```regex
^(#!.*\n)?(# -\*- coding:.*\n)?# Copyright \d{4} fotoview contributors\n# SPDX-License-Identifier: Apache-2\.0
```

### JavaScript/CSS Header Detection
```regex
^\/\*\n \* Copyright \d{4} fotoview contributors\n \* SPDX-License-Identifier: Apache-2\.0\n \*\/
```

### General SPDX Detection (any file)
```regex
SPDX-License-Identifier:\s*Apache-2\.0
```

---

## File Exclusions

**Files that MUST NOT have headers**:

| File Type | Pattern | Reason |
|-----------|---------|--------|
| Configuration | `*.yaml`, `*.yml`, `*.json`, `*.toml` | Structural data, comments break parsers |
| Markdown | `*.md` | Documentation, not source code |
| Images | `*.png`, `*.jpg`, `*.svg` | Binary/XML, not source code |
| Templates | `*.html.tpl` (optional) | May be excluded if minimal logic |
| Generated | `output/**`, `dist/**` | Build artifacts |
| Git files | `.gitignore`, `.gitattributes` | Configuration |
| Python cache | `__pycache__/**`, `*.pyc` | Generated bytecode |

**Files that MUST have headers**:

| File Type | Pattern | Example |
|-----------|---------|---------|
| Python source | `src/**/*.py`, `tests/**/*.py` | `src/generator/build_html.py` |
| JavaScript | `src/static/js/**/*.js` | `src/static/js/gallery.js` |
| CSS | `src/static/css/**/*.css` | `src/static/css/gallery.css` |
| Python init | `**/__init__.py` | `src/__init__.py` |

---

## Automated Verification

### Bash Script Example

```bash
#!/bin/bash
# Check all source files have Apache 2.0 headers

MISSING=0

# Check Python files
for f in $(find src tests -name "*.py"); do
    if ! grep -q "SPDX-License-Identifier: Apache-2.0" "$f"; then
        echo "Missing header: $f"
        MISSING=$((MISSING + 1))
    fi
done

# Check JavaScript files
for f in $(find src/static/js -name "*.js"); do
    if ! grep -q "SPDX-License-Identifier: Apache-2.0" "$f"; then
        echo "Missing header: $f"
        MISSING=$((MISSING + 1))
    fi
done

# Check CSS files
for f in $(find src/static/css -name "*.css"); do
    if ! grep -q "SPDX-License-Identifier: Apache-2.0" "$f"; then
        echo "Missing header: $f"
        MISSING=$((MISSING + 1))
    fi
done

if [ $MISSING -eq 0 ]; then
    echo "✓ All source files have license headers"
    exit 0
else
    echo "✗ $MISSING files missing license headers"
    exit 1
fi
```

### Python Test Example

```python
from pathlib import Path

def test_license_headers():
    """Verify all source files have Apache 2.0 license headers."""
    source_patterns = ["src/**/*.py", "tests/**/*.py", "src/**/*.js", "src/**/*.css"]

    missing = []
    for pattern in source_patterns:
        for file in Path(".").glob(pattern):
            content = file.read_text()
            if "SPDX-License-Identifier: Apache-2.0" not in content:
                missing.append(str(file))

    assert not missing, f"Files missing license headers: {missing}"
```

---

## FAQ

### Q: Can I use a different copyright holder?
**A**: No. For fotoview, use "fotoview contributors" for consistency. Individual contributors retain their own copyright through git history.

### Q: Should I update the year annually?
**A**: Only when significantly modifying a file. Initial files use "2025". If modified in 2026, update to "2025-2026" or leave as "2025" (both acceptable).

### Q: What about files with existing headers?
**A**: fotoview is adding license for first time. No existing headers to conflict with.

### Q: Can I use full Apache license text instead of SPDX?
**A**: No. Full text is 50+ lines and not necessary. SPDX short-form is Apache Software Foundation's recommended approach.

### Q: Do test files need headers?
**A**: Yes. Test files are source code and follow same licensing as main code.

### Q: What about HTML templates?
**A**: Decision: Skip headers in `.html.tpl` files (minimal logic, primarily structure). If templates become complex, add headers.

---

## Change History

- **Version 1.0.0** (2025-11-01): Initial license header format specification

---

## References

- [SPDX License Identifier Spec](https://spdx.dev/ids/)
- [SPDX License List](https://spdx.org/licenses/Apache-2.0.html)
- [Apache Foundation - Applying License](https://www.apache.org/legal/apply-license.html)
- [GitHub - Licensing a Repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
