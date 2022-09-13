import maya.cmds as cmds
import maya.api.OpenMaya as om2
import mgear.shifter.custom_step as cstp


def get_node_from_str(node_name):
    """
    Returns the MObject for the given node if it exists
    :param node_name: The name of the node to query
    :type node_name: str
    :rtype: om2.MObject
    """
    sel = om2.MSelectionList()
    try:
        sel.add(node_name)
    except:
        return None

    return sel.getDependNode(0)


def get_cog_offset(parent, child):
    parent_world_mat = om2.MDagPath.getAPathTo(get_node_from_str(parent)).inclusiveMatrix()  # type: om2.MMatrix
    child_world_mat = om2.MDagPath.getAPathTo(get_node_from_str(child)).inclusiveMatrix()  # type: om2.MMatrix

    return child_world_mat * parent_world_mat.inverse()  # type: om2.MMatrix


class CustomShifterStep(cstp.customShifterMainStep):
    def __init__(self):
        self.name = "Root Controller Setup"

    def run(self, stepDict):
        """Run method.

            i.e:  stepDict["mgearRun"].global_ctl  gets the global_ctl from
                    shifter rig build bas
            i.e:  stepDict["mgearRun"].components["control_C0"].ctl  gets the
                    ctl from shifter component called control_C0
            i.e:  stepDict["otherCustomStepName"].ctlMesh  gets the ctlMesh
                    from a previous custom step called "otherCustomStepName"
        Arguments:
            stepDict (dict): Dictionary containing the objects from
                the previous steps

        Returns:
            None: None
        """
        print('Setting up Root Controller scheme...')

        world_ctl_name = stepDict["mgearRun"].global_ctl.longName()
        local_ctl_name = stepDict["mgearRun"].components["local_C0"].ctl.longName()
        global_ctl_name = stepDict["mgearRun"].components["global_C0"].ctl.longName()

        root_root_name = stepDict["mgearRun"].components["root_C0"].root.longName()
        cmds.parent(root_root_name, '|rig')

        root_ik_cns_name = stepDict["mgearRun"].components["root_C0"].ik_cns.longName()
        root_ctl_name = stepDict["mgearRun"].components["root_C0"].ctl.longName()

        root_ctl_children = cmds.listRelatives(root_ctl_name, c=True, ni=True, s=False, pa=True, typ='transform')
        for child in root_ctl_children:
            cmds.parent(child, local_ctl_name)

        cog_ctl_name = stepDict["mgearRun"].components["cog_C0"].ctl.longName()


        ###
        cmds.addAttr('{}'.format(root_ctl_name), at='enum', en="COG:Local:Global:World:", ln='control_ikref',
                     nn='Ik Ref', k=True)
        # cmds.addAttr('{}.control_ikref'.format(root_ctl_name), e=True, en="COG:Local:Global:World:")
        cmds.addAttr('{}'.format(root_ctl_name), ln='LimitTransX', at='bool', k=True)
        cmds.addAttr('{}'.format(root_ctl_name), ln='LimitTransY', at='bool', k=True)
        cmds.addAttr('{}'.format(root_ctl_name), ln='LimitTransZ', at='bool', k=True)
        cmds.addAttr('{}'.format(root_ctl_name), ln='LimitRotateX', at='bool', k=True)
        cmds.addAttr('{}'.format(root_ctl_name), ln='LimitRotateY', at='bool', k=True)
        cmds.addAttr('{}'.format(root_ctl_name), ln='LimitRotateZ', at='bool', k=True)

        ###
        decomp_node = cmds.createNode('decomposeMatrix', name='root_controller_decomp')
        cond_01 = cmds.createNode('condition', name='root_cond_01')
        cond_02 = cmds.createNode('condition', name='root_cond_02')
        cond_03 = cmds.createNode('condition', name='root_cond_03')
        cond_04 = cmds.createNode('condition', name='root_cond_04')
        wt_add_mat = cmds.createNode('wtAddMatrix', name='root_space_add_mat')
        cog_offset_mat_mult = cmds.createNode('multMatrix', name='root_cog_offet_mult_mat')
        space_mult_mat = cmds.createNode('multMatrix', name='root_space_mult_mat')

        trans_x_cond = cmds.createNode('floatCondition', name='root_trans_x_cond')
        trans_y_cond = cmds.createNode('floatCondition', name='root_trans_y_cond')
        trans_z_cond = cmds.createNode('floatCondition', name='root_trans_z_cond')
        rot_x_cond = cmds.createNode('floatCondition', name='root_rot_x_cond')
        rot_y_cond = cmds.createNode('floatCondition', name='root_rot_y_cond')
        rot_z_cond = cmds.createNode('floatCondition', name='root_rot_z_cond')

        ###
        cmds.connectAttr('{}.control_ikref'.format(root_ctl_name), '{}.firstTerm'.format(cond_01))
        cmds.setAttr('{}.colorIfTrueR'.format(cond_01), 1)
        cmds.setAttr('{}.colorIfFalseR'.format(cond_01), 0)

        cmds.connectAttr('{}.control_ikref'.format(root_ctl_name), '{}.firstTerm'.format(cond_02))
        cmds.setAttr('{}.secondTerm'.format(cond_02), 1)
        cmds.setAttr('{}.colorIfTrueR'.format(cond_02), 1)
        cmds.setAttr('{}.colorIfFalseR'.format(cond_02), 0)

        cmds.connectAttr('{}.control_ikref'.format(root_ctl_name), '{}.firstTerm'.format(cond_03))
        cmds.setAttr('{}.secondTerm'.format(cond_03), 2)
        cmds.setAttr('{}.colorIfTrueR'.format(cond_03), 1)
        cmds.setAttr('{}.colorIfFalseR'.format(cond_03), 0)

        cmds.connectAttr('{}.control_ikref'.format(root_ctl_name), '{}.firstTerm'.format(cond_04))
        cmds.setAttr('{}.secondTerm'.format(cond_04), 3)
        cmds.setAttr('{}.colorIfTrueR'.format(cond_04), 1)
        cmds.setAttr('{}.colorIfFalseR'.format(cond_04), 0)

        ###
        cog_offset_mat = get_cog_offset(cog_ctl_name, root_ctl_name)

        cmds.setAttr('{}.matrixIn[0]'.format(cog_offset_mat_mult), list(cog_offset_mat), type="matrix")
        cmds.connectAttr('{}.worldMatrix[0]'.format(cog_ctl_name), '{}.matrixIn[1]'.format(cog_offset_mat_mult))

        ###
        cmds.connectAttr('{}.matrixSum'.format(cog_offset_mat_mult), '{}.wtMatrix[0].matrixIn'.format(wt_add_mat))
        cmds.connectAttr('{}.outColorR'.format(cond_01), '{}.wtMatrix[0].weightIn'.format(wt_add_mat))

        cmds.connectAttr('{}.worldMatrix[0]'.format(local_ctl_name), '{}.wtMatrix[1].matrixIn'.format(wt_add_mat))
        cmds.connectAttr('{}.outColorR'.format(cond_02), '{}.wtMatrix[1].weightIn'.format(wt_add_mat))

        cmds.connectAttr('{}.worldMatrix[0]'.format(global_ctl_name), '{}.wtMatrix[2].matrixIn'.format(wt_add_mat))
        cmds.connectAttr('{}.outColorR'.format(cond_03), '{}.wtMatrix[2].weightIn'.format(wt_add_mat))

        cmds.connectAttr('{}.worldMatrix[0]'.format(world_ctl_name), '{}.wtMatrix[3].matrixIn'.format(wt_add_mat))
        cmds.connectAttr('{}.outColorR'.format(cond_04), '{}.wtMatrix[3].weightIn'.format(wt_add_mat))

        ###
        cmds.connectAttr('{}.parentInverseMatrix[0]'.format(root_ik_cns_name), '{}.matrixIn[0]'.format(space_mult_mat))
        cmds.connectAttr('{}.matrixSum'.format(wt_add_mat), '{}.matrixIn[1]'.format(space_mult_mat))

        cmds.connectAttr('{}.matrixSum'.format(space_mult_mat), '{}.inputMatrix'.format(decomp_node))

        ###
        cmds.connectAttr('{}.LimitTransX'.format(root_ctl_name), '{}.condition'.format(trans_x_cond))
        cmds.connectAttr('{}.LimitTransY'.format(root_ctl_name), '{}.condition'.format(trans_y_cond))
        cmds.connectAttr('{}.LimitTransZ'.format(root_ctl_name), '{}.condition'.format(trans_z_cond))
        cmds.connectAttr('{}.LimitRotateX'.format(root_ctl_name), '{}.condition'.format(rot_x_cond))
        cmds.connectAttr('{}.LimitRotateY'.format(root_ctl_name), '{}.condition'.format(rot_y_cond))
        cmds.connectAttr('{}.LimitRotateZ'.format(root_ctl_name), '{}.condition'.format(rot_z_cond))

        cmds.setAttr('{}.floatA'.format(trans_x_cond), 0)
        cmds.setAttr('{}.floatA'.format(trans_y_cond), 0)
        cmds.setAttr('{}.floatA'.format(trans_z_cond), 0)
        cmds.setAttr('{}.floatA'.format(rot_x_cond), 0)
        cmds.setAttr('{}.floatA'.format(rot_y_cond), 0)
        cmds.setAttr('{}.floatA'.format(rot_z_cond), 0)

        cmds.connectAttr('{}.outputTranslateX'.format(decomp_node), '{}.floatB'.format(trans_x_cond))
        cmds.connectAttr('{}.outputTranslateY'.format(decomp_node), '{}.floatB'.format(trans_y_cond))
        cmds.connectAttr('{}.outputTranslateZ'.format(decomp_node), '{}.floatB'.format(trans_z_cond))
        cmds.connectAttr('{}.outputRotateX'.format(decomp_node), '{}.floatB'.format(rot_x_cond))
        cmds.connectAttr('{}.outputRotateY'.format(decomp_node), '{}.floatB'.format(rot_y_cond))
        cmds.connectAttr('{}.outputRotateZ'.format(decomp_node), '{}.floatB'.format(rot_z_cond))

        cmds.setAttr('{}.translateX'.format(root_ik_cns_name), l=False)
        cmds.setAttr('{}.translateY'.format(root_ik_cns_name), l=False)
        cmds.setAttr('{}.translateZ'.format(root_ik_cns_name), l=False)
        cmds.setAttr('{}.rotateX'.format(root_ik_cns_name), l=False)
        cmds.setAttr('{}.rotateY'.format(root_ik_cns_name), l=False)
        cmds.setAttr('{}.rotateZ'.format(root_ik_cns_name), l=False)

        cmds.connectAttr('{}.outFloat'.format(trans_x_cond), '{}.translateX'.format(root_ik_cns_name), f=True)
        cmds.connectAttr('{}.outFloat'.format(trans_y_cond), '{}.translateY'.format(root_ik_cns_name), f=True)
        cmds.connectAttr('{}.outFloat'.format(trans_z_cond), '{}.translateZ'.format(root_ik_cns_name), f=True)
        cmds.connectAttr('{}.outFloat'.format(rot_x_cond), '{}.rotateX'.format(root_ik_cns_name), f=True)
        cmds.connectAttr('{}.outFloat'.format(rot_y_cond), '{}.rotateY'.format(root_ik_cns_name), f=True)
        cmds.connectAttr('{}.outFloat'.format(rot_z_cond), '{}.rotateZ'.format(root_ik_cns_name), f=True)

        root_root_name = stepDict["mgearRun"].components["root_C0"].root.longName()
        cmds.connectAttr('{}.ctl_vis'.format('|rig'), '{}.visibility'.format(root_root_name))
        cmds.connectAttr('{}.ctl_vis_on_playback'.format('|rig'), '{}.hideOnPlayback'.format(root_root_name))

        print('Root Controller scheme set up.')
