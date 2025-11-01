# Feature Specification: Tool Rename and CLI Simplification

**Feature Branch**: `006-tool-rename-cli`
**Created**: 2025-11-02
**Status**: Draft
**Input**: User description: "The tool needs a better name than fotoview. Ideate a name and rename all relevant places, It should be callable with a simple command from the root of the project. like uv run fotoview (or rather the new name)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Simple Command Invocation (Priority: P1)

A developer has just cloned the gallery generator project and wants to build their image gallery. Instead of having to remember the full Python module path (`python -m src.generator.build_html`), they can simply type a memorable command from the project root and immediately start generating their gallery.

**Why this priority**: This is the primary interaction point for the tool. Making it simple and intuitive reduces friction for new users and improves the developer experience. Every user will use this command repeatedly.

**Independent Test**: Clone the repository, navigate to the root directory, run the simple command, and verify the gallery is generated successfully in the output directory.

**Acceptance Scenarios**:

1. **Given** a developer is in the project root directory, **When** they run `uv run exposure`, **Then** the gallery is built successfully using default settings from `config/settings.yaml`
2. **Given** a developer wants to override configuration, **When** they run `EXPOSURE_LOCALE=de uv run exposure`, **Then** the gallery is built with German locale
3. **Given** a new user reads the README, **When** they follow the quick start instructions, **Then** the command syntax is clear and works immediately without confusion

---

### User Story 2 - Clear Project Identity (Priority: P2)

A developer is searching for static gallery generators or browsing the project repository. They immediately understand what the tool does from its name and branding. The name is memorable and clearly conveys the purpose of creating image galleries.

**Why this priority**: Project discoverability and memorability are crucial for open source adoption. A clear, purpose-driven name helps users remember the tool and recommend it to others.

**Independent Test**: Show the project name and description to someone unfamiliar with it, and verify they can correctly guess its purpose without additional explanation.

**Acceptance Scenarios**:

1. **Given** a user visits the GitHub repository, **When** they see the project name "exposure", **Then** they understand it relates to image galleries or photo collections
2. **Given** a developer is searching for "static gallery generator", **When** search results include the project, **Then** the name and description clearly indicate it's a gallery tool
3. **Given** someone recommends the tool to a colleague, **When** they mention "exposure", **Then** the colleague can easily remember and search for it later

---

### User Story 3 - Consistent Documentation (Priority: P3)

A developer is reading the project documentation, viewing error messages, or browsing source code. All references to the tool use the consistent new name, creating a cohesive and professional impression. There are no confusing references to old names or inconsistent terminology.

**Why this priority**: While important for professionalism, this is less critical than the functional command invocation. However, consistency prevents confusion and maintains project quality.

**Independent Test**: Search all documentation, code, and configuration files for references to the tool name, and verify all use the consistent new name.

**Acceptance Scenarios**:

1. **Given** a developer reads the README, **When** they see command examples, **Then** all use the new command name consistently
2. **Given** a developer encounters an error message, **When** the message is displayed, **Then** it references "exposure" not "fotoview"
3. **Given** a developer examines the `pyproject.toml`, **When** they check the package name, **Then** it reflects the new tool name
4. **Given** a user views the generated HTML gallery, **When** they check the meta generator tag, **Then** it shows the updated name

---

### Edge Cases

- What happens when a user has the old command (`uv run python -m src.generator.build_html`) bookmarked or in scripts? - Python module invocation continues to work as a language feature, but documentation promotes the new command
- What if translations (German locale files) still reference the old name? - All translation strings are updated to reflect the new name
- What happens to existing gallery.yaml files with old metadata references? - YAML file structure remains unchanged; rename only affects tool name, not data format
- How are LICENSE copyright notices handled? - Copyright notice format is preserved, "exposure contributors" replaces "fotoview contributors"

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Tool MUST be invocable via command `uv run exposure` from the project root directory
- **FR-002**: Command MUST build the gallery using settings from `config/settings.yaml` by default
- **FR-003**: Environment variable prefix MUST change from `FOTOVIEW_` to `EXPOSURE_` for all configuration overrides
- **FR-004**: Package name in `pyproject.toml` MUST be updated to "exposure"
- **FR-005**: All user-facing messages (logs, errors, info) MUST reference "Exposure" as the tool name
- **FR-006**: All documentation files (README.md, docs/, specs/) MUST be updated with the new name
- **FR-007**: Translation files (locales/) MUST have updated strings for the new tool name
- **FR-008**: Generated HTML MUST include correct meta generator tag with new name
- **FR-009**: Source code logger names MUST use "exposure" instead of "fotoview"
- **FR-010**: Project configuration (settings.yaml) MUST retain its structure; only comment headers need name updates
- **FR-011**: LICENSE file MUST be updated with new copyright holder name "exposure contributors"
- **FR-012**: SPDX license headers in source files MUST be updated if they reference the project name
- **FR-013**: Test files MUST be updated to reflect new command invocation patterns
- **FR-014**: GitHub repository name remains "fotoview" to preserve git history and links; only the tool/package name changes

### Key Entities

- **CLI Entry Point**: The command interface users invoke to build galleries (changes from module invocation to simple command)
- **Package Name**: The Python package identifier in pyproject.toml (changes from "fotoview" to "exposure")
- **Environment Variables**: Configuration overrides with specific prefix (changes from `FOTOVIEW_*` to `EXPOSURE_*`)
- **Tool Branding**: All user-facing references to the project name in documentation, messages, and output (changes from "Fotoview" to "Exposure")

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developer can build a gallery with a single command (`uv run exposure`) from project root in under 2 seconds
- **SC-002**: All environment variable examples in documentation use the new `EXPOSURE_` prefix
- **SC-003**: Search for "fotoview" in source code (excluding git history and comments about migration) returns zero results in user-facing strings
- **SC-004**: New users can successfully follow README quick start instructions without encountering old tool name
- **SC-005**: Generated gallery HTML includes `<meta name="generator" content="Exposure">` tag
- **SC-006**: All 100% of existing tests pass after rename with no modifications to test logic, only name updates
- **SC-007**: Command reduces typing from 41 characters (`uv run python -m src.generator.build_html`) to 18 characters (`uv run exposure`), a 56% reduction

## Assumptions

- **A-001**: Repository name on GitHub remains "fotoview" to preserve links, issues, and git history
- **A-002**: YAML configuration file format (`gallery.yaml`) structure is unaffected by rename
- **A-003**: Image files in content directory are not affected; only tool invocation changes
- **A-004**: No existing users yet - clean break for environment variables without backward compatibility
- **A-005**: The name "exposure" is chosen as the new tool name (fundamental photography concept, memorable and descriptive)
- **A-006**: Command invocation uses `uv run` as the package manager, consistent with project's existing tooling
- **A-007**: Backward compatibility for old command (`python -m src.generator.build_html`) is not required; clean break is acceptable
- **A-008**: Translation workflow and tools (Babel, gettext) remain unchanged, only translated strings are updated
