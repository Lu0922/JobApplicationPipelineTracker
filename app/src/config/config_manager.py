# src/config/config_manager.py
import json
import os
from typing import Any

class SystemConfigManager:
    """The universal configuration manager dropped into all 3 consoles.
    Safely boots up with a silent bootstrap fallback to prevent initialization loops.
    """
    def __init__(self, config_path: str = "jsons/config.json"):
        self.config_path = config_path
        self.logger = None  # 🎯 Will be dynamically injected right after setup_logger runs!
        self.config_data = {}
        self.load()

    def load(self):
        """Loads configuration parameters from disk safely."""
        if not os.path.exists(self.config_path):
            self._log_error(f"⚠️  Target parameters file missing at {self.config_path}. Loading defaults.")
            self.config_data = self._get_default_profile()
            return

        try:
            with open(self.config_path, "r") as f:
                self.config_data = json.load(f)
        except Exception as e:
            self._log_error(f"💥 Critical configuration parsing breakdown: {e}")
            self.config_data = self._get_default_profile()

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Retrieves a specific configuration parameter safely using safe fallback bounds."""
        return self.config_data.get(section, {}).get(key, default)

    def set_logger(self, active_logger):
        """🎯 Dynamic Injection Entry: Links your production universal logger post-boot."""
        self.logger = active_logger

    def _log_error(self, message: str):
        """Internal helper to redirect early boot messages before the true logger is alive."""
        if self.logger:
            self.logger.warning(message)
        else:
            print(f"[Early Boot Initialization] {message}")
