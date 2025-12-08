# Exposure Documentation

Complete technical documentation for the Exposure static gallery generator.

## 📚 Documentation Structure

### Core Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| **[architecture.md](architecture.md)** | System design, data flow, build pipeline, components | Developers, LLM assistants |
| **[development.md](development.md)** | Dev workflow, setup, testing, debugging, contributing | Contributors |

### Specialized Guides

| Document | Purpose |
|----------|---------|
| **[hosting.md](hosting.md)** | Deployment configuration, security headers, CSP |
| **[i18n-workflow.md](i18n-workflow.md)** | Translation workflow with Babel & gettext |

### Architecture Decision Records (ADRs)

Located in **[decisions/](decisions/)** - documents key architectural choices with context and rationale:

- **[0001-templating.md](decisions/0001-templating.md)** - Why Jinja2 for HTML generation
- **[0002-type-checking.md](decisions/0002-type-checking.md)** - Why `ty` over mypy/pyright
- **[0003-dark-mode-styling-approach.md](decisions/0003-dark-mode-styling-approach.md)** - CSS-only dark mode
- **[0005-library-modernization.md](decisions/0005-library-modernization.md)** - Pydantic v2 migration
- **[0007-flexible-layout-algorithm.md](decisions/0007-flexible-layout-algorithm.md)** - Justified layout choice
- **[0010-banner-cropping-approach.md](decisions/0010-banner-cropping-approach.md)** - CSS object-fit approach
- **[0012-blur-placeholder-strategy.md](decisions/0012-blur-placeholder-strategy.md)** - Low-quality image placeholders
- **[008-image-preprocessing-approach.md](decisions/008-image-preprocessing-approach.md)** - Thumbnail generation strategy

## 🚀 Quick Start Paths

### New to Exposure?
1. Read [../README.md](../README.md) - Features & quick start
2. Read [architecture.md](architecture.md) - System overview
3. Explore [development.md](development.md) - Setup & workflow

### Want to Contribute?
1. Read [development.md](development.md) - Setup, testing, code style
2. Check [architecture.md](architecture.md) - Understand the system
3. Review relevant ADRs - Context for design decisions

### Deploying a Gallery?
1. Build gallery: `uv run exposure`
2. Review [hosting.md](hosting.md) - Security configuration
3. Deploy `dist/` directory to your hosting platform

### Adding Translations?
1. Read [i18n-workflow.md](i18n-workflow.md)
2. Follow Babel workflow (extract → translate → compile)

### Extending the Code?
1. Read [architecture.md](architecture.md) - Component responsibilities
2. Read source code docstrings - All functions have detailed docs
3. Review relevant ADRs - Design constraints and rationale

## 🔍 Finding Information

### By Topic

**Architecture & Design:**
- System overview → [architecture.md](architecture.md) § System Overview
- Build pipeline → [architecture.md](architecture.md) § Build Pipeline
- Data models → [architecture.md](architecture.md) § Data Models
- Frontend → [architecture.md](architecture.md) § Frontend Architecture

**Development:**
- Setup → [development.md](development.md) § Setup
- Testing → [development.md](development.md) § Testing Strategy
- Debugging → [development.md](development.md) § Debugging Tips
- Code style → [development.md](development.md) § Code Style

**Operations:**
- Deployment → [hosting.md](hosting.md)
- Security → [hosting.md](hosting.md) § Content Security Policy
- Translations → [i18n-workflow.md](i18n-workflow.md)

**API Details:**
- Function signatures → Source code files in `src/generator/`
- Pydantic models → [architecture.md](architecture.md) § Data Models
- Docstrings → All public functions have complete documentation

### By Task

| I want to... | Read this... |
|--------------|--------------|
| Understand how Exposure works | [architecture.md](architecture.md) |
| Set up development environment | [development.md](development.md) § Setup |
| Run tests | [development.md](development.md) § Testing Strategy |
| Add a new feature | [development.md](development.md) § Adding Features |
| Deploy to production | [hosting.md](hosting.md) |
| Add a new language | [i18n-workflow.md](i18n-workflow.md) § Initialize a New Locale |
| Debug build issues | [development.md](development.md) § Debugging Tips |
| Understand a design decision | [decisions/](decisions/) (find relevant ADR) |
| Find a function signature | Source code + docstrings (use `help()` or IDE) |

## 📝 Documentation Standards

### When to Update Documentation

| Change Type | Update |
|-------------|--------|
| New feature | README.md + architecture.md (if architectural change) |
| API change | Update docstrings in source code |
| Build process change | architecture.md § Build Pipeline |
| Configuration option | architecture.md § Configuration System |
| New workflow | Create new guide (e.g., i18n-workflow.md) |
| Architectural decision | Create new ADR in decisions/ |
| Bug fix (user-impacting) | development.md § Common Issues (if applicable) |

### Documentation Locations

- **User-facing features:** README.md
- **System design:** architecture.md
- **Dev workflow:** development.md
- **API details:** Source code docstrings (single source of truth)
- **Specialized workflows:** Dedicated guides (hosting.md, i18n-workflow.md)
- **Design rationale:** ADRs in decisions/

## 🤝 Contributing to Documentation

When contributing documentation:

1. **Keep it accurate** - Code changes should update relevant docs
2. **Be concise** - Respect reader's time
3. **Use examples** - Code snippets over abstract descriptions
4. **Link between docs** - Cross-reference related information
5. **Update this index** - If adding new docs

For ADRs, follow the format:
- **Context** - What problem are we solving?
- **Decision** - What did we decide?
- **Consequences** - What are the impacts?
- **Alternatives Considered** - What else did we evaluate?

## 📖 External References

- **Python:** [docs.python.org](https://docs.python.org/3/)
- **Pydantic:** [docs.pydantic.dev](https://docs.pydantic.dev/)
- **Jinja2:** [jinja.palletsprojects.com](https://jinja.palletsprojects.com/)
- **Pillow:** [pillow.readthedocs.io](https://pillow.readthedocs.io/)
- **pytest:** [docs.pytest.org](https://docs.pytest.org/)
- **Playwright:** [playwright.dev](https://playwright.dev/)
- **Babel:** [babel.pocoo.org](https://babel.pocoo.org/)

---

**Questions?** Check the docs first, then open an issue on GitHub.
