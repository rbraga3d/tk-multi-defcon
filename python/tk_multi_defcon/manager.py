from pprint import pprint

import maya.cmds as cmds
import maya.mel as mel

from tank_vendor import yaml

from .constants import (
    RENDER_SETTINGS_CONFIG_FILE,
    ARNOLD_PLUGIN,
    REDSHIFT_PLUGIN
)
from .file_manager import DefconFileManager


class DefConManager:
    def __init__(self, defcon_app):
        self._defcon_app = defcon_app
        self._engine = self._defcon_app.engine
        self._file_manager = DefconFileManager(self._defcon_app)


    def _get_config(self, config_name):
        """
        Returns the config for the given config name
        return type: dict
        """
        config_path = self._file_manager.get_config_file_path(config_name)

        try:
            with open(config_path, 'r') as config_file:
                return yaml.safe_load(config_file)
            
        except FileNotFoundError:
            self._defcon_app.log_error(
                "Config file not found: {}. "
                "Defcon for {} will be skipped"
                .format(config_path, config_name.split(".")[0].upper())
                
            )

        return {}
    
    def _log_warning_no_settings_found(self, settings_name, config_name):
        self._defcon_app.log_warning(
            "No {} settings found in the {} file. "
            "Defcon for common settings will be skipped."
            .format(settings_name, config_name)
        )

    
class MayaDefConManager(DefConManager):

    # keys defined in the render_settings.yaml file
    _COMMOM_SETTINGS_NAME = "common"
    _ARNOLD_SETTINGS_NAME = "arnold"
    _REDSHIFT_SETTINGS_NAME = "redshift"

    def __init__(self, defcon_app):
        super(MayaDefConManager, self).__init__(defcon_app)
        self._loaded_plugins = cmds.pluginInfo(query=True, listPlugins=True )

        render_settings_config = self._get_config(RENDER_SETTINGS_CONFIG_FILE)
        self.configure_all_render_settings(render_settings_config)




    def _configure_settings_attributes(self, settings):
        for key, value in settings.items():
            attributes_prefix = key
            attributes_settings = value

            defaults_attributes = attributes_settings.get("defaults", {})
            connections_attributes = attributes_settings.get("connections", {})
            others_attributes = attributes_settings.get("others", {})

            # ========================================================
            # DEFAULTS ATTRIBUTES
            # ========================================================
            for attr_name, attr_value in defaults_attributes.items():
                full_attr_name = "{}.{}".format(attributes_prefix, attr_name)
                
                try:
                    if type(attr_value) == str:
                        # we need to pass the type arg because the
                        # attribute value type is a string
                        cmds.setAttr(full_attr_name, attr_value, type="string")
                        continue

                    cmds.setAttr(full_attr_name, attr_value)
                except Exception as e:
                    self._defcon_app.log_error(
                        "Could not set {} attribute. "
                        "Error: {}"
                        .format(full_attr_name, e)
                    )

            # ========================================================
            # CONNECTIONS ATTRIBUTES
            # ========================================================
            for attr_name, attr_value in connections_attributes.items():
                full_attr_name = "{}.{}".format(attributes_prefix, attr_name)

                try:
                    cmds.connectAttr(full_attr_name, attr_value, f=True)
                    continue
                except Exception as e:
                    self._defcon_app.log_error(
                        "Could not connect {} attribute. "
                        "Error: {}"
                        .format(full_attr_name, e)
                    )

            # ========================================================
            # OTHERS ATTRIBUTES
            # ========================================================
            # We need to set some attributes differently as their
            # values are set up using maya mel procedurals
            for attr_name, attr_value in others_attributes.items():
                try:
                    # Frame/Animation ext:
                    if attr_name == "setMayaSoftwareFrameExt":
                        mel.eval(
                            'setMayaSoftwareFrameExt("{}", 0)'.format(attr_value)
                        )

                        continue
                except Exception as e:
                    self._defcon_app.log_error(
                        "Could not set {} attribute. "
                        "Error: {}"
                        .format(attr_name, e)
                    )


    def _configure_settings(self, settings_name, config):
        settings = config.get(settings_name)
        if not settings:
            self._log_warning_no_settings_found(
                settings_name,
                RENDER_SETTINGS_CONFIG_FILE
            )
            return
        
        self._configure_settings_attributes(settings)

    def configure_common_settings(self, config):
        self._configure_settings(self._COMMOM_SETTINGS_NAME, config)


    def configure_redshift_settings(self, config):
        if REDSHIFT_PLUGIN not in self._loaded_plugins:
            self._defcon_app.log_warning(
                "Redshift plugin ({}) not loaded. "
                "Defcon for Redshift will be skipped."
                .format(REDSHIFT_PLUGIN)
            )
            return
        
        self._configure_settings(self._REDSHIFT_SETTINGS_NAME, config)


    def configure_arnold_settings(self, config):
        if ARNOLD_PLUGIN not in self._loaded_plugins:
            self._defcon_app.log_warning(
                "Arnold ({}) plugin not loaded. "
                "Defcon for Arnold will be skipped."
                .format(ARNOLD_PLUGIN)

            )
            return
        
        self._configure_settings(self._ARNOLD_SETTINGS_NAME, config)


    def configure_vray_settings(self, config):
        # TODO: Implement vray settings
        pass


    def configure_all_render_settings(self, config):

        # Common settings
        self.configure_common_settings(config)

        # Arnold settings
        self.configure_arnold_settings(config)

        # Redshift settings
        self.configure_redshift_settings(config)



def create_defcon_manager(defcon_app):
    """
    Create a defcon manager based on the current engine
    """
    engine_name = defcon_app.engine.name

    # Maya defcon manager
    if engine_name == "tk-maya":
        return MayaDefConManager(defcon_app)

