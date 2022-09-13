import maya.cmds as cmds


def get_mesh_textures(mesh_name):
    """
    Given a mesh in the scene, returns the names of all texture maps used in that mesh's materials
    :return: A list of texture names
    :rtype: list
    """
    if not cmds.objExists(mesh_name):
        return []



def get_scene_textures():
    """
    Scrubs the scene for all meshes, and returns any texture maps used in those meshes' materials
    :return: A dict of mesh:[textures]
    :rtype: dict
    """
    pass
