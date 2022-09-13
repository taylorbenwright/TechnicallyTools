"""
The Maya interface for the Object Exporter tool
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om2
from MayaEnv.tools import BaseDialog
from widgets.dialogs import ObjectExporter


class ObjectExporterDialog(BaseDialog.BaseMayaDialog):

    def __init__(self, parent=None):
        super(ObjectExporterDialog, self).__init__(parent=parent)

        self.show()

    def dialog_opened(self):
        pass

    def dialog_closed(self):
        pass
