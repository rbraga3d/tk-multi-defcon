import os

import sgtk

DEFCON_ROOT_CONFIGS_PATH = "code/defcon"

class DefConRootFilePath(sgtk.Hook):
    
    def get_root_configs_path(self):
        app = self.parent
        context = app.engine.context
        sg_project_root_path = context._get_project_roots()[0] # didnt find other method to get the sg project root

        path = os.path.join(
            sg_project_root_path,
            DEFCON_ROOT_CONFIGS_PATH
        )

        return os.path.normpath(path)


    