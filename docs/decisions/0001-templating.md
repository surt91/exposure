# ADR 0001: Use Python String Formatting for HTML Templates

**Status:** Accepted

**Date:** 2025-11-01

**Context:**

The Fotoview gallery generator needs to produce static HTML files from images and metadata. We need a templating approach that is:

- Simple and maintainable
- Fast for build-time generation
- Minimal external dependencies
- Suitable for the limited dynamic content required

The gallery has simple templating needs:
- Inserting asset paths (CSS/JS with hashed filenames)
- Looping over categories and images
- Conditional inclusion of fullscreen modal HTML

**Decision:**

We will use Python's native `str.format()` method for HTML generation rather than a full-featured templating engine like Jinja2, Mako, or Chameleon.

Template files use `{placeholder}` syntax:
- `src/templates/index.html.tpl` - Main page template
- `src/templates/fullscreen.html.part` - Modal component

**Rationale:**

**Advantages:**
1. **Zero Dependencies:** No additional packages required beyond Python stdlib
2. **Simplicity:** Template syntax is immediately readable to Python developers
3. **Performance:** String formatting is fast for build-time generation
4. **Sufficient for Current Needs:** Our templates have minimal logic
5. **Type Safety:** Format strings checked at runtime in build script

**Disadvantages:**
1. **Limited Features:** No filters, template inheritance, or complex control flow
2. **No Auto-escaping:** Must manually handle HTML escaping
3. **Less Powerful:** Cannot iterate in template itself (done in Python)

**Mitigations for Disadvantages:**
- HTML escaping handled explicitly in `build_html.py` for user-provided content
- Complex logic (loops, conditionals) implemented in Python, not templates
- If complexity grows, migration to Jinja2 is straightforward

**Alternatives Considered:**

### Jinja2
**Pros:** Industry standard, powerful features, template inheritance
**Cons:** Additional dependency, overkill for current simple templates
**Decision:** Rejected for MVP; can migrate later if needed

### Mako
**Pros:** Fast, Pythonic
**Cons:** Additional dependency, more complex than needed
**Decision:** Rejected

### Manual String Concatenation
**Pros:** No template files needed
**Cons:** Poor maintainability, hard to edit HTML structure
**Decision:** Rejected

### Template Literals (f-strings)
**Pros:** Native Python, most concise
**Cons:** Mixes code and markup, harder to extract/edit templates
**Decision:** Rejected - separate template files preferred

**Consequences:**

**Positive:**
- Minimal dependency footprint aligns with Static-First Simplicity principle
- Easy for contributors to understand
- Fast build times
- Template files can be edited by designers without Python knowledge

**Negative:**
- Future complex features (e.g., template inheritance, filters) would require refactoring
- Manual HTML escaping required (risk of XSS if not careful)

**Future Migration Path:**

If templating needs grow complex (e.g., need for filters, inheritance, or complex conditionals), we can migrate to Jinja2:

1. Keep template filenames and structure
2. Convert `{variable}` → `{{ variable }}`
3. Add `pip install jinja2` to dependencies
4. Update `build_html.py` to use `jinja2.Template`
5. Tests remain unchanged (output validation)

Migration cost: ~2 hours

**Validation:**

This decision satisfies:
- ✅ Specification Principle I: Static-First Simplicity (minimal dependencies)
- ✅ Performance budgets (build time <5s for 50 images)
- ✅ Maintainability (templates are human-readable)

**References:**

- [Python str.format() Documentation](https://docs.python.org/3/library/stdtypes.html#str.format)
- [ADR Template](https://github.com/joelparkerhenderson/architecture-decision-record)
- Research document: `specs/001-image-gallery/research.md` (Templating Approach section)

**Related Decisions:**

- None yet (first ADR)

**Notes:**

Current template complexity metrics:
- `index.html.tpl`: 4 placeholders, 1 loop (handled in Python)
- `fullscreen.html.part`: Static HTML, no placeholders

If placeholder count exceeds 10 or logic complexity increases significantly, revisit this decision.
