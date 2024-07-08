import urllib.request
from pprint import pprint
import maya.cmds as cmds
import maya.mel as mel

from tank_vendor import yaml

from .constants import (
    ENTITY_DEFAULTCONFIG,
    ARNOLD_PLUGIN,
    REDSHIFT_PLUGIN
)
from .file_manager import DefconFileManager
from .utils import resolve_image_file_prefix


class DefConManager:

    _SG_ENGINE_CONFIG_FILE_FIELDS = {
        "tk-maya": "sg_maya_config_file"
    }

    def __init__(self, defcon_app):
        self._defcon_app = defcon_app
        self._engine = self._defcon_app.engine
        self._context = self._defcon_app.engine.context
        self._shotgun = self._defcon_app.shotgun
        self._file_manager = DefconFileManager(self._defcon_app)
        self._default_config_data = self.get_cur_engine_default_config_from_shotgun()


    def get_cur_engine_default_config_file_path(self):
        return self._file_manager.get_cur_engine_default_config_file_path()
    

    def get_cur_engine_default_config(self):
        """
        Returns the current engine defaults config
        return type: dict
        """
        default_config_file_path = self._file_manager.get_cur_engine_default_config_file_path()

        try:
            with open(default_config_file_path, 'r') as default_config_file:
                return yaml.safe_load(default_config_file)
            
        except FileNotFoundError:
            self._defcon_app.log_error(
                "Default config file not found: {}. "
                "Defcon will be skiped."
                .format(default_config_file_path)
                
            )

        return


    def get_cur_engine_default_config_from_shotgun(self):
        """
        Returns the data from the default config file uplodaded 
        to shotgun DefaultConfig entity, we don't need to download the
        config file and can use the configuration directly.

        return type: dict or None

        """

        sg_engine_config_file_field = self._SG_ENGINE_CONFIG_FILE_FIELDS[
            self._engine.name
        ]
    
        project_id = self._context.project['id']

        filters = [
            ['project', 'is', {'type': 'Project', 'id': project_id}]
        ]

        fields = [
            "project",
            sg_engine_config_file_field
        ]

        
        # let's try to retrieve Default Config entity data
        try:
            data = self._shotgun.find_one(ENTITY_DEFAULTCONFIG, filters, fields)

        except Exception as e:
            self._defcon_app.log_error(
            "Default config not loaded from shotgun site"
            "Defcon will be skiped. Error: {}"
            .format(e)
            
            )

            return
        
        # check data
        if data == None:
            self._defcon_app.log_error(
                "Couldn't find Default Config entity data. "
                "Please check if there's any Default Config associated"
                "with the current project in the shotgun site."
                "Defcon will be skipped."
            )

            return


        # check if there's an uplodaded config file
        if not data[sg_engine_config_file_field]:
            self._defcon_app.log_error(
                "No configuration file uploaded to the current engine."
                "Please upload a valid configuration file and try again."
                "Defcon will be skipped."
            )

            return

        # check if uplodaded file is a yaml file
        file_name = data[sg_engine_config_file_field]['name']
        file_extension = file_name.split('.')[-1]

        if file_extension not in ["yml", "yaml"]:
            self._defcon_app.log_error(
                "Configuration file is not a YAML file. "
                "Please upload a YAML file and try again."
                "Defcon will be skipped."
            )

            return

        
        # we will use requests to get the default config file data
        # directly from the shotgun site
        file_url = data[sg_engine_config_file_field]['url']
        response = urllib.request.urlopen(file_url)

        # check request response
        if response.status != 200:
            self._defcon_app.log_warning(
                "Default config not loaded from shotgun site"
                "Defcon will be skiped. Status code: {}"
                .format(response.status_code)
            )

            return 

        content = response.read().decode("utf-8")
        config = yaml.safe_load(content)

        return config

    
    def get_stringed_config(self):
        return yaml.dump(
            self._default_config_data,
            default_flow_style=False,
            sort_keys=False,
            indent=6
        )

    def _log_warning_no_settings_found(self, settings_name):
        self._defcon_app.log_warning(
            "No {} settings found in the default config file. "
            "Defcon for common settings will be skipped."
            .format(settings_name)
        )

    
class MayaDefConManager(DefConManager):

    # keys defined in the render_settings.yaml file
    _COMMOM_SETTINGS_NAME = "common"
    _ARNOLD_SETTINGS_NAME = "arnold"
    _REDSHIFT_SETTINGS_NAME = "redshift"

    def __init__(self, defcon_app):
        super(MayaDefConManager, self).__init__(defcon_app)
        self._loaded_plugins = cmds.pluginInfo(query=True, listPlugins=True )



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


    def _configure_settings(self, settings_name):
        settings = self._default_config_data.get(settings_name)

        if not settings:
            self._log_warning_no_settings_found(settings_name)
            return
        

        # Remove the imageFilePrefix attribute from the common settings
        # configuration because we will configure it separetely
        if settings_name == self._COMMOM_SETTINGS_NAME:
            settings["defaultRenderGlobals"]["defaults"].pop(
                "imageFilePrefix"
            )

        self._configure_settings_attributes(settings)


    def configure_image_file_prefix(self):
        """
        Configure the image file prefix in the common render globals
        tab.
        """
        common_settings = self._default_config_data.get(
            self._COMMOM_SETTINGS_NAME
        )

        default_render_globals = common_settings.get("defaultRenderGlobals")
        image_file_prefix_value = default_render_globals["defaults"]["imageFilePrefix"]

        full_attr_name = "defaultRenderGlobals.imageFilePrefix"

        resolved_prefix = resolve_image_file_prefix(
            self._engine,
            image_file_prefix_value
        )

        try:

            cmds.setAttr(
                full_attr_name,
                resolved_prefix,
                type="string"
            )

        except Exception as e:
            self._defcon_app.log_error(
                "Could not set {} attribute. "
                "Error: {}"
                .format(full_attr_name, e)
            )


    def configure_common_settings(self):
        self._configure_settings(self._COMMOM_SETTINGS_NAME)


    def configure_redshift_settings(self):
        if REDSHIFT_PLUGIN not in self._loaded_plugins:
            self._defcon_app.log_warning(
                "Redshift plugin ({}) not loaded. "
                "Defcon for Redshift will be skipped."
                .format(REDSHIFT_PLUGIN)
            )
            return
        
        self._configure_settings(self._REDSHIFT_SETTINGS_NAME)


    def configure_arnold_settings(self):
        if ARNOLD_PLUGIN not in self._loaded_plugins:
            self._defcon_app.log_warning(
                "Arnold ({}) plugin not loaded. "
                "Defcon for Arnold will be skipped."
                .format(ARNOLD_PLUGIN)

            )
            return
        
        self._configure_settings(self._ARNOLD_SETTINGS_NAME)


    def configure_vray_settings(self):
        # TODO: Implement vray settings
        pass


    def configure_all_render_settings(self):

        # Common settings
        self.configure_common_settings()

        # Arnold settings
        self.configure_arnold_settings()

        # Redshift settings
        self.configure_redshift_settings()



def create_defcon_manager(defcon_app):
    """
    Create a defcon manager based on the current engine
    """
    engine_name = defcon_app.engine.name

    # Maya defcon manager
    if "maya" in engine_name:
        return MayaDefConManager(defcon_app)

