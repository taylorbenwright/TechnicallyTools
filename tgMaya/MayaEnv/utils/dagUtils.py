"""
Utilities having to do with DAG nodes and their creation, editing, etc.
These methods should not be about DG nodes, only DAG nodes.

All of these methods take in an MObject. They can do things with cmds but should always return an API object, if
    anything
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om2
import MayaEnv.utils.apiUtils as apiUtils


def return_all_dag_poses(node, rtype='str'):
    """
    Returns all dagPose nodes connected to this node
    :param node: The node to query
    :type node: str
    :param rtype: The type of object to return, either a full path string or an MObject
    :type rtype: str
    :return: All dagPoses connected to this object, either in a list or a MObjectArray
    :rtype: list[str] || om2.MObjectArray
    """
    node_mobj = apiUtils.get_node_from_str(node)
    dag_pose_nodes = apiUtils.get_outgoing_dp_nodes(node_mobj, plug_filter='message', type_filter=om2.MFn.kDagPose,
                                                    clip_duplicates=True)
    if rtype == 'str':
        return [om2.MFnDependencyNode(dag_node).name() for dag_node in dag_pose_nodes]
    else:
        return dag_pose_nodes


def assume_dag_pose(node, pose_name):
    """
    Taking a node name and a pose name, restore the node and its hierarchy to the saved dagPose called pose_name if that
    pose exists
    :param node: The node (and subsequent hierarchy) to restore
    :type node: str
    :param pose_name: The name of the dagPose to restore to
    :type pose_name: str
    :return: If the operation was successful or not
    :rtype: bool
    """
    if pose_name in return_all_dag_poses(node):
        cmds.dagPose(node, name=pose_name, restore=True)
        return True
    return False


def get_node_full_path(node):
    """
    Given a DAG node MObject, return its full object path
    :param node: The node to query
    :type node: om2.MObject
    :return: Full path to this object in the scene
    :rtype: str
    """
    return om2.MFnDagNode(node).getPath().fullPathName()


def get_node_transform(node, world_space=True):
    """
    Given an MObject, returns the object's MMatrix in the queried space
    :param node: The node to query
    :type node: om2.MObject
    :param world_space: Whether to get the MMatrix in world space or not (thus local space)
    :type world_space: bool
    :return: The matrix of the queried node
    :rtype: om2.MMatrix
    """
    mfn_dagnode = om2.MFnDagNode(node)

    node_path = mfn_dagnode.getPath().fullPathName()
    node_matrix = cmds.xform(node_path, q=True, m=True, ws=world_space)
    return om2.MMatrix(node_matrix)


def get_node_parent(node):
    """
    Returns the node's parent, if there is one. Otherwise a null MObject
    :param node: the node to query
    :type node: om2.MObject
    :return: The found node
    :rtype: om2.MObject
    """
    mfn_dagnode = om2.MFnDagNode(node)

    return mfn_dagnode.parent(0)


def dag_factory(node_type, node_name):
    """
    Factory function to create an arbitrary DAG node with the given name and then return it.
    :param node_type: The type of DAG node we want to create. Must be the exact name
    :type node_type: str
    :param node_name: The name to give this node
    :type node_name: str
    :return: Returns the MObject that was created
    :rtype: om2.MObject
    """
    mfn_dagnode = om2.MFnDagNode()
    new_node = mfn_dagnode.create(node_type, name=node_name)

    return new_node if new_node else None


def create_locator_at_dag(node, locator_name=None):
    """
    Create a new locator at the position and rotation of a given dag node, then return the locator MObject
    :param node: The node to place at locator at
    :type node: om2.MObject
    :param locator_name: The name to give our newly-minted locator. If None, just a default name.
    :type locator_name: str
    :return: The newly created locator
    :rtype: om2.MObject
    """
    node_transform = get_node_transform(node)

    new_locator = dag_factory('locator', locator_name)
    cmds.xform(get_node_full_path(new_locator), m=node_transform, ws=True)

    return new_locator


def create_null_at_dag(node, null_name=None):
    """
    Creates a null at the location of the dag node specified
    :param node: The node to place a null at
    :type node: om2.MObject
    :param null_name: the name to give out newly created null. If None, just a default name.
    :type null_name: str
    :return: The newly created null
    :rtype: om2.MObject
    """
    node_transform = get_node_transform(node)

    new_null = dag_factory('transform', null_name)
    cmds.xform(get_node_full_path(new_null), m=node_transform, ws=True)

    return new_null


def create_jnts_at_dag(node, jnt_name=None):
    """
    Creates a joint at the location of the dag node specified
    :param node: The node to place a joint at
    :type node: om2.MObject
    :param jnt_name: the name to give out newly created joints. If None, just a default name.
    :type jnt_name: str
    :return: The newly created null
    :rtype: om2.MObject
    """
    node_transform = get_node_transform(node)

    new_jnt = dag_factory('joint', jnt_name)
    jnt_name = get_node_full_path(new_jnt)
    cmds.xform(jnt_name, m=node_transform, ws=True)
    rotations = cmds.getAttr('{}.rotate'.format(jnt_name))[0]
    cmds.setAttr('{}.rotate'.format(jnt_name), 0.0, 0.0, 0.0)
    cmds.setAttr('{}.jointOrient'.format(jnt_name), rotations[0], rotations[1], rotations[2])

    return new_jnt


# def sandwich_node(node):
#     """
#     Sandwiches a node between two transforms
#     :param node: The node to sandwich
#     :type node: om2.MObject
#     :return: A list of the zero node and the result node
#     :rtype: list
#     """
#     node_name = om2.MFnDependencyNode(node).name()
#     zero_node = create_null_at_dag(node, null_name=node_name + '_zero')
#     res_node = create_null_at_dag(node, null_name=node_name + '_res')
#     om2.MFnDependencyNode(node).
