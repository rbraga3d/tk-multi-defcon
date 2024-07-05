import os


class DefconFileManager:
    def __init__(self, defcon_app):
        self._defcon_app = defcon_app

    def get_root_default_configs_path(self):
        """
        Returns the root default configs path
        obtained from a hook
        """
        default_configs_path = self._defcon_app.execute_hook_method(
            "hook_root_default_configs_path",
            "get_root_default_configs_path"
        )

        return default_configs_path
    
    def get_cur_engine_default_config_file_path(self):
        """
        Return the defaults config file for the
        current engine.
        """

        engine_name = self._defcon_app.engine.name
        engine_default_config_file = None

        if "maya" in engine_name:
            engine_default_config_file = self._defcon_app.get_setting(
                "maya_default_config_file"
            )

        root_default_configs_path = self.get_root_default_configs_path()
        engine_config_file_path = os.path.join(
            root_default_configs_path,
            engine_default_config_file
        )

        return os.path.normpath(engine_config_file_path)



