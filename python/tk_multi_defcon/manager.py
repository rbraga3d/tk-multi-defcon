from tank_vendor import yaml

from .constants import (
    RENDER_SETTINGS_FILE,
    ARNOLD_SETTINGS_FILE,
    REDSHIFT_SETTINGS_FILE,
    VRAY_SETTINGS_FILE
)
from .file_manager import DefconFileManager


class DefConManager:
    def __init__(self, defcon_app):
        self._defcon_app = defcon_app
        self._engine = self._defcon_app.engine
        self._file_manager = DefconFileManager(self._defcon_app)


    def _get_config(self, config_name):
        config_path = self._file_manager.get_config_file_path(config_name)
        return config_path

    
class MayaDefConManager(DefConManager):

    def __init__(self, defcon_app):
        super(MayaDefConManager, self).__init__(defcon_app)

        config_file = self._get_config(RENDER_SETTINGS_FILE)
        print("CONFIG FILE = ", config_file)

    def configure_render_settings(self):
        pass

    def configure_arnold_settings(self):
        pass

    def configure_redshift_settings(self):
        pass

    def configure_vray_settings(self):
        pass


def create_defcon_manager(defcon_app):
    """
    Create a defcon manager based on the current engine
    """
    engine_name = defcon_app.engine.name

    # Maya defcon manager
    if engine_name == "tk-maya":
        return MayaDefConManager(defcon_app)

