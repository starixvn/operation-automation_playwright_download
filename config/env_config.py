import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import logger


class EnvConfig:
    """Environment configuration manager that loads from .env.json file"""

    def __init__(self, config_file: str = ".env.json"):
        self.config_file = Path(config_file)
        self.config_data: Dict[str, str] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from .env.json file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse the file content line by line
                for line in content.split("\n"):
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue

                    # Parse KEY=VALUE format
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        self.config_data[key] = value

                logger.info(f"Loaded configuration from {self.config_file}")
                logger.debug(f"Loaded {len(self.config_data)} configuration values")
            else:
                logger.warning(
                    f"Config file {self.config_file} not found, using environment variables only"
                )
                self.config_data = {}
        except Exception as e:
            logger.error(f"Error loading config file {self.config_file}: {e}")
            self.config_data = {}

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value with fallback to environment variable"""
        # First try config file
        if key in self.config_data:
            return self.config_data[key]

        # Fallback to environment variable
        return os.getenv(key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value"""
        value = self.get(key, str(default))
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return bool(value)

    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value"""
        value = self.get(key, str(default))
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float configuration value"""
        value = self.get(key, str(default))
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def get_list(
        self, key: str, default: Optional[list] = None, separator: str = ","
    ) -> list:
        """Get list configuration value"""
        if default is None:
            default = []

        value = self.get(key)
        if value is None:
            return default

        try:
            # Split by separator if it's a string
            if isinstance(value, str):
                return [item.strip() for item in value.split(separator) if item.strip()]
            # Return as-is if it's already a list
            elif isinstance(value, list):
                return value
            else:
                return [str(value)]
        except TypeError:
            return default

    def set(self, key: str, value: str) -> None:
        """Set configuration value"""
        self.config_data[key] = str(value)

    def save(self) -> None:
        """Save current configuration to file"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                f.write("# Environment Configuration\n")
                f.write("# Generated automatically\n\n")

                for key, value in self.config_data.items():
                    f.write(f"{key}={value}\n")

            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config file {self.config_file}: {e}")

    def list_all(self) -> Dict[str, str]:
        """Get all configuration values"""
        return self.config_data.copy()


# Global configuration instance
config = EnvConfig()
