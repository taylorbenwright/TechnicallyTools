"""
Utility functions for working with HIK in Maya.

Working with HIK is a pain. There is no proper API for it. Much of the guts are in MEL, and thus we need to call
mel.eval a lot. Further, the HIK UI needs to be visible for some of this to work.
"""

import maya.cmds as cmds
import maya.mel as mel
import os


def read_scripts():
    """
    We need to read in these scripts in case they aren't already in memory.
    :return: Nothing
    :rtype: None
    """
    MAYA_LOCATION = os.environ['MAYA_LOCATION']
    mel.eval('source "' + MAYA_LOCATION + '/scripts/others/hikGlobalUtils.mel"')
    mel.eval('source "' + MAYA_LOCATION + '/scripts/others/hikCharacterControlsUI.mel"')
    mel.eval('source "' + MAYA_LOCATION + '/scripts/others/hikDefinitionOperations.mel"')


def set_character(character_name):
    """
    Sets the Character on the current HIK Character
    :param character_name: The name of the character to set the Character to
    :type character_name: str
    :return: Nothing
    :rtype: None
    """
    mel.eval("HIKCharacterControlsTool;")

    read_scripts()

    all_chars = cmds.optionMenuGrp("hikCharacterList", query=True, itemListLong=True)

    for ind, item in enumerate(all_chars):
        option_menu = "hikCharacterList|OptionMenu"
        char = cmds.menuItem(item, query=True, label=True)
        if char == (' {}'.format(char)):
            cmds.optionMenu(option_menu, edit=True, select=ind+1)
            break

    mel.eval('global string $gHIKCurrentCharacter = "{}";'.format(character_name))
    mel.eval('hikUpdateCurrentSourceFromUI()')
    mel.eval('hikUpdateContextualUI()')
    mel.eval('hikControlRigSelectionChangedCallback')


def set_source_on_character(character_name, source_name):
    """
    Sets the Source on the current HIK Character
    :param character_name: The name of the character to set the source on
    :type character_name: str
    :param source_name: The name of the HIK character to set as Source
    :type source_name: str
    :return: Nothing
    :rtype: None
    """
    mel.eval("HIKCharacterControlsTool;")

    read_scripts()

    all_source_chars = cmds.optionMenuGrp("hikSourceList", query=True, itemListLong=True)

    for ind, item in enumerate(all_source_chars):
        option_menu = "hikSourceList|OptionMenu"
        source_char = cmds.menuItem(item, query=True, label=True)

        if source_char == (' {}'.format(source_name)):
            cmds.optionMenu(option_menu, edit=True, select=ind+1)
            break

    mel.eval('global string $gHIKCurrentCharacter = "{}";'.format(character_name))
    mel.eval('hikUpdateCurrentSourceFromUI()')
    mel.eval('hikUpdateContextualUI()')
    mel.eval('hikControlRigSelectionChangedCallback')


def bake_current_character():
    """
    Bakes the currently-active HIK character
    :return: Nothing
    :rtype: None
    """
    mel.eval('hikBakeCharacter 0;')
    mel.eval('hikSetCurrentSourceFromCharacter(hikGetCurrentCharacter());')
    mel.eval('hikUpdateSourceList;')
    mel.eval('hikUpdateContextualUI;')
