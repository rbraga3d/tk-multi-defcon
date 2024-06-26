from .constants import (
    RENDER_SETTINGS_FILE_NAME,
    ARNOLD_SETTINGS,
    REDSHIFT_SETTINGS,
    VRAY_SETTINGS
)
from .file_manager import ConfigFileManager


class DefConManager:
    def __init__(self, defcon_app):
        self._defcon_app = defcon_app
        self._engine = self._defcon_app.engine
        self._file_manager = ConfigFileManager()
    

class MayaDefConManager(DefConManager):

    def configure_render_settings(self):
        pass

    def configure_arnold_settings(self):
        pass

    def configure_redshift_settings(self):
        pass

    def configure_vray_settings(self):
        pass


