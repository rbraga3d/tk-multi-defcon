import os

import sgtk

DEFCON_ROOT_CONFIGS_DIR = "config/studio/defcon"

class DefConRootFilePath(sgtk.Hook):
    
    def get_root_default_configs_path(self):
        path = os.path.join(
            os.environ["TANK_CURRENT_PC"],
            DEFCON_ROOT_CONFIGS_DIR
        )

        return os.path.normpath(path)


    