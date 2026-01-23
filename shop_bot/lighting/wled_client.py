"""HTTP client for WLED JSON API."""

import requests
from django.conf import settings


class WLEDClient:
    """Client for communicating with WLED controller via JSON API."""

    def __init__(self, host: str = None):
        """Initialize client with WLED host URL.

        Args:
            host: WLED host URL (defaults to settings.WLED_HOST)
        """
        self.host = host or getattr(settings, 'WLED_HOST', 'http://192.168.1.23')
        self.host = self.host.rstrip('/')

    def get_state(self) -> dict:
        """Get current WLED state.

        Returns:
            State dictionary from WLED
        """
        response = requests.get(f"{self.host}/json/state", timeout=5)
        response.raise_for_status()
        return response.json()

    def set_state(self, data: dict) -> dict:
        """Set WLED state.

        Args:
            data: State data to set

        Returns:
            Response from WLED
        """
        response = requests.post(f"{self.host}/json/state", json=data, timeout=5)
        response.raise_for_status()
        return response.json()

    def set_segments(
        self,
        segment_ids: list[int],
        color: list[int] = None,
        brightness: int = None,
        on: bool = None,
        effect: int = None
    ) -> dict:
        """Set properties for one or more segments.

        Args:
            segment_ids: List of segment IDs to modify
            color: RGB color as [R, G, B]
            brightness: Brightness level 0-255
            on: Power state (True=on, False=off)
            effect: Effect ID

        Returns:
            Response from WLED
        """
        seg_data = []
        for seg_id in segment_ids:
            seg = {'id': seg_id}
            if color is not None:
                seg['col'] = [color]
            if brightness is not None:
                seg['bri'] = brightness
            if on is not None:
                seg['on'] = on
            if effect is not None:
                seg['fx'] = effect
            seg_data.append(seg)

        return self.set_state({'seg': seg_data})

    def get_effects(self) -> list[str]:
        """Get list of available effects.

        Returns:
            List of effect names
        """
        response = requests.get(f"{self.host}/json/effects", timeout=5)
        response.raise_for_status()
        return response.json()
