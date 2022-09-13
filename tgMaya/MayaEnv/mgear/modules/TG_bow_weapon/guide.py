"""
Guide for the two-handed weapon module
"""

from functools import partial
from PySide2 import QtWidgets, QtCore
from MayaEnv.mgear import utils as mgear_utils

from mgear.shifter.component import guide
from mgear.core import transform, pyqt

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.general.mayaMixin import MayaQDockWidget


# guide info
AUTHOR = "TB Wright"
URL = "www.tbwrightartist.com"
EMAIL = "tbwrightartist@gmail.com"
VERSION = [1, 0, 0]
TYPE = "TG_bow_weapon"
NAME = "bowweapon"
DESCRIPTION = "Module for bow and arrow. Assumes that the right hand is the arrow hand and the left hand is the bow " \
              "hand."
##########################################################
# CLASS
##########################################################


class Guide(guide.ComponentGuide):

    compType = TYPE
    compName = NAME
    description = DESCRIPTION

    author = AUTHOR
    url = URL
    email = EMAIL
    version = VERSION

    connectors = ["orientation"]

    def postInit(self):
        self.save_transform = ['root', 'grip', 'arm_top', 'arm_bottom', 'top', 'bottom', 'string', 'arrow']

    def addObjects(self):
        self.root = self.addRoot()
        self.grip = self.addLoc('grip', self.root, transform.getOffsetPosition(self.root, [0, 0, 0]))
        self.arm_top = self.addLoc('arm_top', self.grip, transform.getOffsetPosition(self.grip, [0, 5, 0]))
        self.arm_bottom = self.addLoc('arm_bottom', self.grip, transform.getOffsetPosition(self.grip, [0, -5, 0]))
        self.top = self.addLoc('top', self.arm_top, transform.getOffsetPosition(self.arm_top, [0, 5, -5]))
        self.bottom = self.addLoc('bottom', self.arm_bottom, transform.getOffsetPosition(self.arm_bottom, [0, -5, -5]))
        self.string = self.addLoc('string', self.grip, transform.getOffsetPosition(self.grip, [0, 0, -5]))
        self.arrow = self.addLoc('arrow', self.grip, transform.getOffsetPosition(self.grip, [0, 0, -10]))

        self.top_disp_crv = self.addDispCurve('top_crv', [self.arm_top, self.top], degree=3)
        self.bottom_disp_crv = self.addDispCurve('bottom_crv', [self.arm_bottom, self.bottom], degree=1)
        self.string_crv = self.addDispCurve('string_crv', [self.top, self.string, self.bottom], degree=1)

    def addParameters(self):
        self.grip_ikref_array = self.addParam('grip_ikref_array', 'string', '', niceName='Grip Space')
        self.bowstring_ikref_array = self.addParam('string_ikref_array', 'string', '', niceName='Bowstring Space')
        self.arrow_ikref_array = self.addParam('arrow_ikref_array', 'string', '', niceName='Arrow Space')

        self.bow_tension = self.addParam("bow_tension", "double", 0, 0, 1)
        self.bow_flexibility = self.addParam("bow_flexibility", "double", 0, 0, 1)
        self.arrow_aim = self.addParam('arrow_aim', 'bool', False)

        self.grip_RotOrder = self.addParam("grip_rotorder", "long", 0, 0, 5)

        self.pUseIndex = self.addParam("useIndex", "bool", False)
        self.pParentJointIndex = self.addParam("parentJointIndex", "long", -1, None, None)

    def postDraw(self):
        return

##########################################################
# Setting Page
##########################################################


class settingsTab(QtWidgets.QDialog):
    """The Component settings UI"""

    def __init__(self, parent=None):
        super(settingsTab, self).__init__(parent)

        ro_list = ["XYZ", "YZX", "ZXY", "XZY", "YXZ", "ZYX"]

        self.setObjectName("Form")
        main_layout = QtWidgets.QVBoxLayout(self)

        grip_groupbox = QtWidgets.QGroupBox('Grip: ')
        grip_layout = QtWidgets.QVBoxLayout(grip_groupbox)
        self.grip_ro_cmb = QtWidgets.QComboBox()
        self.grip_ro_cmb.addItems(ro_list)
        grp_ikref_grpbox, self.grip_ikref_list, self.grip_ikref_add_but, self.grip_ikref_remove_but = mgear_utils.ik_reference_groubox()
        grip_layout.addWidget(self.grip_ro_cmb)
        grip_layout.addWidget(grp_ikref_grpbox)

        string_groupbox = QtWidgets.QGroupBox('Bowstring: ')
        string_layout = QtWidgets.QVBoxLayout(string_groupbox)
        string_ikref_grpbox, self.string_ikref_list, self.string_ikref_add_but, self.string_ikref_remove_but = mgear_utils.ik_reference_groubox()
        string_layout.addWidget(string_ikref_grpbox)

        arrow_groupbox = QtWidgets.QGroupBox('Arrow: ')
        arrow_layout = QtWidgets.QVBoxLayout(arrow_groupbox)
        arrow_ikref_grpbox, self.arrow_ikref_list, self.arrow_ikref_add_but, self.arrow_ikref_remove_but = mgear_utils.ik_reference_groubox()
        arrow_layout.addWidget(arrow_ikref_grpbox)

        main_layout.addWidget(grip_groupbox)
        main_layout.addWidget(string_groupbox)
        main_layout.addWidget(arrow_groupbox)


class componentSettings(MayaQWidgetDockableMixin, guide.componentMainSettings):
    """Create the component setting window"""

    def __init__(self, parent=None):
        self.toolName = TYPE
        # Delete old instances of the component settings window.
        pyqt.deleteInstances(self, MayaQDockWidget)

        super(self.__class__, self).__init__(parent=parent)
        self.settingsTab = settingsTab()

        self.setup_componentSettingWindow()
        self.create_componentControls()
        self.populate_componentControls()
        self.create_componentLayout()
        self.create_componentConnections()

    def setup_componentSettingWindow(self):
        self.mayaMainWindow = pyqt.maya_main_window()

        self.setObjectName(self.toolName)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(TYPE)
        self.resize(280, 520)

    def create_componentControls(self):
        return

    def populate_componentControls(self):
        """Populate Controls

        Populate the controls values from the custom attributes of the
        component.

        """
        # populate tab
        self.tabs.insertTab(1, self.settingsTab, "Component Settings")

        self.settingsTab.grip_ro_cmb.setCurrentIndex(self.root.attr("grip_rotorder").get())

        grip_ikref_array_items = self.root.attr("grip_ikref_array").get().split(",")
        for item in grip_ikref_array_items:
            self.settingsTab.grip_ikref_list.addItem(item)

        string_ikref_array_items = self.root.attr("string_ikref_array").get().split(",")
        for item in string_ikref_array_items:
            self.settingsTab.string_ikref_list.addItem(item)

        arrow_ikref_array_items = self.root.attr("arrow_ikref_array").get().split(",")
        for item in arrow_ikref_array_items:
            self.settingsTab.arrow_ikref_list.addItem(item)

    def create_componentLayout(self):
        self.settings_layout = QtWidgets.QVBoxLayout()
        self.settings_layout.addWidget(self.tabs)
        self.settings_layout.addWidget(self.close_button)

        self.setLayout(self.settings_layout)

    def create_componentConnections(self):
        self.settingsTab.grip_ro_cmb.currentIndexChanged.connect(
            partial(self.updateComboBox,
                    self.settingsTab.grip_ro_cmb,
                    "grip_rotorder"))

        self.settingsTab.grip_ikref_add_but.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.grip_ikref_list,
                    "grip_ikref_array"))

        self.settingsTab.grip_ikref_remove_but.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.grip_ikref_list,
                    "grip_ikref_array"))

        self.settingsTab.string_ikref_add_but.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.string_ikref_list,
                    "string_ikref_array"))

        self.settingsTab.string_ikref_remove_but.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.string_ikref_list,
                    "string_ikref_array"))

        self.settingsTab.arrow_ikref_add_but.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.arrow_ikref_list,
                    "arrow_ikref_array"))

        self.settingsTab.arrow_ikref_remove_but.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.arrow_ikref_list,
                    "arrow_ikref_array"))

        self.settingsTab.grip_ikref_list.installEventFilter(self)
        self.settingsTab.string_ikref_list.installEventFilter(self)
        self.settingsTab.arrow_ikref_remove_but.installEventFilter(self)

    def eventFilter(self, sender, event):
        if event.type() == QtCore.QEvent.ChildRemoved:
            if sender == self.settingsTab.grip_ikref_list:
                self.updateListAttr(sender, 'grip_ikref_array')
            elif sender == self.settingsTab.string_ikref_list:
                self.updateListAttr(sender, 'string_ikref_array')
            elif sender == self.settingsTab.arrow_ikref_list:
                self.updateListAttr(sender, 'arrow_ikref_array')
            return True
        else:
            return QtWidgets.QDialog.eventFilter(self, sender, event)

    def dockCloseEventTriggered(self):
        pyqt.deleteInstances(self, MayaQDockWidget)
