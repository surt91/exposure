# ADR 0002: Type Checking with ty from Astral

**Status**: Accepted
**Date**: 2025-11-01
**Deciders**: exposure development team

## Context

The exposure codebase needs static type checking to:
- Catch type-related bugs during development
- Improve code documentation through type annotations
- Enforce type safety through CI gates
- Provide developers with immediate feedback on type errors

## Decision

We will use **ty** (v0.0.1-alpha.25) from Astral as our static type checker, configured in `pyproject.toml`.

## Rationale

### Why ty over mypy?

1. **Astral Ecosystem Alignment**
   - Project already uses `uv` (package management) and `ruff` (linting)
   - Astral has proven track record with Python tooling
   - Unified tooling simplifies development workflow

2. **Performance**
   - ty is built in Rust, offering significantly faster type checking than Python-based alternatives
   - Expected to meet <5 second feedback requirement for developers
   - Rust-based tools from Astral (ruff) have demonstrated exceptional performance

3. **Strategic Bet on the Future**
   - Astral's track record:
     - `uv`: Revolutionary Python package/project management
     - `ruff`: Became industry standard linter in <2 years
   - Early adoption allows us to influence development and learn the tool
   - Type annotations are standard Python, easy migration if needed

4. **Modern Python Support**
   - Native Python 3.11+ syntax support (list[str], X | Y unions)
   - Designed for modern Python workflows
   - Simple configuration following ruff patterns

### Acknowledged Risks

- **Alpha Status**: ty is at v0.0.1-alpha.25 (experimental)
- **Documentation**: Limited compared to mature tools like mypy
- **Ecosystem**: Smaller community and fewer integrations

### Mitigation Strategies

- Type annotations use standard Python syntax (PEP 484) - portable to mypy if needed
- Small codebase (~500-1000 LOC) makes tool experimentation low-risk
- Can migrate to mypy without code changes if ty has blockers

## Consequences

### Positive

- ✅ Fastest type checking available (Rust implementation)
- ✅ Unified Astral tooling (uv + ruff + ty)
- ✅ Excellent error messages (observed in testing)
- ✅ Simple configuration
- ✅ Future-ready tooling choice

### Negative

- ⚠️ Alpha software may have bugs or breaking changes
- ⚠️ Limited IDE integration initially
- ⚠️ Smaller community for support

### Neutral

- 📝 Configuration format uses `[tool.ty]` section in `pyproject.toml`
- 📝 Commands: `uv run ty check src/`
- 📝 Exit codes: 0 = success, 1 = errors, 2 = fatal

## Implementation

### Configuration

```toml
[tool.ty]
[tool.ty.environment]
python-version = "3.11"
```

### CI Integration

```yaml
- name: Type check
  run: uv run ty check src/
```

### Dependencies

```toml
[dependency-groups]
dev = [
    "ty",
    "types-PyYAML>=6.0",
    "types-Pillow>=10.0",
]
```

## Validation

Type checking was validated by:
1. ✅ ty successfully analyzes all source code
2. ✅ ty catches intentional type errors with clear messages
3. ✅ All existing code passes type checking (codebase already well-typed)
4. ✅ CI integration working

## Alternatives Considered

### mypy
- **Pros**: Industry standard, mature, extensive documentation
- **Cons**: Python-based (slower), separate ecosystem from uv/ruff
- **Decision**: Rejected in favor of Astral ecosystem alignment

### pyright
- **Pros**: Fast, Microsoft backing, good IDE support
- **Cons**: Different ecosystem, Node.js dependency
- **Decision**: Rejected in favor of Python-native solution

### pyre
- **Pros**: Fast, Facebook backing
- **Cons**: Less community adoption, focused on large codebases
- **Decision**: Rejected due to overhead for small project

### pytype
- **Pros**: Type inference capabilities
- **Cons**: Slower, less strict mode options
- **Decision**: Rejected due to performance and strictness goals

## References

- [ty GitHub Repository](https://github.com/astral-sh/ty)
- [Astral](https://astral.sh/)
- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [PEP 604 - Union Syntax](https://www.python.org/dev/peps/pep-0604/)
- Feature specification: `/specs/002-type-checking/spec.md`
- Research decisions: `/specs/002-type-checking/research.md`

## Review

This decision should be reviewed after:
- ty reaches beta or stable release
- 6 months of usage to assess stability and performance
- Any blocking issues that prevent development
