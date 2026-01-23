"""High-level service functions for lighting control."""

from .wled_client import WLEDClient
from .zones import resolve_zone, get_zone_display_name


# Named color mappings to RGB values
COLOR_MAP = {
    'red': [255, 0, 0],
    'green': [0, 255, 0],
    'blue': [0, 0, 255],
    'white': [255, 255, 255],
    'warm': [255, 180, 100],
    'cool': [200, 220, 255],
    'orange': [255, 165, 0],
    'purple': [128, 0, 128],
    'yellow': [255, 255, 0],
    'pink': [255, 105, 180],
    'cyan': [0, 255, 255],
    'magenta': [255, 0, 255],
    'off': [0, 0, 0],
}

# Common effect name mappings to WLED effect IDs
EFFECT_MAP = {
    'solid': 0,
    'blink': 1,
    'breathe': 2,
    'wipe': 3,
    'random': 4,
    'rainbow': 9,
    'scan': 10,
    'fade': 11,
    'chase': 28,
    'fire': 66,
    'twinkle': 74,
    'fireworks': 90,
}


def parse_color(color: str) -> list[int]:
    """Parse a color string to RGB values.

    Args:
        color: Color name (red, blue, etc.) or hex code (#FF0000)

    Returns:
        RGB values as [R, G, B]

    Raises:
        ValueError: If color cannot be parsed
    """
    color = color.lower().strip()

    if color in COLOR_MAP:
        return COLOR_MAP[color]

    if color.startswith('#'):
        hex_val = color[1:]
        if len(hex_val) == 6:
            return [int(hex_val[i:i+2], 16) for i in (0, 2, 4)]

    raise ValueError(f"Unknown color: {color}")


def parse_effect(effect: str) -> int:
    """Parse an effect name to WLED effect ID.

    Args:
        effect: Effect name

    Returns:
        WLED effect ID

    Raises:
        ValueError: If effect is unknown
    """
    effect = effect.lower().strip()

    if effect in EFFECT_MAP:
        return EFFECT_MAP[effect]

    # Try to parse as int
    try:
        return int(effect)
    except ValueError:
        pass

    raise ValueError(f"Unknown effect: {effect}. Available: {', '.join(EFFECT_MAP.keys())}")


def set_zone_power(zone: str, on: bool) -> str:
    """Turn a zone on or off.

    Args:
        zone: Zone name
        on: True to turn on, False to turn off

    Returns:
        Status message
    """
    client = WLEDClient()
    segments = resolve_zone(zone)
    client.set_segments(segments, on=on)
    state = "on" if on else "off"
    return f"Turned {zone} {state}"


def set_zone_color(zone: str, color: list[int]) -> str:
    """Set the color of a zone.

    Args:
        zone: Zone name
        color: RGB values as [R, G, B]

    Returns:
        Status message
    """
    client = WLEDClient()
    segments = resolve_zone(zone)
    client.set_segments(segments, color=color, on=True)
    return f"Set {zone} to RGB({color[0]}, {color[1]}, {color[2]})"


def set_zone_brightness(zone: str, brightness: int) -> str:
    """Set the brightness of a zone.

    Args:
        zone: Zone name
        brightness: Brightness level 0-255

    Returns:
        Status message
    """
    client = WLEDClient()
    segments = resolve_zone(zone)
    client.set_segments(segments, brightness=brightness)
    pct = round(brightness / 255 * 100)
    return f"Set {zone} brightness to {pct}%"


def set_zone_effect(zone: str, effect: str) -> str:
    """Set a lighting effect on a zone.

    Args:
        zone: Zone name
        effect: Effect name or ID

    Returns:
        Status message
    """
    client = WLEDClient()
    segments = resolve_zone(zone)
    effect_id = parse_effect(effect)
    client.set_segments(segments, effect=effect_id, on=True)
    return f"Set {zone} effect to {effect}"


def get_light_status() -> str:
    """Get the current status of all lights.

    Returns:
        Formatted status string
    """
    client = WLEDClient()
    state = client.get_state()

    lines = []
    lines.append(f"Power: {'ON' if state.get('on') else 'OFF'}")
    lines.append(f"Master brightness: {round(state.get('bri', 0) / 255 * 100)}%")

    segments = state.get('seg', [])
    for seg in segments:
        seg_id = seg.get('id', 0)
        name = get_zone_display_name(seg_id)
        seg_on = "ON" if seg.get('on', False) else "OFF"
        seg_bri = round(seg.get('bri', 0) / 255 * 100)
        lines.append(f"  {name}: {seg_on} ({seg_bri}%)")

    return "\n".join(lines)
