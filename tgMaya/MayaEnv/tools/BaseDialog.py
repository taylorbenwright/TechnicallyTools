"""
This is the generalized QDialog for use in Maya. We add agnostic tools to this.
"""

from PySide2 import QtWidgets, QtGui
from PySide2.QtCore import Qt
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin


class BaseMayaDialog(MayaQWidgetBaseMixin, QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(BaseMayaDialog, self).__init__(parent=parent)

        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self.tool = None
        self.main_layout = QtWidgets.QVBoxLayout()
        
    def show(self):
        if self.tool is not None:
            self.main_layout.addWidget(self.tool)
        self.setLayout(self.main_layout)
        super(BaseMayaDialog, self).show()

    def showEvent(self, *args):
        super(BaseMayaDialog, self).showEvent(*args)
        self.dialog_opened()

    def closeEvent(self, *args):
        super(BaseMayaDialog, self).closeEvent(*args)
        self.dialog_closed()

    def dialog_opened(self):
        """
        Called after the dialog UI is fully shown. This is where we want to do lookups, etc
        :return: Nothing
        :rtype: None
        """
        raise NotImplementedError

    def dialog_closed(self):
        """
        Called after the dialog is closed. Teardown stuff can happen here
        :return: Nothing
        :rtype: None
        """
        raise NotImplementedError

