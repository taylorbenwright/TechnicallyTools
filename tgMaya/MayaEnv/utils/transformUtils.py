"""
Utilities relating to transforming scene DAG nodes.
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om2


def get_axis(matrix, axis):
    """
    Returns an MVector describing the requested matrix axis

    :param matrix: The matrix used for axis lookup
    :type matrix: om2.MMatrix

    :param axis: The axis name or index corresponding to ('x', 'y', 'z'), where 0=x, 1=y, 2=z
    :type axis: int|str|unicode

    :return: The requested axis as a vector
    :rtype: om2.MVector
    """

    if not type(matrix) is om2.MMatrix:
        raise TypeError('matrix must be type MMatrix')

    axis_names = ('x', 'y', 'z')
    axis_slices = ((0, 3), (4, 7), (8, 11))

    lookup = axis if type(axis) is int \
        else axis_names.index(axis) if isinstance(axis, str) and axis in axis_names else None
    if lookup is None:
        raise TypeError('axis must be valid name from {} or corresponding index'.format(axis_names))

    axis_request = axis_slices[lookup]
    return om2.MVector(list(matrix)[slice(*axis_request)]).normalize()


def get_axes(matrix):
    """
    Returns a list of x, y, and z axis vectors

    :param matrix: The matrix used for axis lookup
    :type matrix: om2.MMatrix

    :return: list of vectors describing x, y, and z axis direction components
    :rtype:
    """
    if not type(matrix) is om2.MMatrix:
        raise TypeError('matrix must be type MMatrix')
    return [get_axis(matrix, i) for i in range(3)]


def set_axis(matrix, axis, vec):
    """
    Convenience method to set an axis component of a 4x4 matrix

    :param matrix: The input matrix to augment
    :type matrix: om2.MMatrix

    :param axis: The axis name ['x', 'y', 'z', 't'] or corresponding row index [0=x, 1=y, 2=z, 3=t]
    :type axis: int|str|unicode

    :param vec: Iterable representing components of a vector of (x, y, z)
    :type vec: list|tuple|om2.MVector

    :return: Nothing
    :rtype: None
    """

    if not type(matrix) is om2.MMatrix:
        raise TypeError('matrix must be of type MMatrix')

    axis_names = ('x', 'y', 'z', 't')
    row_start = (0, 4, 8, 12)

    axis_lookup = axis if type(axis) is int \
        else axis_names.index(axis) if isinstance(axis, str) and axis in axis_names else None
    if axis_lookup is None:
        raise TypeError('axis must be valid name from {} or corresponding index'.format(axis_names))

    row_start = row_start[axis_lookup]

    vec = vec if type(vec) is om2.MVector else om2.MVector(vec)
    if row_start < 12:
        vec.normalize()

    for v, m in enumerate(range(row_start, row_start+3)):
        matrix.__setitem__(m, vec[v])


def from_vectors(x=None, y=None, z=None, t=None):
    """
    Returns an MMatrix from vector components

    :param x: Iterable representing components of a vector of (x, y, z)
    :type x: ist|tuple|om2.MVector

    :param y: Iterable representing components of a vector of (x, y, z)
    :type y: ist|tuple|om2.MVector

    :param z: Iterable representing components of a vector of (x, y, z)
    :type z: ist|tuple|om2.MVector

    :param t: Iterable representing components of a vector of (x, y, z)
    :type t: ist|tuple|om2.MVector

    :return: matrix from vector components
    :rtype: om2.MMatrix
    """
    result = om2.MMatrix()

    if x:
        set_axis(result, 0, x)
    if y:
        set_axis(result, 1, y)
    if z:
        set_axis(result, 2, z)
    if t:
        set_axis(result, 3, t)

    return result


def closest_cardinal(in_matrix, space=om2.MSpace.kWorld):
    """
    Returns the closest matrix to the input whose directional axis are cardinal aligned

    :param in_matrix:  The input matrix
    :type in_matrix: list|tuple|om2.MMatrix

    :return: A cardinal aligned matrix
    :rtype: om2.MMatrix
    """
    in_matrix = in_matrix if type(in_matrix) == om2.MMatrix else om2.MMatrix(in_matrix)

    cardinals = {'x': om2.MVector(1., 0., 0.), '-x': om2.MVector(-1., 0., 0.),
                 'y': om2.MVector(0., 1., 0.), '-y': om2.MVector(0., -1., 0.),
                 'z': om2.MVector(0., 0., 1.), '-z': om2.MVector(0., 0., -1.)}

    vec_in_t = om2.MTransformationMatrix(in_matrix).translation(space)
    vec_in_s = om2.MTransformationMatrix(in_matrix).scale(space)

    vec_in_x = get_axis(in_matrix, 'x')
    vec_in_y = get_axis(in_matrix, 'y')

    # TODO: Loop using rotation order to determine results
    dots = sorted([(vec_in_x * vec_cardinal, axis) for axis, vec_cardinal in cardinals.items()])
    vec_closest_x = cardinals[dots.pop()[1]]

    remaining = {axis: vec for axis, vec in cardinals.items() if vec != vec_closest_x}
    dots = sorted([(vec_in_y * vec_cardinal, axis) for axis, vec_cardinal in remaining.items()])
    vec_closest_y = cardinals[dots.pop()[1]]

    vec_closest_z = (vec_closest_x ^ vec_closest_y).normalize()

    cardinal_matrix = from_vectors(vec_closest_x, vec_closest_y, vec_closest_z, vec_in_t)

    cardinal_xform = om2.MTransformationMatrix(cardinal_matrix)
    cardinal_xform.setScale(vec_in_s, space)

    return cardinal_xform.asMatrix()


def align_to_cardinal(*args):
    """
    Aligns all selected objects to the nearest cardinal rotation
    :return: Nothing
    :rtype: None
    """
    for obj in cmds.ls(sl=True):
        mat = cmds.xform(obj, ws=True, m=True, q=True)
        mmat = closest_cardinal(mat)
        cmds.xform(obj, ws=True, m=mmat)


def stash_rotation_in_joint_orients(*args):
    """
    Zeroes out the rotations on all selected joints, and stashes the final joint orient in the joint orient attr
    :return: Nothing
    :rtype: None
    """
    for jnt in cmds.ls(sl=True, type='joint'):
        jnt_xmat = om2.MMatrix(cmds.xform(jnt, ws=True, q=True, m=True))
        cmds.setAttr('{}.jointOrient'.format(jnt), 0.0, 0.0, 0.0)
        cmds.xform(jnt, ws=True, m=jnt_xmat)

        rotations = cmds.getAttr('{}.rotate'.format(jnt))[0]
        cmds.setAttr('{}.rotate'.format(jnt), 0.0, 0.0, 0.0)
        cmds.setAttr('{}.jointOrient'.format(jnt), rotations[0], rotations[1], rotations[2])
