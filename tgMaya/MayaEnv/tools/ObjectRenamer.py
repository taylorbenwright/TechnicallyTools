"""
The Maya interface for the Object Renamer tool
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om2
from MayaEnv.tools import BaseDialog
from widgets.dialogs import ObjectRenamer


class ObjectRenameDialog(BaseDialog.BaseMayaDialog):

    def __init__(self, parent=None):
        super(ObjectRenameDialog, self).__init__(parent=parent)

        self._callback = None
        self._current_selection = []
        self.tool = ObjectRenamer.ObjectRenamer()

        self.setWindowTitle('Object Renamer')

        self.show()

    def on_tool_ready(self):
        """
        Called when the tool is ready again after initialization or after a Rename action has happened to this what am I doing this for
        :return: Nothing
        :rtype: None
        """
        self.on_selection_changed(None)

    def on_selection_changed(self, client_data):
        """
        Called whenever a selection is changed in the scene
        :param client_data: Nothing is passed in here
        :type client_data: None
        :return: Nothing
        :rtype: None
        """
        current_sel = cmds.ls(sl=True, l=True)
        self._current_selection = current_sel
        short_name_list = [name.split('|')[-1] for name in self._current_selection]
        self.tool.selection_changed(short_name_list)

    def on_renamed(self, new_names):
        """
        Receive the new names from the tool and perform the renaming action
        :param new_names: A list of new name strings for the current selection
        :type new_names: list[str]
        :return: Nothing
        :rtype: None
        """
        if len(new_names) != len(self._current_selection):
            return

        zip_obj = list(zip(self._current_selection, new_names))
        for cur_name, new_name in reversed(zip_obj):
            cmds.rename(cur_name, new_name)

    def add_selection_changed_callback(self):
        event = om2.MEventMessage.addEventCallback('SelectionChanged', self.on_selection_changed)
        self._callback = event

    def remove_selection_changed_callback(self):
        om2.MMessage.removeCallback(self._callback)
        self._callback = None

    def dialog_opened(self):
        self.tool.renamed.connect(self.on_renamed)
        self.tool.ready.connect(self.on_tool_ready)
        self.tool.dialog_opened()
        self.add_selection_changed_callback()

    def dialog_closed(self):
        self.remove_selection_changed_callback()
        self.tool.dialog_closed()


def create_dialog(*args):
    obj_renamer_tool = ObjectRenameDialog()
    obj_renamer_tool.show()
