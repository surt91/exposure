# Feature Specification: Apache 2.0 License

**Feature Branch**: `004-apache-license`
**Created**: 2025-11-01
**Status**: Draft
**Input**: User description: "add apache 2.0 license"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Legal Clarity for Users and Contributors (Priority: P1)

A potential user or contributor visits the repository to understand the terms under which they can use, modify, or contribute to the fotoview project. They find a clear Apache 2.0 license that grants them broad permissions with minimal restrictions, giving them confidence to adopt or contribute to the project.

**Why this priority**: This is the fundamental requirement - without a license file, the project's legal status is unclear. This is the minimum viable deliverable that provides immediate value.

**Independent Test**: Can be fully tested by checking that a LICENSE file exists in the repository root with complete Apache 2.0 license text, and that users can read and understand their rights.

**Acceptance Scenarios**:

1. **Given** a user visits the repository root, **When** they look for licensing information, **Then** they find a LICENSE file with Apache 2.0 license text
2. **Given** a developer wants to use fotoview in their project, **When** they read the LICENSE file, **Then** they understand they can use, modify, and distribute the software under Apache 2.0 terms
3. **Given** a potential contributor reviews the project, **When** they check the license, **Then** they know their contributions will be under Apache 2.0 terms

---

### User Story 2 - GitHub License Badge and Recognition (Priority: P2)

A visitor views the repository on GitHub and immediately sees the Apache 2.0 license badge displayed prominently, with GitHub's license detection correctly identifying the project as Apache 2.0 licensed. This provides instant visual confirmation of the licensing terms.

**Why this priority**: This is a nice-to-have enhancement that improves discoverability and trust, but is not required for legal validity. GitHub automatically detects licenses from properly formatted LICENSE files, making this largely automatic.

**Independent Test**: Can be tested by viewing the repository on GitHub and confirming that the license badge appears in the repository sidebar and that GitHub's license detection shows "Apache-2.0".

**Acceptance Scenarios**:

1. **Given** a user views the repository on GitHub, **When** they look at the repository sidebar, **Then** they see "License: Apache-2.0" with a badge
2. **Given** a user searches GitHub for Apache 2.0 licensed projects, **When** the search runs, **Then** fotoview appears in the results
3. **Given** a user clicks the license badge, **When** the page loads, **Then** they see the full LICENSE file content

---

### Edge Cases

- What happens when files are generated dynamically (build outputs) - should they have license headers?
- How does the license apply to user-provided content (gallery images and YAML files)?
- What happens to existing third-party dependencies with different licenses (PyYAML, Pillow)?
- How should license headers be formatted in non-Python files (CSS, JavaScript, HTML)?
- What happens when files are too small to reasonably include a full header (single-line config files)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Repository root MUST contain a LICENSE file with complete Apache License 2.0 text
- **FR-002**: LICENSE file MUST include copyright notice with year 2025 and copyright holder "fotoview contributors"
- **FR-003**: README.md MUST include a "License" section referencing Apache 2.0
- **FR-004**: pyproject.toml MUST declare license as "Apache-2.0" in project metadata
- **FR-005**: User content (gallery.yaml, images) MUST be explicitly excluded from Apache 2.0 scope (separate copyright)
- **FR-006**: NOTICE file MUST be created if project includes modified third-party code (currently not applicable)

### Key Entities

- **LICENSE File**: Primary license document containing full Apache License 2.0 text with copyright notice
- **Copyright Notice**: Statement identifying copyright year (2025) and holder (fotoview contributors)
- **License Metadata**: Machine-readable license declaration in pyproject.toml and README.md

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: LICENSE file exists in repository root with exact Apache License 2.0 text (361 lines)
- **SC-002**: GitHub license detection correctly identifies repository as "Apache-2.0"
- **SC-003**: pyproject.toml metadata includes `license = "Apache-2.0"` field
- **SC-004**: README.md contains License section with link to LICENSE file
- **SC-005**: Automated license scanning tools (licensee, FOSSA) correctly identify repository as Apache 2.0
- **SC-006**: No license conflicts exist between project license and dependency licenses
- **SC-007**: Copyright year matches current year (2025) in LICENSE file

## Assumptions

- **A-001**: Project uses standard Apache License 2.0 version 2.0 (January 2004) without modifications
- **A-002**: Copyright holder is "fotoview contributors" (collective authorship model, typical for open source)
- **A-003**: All existing code was created by project contributors and has no third-party copyright conflicts
- **A-004**: Generated files (HTML output, Python bytecode) are covered by LICENSE file
- **A-005**: Test files follow same licensing as source files (included in Apache 2.0 scope)
- **A-006**: Source files do not require individual license headers - LICENSE file at repository root is sufficient
- **A-007**: User-provided content (gallery images, gallery.yaml) retains user's copyright (not project copyright)
- **A-008**: Dependencies (PyYAML, Pillow) have Apache 2.0-compatible licenses (verified: MIT, HPND)
- **A-009**: No NOTICE file required unless project includes substantial third-party modifications (not applicable)
- **A-010**: LICENSE file in repository root legally covers all source files without needing individual headers

## Constraints

- **C-001**: MUST use unmodified Apache License 2.0 text (no custom variations)
- **C-002**: MUST include copyright year and holder in LICENSE file
- **C-004**: MUST comply with SPDX specification for license identifiers
- **C-005**: MUST NOT claim copyright over user-provided content (images, gallery configurations)
- **C-006**: License choice MUST be compatible with all existing dependencies

## Dependencies

- **D-001**: GitHub's license detection feature for automatic badge display
- **D-002**: SPDX license identifier standard for machine-readable metadata in pyproject.toml
- **D-003**: Apache Software Foundation for official Apache 2.0 license text
- **D-004**: Existing dependency licenses must be Apache 2.0-compatible (PyYAML: MIT ✓, Pillow: HPND ✓)
