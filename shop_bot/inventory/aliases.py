# Taxonomy: search term → list of patterns to also search for
ALIASES = {
    # Cap screws (all types)
    "screw": ["SHCS", "BHCS", "FHCS", "GRUB"],
    "screws": ["SHCS", "BHCS", "FHCS", "GRUB"],
    "cap screw": ["SHCS", "BHCS", "FHCS"],
    "cap screws": ["SHCS", "BHCS", "FHCS"],

    # Specific cap screw types
    "socket head": ["SHCS"],
    "socket head cap screw": ["SHCS"],
    "button head": ["BHCS"],
    "button head cap screw": ["BHCS"],
    "flat head": ["FHCS"],
    "flat head cap screw": ["FHCS"],
    "countersunk": ["FHCS"],

    # Grub/set screws
    "grub": ["GRUB"],
    "grub screw": ["GRUB"],
    "set screw": ["GRUB"],

    # Nuts
    "nut": ["HEX NUT"],
    "nuts": ["HEX NUT"],
    "hex nut": ["HEX NUT"],

    # Washers
    "washer": ["WASHER"],
    "washers": ["WASHER"],
    "flat washer": ["WASHER"],
}


def expand_query(query: str) -> list[str]:
    """Expand a search query into multiple search terms."""
    query_lower = query.lower().strip()

    # Start with the original query
    terms = [query]

    # Check if any alias matches (substring or exact)
    for alias, expansions in ALIASES.items():
        if alias in query_lower:
            terms.extend(expansions)

    return list(set(terms))  # Deduplicate
