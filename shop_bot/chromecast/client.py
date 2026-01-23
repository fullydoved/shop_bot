import pychromecast
from django.conf import settings
import threading
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class ChromecastManager:
    """Singleton manager for Chromecast connection."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.cast = None
        self.browser = None
        self._initialized = True

    def connect(self, timeout: int = 10) -> bool:
        """Connect to the configured Chromecast by IP or discovery."""
        if self.cast and self.cast.socket_client.is_connected:
            return True

        host = getattr(settings, 'CHROMECAST_HOST', None)
        device_name = getattr(settings, 'CHROMECAST_NAME', 'Shop Speakers')

        try:
            # Prefer direct IP connection (works in WSL2/Docker)
            if host:
                # API requires tuple: (ip, port, uuid, model_name, friendly_name)
                host_info = (host, 8009, UUID('00000000-0000-0000-0000-000000000000'), None, device_name)
                self.cast = pychromecast.get_chromecast_from_host(host_info)
                self.cast.wait()
                logger.info(f"Connected to Chromecast at {host}")
                return True

            # Fallback to mDNS discovery
            chromecasts, browser = pychromecast.get_listed_chromecasts(
                friendly_names=[device_name],
                discovery_timeout=timeout
            )
            if chromecasts:
                self.cast = chromecasts[0]
                self.browser = browser
                self.cast.wait()
                logger.info(f"Connected to Chromecast: {device_name}")
                return True
            logger.warning(f"Chromecast '{device_name}' not found")
            return False
        except Exception as e:
            logger.error(f"Chromecast connection error: {e}")
            return False

    def get_cast(self):
        """Get the cast device, connecting if needed."""
        if not self.cast or not self.cast.socket_client.is_connected:
            self.connect()
        return self.cast

    def cleanup(self):
        """Stop discovery browser."""
        if self.browser:
            pychromecast.discovery.stop_discovery(self.browser)
            self.browser = None
        self.cast = None


# Module-level singleton
_manager = None


def get_manager() -> ChromecastManager:
    global _manager
    if _manager is None:
        _manager = ChromecastManager()
    return _manager
