"""
Called each time Maya is opened. Sets up our menus and units
"""

import maya.cmds as cmds
import maya.utils as mutils


def execute():
    """
    Ensure the Maya GUI has fully loaded before kicking off our startup routine
    :return: Nothing
    """
    if cmds.about(batch=True):
        initialize()
    else:
        mutils.executeDeferred(initialize)


def initialize():
    """
    Initializes everything needed for a Maya session, ie. menues, marking menues, shelves, etc
    :return: Nothing
    """
    import MayaEnv.ui.main_menu as main_menu

    main_menu.create()

    if cmds.currentUnit(q=True, t=True) != 'ntsc':
        cmds.currentUnit(t='ntsc')
