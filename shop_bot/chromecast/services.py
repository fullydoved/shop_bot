from .client import get_manager


def _get_media_controller():
    """Get media controller, ensuring connection."""
    manager = get_manager()
    cast = manager.get_cast()
    if not cast:
        raise ConnectionError("Chromecast not available")
    return cast.media_controller, cast


def music_pause() -> str:
    mc, _ = _get_media_controller()
    mc.pause()
    return "Paused the music"


def music_play() -> str:
    mc, _ = _get_media_controller()
    mc.play()
    return "Resumed playback"


def music_stop() -> str:
    mc, _ = _get_media_controller()
    mc.stop()
    return "Stopped the music"


def music_skip() -> str:
    mc, _ = _get_media_controller()
    mc.queue_next()
    return "Skipped to next track"


def music_previous() -> str:
    mc, _ = _get_media_controller()
    mc.queue_prev()
    return "Playing previous track"


def music_volume(level: int) -> str:
    """Set volume (0-100)."""
    _, cast = _get_media_controller()
    volume = max(0, min(100, level)) / 100.0
    cast.set_volume(volume)
    return f"Set volume to {level}%"


def music_volume_up(amount: int = 10) -> str:
    _, cast = _get_media_controller()
    current = cast.status.volume_level
    new_level = min(1.0, current + amount / 100.0)
    cast.set_volume(new_level)
    return f"Volume up to {int(new_level * 100)}%"


def music_volume_down(amount: int = 10) -> str:
    _, cast = _get_media_controller()
    current = cast.status.volume_level
    new_level = max(0.0, current - amount / 100.0)
    cast.set_volume(new_level)
    return f"Volume down to {int(new_level * 100)}%"


def music_status() -> str:
    mc, cast = _get_media_controller()
    mc.update_status()  # Refresh status
    status = mc.status

    if not status or status.player_state == "IDLE":
        return "Nothing playing right now"

    lines = []
    if status.title:
        lines.append(f"Playing: {status.title}")
    if status.artist:
        lines.append(f"Artist: {status.artist}")
    if status.album_name:
        lines.append(f"Album: {status.album_name}")

    lines.append(f"Status: {status.player_state}")
    lines.append(f"Volume: {int(cast.status.volume_level * 100)}%")

    return "\n".join(lines) if lines else "Music is playing"
