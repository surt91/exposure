<!--
Sync Impact Report
Version change: 0.0.0 → 1.0.0
Modified principles: (all newly defined)
Added sections: Implementation Constraints, Development Workflow & Quality Gates
Removed sections: None (template placeholders replaced)
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ updated
  - .specify/templates/spec-template.md ✅ aligned (no constitution-specific gates)
  - .specify/templates/tasks-template.md ✅ aligned (independent stories unchanged)
  - .specify/templates/checklist-template.md ✅ aligned (generic)
  - .specify/templates/agent-file-template.md ✅ aligned (no conflicting guidance)
Deferred TODOs: None
-->

# Fotoview Constitution

## Core Principles

### I. Static-First Simplicity
All delivery MUST be static assets (HTML, CSS, JS, images). No backend runtime
code or server-side rendering framework unless a documented exception is
approved in governance. Dependencies MUST be minimal: prefer vanilla JS and
progressive enhancement. Build tooling MUST remain replaceable (single
bundler optional). Avoid introducing a client-side SPA framework unless user
navigation requirements cannot be met with multi-page static HTML.

### II. Performance & Accessibility
Each release MUST achieve Lighthouse scores ≥ 90 for Performance and
Accessibility on a 3G throttled profile. Initial HTML payload MUST be ≤ 30KB
uncompressed; total critical CSS ≤ 25KB; total uncompressed JS shipped to the
initial page ≤ 75KB. Images MUST be optimized and lazy‑loaded where offscreen.
Semantic HTML and ARIA usage MUST enable keyboard-only navigation. Any new
interactive component MUST include an accessibility test (axe) in CI.

### III. Content Integrity & Versioning
All user-visible content (HTML, Markdown, images, CSS, JS) MUST reside in
source control. Each release MUST be tagged with a semantic version.
Fingerprint (hash) static assets in build outputs to prevent stale caching.
Builds MUST be reproducible: same commit → identical `dist/` hash set. No
generated content may remain untracked—build scripts MUST output only derived
artifacts. Content changes MUST describe rationale in CHANGELOG.

### IV. Security & Privacy Baseline
No third-party scripts are allowed unless explicitly approved (listed in
`docs/third-party.md`). Default deployment MUST send zero tracking/analytics
events. If analytics is introduced it MUST be privacy‑respecting and opt‑in.
Security headers (Content-Security-Policy, X-Content-Type-Options,
Referrer-Policy, Permissions-Policy) MUST be documented in `docs/hosting.md`.
External forms or data collection MUST undergo a privacy review before merge.

### V. Documentation & Traceability
README MUST contain quickstart (develop, build, deploy) and performance budget
summary. CHANGELOG MUST record every version with category entries: Added,
Changed, Removed, Security. Architectural or tooling decisions MUST be
captured as lightweight ADRs in `docs/decisions/` (filename format:
`NNN-title.md`). Each principle violation MUST include justification in the
PR description and link to an ADR if persistent.

## Implementation Constraints

**Allowed Stack**: HTML5, CSS3 (utility framework optional: Tailwind), Vanilla
ES Modules JavaScript. Optional tooling: Vite OR no bundler. Hosting: GitHub
Pages, Netlify, or any static CDN—MUST support required security headers.

**Testing Minimum**: Automated link checking, axe accessibility scan, build
reproducibility hash check script, performance budget verification (e.g., via
Lighthouse CI or webhint). No server-side tests required.

**Asset Policy**: Images MUST be compressed (WebP or AVIF preferred). Fonts
MUST be subsetted; self-host where practical. Inline critical CSS allowed up
to 10KB.

## Development Workflow & Quality Gates

1. Branch per change; PR MUST reference CHANGELOG draft entry.
2. CI Gates (all MUST pass):
	- Build reproducibility check (rerun build; compare file hashes)
	- Accessibility scan (axe) passes with zero critical violations
	- Performance budget thresholds met (LCP ≤ 2.5s on emulated 3G; TTI ≤ 5s)
	- Asset size limits respected (HTML/CSS/JS as defined in Principle II)
	- No unapproved third-party scripts; dependency diff reviewed
3. Versioning:
	- Patch: content/typo/style clarification (no budget or principle impact)
	- Minor: new page/component or expanded documentation
	- Major: principle change, structural tooling change, or removal of page
4. Release: Merge main → tag version → update CHANGELOG → deploy.
5. Monthly governance review: verify principles still minimal; prune unused
	tooling.

## Governance

This constitution supersedes conflicting guidance. Amendments REQUIRE a PR
including: proposed change, rationale, impact assessment (performance,
security, accessibility), and version bump justification. Principle additions
or removals → MINOR or MAJOR version per Versioning rule. Emergency security
changes may fast-track but MUST add retroactive ADR within 48h.

Compliance Review: Each PR reviewer MUST confirm gates and principles are met.
Any approved violation MUST include an ADR and triggers a scheduled review to
remove the deviation.

Versioning Policy: See Development Workflow section; semantic versioning is
mandatory. Tooling upgrades require documenting expected impact. This file is
authoritative—templates derive gates from these sections.

**Version**: 1.0.0 | **Ratified**: 2025-10-31 | **Last Amended**: 2025-10-31
