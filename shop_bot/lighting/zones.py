"""Zone configuration and name resolution for WLED segments."""

ZONES = {
    # Wall zones
    'west': {'segment': 0, 'type': 'wall'},
    'w': {'segment': 0, 'type': 'wall'},
    'south': {'segment': 2, 'type': 'wall'},
    's': {'segment': 2, 'type': 'wall'},
    'east': {'segment': 4, 'type': 'wall'},
    'e': {'segment': 4, 'type': 'wall'},
    'north': {'segment': 6, 'type': 'wall'},
    'n': {'segment': 6, 'type': 'wall'},
    # Corner zones
    'southwest': {'segment': 1, 'type': 'corner'},
    'sw': {'segment': 1, 'type': 'corner'},
    'southeast': {'segment': 3, 'type': 'corner'},
    'se': {'segment': 3, 'type': 'corner'},
    'northeast': {'segment': 5, 'type': 'corner'},
    'ne': {'segment': 5, 'type': 'corner'},
    'northwest': {'segment': 7, 'type': 'corner'},
    'nw': {'segment': 7, 'type': 'corner'},
}


def resolve_zone(name: str) -> list[int]:
    """Return segment IDs for a zone name.

    Args:
        name: Zone name (all, walls, corners, or specific wall/corner)

    Returns:
        List of segment IDs

    Raises:
        ValueError: If zone name is unknown
    """
    name = name.lower().strip()

    if name == 'all':
        return list(range(8))
    if name == 'walls':
        return [0, 2, 4, 6]
    if name == 'corners':
        return [1, 3, 5, 7]

    zone = ZONES.get(name)
    if zone:
        return [zone['segment']]

    raise ValueError(f"Unknown zone: {name}")


def get_zone_display_name(segment_id: int) -> str:
    """Get a human-readable name for a segment ID."""
    segment_names = {
        0: 'west wall',
        1: 'southwest corner',
        2: 'south wall',
        3: 'southeast corner',
        4: 'east wall',
        5: 'northeast corner',
        6: 'north wall',
        7: 'northwest corner',
    }
    return segment_names.get(segment_id, f'segment {segment_id}')
