# ADR 0005: Library Modernization and Internationalization

**Status**: Accepted
**Date**: 2025-11-01
**Deciders**: Development Team
**Feature**: 005-library-refactor-i18n

## Context

The fotoview static gallery generator was initially built with Python dataclasses, string concatenation for HTML generation, and print() statements for console output. As the project matures, we need to modernize the codebase to improve maintainability, type safety, and support internationalization.

### Current Issues

1. **Data Validation**: Dataclasses provide no automatic validation, leading to manual validation code scattered throughout the codebase
2. **HTML Generation**: String concatenation mixes presentation logic with business logic, making templates hard to maintain
3. **Logging**: print() statements cannot be configured, disabled, or redirected, making debugging difficult
4. **Internationalization**: No mechanism to support multiple languages for UI strings

## Decision

We will modernize the codebase by adopting three industry-standard Python libraries:

### 1. Pydantic v2 for Data Models

**Decision**: Replace all dataclasses with Pydantic BaseModel

**Rationale**:
- Automatic validation with clear error messages
- Built-in serialization for YAML round-tripping
- Better IDE support and type checking
- Field validators for complex constraints
- Backward compatible with existing YAML structure

**Alternative Considered**: Keep dataclasses + manual validation
- **Rejected**: More boilerplate, no automatic validation, harder to maintain

### 2. Jinja2 for HTML Templating

**Decision**: Replace string concatenation with Jinja2 templates

**Rationale**:
- Industry-standard Python templating (used by Flask, Django, Ansible)
- Separates presentation from logic
- Template inheritance reduces duplication
- Auto-escaping prevents XSS vulnerabilities
- Fast and mature (stable API since 2008)

**Alternative Considered**: Keep string formatting
- **Rejected**: Hard to maintain, no auto-escaping, logic mixed with presentation

### 3. Babel for Internationalization

**Decision**: Use Babel with gettext (.po/.mo files) for i18n

**Rationale**:
- Native Jinja2 integration via jinja2.ext.i18n extension
- Industry standard with professional tooling
- Automatic string extraction with pybabel
- Translator-friendly .po file format (GUI tools available)
- Fast compiled .mo binaries for runtime

**Alternative Considered**: Simple YAML dictionary
- **Rejected**: No Jinja2 integration, manual string extraction, no translator tooling

### 4. Standard logging Module

**Decision**: Replace print() with Python standard logging

**Rationale**:
- Standard library (no new dependencies)
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- Can be redirected, disabled, or formatted
- Better for library/tool development

**Alternative Considered**: Keep print()
- **Rejected**: Not configurable, can't be disabled, no severity levels

## Consequences

### Positive

- **Improved Maintainability**: Cleaner separation of concerns, less boilerplate
- **Better Type Safety**: Pydantic catches validation errors at runtime with clear messages
- **Easier HTML Modifications**: Templates can be edited without touching Python code
- **Professional i18n**: Standard tooling for translators, supports German and future languages
- **Better Developer Experience**: Modern libraries with excellent documentation and IDE support

### Negative

- **Migration Effort**: Requires updating existing code, tests, and documentation
- **New Dependencies**: Adds pydantic, jinja2, and babel to dependency tree
- **Learning Curve**: Team needs to learn new library patterns
- **Potential Performance Impact**: Pydantic validation and Jinja2 rendering add overhead (acceptable for build tool)

### Neutral

- **Breaking Changes Acceptable**: No production users yet, so we can freely modify internal APIs
- **Test Suite Critical**: Existing tests will catch regressions during migration
- **Backward Compatibility**: YAML files should remain compatible, but not guaranteed

## Implementation Plan

Implementation follows user story priorities:

1. **Phase 1 (P1)**: Core refactoring - Pydantic models, Jinja2 templates, standard logging
2. **Phase 2 (P2)**: Internationalization - Babel setup with English and German locales
3. **Phase 3 (P3)**: Enhanced configuration - pydantic-settings for environment variables (optional)

See `/specs/005-library-refactor-i18n/tasks.md` for complete task breakdown.

## Validation

Success will be measured by:

- All existing tests pass with minor updates (SC-001)
- Code complexity reduces by 30%+ in HTML generation (SC-002)
- Clear field-level validation errors for config (SC-003)
- Developers can add translations in <2 minutes (SC-004)
- HTML output functionally equivalent (SC-005)
- Build time remains reasonable (SC-006)
- Language switching via single config value (SC-007)

## References

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Babel Documentation](https://babel.pocoo.org/)
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- Feature Specification: `/specs/005-library-refactor-i18n/spec.md`
- Research Document: `/specs/005-library-refactor-i18n/research.md`
