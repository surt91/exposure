# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2024 Hendrik Schawe

"""Tests for internationalization (i18n) support."""

from src.generator.i18n import _, gettext, ngettext, setup_i18n


def test_setup_i18n_english():
    """Test i18n setup with English locale (default)."""
    translations = setup_i18n("en")
    assert translations is not None

    # English is the source language, should return original strings
    result = _("Exposure Gallery Generator")
    assert result == "Exposure Gallery Generator"


def test_setup_i18n_german():
    """Test i18n setup with German locale."""
    translations = setup_i18n("de")
    assert translations is not None

    # Should return German translation
    result = _("Exposure Gallery Generator")
    assert result == "Exposure Galerie-Generator"


def test_setup_i18n_nonexistent_locale():
    """Test i18n setup with non-existent locale (should fallback to English)."""
    translations = setup_i18n("fr")  # French not available
    assert translations is not None

    # Should fallback to English (original string)
    result = _("Exposure Gallery Generator")
    assert result == "Exposure Gallery Generator"


def test_translate_function():
    """Test the _() translation function."""
    setup_i18n("de")

    # Test simple string
    assert _("Categories:") == "Kategorien:"

    # Test string with formatting placeholder
    assert _("Generating gallery HTML...") == "Generiere Galerie-HTML..."


def test_translate_with_parameters():
    """Test gettext() with parameter substitution using named placeholders."""
    setup_i18n("de")

    # Test with named parameter (dict-style)
    # Note: The actual log messages use %s and %d (old-style), not %(name)s
    # This test verifies the gettext() function works for dict-style formatting
    result = gettext("Found %(count)s images", count=42)
    assert "42" in result


def test_translate_fallback_to_english():
    """Test that missing translations fall back to English."""
    setup_i18n("de")

    # This string doesn't exist in translations
    untranslated = _("This string is not translated")
    assert untranslated == "This string is not translated"


def test_ngettext_singular():
    """Test plural forms with singular count."""
    setup_i18n("en")

    result = ngettext("1 image", "%(count)s images", 1)
    assert result == "1 image"


def test_ngettext_plural():
    """Test plural forms with plural count."""
    setup_i18n("en")

    result = ngettext("1 image", "%(count)s images", 5)
    assert result == "%(count)s images"


def test_setup_i18n_custom_locales_dir(tmp_path):
    """Test i18n setup with custom locales directory."""
    # Create a temporary locales directory
    custom_locales = tmp_path / "locales"
    custom_locales.mkdir()

    # Should not crash with non-existent locale in custom dir
    translations = setup_i18n("de", locales_dir=custom_locales)
    assert translations is not None

    # Should fallback to English
    result = _("Test string")
    assert result == "Test string"


def test_translations_persist_across_calls():
    """Test that translation state persists across multiple _() calls."""
    setup_i18n("de")

    # Multiple translation calls should work
    result1 = _("Categories:")
    result2 = _("Exposure Gallery Generator")

    assert result1 == "Kategorien:"
    assert result2 == "Exposure Galerie-Generator"


def test_switch_locale():
    """Test switching between locales."""
    # Start with German
    setup_i18n("de")
    assert _("Categories:") == "Kategorien:"

    # Switch to English
    setup_i18n("en")
    assert _("Categories:") == "Categories:"

    # Switch back to German
    setup_i18n("de")
    assert _("Categories:") == "Kategorien:"


def test_formatted_strings_german():
    """Test that formatted strings work correctly in German."""
    setup_i18n("de")

    # These strings should be translatable
    scanning = _("Scanning images in %s...")
    assert "Scanne Bilder" in scanning

    found = _("Found %d image files")
    assert "Bilddateien gefunden" in found


def test_special_characters_in_translations():
    """Test that German umlauts and special characters work."""
    setup_i18n("de")

    result = _("✓ Gallery built successfully!")
    assert "✓" in result
    assert "erfolgreich" in result
