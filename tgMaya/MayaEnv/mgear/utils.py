"""
Contains various utilities used in the creation of mGear modules, both the rigs and guides.
"""

import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore
from mgear.core.anim_utils import reset_selected_channels_value


fk_controllers = ['shoulder_L0_ctl',
                  'arm_L0_fk0_ctl',
                  'arm_L0_fk1_ctl',
                  'arm_L0_fk2_ctl',
                  'shoulder_R0_ctl',
                  'arm_R0_fk0_ctl',
                  'arm_R0_fk1_ctl',
                  'arm_R0_fk2_ctl',
                  'thumb_L0_fk0_ctl',
                  'thumb_L0_fk1_ctl',
                  'thumb_L0_fk2_ctl',
                  'finger_L3_fk0_ctl',
                  'finger_L3_fk1_ctl',
                  'finger_L3_fk2_ctl',
                  'finger_L2_fk0_ctl',
                  'finger_L2_fk1_ctl',
                  'finger_L2_fk2_ctl',
                  'finger_L1_fk0_ctl',
                  'finger_L1_fk1_ctl',
                  'finger_L1_fk2_ctl',
                  'finger_L0_fk0_ctl',
                  'finger_L0_fk1_ctl',
                  'finger_L0_fk2_ctl',
                  'thumb_R0_fk0_ctl',
                  'thumb_R0_fk1_ctl',
                  'thumb_R0_fk2_ctl',
                  'finger_R0_fk0_ctl',
                  'finger_R0_fk1_ctl',
                  'finger_R0_fk2_ctl',
                  'finger_R1_fk0_ctl',
                  'finger_R1_fk1_ctl',
                  'finger_R1_fk2_ctl',
                  'finger_R2_fk0_ctl',
                  'finger_R2_fk1_ctl',
                  'finger_R2_fk2_ctl',
                  'finger_R3_fk0_ctl',
                  'finger_R3_fk1_ctl',
                  'finger_R3_fk2_ctl',
                  'spine_C0_fk0_ctl',
                  'spine_C0_fk1_ctl',
                  'spine_C0_fk2_ctl',
                  'spine_C0_fk3_ctl',
                  'spine_C0_fk4_ctl',
                  'leg_L0_fk0_ctl',
                  'leg_L0_fk1_ctl',
                  'leg_L0_fk2_ctl',
                  'leg_R0_fk0_ctl',
                  'leg_R0_fk1_ctl',
                  'leg_R0_fk2_ctl']


def ik_reference_groubox(title=None):
    """
    Creates the IK Reference List groupbox and the add/remove buttons, then returns the list and buttons in a tuple
    :param title: The title to give the groupbox.
    :type title:
    :return:
    :rtype:
    """
    grpbox_title = 'IK Reference Array' if title is None else title

    top_ikref_groupbox = QtWidgets.QGroupBox(grpbox_title)
    top_ikref_layout = QtWidgets.QHBoxLayout(top_ikref_groupbox)
    ikref_list = QtWidgets.QListWidget()
    ikref_list.setDragDropOverwriteMode(True)
    ikref_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
    ikref_list.setDefaultDropAction(QtCore.Qt.MoveAction)
    ikref_list.setAlternatingRowColors(True)
    ikref_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    ikref_list.setSelectionRectVisible(False)
    top_ikref_layout.addWidget(ikref_list)

    top_ikbuts_layout = QtWidgets.QVBoxLayout()
    ikref_add_but = QtWidgets.QPushButton('<<')
    ikref_remove_but = QtWidgets.QPushButton('>>')
    top_ikref_but_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
    top_ikbuts_layout.addWidget(ikref_add_but)
    top_ikbuts_layout.addWidget(ikref_remove_but)
    top_ikbuts_layout.addItem(top_ikref_but_spacer)
    top_ikref_layout.addLayout(top_ikbuts_layout)

    return top_ikref_groupbox, ikref_list, ikref_add_but, ikref_remove_but


"""
Below here is a bunch of Anim Picker scripts. These are not really full scripts and are only intended for use in the 
Anim Picker tool.

# Variable reference for custom script execution on pickers.
# Use the following variables in your code to access related data:
# __CONTROLS__ for picker item associated controls (will return sets and not content).
# __FLATCONTROLS__ for associated controls and control set content.
# __NAMESPACE__ for current picker namespace
# __INIT__ use 'if not' statement to avoid code execution on creation.
# __SELF__ to get access to the PickerItem() instace. (Change color, size, etc)

"""

# if not __INIT__:
#     import maya.cmds as cmds
#
#     for ctl in __FLATCONTROLS__:
#         cmds.xform(ctl, t=[0,0,0], ro=[0,0,0], s=[1,1,1], ws=False)


def select_rig_controllers():
    fk_controllers = ['*:shoulder_L0_ctl',
                      '*:arm_L0_fk0_ctl',
                      '*:arm_L0_fk1_ctl',
                      '*:arm_L0_fk2_ctl',
                      '*:shoulder_R0_ctl',
                      '*:arm_R0_fk0_ctl',
                      '*:arm_R0_fk1_ctl',
                      '*:arm_R0_fk2_ctl',
                      '*:thumb_L0_fk0_ctl',
                      '*:thumb_L0_fk1_ctl',
                      '*:thumb_L0_fk2_ctl',
                      '*:finger_L3_fk0_ctl',
                      '*:finger_L3_fk1_ctl',
                      '*:finger_L3_fk2_ctl',
                      '*:finger_L2_fk0_ctl',
                      '*:finger_L2_fk1_ctl',
                      '*:finger_L2_fk2_ctl',
                      '*:finger_L1_fk0_ctl',
                      '*:finger_L1_fk1_ctl',
                      '*:finger_L1_fk2_ctl',
                      '*:finger_L0_fk0_ctl',
                      '*:finger_L0_fk1_ctl',
                      '*:finger_L0_fk2_ctl',
                      '*:thumb_R0_fk0_ctl',
                      '*:thumb_R0_fk1_ctl',
                      '*:thumb_R0_fk2_ctl',
                      '*:finger_R0_fk0_ctl',
                      '*:finger_R0_fk1_ctl',
                      '*:finger_R0_fk2_ctl',
                      '*:finger_R1_fk0_ctl',
                      '*:finger_R1_fk1_ctl',
                      '*:finger_R1_fk2_ctl',
                      '*:finger_R2_fk0_ctl',
                      '*:finger_R2_fk1_ctl',
                      '*:finger_R2_fk2_ctl',
                      '*:finger_R3_fk0_ctl',
                      '*:finger_R3_fk1_ctl',
                      '*:finger_R3_fk2_ctl',
                      '*:spine_C0_fk0_ctl',
                      '*:spine_C0_fk1_ctl',
                      '*:spine_C0_fk2_ctl',
                      '*:spine_C0_fk3_ctl',
                      '*:spine_C0_fk4_ctl',
                      '*:leg_L0_fk0_ctl',
                      '*:leg_L0_fk1_ctl',
                      '*:leg_L0_fk2_ctl',
                      '*:leg_R0_fk0_ctl',
                      '*:leg_R0_fk1_ctl',
                      '*:leg_R0_fk2_ctl']

    cmds.select(fk_controllers)


def select_rig_bones():
    jnts = ['*:spine_01',
            '*:spine_02',
            '*:spine_03',
            '*:spine_04',
            '*:spine_05',
            '*:spine_06',
            '*:clavicle_L',
            '*:upperarm_L',
            '*:forearm_L',
            '*:hand_L',
            '*:spine_01',
            '*:spine_02',
            '*:spine_03',
            '*:spine_04',
            '*:spine_05',
            '*:spine_06',
            '*:clavicle_L',
            '*:upperarm_L',
            '*:forearm_L',
            '*:hand_L',
            '*:pointer_L_01',
            '*:pointer_L_02',
            '*:pointer_L_03',
            '*:middle_L_01',
            '*:middle_L_02',
            '*:middle_L_03',
            '*:ring_L_01',
            '*:ring_L_02',
            '*:ring_L_03',
            '*:pinky_L_01',
            '*:pinky_L_02',
            '*:pinky_L_03',
            '*:clavicle_R',
            '*:upperarm_R',
            '*:forearm_R',
            '*:hand_R',
            '*:spine_01',
            '*:spine_02',
            '*:spine_03',
            '*:spine_04',
            '*:spine_05',
            '*:spine_06',
            '*:clavicle_L',
            '*:upperarm_L',
            '*:forearm_L',
            '*:hand_L',
            '*:pointer_L_01',
            '*:pointer_L_02',
            '*:pointer_L_03',
            '*:middle_L_01',
            '*:middle_L_02',
            '*:middle_L_03',
            '*:ring_L_01',
            '*:ring_L_02',
            '*:ring_L_03',
            '*:pinky_L_01',
            '*:pinky_L_02',
            '*:pinky_L_03',
            '*:clavicle_R',
            '*:upperarm_R',
            '*:forearm_R',
            '*:hand_R',
            '*:pointer_R_01',
            '*:pointer_R_02',
            '*:pointer_R_03',
            '*:middle_R_01',
            '*:middle_R_02',
            '*:middle_R_03',
            '*:ring_R_01',
            '*:ring_R_02',
            '*:ring_R_03',
            '*:pinky_R_01',
            '*:pinky_R_02',
            '*:pinky_R_03',
            '*:weapon_R',
            '*:thigh_L',
            '*:calf_L',
            '*:foot_L',
            '*:ball_L',
            '*:thigh_R',
            '*:calf_R',
            '*:foot_R',
            '*:ball_R']

    cmds.select(jnts)
