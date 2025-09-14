# Do NOT re-export the 'settings' instance here to avoid name shadowing of the submodule.
from .settings import Settings, get_settings, reset_settings_cache

__all__ = ["Settings", "get_settings", "reset_settings_cache"]
