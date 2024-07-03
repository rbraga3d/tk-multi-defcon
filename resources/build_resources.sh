#!/usr/bin/env bash
#
# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

# The path to output all built .py files to:
UI_PYTHON_PATH=../python/tk_multi_defcon/ui
PYTHON_2_BASE="C:/Python27"
UIC_PATH="${PYTHON_2_BASE}/Scripts"
RCC_PATH="${PYTHON_2_BASE}/Lib/site-packages/PySide"


# Helper functions to build UI files
function build_qt {
    echo " > Building " $2

    # compile ui to python
    $1 $2 > $UI_PYTHON_PATH/$3.py

    # replace PySide imports with sgtk.platform.qt imports
    sed -i $UI_PYTHON_PATH/$3.py -e "s/from PySide import/from tank.platform.qt import/g" -e "/# Created:/d" $UI_PYTHON_PATH/$3.py
}

function build_ui {
    build_qt "${PYTHON_2_BASE}/python.exe ${UIC_PATH}/pyside-uic.exe --from-imports" "$1.ui" "$1"
}

function build_res {
    build_qt "${RCC_PATH}/pyside-rcc.exe" "$1.qrc" "$1_rc"
}


# build UI's:
echo "building user interfaces..."
build_ui dialog


# build resources
echo "building resources..."
build_res resources