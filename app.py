from sgtk.platform import Application


class DefConApp(Application):
    """
    The app entry point. This class is responsible for initializing and tearing down
    the application, handle menu registration etc.
    """


    def init_app(self):
        """
        Called as the application is being initialized
        """

        defcon_module = self.import_module("tk_multi_defcon")
        self._manager = defcon_module.manager.create_defcon_manager(self)


        # maya's menu callback
        #menu_callback = lambda: defcon_module.dialog.show_dialog(self)

        # now register the command with the engine
        #self.engine.register_command("Defcon Settings...", menu_callback)




        
