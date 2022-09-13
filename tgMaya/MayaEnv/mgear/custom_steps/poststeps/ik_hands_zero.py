import maya.cmds as cmds
import mgear.shifter.custom_step as cstp


class CustomShifterStep(cstp.customShifterMainStep):
    def __init__(self):
        self.name = "IK Hands Zero"

    def run(self, stepDict):
        print('Fixing IK Hand transforms...')

        ik_l_hand_parent = stepDict["mgearRun"].components["arm_L0"].ik_cns.longName()
        ik_l_hand_ctl = stepDict["mgearRun"].components["arm_L0"].ik_ctl.longName()
        ik_r_hand_parent = stepDict["mgearRun"].components["arm_R0"].ik_cns.longName()
        ik_r_hand_ctl = stepDict["mgearRun"].components["arm_R0"].ik_ctl.longName()

        ik_l_ctl_ws_xform = cmds.xform(ik_l_hand_ctl, q=True, m=True, ws=True)
        l_hand_zero = cmds.createNode('transform', n='arm_L0_ctl_zero')
        cmds.xform(l_hand_zero, m=ik_l_ctl_ws_xform, ws=True)
        cmds.parent(l_hand_zero, ik_l_hand_parent)
        cmds.parent(ik_l_hand_ctl, l_hand_zero)

        ik_r_ctl_ws_xform = cmds.xform(ik_r_hand_ctl, q=True, m=True, ws=True)
        r_hand_zero = cmds.createNode('transform', n='arm_R0_ctl_zero')
        cmds.xform(r_hand_zero, m=ik_r_ctl_ws_xform, ws=True)
        cmds.parent(r_hand_zero, ik_r_hand_parent)
        cmds.parent(ik_r_hand_ctl, r_hand_zero)

        print('IK Hand Transforms fixed.')
