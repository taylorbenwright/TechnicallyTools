import os
import sys
from functools import partial
import maya.cmds as cmds
import maya.mel as mel
import MayaEnv.utils.sceneUtils as scene_utils
import MayaEnv.utils.transformUtils as transform_utils
import MayaEnv.ui.option_box as option_box
import MayaEnv.tools.ObjectRenamer as object_renamer
import MayaEnv.tools.MatrixConstraint as matrix_constraint
import MayaEnv.tools.HIKTransfer as hik_transfer
import MayaEnv.tools.ngSkinExporter as ngskin_exporter


_TG_MENU_ROOT = None  # Handle for the root menuItem


def append_divider(parent):
    """
    Convenience method to append a divider menuItem to the parent ui

    :param parent: The parent UI for this divider
    """
    return cmds.menuItem(parent=parent, divider=True)


def create():
    """
    Creates the "Technically Games" menu
    :return: Nothing
    :rtype: None
    """

    if not cmds.about(batch=True):
        print("Creating Menu")

        global _TG_MENU_ROOT

        maya_window = mel.eval('$TGTEMP__ = $gMainWindow')
        cmds.setParent(maya_window)

        _TG_MENU_ROOT = cmds.menu('tgMenu',
                                  label='Technically Games',
                                  tearOff=True,
                                  allowOptionBoxes=True)

        append_tools_section()
        append_rigging_section()
        append_mocap_section()
        append_utils_section()


def append_tools_section():
    section_parent = _TG_MENU_ROOT

    tools_menu = cmds.menuItem('toolsItems',
                               parent=section_parent,
                               label='Tools',
                               subMenu=True,
                               tearOff=True)

    cmds.menuItem(parent=tools_menu, divider=True, dividerLabel='Tools')

    cmds.menuItem('renameObjectsTool',
                  parent=tools_menu,
                  label='Object Renamer',
                  annotation='Robust tool for renaming objects',
                  sourceType='python',
                  command=object_renamer.create_dialog)

    cmds.menuItem('ngSkinExporter',
                  parent=tools_menu,
                  label='ngSkin Exporter',
                  annotation='Exporter for use with ngSkin layers',
                  sourceType='python',
                  command=ngskin_exporter.create_dialog)


def append_rigging_section():
    section_parent = _TG_MENU_ROOT

    rigging_menu = cmds.menuItem('riggingItems',
                                 parent=section_parent,
                                 label='Rigging',
                                 subMenu=True,
                                 tearOff=True)

    cmds.menuItem(parent=rigging_menu, divider=True, dividerLabel='Rigging Utilities')

    cmds.menuItem('makeCardinal',
                  parent=rigging_menu,
                  label='Make Rotation Cardinal',
                  annotation='Sets the rotation of all selected objects to the nearest cardinal world space rotation',
                  sourceType='python',
                  command=transform_utils.align_to_cardinal)

    cmds.menuItem('stashJointOrient',
                  parent=rigging_menu,
                  label='Stash Joint Orient',
                  annotation='Zeroes out the rotation of all selected joints and stashes the previous rotation into the joint orients',
                  sourceType='python',
                  command=transform_utils.stash_rotation_in_joint_orients)

    cmds.menuItem(parent=rigging_menu, divider=True, dividerLabel='Rigging Tools')

    cmds.menuItem('matrixConstraint',
                  parent=rigging_menu,
                  label='Matrix Constraint',
                  annotation='Creates a constraint between objects',
                  sourceType='python',
                  command=matrix_constraint.create_dialog,
                  version='2020')


def append_utils_section():
    section_parent = _TG_MENU_ROOT

    utils_menu = cmds.menuItem('utilsItems',
                               parent=section_parent,
                               label='Utilities',
                               subMenu=True,
                               tearOff=True)

    cmds.menuItem(parent=utils_menu, divider=True, dividerLabel='Node Utilities')

    cmds.menuItem('locsAtObjects',
                  parent=utils_menu,
                  label='Create Locators',
                  annotation='Creates a locator at every selected object',
                  sourceType='python',
                  command=partial(scene_utils_run, 'create_locator_at_selected_objects', 'loc', False))

    cmds.menuItem('nullsAtObjects',
                  parent=utils_menu,
                  label='Create Nulls',
                  annotation='Creates an empty transform at every selected object',
                  sourceType='python',
                  command=partial(scene_utils_run, 'create_transform_at_selected_objects', '_grp', False))

    cmds.menuItem('grpsAboveObjects',
                  parent=utils_menu,
                  label='Create Null Parents',
                  annotation='Creates an empty transform as the parent of every selected object',
                  sourceType='python',
                  command=partial(scene_utils_run, 'create_nulls_above_selected_objects', '_grp', False))

    cmds.menuItem('grpsBelowObjects',
                  parent=utils_menu,
                  label='Create Null Children',
                  annotation='Creates an empty transform as a child of every selected object',
                  sourceType='python',
                  command=partial(scene_utils_run, 'create_nulls_below_selected_objects', '_grp', False))

    cmds.menuItem('jntsAtObjects',
                  parent=utils_menu,
                  label='Create Joints at Objects',
                  annotation='Creates a joint at every selected object',
                  sourceType='python',
                  command=partial(scene_utils_run, 'create_joints_at_selected_objects', '_jnt', False, False))


def append_mocap_section():
    section_parent = _TG_MENU_ROOT

    mocap_menu = cmds.menuItem('mocapItems',
                                 parent=section_parent,
                                 label='Mocap',
                                 subMenu=True,
                                 tearOff=True)

    cmds.menuItem('xsenseHIKRetargeter',
                  parent=mocap_menu,
                  label='XSens HIK Retargeter',
                  annotation='Retarget XSense suit data onto an HIK Character',
                  sourceType='python',
                  command=hik_transfer.create_dialog,
                  version='2020')


def delete():
    """
    Removes the CG Menu from Maya
    :return: Nothing
    :rtype: None
    """
    if _TG_MENU_ROOT is not None:
        try:
            cmds.deleteUI(_TG_MENU_ROOT)
        except RuntimeError:
            pass


def scene_utils_run(*args):
    """
    :param args:
    :type args:
    :return:
    :rtype:
    """
    method_to_call = getattr(scene_utils, args[0], None)

    if method_to_call:
        method_to_call()
