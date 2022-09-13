import maya.cmds as cmds
import maya.api.OpenMaya as om2
from MayaEnv.utils.apiUtils import get_node_from_str, rotate_order_string_to_meulerangle_constant


def get_offset_matrix(target, source):
    """
    Retrieves the offset matrix between the target and the source and returns it as an MMatrix
    :param target: The target object to find the offset matrix from
    :type target: str
    :param source: The source object to find the offset matrix to
    :type source: str
    :return: The MMatrix that defines the offset
    :rtype: om2.MMatrix
    """
    parent_world_mat = om2.MDagPath.getAPathTo(get_node_from_str(source)).inclusiveMatrix()  # type: om2.MMatrix
    child_world_mat = om2.MDagPath.getAPathTo(get_node_from_str(target)).inclusiveMatrix()  # type: om2.MMatrix

    return child_world_mat * parent_world_mat.inverse()  # type: om2.MMatrix


def matrix_constraint(target, sources, maintain_offset=False,
                      translate_x=True, translate_y=True, translate_z=True,
                      rotate_x=True, rotate_y=True, rotate_z=True,
                      scale_x=True, scale_y=True, scale_z=True):
    """
    Creates a matrix constraint between a list of sources and a target. Optionally will maintain offset.
    :param sources: A list of the sources we wish to use to constrain the target
    :type sources: list
    :param maintain_offset: Should we maintain the target's offset from the sources?
    :type maintain_offset: bool
    :param translate_x: Should we constrain the translateX attr?
    :type translate_x: bool
    :param translate_y: Should we constrain the translateY attr?
    :type translate_y: bool
    :param translate_z: Should we constrain the translateZ attr?
    :type translate_z: bool
    :param rotate_x: Should we constrain the rotateX attr?
    :type rotate_x: bool
    :param rotate_y: Should we constrain the rotateY attr?
    :type rotate_y: bool
    :param rotate_z: Should we constrain the rotateZ attr?
    :type rotate_z: bool
    :param scale_x: Should we constrain the scaleX attr?
    :type scale_x: bool
    :param scale_y: Should we constrain the scaleY attr?
    :type scale_y: bool
    :param scale_z: Should we constrain the scaleZ attr?
    :type scale_z: bool
    :param target: The target we wish to be constrained.
    :type target: str
    :return: Returns the wtAddMatrix node
    :rtype: str
    """

    cmds.undoInfo(openChunk=True)

    mat_const_name = '{}_matrixConstraint'.format(target)
    mult_mats = []
    last_node = None

    if len(sources) > 1:
        last_node = cmds.createNode('wtAddMatrix', name='{}_wtAddMatrix'.format(mat_const_name))
    final_decomp_node = cmds.createNode('decomposeMatrix', name='{}_decomposeMatrix'.format(mat_const_name))

    for ind, src in enumerate(sources):
        mat_ind = 0
        mult_mat = cmds.createNode('multMatrix', name='{}_multMatrix_{}'.format(mat_const_name, ind))
        mult_mats.append(mult_mat)
        if maintain_offset:
            # create the offset matrix
            offset_mat_node = cmds.createNode('holdMatrix', name='{}_offsetMatrix_{}'.format(mat_const_name, ind))
            cmds.setAttr('{}.inMatrix'.format(offset_mat_node), list(get_offset_matrix(target, src)), type='matrix')
            cmds.connectAttr('{}.outMatrix'.format(offset_mat_node), '{}.matrixIn[{}]'.format(mult_mat, mat_ind), force=True)
            mat_ind += 1

        cmds.connectAttr('{}.worldMatrix[0]'.format(src), '{}.matrixIn[{}]'.format(mult_mat, mat_ind), force=True)
        mat_ind += 1
        cmds.connectAttr('{}.parentInverseMatrix[0]'.format(target), '{}.matrixIn[{}]'.format(mult_mat, mat_ind), force=True)
        mat_ind += 1

        if len(sources) > 1:
            cmds.connectAttr('{}.matrixSum'.format(mult_mat), '{}.wtMatrix[{}].matrixIn'.format(last_node, ind))
            if ind == 0:
                cmds.setAttr('{}.wtMatrix[0].weightIn'.format(last_node), 1)
        else:
            last_node = mult_mat

    cmds.connectAttr('{}.matrixSum'.format(last_node), '{}.inputMatrix'.format(final_decomp_node))

    final_rot_port = '{}.outputRotate'.format(final_decomp_node)

    if cmds.objectType(target, isType='joint'):
        euler_to_quat_node = cmds.createNode('eulerToQuat', name='{}_eulerToQuat'.format(mat_const_name))
        invert_quat_node = cmds.createNode('quatInvert', name='{}_invertQuat'.format(mat_const_name))
        quat_prod_node = cmds.createNode('quatProd', name='{}_quatProd'.format(mat_const_name))
        quat_to_euler_node = cmds.createNode('quatToEuler', name='{}_quatToEuler'.format(mat_const_name))

        cmds.connectAttr('{}.jointOrient'.format(target), '{}.inputRotate'.format(euler_to_quat_node))
        cmds.connectAttr('{}.rotateOrder'.format(target), '{}.inputRotateOrder'.format(euler_to_quat_node))
        cmds.connectAttr('{}.outputQuat'.format(euler_to_quat_node), '{}.inputQuat'.format(invert_quat_node))
        cmds.connectAttr('{}.outputQuat'.format(final_decomp_node), '{}.input1Quat'.format(quat_prod_node))
        cmds.connectAttr('{}.outputQuat'.format(invert_quat_node), '{}.input2Quat'.format(quat_prod_node))
        cmds.connectAttr('{}.outputQuat'.format(quat_prod_node), '{}.inputQuat'.format(quat_to_euler_node))
        final_rot_port = '{}.outputRotate'.format(quat_to_euler_node)

    if translate_x:
        cmds.connectAttr('{}.outputTranslateX'.format(final_decomp_node), '{}.translateX'.format(target))
    if translate_y:
        cmds.connectAttr('{}.outputTranslateY'.format(final_decomp_node), '{}.translateY'.format(target))
    if translate_z:
        cmds.connectAttr('{}.outputTranslateZ'.format(final_decomp_node), '{}.translateZ'.format(target))
    if rotate_x:
        cmds.connectAttr('{}X'.format(final_rot_port), '{}.rotateX'.format(target))
    if rotate_y:
        cmds.connectAttr('{}Y'.format(final_rot_port), '{}.rotateY'.format(target))
    if rotate_z:
        cmds.connectAttr('{}Z'.format(final_rot_port), '{}.rotateZ'.format(target))
    if scale_x:
        cmds.connectAttr('{}.outputScaleX'.format(final_decomp_node), '{}.scaleX'.format(target))
    if scale_y:
        cmds.connectAttr('{}.outputScaleY'.format(final_decomp_node), '{}.scaleY'.format(target))
    if scale_z:
        cmds.connectAttr('{}.outputScaleZ'.format(final_decomp_node), '{}.scaleZ'.format(target))

    cmds.undoInfo(closeChunk=True)

    return last_node
