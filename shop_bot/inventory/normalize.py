"""Normalize fastener names to standard format.

Standard formats:
- Screws: TYPE SIZExLENGTH (e.g., "SHCS M3x6mm")
- Nuts: HEX NUT SIZE (e.g., "HEX NUT M3")
- Washers: WASHER SIZE (e.g., "WASHER M5")
- Grub screws: GRUB SIZExLENGTH (e.g., "GRUB M4x5mm")
"""

import re

# Patterns to identify fastener types
SCREW_TYPES = {
    "SHCS": [
        r"socket\s*head(\s*(cap\s*)?(screw)?)?",
        r"shcs",
    ],
    "BHCS": [
        r"button\s*head(\s*(cap\s*)?(screw)?)?",
        r"bhcs",
    ],
    "FHCS": [
        r"flat\s*head(\s*(cap\s*)?(screw)?)?",
        r"counter\s*sunk(\s*screw)?",
        r"fhcs",
    ],
    "GRUB": [
        r"grub(\s*screw)?",
        r"set\s*screw",
    ],
}

NUT_PATTERNS = [
    r"hex\s*nut",
    r"nut",
]

WASHER_PATTERNS = [
    r"(flat\s*)?washer",
]

# Regex for metric size (M2, M3, M4, etc.) - allows x or space after
METRIC_SIZE_RE = re.compile(r"\b(m\d+(?:\.\d+)?)", re.IGNORECASE)

# Regex for SIZExLENGTH pattern (e.g., M3x6, M4x10mm)
SIZE_LENGTH_RE = re.compile(
    r"\b(m\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(?:mm)?",
    re.IGNORECASE
)

# Regex for standalone length (number with optional mm suffix)
LENGTH_RE = re.compile(r"\b(\d+(?:\.\d+)?)\s*mm\b", re.IGNORECASE)


def _extract_metric_size(text: str) -> str | None:
    """Extract metric size like M3, M4, M5 from text."""
    match = METRIC_SIZE_RE.search(text)
    if match:
        return match.group(1).upper()
    return None


def _extract_length(text: str, size: str | None = None) -> str | None:
    """Extract length in mm from text."""
    # First try to find SIZExLENGTH pattern
    match = SIZE_LENGTH_RE.search(text)
    if match:
        length = match.group(2)
        return length.rstrip("0").rstrip(".") if "." in length else length

    # Look for standalone length with mm suffix
    for match in LENGTH_RE.finditer(text):
        length = match.group(1)
        # Skip if this is part of the metric size
        if size and f"M{length}" == size.upper():
            continue
        if float(length) > 0:
            return length.rstrip("0").rstrip(".") if "." in length else length

    # Look for standalone number that could be a length (common pattern: "M3 socket head 6mm" or "M3 socket head 6")
    if size:
        # Remove the size from text to find other numbers
        text_without_size = re.sub(r"\b" + re.escape(size) + r"\b", "", text, flags=re.IGNORECASE)
        # Find any number that's not obviously something else
        for match in re.finditer(r"\b(\d+(?:\.\d+)?)\b", text_without_size):
            length = match.group(1)
            val = float(length)
            # Reasonable screw lengths are 2-100mm
            if 2 <= val <= 100:
                return length.rstrip("0").rstrip(".") if "." in length else length

    return None


def _match_patterns(text: str, patterns: list[str]) -> bool:
    """Check if text matches any of the patterns."""
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower):
            return True
    return False


def _identify_screw_type(text: str) -> str | None:
    """Identify which screw type the text refers to."""
    text_lower = text.lower()
    for screw_type, patterns in SCREW_TYPES.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return screw_type
    return None


def normalize_fastener_name(name: str) -> str:
    """Normalize a fastener name to standard format.

    Returns the original name if it doesn't match a known fastener pattern.

    Examples:
        "socket head cap screw M3x6mm" -> "SHCS M3x6mm"
        "m3 socket head 6mm" -> "SHCS M3x6mm"
        "M5 hex nut" -> "HEX NUT M5"
        "washer M4" -> "WASHER M4"
        "grub screw M4x5" -> "GRUB M4x5mm"
    """
    name = name.strip()

    # Try to extract metric size
    size = _extract_metric_size(name)
    if not size:
        # No metric size found, return as-is
        return name

    # Check for screw types (these have length)
    screw_type = _identify_screw_type(name)
    if screw_type:
        length = _extract_length(name, size)
        if length:
            return f"{screw_type} {size}x{length}mm"
        else:
            # Screw without length - return as-is since it's incomplete
            return name

    # Check for hex nuts
    if _match_patterns(name, NUT_PATTERNS):
        return f"HEX NUT {size}"

    # Check for washers
    if _match_patterns(name, WASHER_PATTERNS):
        return f"WASHER {size}"

    # No pattern matched, return as-is
    return name
