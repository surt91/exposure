#!/bin/bash
# Accessibility testing placeholder using axe-core
# This script will be integrated into CI to scan generated HTML

echo "Accessibility Test Placeholder"
echo "================================"
echo ""
echo "This script will run axe-core tests against dist/*.html"
echo "Integration with CI coming in Phase 6 (T052)"
echo ""
echo "Manual testing:"
echo "  1. Build the gallery: uv run python -m src.generator.build_html"
echo "  2. Serve dist/ with: python -m http.server --directory dist 8000"
echo "  3. Run axe DevTools extension in browser"
echo ""
