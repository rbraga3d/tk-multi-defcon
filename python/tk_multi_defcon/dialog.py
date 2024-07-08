# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.



import maya.cmds as cmds
import sgtk
# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from .ui.dialog import Ui_Dialog
from .manager import create_defcon_manager


# standard toolkit logger
logger = sgtk.platform.get_logger(__name__)


def show_dialog(app_instance):
    """
    Shows the main dialog window.
    """
    # in order to handle UIs seamlessly, each toolkit engine has methods for launching
    # different types of windows. By using these methods, your windows will be correctly
    # decorated and handled in a consistent fashion by the system.

    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    app_instance.engine.show_dialog("DefCon", app_instance, AppDialog)


class AppDialog(QtGui.QWidget):
    """
    Main application dialog window
    """
    _RENDER_SETTINGS_TAB_WIDTH = 450
    _CONFIGS_TAB_WIDTH = 780

    def __init__(self):
        """
        Constructor
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)

        # now load in the UI that was created in the UI designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)


        self._app = sgtk.platform.current_bundle()
        self._app.manager = create_defcon_manager(self._app)
        

        # logging happens via a standard toolkit logger
        logger.info("Launching Defcon Application...")

        # ============================================================================
        # TABS
        # ============================================================================
        self.ui.main_tab_widget.setTabText(0, "Render Settings")
        self.ui.main_tab_widget.setTabText(1, "Configs")

        self.ui.main_tab_widget.currentChanged.connect(self._on_tab_changed) 

        # ============================================================================
        # LABELS
        # ============================================================================
        self.ui.config_file_label.setText(
            "Config file: {}".format(
                self._app.manager.get_cur_engine_default_config_file_path()
            )
        )
        

        # ============================================================================
        # PLAINT TEXT
        # ============================================================================
        self.ui.configs_plaint_text.setPlainText(
            self._app.manager.get_stringed_config()
        )

        # ============================================================================
        # BUTTONS
        # ============================================================================
        self.ui.config_image_file_prefix_button.clicked.connect(
            self._on_image_file_prefix_button_clicked
        )

        self.ui.config_render_settings_button.clicked.connect(
            self._on_render_settings_button_clicked
        )

        self.ui.config_arnold_button.clicked.connect(
            self._on_arnold_button_clicked
        )

        self.ui.config_redshift_button.clicked.connect(
            self._on_redshift_button_clicked
        )

        if cmds.file(query=True, sn=True):
            # we will enable this button only if the scene has been saved
            # so we can get the file name to use for the image file prefix
            # confi
            self.ui.config_image_file_prefix_button.setEnabled(True)
        else:
            # set a tool tip for the disabled button
            self.ui.config_image_file_prefix_button.setToolTip(
                "Please save your scene to enable this button."
            )


    def _on_tab_changed(self, index):
        window = self.window()
        window_height = window.height()
        if index == 0:
            window.resize(self._RENDER_SETTINGS_TAB_WIDTH, window_height)
        elif index == 1:
            window.resize(self._CONFIGS_TAB_WIDTH, window_height)
        

    def _on_image_file_prefix_button_clicked(self):
        if not self._can_override("Image File Prefix"):
            return
        
        self._app.manager.configure_image_file_prefix()

    def _on_render_settings_button_clicked(self):
        if not self._can_override("Render Common"):
            return
        
        self._app.manager.configure_common_settings()

    def _on_arnold_button_clicked(self):
        if not self._can_override("Arnold"):
            return
        
        self._app.manager.configure_arnold_settings()

    def _on_redshift_button_clicked(self):
        if not self._can_override("Redshift"):
            return
        
        self._app.manager.configure_redshift_settings()


    def _show_override_warning_message(self, settings_to_override):
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Warning)
        msg.setText("ATTENTION!")
        msg.findChild(QtGui.QLabel, "qt_msgbox_label").setFixedWidth(250)
        msg.setInformativeText("This will override current {} settings!".format(
            settings_to_override
            )
        )

        msg.setWindowTitle("Override Settings?")
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        
        return msg.exec()
    

    def _can_override(self, settings_to_override):
        button_clicked = self._show_override_warning_message(
            settings_to_override
        )

        return True if button_clicked == QtGui.QMessageBox.Ok else False