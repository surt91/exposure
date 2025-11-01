# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2024 Hendrik Schawe

"""Internationalization (i18n) support for fotoview gallery generator.

This module provides translation infrastructure using Babel/gettext.
Translations are loaded from .mo files in the locales/ directory.
"""

from pathlib import Path
from typing import Any

from babel.support import NullTranslations, Translations

_translations: Translations | NullTranslations | None = None


def setup_i18n(
    locale: str = "en", locales_dir: Path | None = None
) -> Translations | NullTranslations:
    """Setup internationalization for the given locale.

    Args:
        locale: Language code (e.g., "en", "de"). Defaults to English.
        locales_dir: Directory containing translation files. If None, uses
                     default locales/ directory at project root.

    Returns:
        Translations object that can be used for Jinja2 integration.

    Example:
        >>> translations = setup_i18n("de")
        >>> print(_("Hello"))  # Returns German translation
    """
    global _translations

    if locales_dir is None:
        # Default to locales/ at project root (3 levels up from this file)
        locales_dir = Path(__file__).parent.parent.parent / "locales"

    if locale == "en":
        # English is the source language, no translation needed
        _translations = NullTranslations()
    else:
        try:
            _translations = Translations.load(locales_dir, [locale])
        except (FileNotFoundError, OSError):
            # Fallback to English if locale not found
            _translations = NullTranslations()

    return _translations


def _(message: str) -> str:
    """Get translated message for the currently configured locale.

    This is the main translation function used throughout the codebase.

    Args:
        message: English message to translate (msgid in .po files)

    Returns:
        Translated message, or original message if no translation exists

    Example:
        >>> _("Image Gallery")
        "Bildergalerie"  # if locale is "de"
    """
    if _translations is None:
        return message
    return _translations.gettext(message)


def gettext(message: str, **kwargs: Any) -> str:
    """Get translated message with parameter substitution.

    Args:
        message: Message template with %(name)s placeholders
        **kwargs: Values to substitute into the template

    Returns:
        Translated and formatted message

    Example:
        >>> gettext("Found %(count)s images", count=42)
        "42 Bilder gefunden"  # if locale is "de"
    """
    translated = _(message)
    if kwargs:
        return translated % kwargs
    return translated


def ngettext(singular: str, plural: str, n: int) -> str:
    """Get translated message with plural form handling.

    Args:
        singular: Singular form (e.g., "1 image")
        plural: Plural form (e.g., "%(count)s images")
        n: Count to determine singular vs plural

    Returns:
        Appropriate translated form based on count

    Example:
        >>> ngettext("1 image", "%(count)s images", 5)
        "5 Bilder"  # if locale is "de"
    """
    if _translations is None:
        return singular if n == 1 else plural
    return _translations.ngettext(singular, plural, n)
