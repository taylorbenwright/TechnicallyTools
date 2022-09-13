"""
Everything in here is designed to be easy to use in a Maya scene without having to deal with multiple lines of code
Preferably everything here returns something helpful with one line in the Python command line
"""
import maya.cmds as cmds
import maya.api.OpenMaya as om2
from itertools import tee
import MayaEnv.utils.apiUtils as apiUtils
import MayaEnv.utils.dagUtils as dagUtils

WORLD_ID = 247  # the MFn designation for the kWorld object


def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def create_locator_at_selected_objects(name_token='loc', select_when_done=False):
    """
    Takes the current scene selection and creates a new locator at each. Names the locators with a numerated name if
    desired
    :param name_token: A name to give these locators. Will be suffixed with *_1, *_2, etc
    :type name_token: str
    :param select_when_done: Should we select the locators when we are done?
    :type select_when_done: bool
    :return: Returns the names of all the created locators
    :rtype: list[str]
    """
    created_locators = []
    token_num = 0
    selected = cmds.ls(sl=True)
    for sel in selected:
        token_num += 1
        sel_mobj = apiUtils.get_node_from_str(sel)

        new_locator = dagUtils.create_locator_at_dag(sel_mobj, locator_name=name_token+str(token_num))

        created_locators.append(dagUtils.get_node_full_path(new_locator))

    if select_when_done:
        cmds.select(created_locators)

    return created_locators


def create_transform_at_selected_objects(suffix='_grp', select_when_done=False):
    """
    Takes the current scene selection and creates a new transform at each. Names the transform with a suffix
    :param suffix: A suffix to give these transform
    :type suffix: str
    :param select_when_done: Should we select the transforms when we are done?
    :type select_when_done: bool
    :return: Returns the names of all the created transforms
    :rtype: list[str]
    """
    created_xforms = []
    token_num = 0
    selected = cmds.ls(sl=True)
    for sel in selected:
        token_num += 1
        sel_mobj = apiUtils.get_node_from_str(sel)

        new_locator = dagUtils.create_null_at_dag(sel_mobj, null_name=sel+suffix)

        created_xforms.append(dagUtils.get_node_full_path(new_locator))

    if select_when_done:
        cmds.select(created_xforms)

    return created_xforms


def create_nulls_above_selected_objects(suffix='_grp', select_when_done=False):
    """
    Creates nulls above every selected object. Will suffix each new node with the suffix
    :param suffix: The suffix to add to the created null objects
    :type suffix: str
    :param select_when_done: should we select all these nodes when we are done?
    :type select_when_done: bool
    :return: Returns the names of all the created nulls
    :rtype: list[str]
    """
    created_nulls = []
    selected = cmds.ls(sl=True)
    for sel in selected:
        sel_mobj = apiUtils.get_node_from_str(sel)  # get selected mobj
        sel_mobj_parent = dagUtils.get_node_parent(sel_mobj)  # get selected mobj's parent

        new_null = dagUtils.create_null_at_dag(sel_mobj, null_name=sel+suffix)  # create new null
        new_mfndag = om2.MFnDagNode(new_null)  # get new null mfn dag
        new_mfndag.addChild(sel_mobj)  # add the selected object as this new null's child

        identity_matrix = om2.MTransformationMatrix()
        cmds.xform(sel, os=True, m=identity_matrix.asMatrix())
        sel_ws_forxm = cmds.xform(sel, ws=True, m=True, q=True)

        if sel_mobj_parent.apiType() is not WORLD_ID:
            parent_mfndag = om2.MFnDagNode(sel_mobj_parent)
            parent_mfndag.addChild(new_null)
            cmds.xform(dagUtils.get_node_full_path(new_null), ws=True, m=sel_ws_forxm)

        created_nulls.append(dagUtils.get_node_full_path(new_null))

    if select_when_done:
        cmds.select(created_nulls)

    return created_nulls


def create_nulls_below_selected_objects(suffix='_grp', select_when_done=False):
    """
    Creates nulls below every selected object in the hierarchy. Will suffix each new node with the suffix
    :param suffix: The suffix to add to the created null objects
    :type suffix: str
    :param select_when_done: should we select all these nodes when we are done?
    :type select_when_done: bool
    :return: Returns the names of all the created nulls
    :rtype: list[str]
    """
    created_nulls = []
    selected = cmds.ls(sl=True)
    for sel in selected:
        sel_mobj = apiUtils.get_node_from_str(sel)  # get selected mobj
        sel_mfndag = om2.MFnDagNode(sel_mobj)

        new_null = dagUtils.create_null_at_dag(sel_mobj, null_name=sel+suffix)  # create new null

        sel_mfndag.addChild(new_null)  # add the selected object as this new null's child
        identity_matrix = om2.MTransformationMatrix()
        cmds.xform(dagUtils.get_node_full_path(new_null), os=True, m=identity_matrix.asMatrix())

        created_nulls.append(dagUtils.get_node_full_path(new_null))

    if select_when_done:
        cmds.select(created_nulls)

    return created_nulls


def create_joints_at_selected_objects(suffix='_jnt', select_when_done=False, create_chain=False):
    """
    Creates a joint at the transform of each selected object with the specified suffix. Can optionally be added to a
    chain
    :param suffix: The suffix to add to the created null objects
    :type suffix: str
    :param select_when_done: should we select all these nodes when we are done?
    :type select_when_done: bool
    :param create_chain: Should we create all these joints in a chain?
    :type create_chain: bool
    :return: Returns the names of all the created joints
    :rtype: list[str]
    """
    created_jnts = []
    selected = cmds.ls(sl=True)
    for sel in selected:
        sel_mobj = apiUtils.get_node_from_str(sel)

        new_jnt = dagUtils.create_jnts_at_dag(sel_mobj, jnt_name=sel+suffix)

        created_jnts.append(dagUtils.get_node_full_path(new_jnt))

    if create_chain and len(created_jnts) > 1:
        for child, parent in pairwise(reversed(created_jnts)):
            cmds.parent(child, parent)

    if select_when_done:
        cmds.select(created_jnts)

    return created_jnts
