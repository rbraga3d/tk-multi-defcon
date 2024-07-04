# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
import os
import sys
import threading

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from .ui.dialog import Ui_Dialog

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
    app_instance.engine.show_dialog("Defcon App...", app_instance, AppDialog)


class AppDialog(QtGui.QWidget):
    """
    Main application dialog window
    """

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
        

        # logging happens via a standard toolkit logger
        logger.info("Launching Defcon Application...")


        # ============================================================================
        # BUTTON CONNECTIONS
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


    def _on_image_file_prefix_button_clicked(self):
        self._app.manager.configure_image_file_prefix()

    def _on_render_settings_button_clicked(self):
        self._app.manager.configure_common_settings()

    def _on_arnold_button_clicked(self):
        self._app.manager.configure_arnold_settings()

    def _on_redshift_button_clicked(self):
        self._app.manager.configure_redshift_settings()
