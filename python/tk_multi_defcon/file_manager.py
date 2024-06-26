import os

from .constants import (
    ENGINES_DIR_NAME
)


class DefconFileManager:
    def __init__(self, defcon_app):
        self._defcon_app = defcon_app

    def get_root_configs_path(self):
        """
        Returns the root configs path
        obtained from a hook
        """
        configs_path = self._defcon_app.execute_hook_method(
            "hook_root_configs_path",
            "get_root_configs_path"
        )

        return configs_path
    
    def get_current_engine_configs_path(self):
        """
        Return the name of the engine dir based on the
        sg_engine name. 
            e.g:
                tk-maya -> maya
                tk-nuke -> nuke
        """
        engine_name = self._defcon_app.engine.name
        root_configs_path = self.get_root_configs_path()
        engine_configs_path = os.path.join(
            root_configs_path,
            ENGINES_DIR_NAME[engine_name]
        )

        return os.path.normpath(engine_configs_path)

    def get_config_file_path(self, config_name):
        """
        Return the path to the config file
        """
        engine_configs_path = self.get_current_engine_configs_path()
        config_file_path = os.path.join(
            engine_configs_path,
            config_name
        )

        return os.path.normpath(config_file_path)

