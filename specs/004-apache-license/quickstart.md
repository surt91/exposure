# Quickstart: Apache 2.0 License

**Feature**: 004-apache-license | **Date**: 2025-11-01 | **Phase**: 1 (Design)

## Overview

This guide explains how to add Apache 2.0 license to the fotoview project, including creating the LICENSE file, adding SPDX headers to source files, and updating project metadata.

---

## For Contributors

### Understanding the License

**What is Apache 2.0?**
- Permissive open source license
- Allows anyone to use, modify, and distribute the code
- Requires preservation of copyright and license notices
- Provides explicit patent grant
- Compatible with most other licenses (MIT, BSD, etc.)

**What it means for you:**
- You can use fotoview in commercial or personal projects
- You can modify the code
- You must include the LICENSE file when distributing
- You grant others the same rights when contributing

**Official Text**: https://www.apache.org/licenses/LICENSE-2.0

---

## For Maintainers

### Initial License Addition (One-Time Setup)

#### Step 1: Create LICENSE File

```bash
# Download official Apache 2.0 license text
curl https://www.apache.org/licenses/LICENSE-2.0.txt > LICENSE

# Add copyright notice at the beginning
echo -e "Copyright 2025 fotoview contributors\n\n$(cat LICENSE)" > LICENSE

# Verify file created correctly
wc -l LICENSE  # Should be 361 lines
head -3 LICENSE  # Should show copyright notice
```

Expected output:
```
Copyright 2025 fotoview contributors

                                 Apache License
```

#### Step 2: Add License Headers to Source Files

**Python Files** (~17 files):

```bash
# For files WITHOUT shebang/encoding
for file in src/**/*.py tests/**/*.py; do
    echo "# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0

$(cat $file)" > $file
done
```

**For files WITH shebang/encoding, manually edit** to place header after these lines.

Example edit for `src/generator/build_html.py`:
```python
# Before:
#!/usr/bin/env python3
import sys

# After:
#!/usr/bin/env python3
# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0

import sys
```

**JavaScript Files** (~3 files in `src/static/js/`):

```bash
for file in src/static/js/*.js; do
    echo "/*
 * Copyright 2025 fotoview contributors
 * SPDX-License-Identifier: Apache-2.0
 */

$(cat $file)" > $file
done
```

**CSS Files** (~2 files in `src/static/css/`):

```bash
for file in src/static/css/*.css; do
    echo "/*
 * Copyright 2025 fotoview contributors
 * SPDX-License-Identifier: Apache-2.0
 */

$(cat $file)" > $file
done
```

⚠️ **WARNING**: Above commands overwrite files. Backup first or use git to revert if needed.

**Safer Manual Approach**:
1. Open each file in editor
2. Copy appropriate header from `contracts/license-header-format.md`
3. Paste at top (after shebang/encoding if present)
4. Save file

#### Step 3: Update pyproject.toml

Add license field to `[project]` section:

```toml
[project]
name = "fotoview"
version = "0.1.0"
description = "Static image gallery generator"
license = "Apache-2.0"  # <-- ADD THIS LINE
```

Optional: Add classifier for PyPI:
```toml
classifiers = [
    "License :: OSI Approved :: Apache Software License",
]
```

#### Step 4: Update README.md

Add License section (typically near end, before any acknowledgments):

```markdown
## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
```

Optional: Add badge at top:
```markdown
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
```

#### Step 5: Commit Changes

```bash
# Stage all changes
git add LICENSE src/ tests/ pyproject.toml README.md

# Commit with descriptive message
git commit -m "feat: add Apache 2.0 license

- Add LICENSE file with Apache 2.0 text
- Add SPDX headers to all source files (Python, JS, CSS)
- Update pyproject.toml with license metadata
- Add License section to README.md"

# Push to GitHub
git push origin main
```

#### Step 6: Verify GitHub Detection

After pushing, GitHub will automatically detect the license within ~24 hours:
1. Visit repository on GitHub
2. Check sidebar shows "License: Apache-2.0"
3. Click license badge to view LICENSE file

---

## Verification Checklist

### Manual Verification

- [ ] LICENSE file exists in repository root
- [ ] LICENSE file is 361 lines
- [ ] LICENSE file starts with "Copyright 2025 fotoview contributors"
- [ ] All Python files in `src/` have license header
- [ ] All Python files in `tests/` have license header
- [ ] All JavaScript files in `src/static/js/` have license header
- [ ] All CSS files in `src/static/css/` have license header
- [ ] pyproject.toml contains `license = "Apache-2.0"`
- [ ] README.md contains License section
- [ ] No headers in config/, docs/, or generated files

### Automated Verification

**Check all headers present**:
```bash
# Count files that should have headers
EXPECTED=$(find src tests -name "*.py" -o -name "*.js" -o -name "*.css" | wc -l)

# Count files with SPDX headers
ACTUAL=$(find src tests -name "*.py" -o -name "*.js" -o -name "*.css" | xargs grep -l "SPDX-License-Identifier: Apache-2.0" | wc -l)

echo "Expected: $EXPECTED"
echo "Actual: $ACTUAL"

if [ $EXPECTED -eq $ACTUAL ]; then
    echo "✓ All files have license headers"
else
    echo "✗ Missing headers in some files"
fi
```

**Find files missing headers**:
```bash
# Python files missing headers
find src tests -name "*.py" | while read f; do
    grep -q "SPDX-License-Identifier: Apache-2.0" "$f" || echo "Missing: $f"
done

# JS files missing headers
find src/static/js -name "*.js" | while read f; do
    grep -q "SPDX-License-Identifier: Apache-2.0" "$f" || echo "Missing: $f"
done

# CSS files missing headers
find src/static/css -name "*.css" | while read f; do
    grep -q "SPDX-License-Identifier: Apache-2.0" "$f" || echo "Missing: $f"
done
```

### Optional: License Scanning Tools

**licensee** (Ruby gem):
```bash
gem install licensee
licensee detect .
# Should output: "Apache-2.0"
```

**FOSSA CLI** (requires account):
```bash
fossa analyze
fossa test
```

---

## File-Specific Examples

### Python File with Shebang

**File**: `src/generator/build_html.py`

```python
#!/usr/bin/env python3
# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0

"""Build static HTML gallery from YAML configuration."""

import sys
from pathlib import Path

def build_gallery(config_path):
    pass
```

### Python `__init__.py`

**File**: `src/__init__.py`

```python
# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0

"""fotoview static gallery generator."""

__version__ = "0.1.0"
```

### JavaScript File

**File**: `src/static/js/gallery.js`

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
    const images = document.querySelectorAll('.image-item');
    // Implementation...
}
```

### CSS File

**File**: `src/static/css/gallery.css`

```css
/*
 * Copyright 2025 fotoview contributors
 * SPDX-License-Identifier: Apache-2.0
 */

/* Modern Image Gallery Styles */
:root {
    --color-bg: #ffffff;
    --color-text: #1a1a1a;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
```

---

## Troubleshooting

### Problem: GitHub not detecting license

**Solution**:
1. Verify LICENSE file is in repository root (not subfolder)
2. Check LICENSE file is plain text (not PDF, not inside ZIP)
3. Wait 24 hours for GitHub's detection to run
4. Verify file is named `LICENSE` exactly (not `LICENSE.txt` or `license`)

### Problem: License header breaks Python script

**Cause**: Header placed before shebang

**Solution**:
```python
# Wrong:
# Copyright 2025 fotoview contributors
#!/usr/bin/env python3

# Correct:
#!/usr/bin/env python3
# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0
```

### Problem: Bulk header addition script fails

**Cause**: Shell expansion issues or file paths with spaces

**Solution**: Use manual approach or Python script:
```python
from pathlib import Path

header_py = """# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0

"""

header_js_css = """/*
 * Copyright 2025 fotoview contributors
 * SPDX-License-Identifier: Apache-2.0
 */

"""

for file in Path("src").rglob("*.py"):
    content = file.read_text()
    if "SPDX-License-Identifier" not in content:
        file.write_text(header_py + content)

for file in Path("src").rglob("*.js"):
    content = file.read_text()
    if "SPDX-License-Identifier" not in content:
        file.write_text(header_js_css + content)
```

### Problem: pyproject.toml syntax error

**Cause**: Wrong format for license field

**Solution**:
```toml
# Wrong:
license = { text = "Apache-2.0" }  # Old format

# Correct:
license = "Apache-2.0"  # PEP 621 format
```

---

## Maintenance

### When to Update Copyright Year

**Option 1: Update on modification**
- When significantly editing a file in 2026, change "2025" to "2025-2026"
- Advantage: Accurate modification tracking
- Disadvantage: Creates noise in git history

**Option 2: Keep original year**
- Leave all headers as "2025" (initial license year)
- Rely on git history for modification dates
- Advantage: Cleaner git history
- Disadvantage: Less explicit about changes

**Recommendation**: Option 2 (keep original year, use git history)

### Adding Headers to New Files

When creating new source files:

1. **Use IDE template** (if available)
2. **Copy from existing file** of same language
3. **Remember**: Header goes before any code (after shebang/encoding only)

Example for new Python file:
```python
# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0

"""New module description."""

# Your code here
```

### CI Enforcement (Optional Enhancement)

Add to `.github/workflows/ci.yml`:

```yaml
- name: Check License Headers
  run: |
    MISSING=0
    for f in $(find src tests -name "*.py" -o -name "*.js" -o -name "*.css"); do
        if ! grep -q "SPDX-License-Identifier: Apache-2.0" "$f"; then
            echo "Missing header: $f"
            MISSING=$((MISSING + 1))
        fi
    done
    if [ $MISSING -gt 0 ]; then
        echo "::error::$MISSING files missing license headers"
        exit 1
    fi
```

---

## FAQ

### Q: Why Apache 2.0?
**A**: Permissive, patent-grant included, widely adopted, compatible with most licenses.

### Q: Can I use fotoview in commercial projects?
**A**: Yes! Apache 2.0 allows commercial use.

### Q: Do I need to include LICENSE when using fotoview?
**A**: Yes, if you distribute fotoview or modified versions. Not required for internal use.

### Q: What about user-provided content (images, YAML)?
**A**: User content retains user's copyright. fotoview license applies to the software only.

### Q: Can I change the license later?
**A**: Changing license requires agreement from all contributors (complicated). Choose carefully.

### Q: What about third-party dependencies?
**A**: PyYAML (MIT) and Pillow (HPND) are compatible with Apache 2.0. No conflicts.

---

## Resources

- [Apache License 2.0 Full Text](https://www.apache.org/licenses/LICENSE-2.0)
- [SPDX License List](https://spdx.org/licenses/)
- [Apache Foundation - License FAQ](https://www.apache.org/foundation/license-faq.html)
- [Choose a License Guide](https://choosealicense.com/licenses/apache-2.0/)
- [GitHub Licensing Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- [PEP 621 - Python Project Metadata](https://peps.python.org/pep-0621/)

---

## Next Steps

After adding license:

1. **Phase 2**: Run `/speckit.tasks` to generate detailed implementation tasks
2. **Implementation**: Follow tasks.md to apply license systematically
3. **Testing**: Run verification checklist
4. **Deployment**: Commit and push changes
5. **Verification**: Confirm GitHub license detection

For implementation tasks, see `specs/004-apache-license/tasks.md` (created in Phase 2).
