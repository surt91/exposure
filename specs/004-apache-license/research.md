# Research: Apache 2.0 License

**Feature**: 004-apache-license | **Date**: 2025-11-01 | **Phase**: 0 (Technology Decisions)

## Research Questions

### RQ-001: Apache 2.0 License Source

**Question**: Where to obtain official Apache License 2.0 text?

**Decision**: Use official Apache Software Foundation source

**Rationale**:
- Apache Software Foundation provides canonical license text at https://www.apache.org/licenses/LICENSE-2.0.txt
- GitHub also recognizes official text from https://choosealicense.com/licenses/apache-2.0/
- Plain text format (361 lines) suitable for direct inclusion in repository

**Alternatives Considered**:
- Copy from another project: Risk of modifications/errors
- Use shortened version: Not legally valid (must use complete text)
- Generate programmatically: Unnecessary complexity for static text

**Implementation**: Download official text and save as `LICENSE` file in repository root

---

### RQ-002: License Header Format

**Question**: What format should license headers use in source files?

**Decision**: SPDX short-form identifier format

**Rationale**:
- SPDX (Software Package Data Exchange) is industry standard for machine-readable license info
- Short-form reduces boilerplate (5 lines vs 50+ lines of full Apache header)
- Recognized by GitHub, GitLab, license scanning tools (licensee, FOSSA, Black Duck)
- Recommended by Apache Software Foundation for Apache 2.0 projects

**Format**:
```python
# Copyright 2025 fotoview contributors
# SPDX-License-Identifier: Apache-2.0
```

```css
/*
 * Copyright 2025 fotoview contributors
 * SPDX-License-Identifier: Apache-2.0
 */
```

**Alternatives Considered**:
- Full Apache header boilerplate: Too verbose (adds 50+ lines per file)
- No headers: Legal but reduces clarity when files shared individually
- Custom format: Not machine-readable by standard tools

**Reference**: https://spdx.dev/ids/

---

### RQ-003: Copyright Holder Name

**Question**: Who should be listed as copyright holder?

**Decision**: "fotoview contributors"

**Rationale**:
- Collective authorship model common for open source projects
- Avoids need to track individual contributors in every file
- Consistent with projects like Linux kernel, Git, many Apache projects
- Simplified for projects without formal legal entity (foundation, company)

**Alternatives Considered**:
- Individual author names: Requires maintaining per-file attribution
- Organization name: No formal organization exists for fotoview
- "The fotoview authors": Synonymous with "contributors", less common

**Note**: Contributors retain their own copyright; this is aggregating attribution

---

### RQ-004: Which Files Need License Headers?

**Question**: Should all files in repository have license headers?

**Decision**: Only source code files (Python, JavaScript, CSS)

**Rationale**:
- LICENSE file covers entire repository legally
- Headers provide convenience for files shared outside repository context
- Some file types shouldn't have headers:
  - JSON/YAML: Structural data, comments can break parsers
  - Images: Binary files, metadata is complex
  - Markdown: Documentation, not "source code"
  - Generated files: Output artifacts, already covered by source

**Included**:
- Python files (`.py`): All files in `src/` and `tests/`
- JavaScript files (`.js`): All files in `src/static/js/`
- CSS files (`.css`): All files in `src/static/css/`

**Excluded**:
- Configuration: `config/*.yaml`, `pyproject.toml` (except metadata field), `.github/*.yml`
- Documentation: `docs/*.md`, `README.md` (except License section), `specs/**`
- User content: `content/` directory, `gallery.yaml` files
- Generated: `output/`, `dist/`, `__pycache__/`, `.pytest_cache/`
- Git files: `.gitignore`, `.gitattributes`

**Total**: Approximately 25 source files need headers

---

### RQ-005: License Header Automation

**Question**: Should we use automated tools to add license headers?

**Decision**: Manual addition for initial license (no automation tool)

**Rationale**:
- One-time operation (adding license to existing project)
- Only ~25 files to modify
- Manual approach ensures correct placement (after shebang, encoding declarations)
- Automated tools add complexity without significant benefit for one-time use

**For Future**:
- Pre-commit hook to verify headers exist (optional enhancement)
- CI check with tools like `addlicense` or `licensecheck` (optional)
- For now, manual verification during code review is sufficient

**Alternatives Considered**:
- `addlicense` tool (Google): Adds headers automatically but requires Go installation
- `licenseheaders` (Python): Good for ongoing maintenance, overkill for one-time
- pre-commit hook: Useful for enforcement, not needed for initial addition

---

### RQ-006: pyproject.toml License Field

**Question**: How to declare license in pyproject.toml metadata?

**Decision**: Use `license = "Apache-2.0"` field with SPDX identifier

**Rationale**:
- PEP 621 standard for Python project metadata
- `license` field accepts SPDX identifier string
- Recognized by PyPI, pip, packaging tools
- Matches LICENSE file content

**Format**:
```toml
[project]
license = "Apache-2.0"
```

**Alternatives Considered**:
- Old format: `license = {text = "Apache-2.0"}` (deprecated in PEP 621)
- License file reference: `license = {file = "LICENSE"}` (redundant)
- Classifier only: `"License :: OSI Approved :: Apache Software License"` (insufficient alone)

**Note**: Should also add classifier for maximum compatibility:
```toml
classifiers = [
    "License :: OSI Approved :: Apache Software License",
]
```

---

### RQ-007: README.md License Section

**Question**: How should license be documented in README?

**Decision**: Add "License" section with link to LICENSE file

**Format**:
```markdown
## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
```

**Rationale**:
- Standard practice for open source projects
- Provides human-readable summary
- Links to full license text for details
- Concise (2 lines)

**Alternatives Considered**:
- Full license text in README: Too verbose
- Badge only: Less clear than text explanation
- No README mention: Reduces discoverability

**Optional Enhancement**: Add license badge from shields.io:
```markdown
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
```

---

### RQ-008: Dependency License Compatibility

**Question**: Are existing dependencies compatible with Apache 2.0?

**Decision**: All dependencies are compatible

**Verification**:
- PyYAML: MIT License ✓ (permissive, compatible)
- Pillow: HPND License (Historical Permission Notice and Disclaimer) ✓ (permissive, compatible)
- pytest: MIT License ✓
- playwright: Apache 2.0 ✓ (same license)
- ruff: MIT License ✓
- pre-commit: MIT License ✓

**Incompatible Licenses** (none present):
- GPL (copyleft - requires derivative works to be GPL)
- AGPL (strong copyleft)

**Rationale**: MIT and HPND are permissive licenses compatible with Apache 2.0. No license conflicts exist.

**Reference**: https://www.apache.org/legal/resolved.html#category-a

---

### RQ-009: NOTICE File Requirement

**Question**: Does Apache 2.0 require a NOTICE file?

**Decision**: No NOTICE file needed for fotoview

**Rationale**:
- NOTICE file is required only if:
  - Distributing modified third-party code with its own NOTICE
  - Project includes substantial attributions beyond copyright
- Fotoview has:
  - No modified third-party source code
  - No bundled third-party components with NOTICE requirements
  - Simple copyright attribution (covered by license headers)

**When NOTICE Would Be Needed**:
- If we bundle modified Apache-licensed library (copy code into our repo)
- If dependency explicitly requires attribution beyond license

**Alternatives Considered**:
- Create empty NOTICE: Confusing and unnecessary
- Add NOTICE with contributor list: Not required, handled by git history

**Reference**: Apache License 2.0 Section 4(d) - NOTICE file requirements

---

### RQ-010: Copyright Year Strategy

**Question**: Should copyright year be updated annually?

**Decision**: Use "2025" (current year) initially, update on modification

**Rationale**:
- Initial copyright year is when project first publicly released with license
- Standard practice: Update year when file is significantly modified
- Alternatives:
  - Year range "2025-YYYY": Update when modified
  - Single year "2025": Simplest, least maintenance
  - No year: Not recommended for copyright notices

**Recommendation**: Use "2025" for initial license addition. In future:
- Update to "2025-2026" if file modified in 2026
- Or keep "2025" and rely on git history for modification dates
- No need for automated year updating (creates noise)

**Common Practice**: Many projects keep original year and don't update unless major rewrite

---

## Summary of Decisions

| ID | Question | Decision | Impact |
|----|----------|----------|--------|
| RQ-001 | License source | Apache Software Foundation official text | 361-line LICENSE file |
| RQ-002 | Header format | SPDX short-form | 2-5 line headers per file |
| RQ-003 | Copyright holder | "fotoview contributors" | Collective authorship |
| RQ-004 | Files needing headers | ~25 Python/JS/CSS files | Exclude config, docs, generated |
| RQ-005 | Automation | Manual addition (one-time) | No tooling dependencies |
| RQ-006 | pyproject.toml | `license = "Apache-2.0"` | SPDX identifier field |
| RQ-007 | README section | 2-line License section with link | Standard practice |
| RQ-008 | Dependency compatibility | All compatible (MIT, HPND) | No conflicts |
| RQ-009 | NOTICE file | Not required | No third-party attributions |
| RQ-010 | Copyright year | "2025" | Update on modification |

**Total Estimated Changes**:
- 1 new file (LICENSE: 361 lines)
- ~25 files with added headers (2-5 lines each: ~75 lines total)
- 1 file modified (pyproject.toml: +1 line for license field)
- 1 file modified (README.md: +3 lines for License section)

**Total Addition**: ~440 lines across 28 files

---

## Next Steps (Phase 1)

1. Create `data-model.md`: Define License Header entity structure
2. Create `contracts/license-header-format.md`: Document header formats per language
3. Create `contracts/spdx-identifiers.md`: Document SPDX compliance
4. Create `quickstart.md`: Guide for adding license headers, verifying compliance
5. Update agent context: Run `update-agent-context.sh`

---

## References

- [Apache License 2.0 Official Text](https://www.apache.org/licenses/LICENSE-2.0.txt)
- [SPDX License List](https://spdx.org/licenses/)
- [SPDX Usage Guide](https://spdx.dev/ids/)
- [Apache Foundation License FAQ](https://www.apache.org/foundation/license-faq.html)
- [Apache Compatible Licenses](https://www.apache.org/legal/resolved.html)
- [PEP 621 - Project Metadata](https://peps.python.org/pep-0621/)
- [GitHub License Detection](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
