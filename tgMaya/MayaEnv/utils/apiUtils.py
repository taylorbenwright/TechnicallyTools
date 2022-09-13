import maya.api.OpenMaya as om2


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


def rotate_order_string_to_meulerangle_constant(rotate_order):
    """
    Takes in a rotate order string and returns the cooresponding MEulerAngler rotation order constant
    :param rotate_order: The rotation order to query
    :type rotate_order: str
    :return: The MEulerAngle rotation order constant integer
    :rtype: int
    """
    rot_order_str = 'k{}'.format(rotate_order.upper())
    return getattr(om2.MEulerRotation, rot_order_str)


def get_outgoing_dp_nodes(node, plug_filter=None, type_filter=None, clip_duplicates=False):
    """
    Taking in an MObject, returns all or a subset of outgoing destination nodes. Can be filtered by plug and destination
    node, and duplicates can be omitted.
    :param node: The node we wish to query
    :type node: om2.MObject
    :param plug_filter: Do we want to filter our return by plug? Eg. get all outgoing dp nodes connected to a Message
                        plug
    :type plug_filter: str
    :param type_filter: The type of node we wish to filter for. Eg. get all dagPose nodes
    :type type_filter: om2.MFn
    :param clip_duplicates: Should we remove all duplicate MObjs from the final list?
    :type clip_duplicates: bool
    :return: returns all nodes that we want from the queried node
    :rtype: om2.MObjectArray
    """
    dest_node_array = om2.MObjectArray()

    dep_node = om2.MFnDependencyNode(node)
    plug_array = dep_node.getConnections()  # type: om2.MPlugArray

    for plug in plug_array:
        if plug_filter is not None and plug.partialName(useLongNames=True) != plug_filter:
            continue

        dest_plug_array = plug.connectedTo(False, True)  # type: om2.MPlugArray
        for dest_plug in dest_plug_array:
            dest_node = dest_plug.node()  # type: om2.MObject

            if type_filter is not None and dest_node.apiType() != type_filter:
                continue

            if clip_duplicates and dest_node in dest_node_array:
                continue

            dest_node_array.append(dest_node)

    return dest_node_array
