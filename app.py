from sgtk.platform import Application
from pprint import pprint

class DefConApp(Application):
    """
    The app entry point. This class is responsible for initializing and tearing down
    the application, handle menu registration etc.
    """

    def init_app(self):
        """
        Called as the application is being initialized
        """

        # first, we use the special import_module command to access the app module
        # that resides inside the python folder in the app. This is where the actual UI
        # and business logic of the app is kept. By using the import_module command,
        # toolkit's code reload mechanism will work properly.
        defcon_module = self.import_module("tk_multi_defcon")
        self._manager = defcon_module.manager.DefConManager(self)


        # now register a *command*, which is normally a menu entry of some kind on a Shotgun
        # menu (but it depends on the engine). The engine will manage this command and
        # whenever the user requests the command, it will call out to the callback.

        # first, set up our callback, calling out to a method inside the app module contained
        # in the python folder of the app
        menu_callback = lambda: defcon_module.dialog.show_dialog(self)

        # now register the command with the engine
        self.engine.register_command("Defcon Settings...", menu_callback)



        file_path = self.execute_hook_method(
            "hook_root_configs_path",
            "get_root_configs_path"
        )

        pprint("ROOT PATH = " + file_path)



        
