"""
Guide for the Technically Games Chain module
"""

from functools import partial

from mgear.shifter.component import guide
from mgear.core import pyqt
from mgear.vendor.Qt import QtWidgets, QtCore

from PySide2 import QtWidgets
from PySide2 import QtCore

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.general.mayaMixin import MayaQDockWidget


# guide info
AUTHOR = "TB Wright"
URL = "www.tbwrightartist.com"
EMAIL = "tbwrightartist@gmail.com"
VERSION = [1, 0, 0]
TYPE = "TG_chain"
NAME = "chain"
DESCRIPTION = "A module that makes a simple FK chain with an FK controller at the top"


class Guide(guide.ComponentGuide):
    """Component Guide Class"""

    compType = TYPE
    compName = NAME
    description = DESCRIPTION

    author = AUTHOR
    url = URL
    email = EMAIL
    version = VERSION

    def postInit(self):
        """Initialize the position for the guide"""

        self.save_transform = ["root", "#_loc"]
        self.save_blade = ["blade"]
        self.addMinMax("#_loc", 1, -1)

    def addObjects(self):
        """Add the Guide Root, blade and locators"""

        self.root = self.addRoot()
        self.locs = self.addLocMulti("#_loc", self.root)
        self.blade = self.addBlade("blade", self.root, self.locs[0])

        centers = [self.root]
        centers.extend(self.locs)
        self.dispcrv = self.addDispCurve("crv", centers)

    def addParameters(self):
        """Add the configurations settings"""

        self.pNeutralPose = self.addParam("neutralpose", "bool", False)
        self.pOverrideNegate = self.addParam("overrideNegate", "bool", False)
        self.pAddJoints = self.addParam("addJoints", "bool", True)
        self.pUseIndex = self.addParam("useIndex", "bool", False)
        self.pParentJointIndex = self.addParam(
            "parentJointIndex", "long", -1, None, None)


class settingsTab(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(settingsTab, self).__init__(parent)
        self.generate_ui()

    def generate_ui(self):
        self.setObjectName('Form')
        main_layout = QtWidgets.QVBoxLayout(self)

        self.neutral_pose_cb = QtWidgets.QCheckBox('Neutral Pose')
        self.override_cb = QtWidgets.QCheckBox('Override Negate Axis for R side')
        self.joint_cb = QtWidgets.QCheckBox('Add Joints')

        main_layout.addWidget(self.neutral_pose_cb)
        main_layout.addWidget(self.override_cb)
        main_layout.addWidget(self.joint_cb)
        main_layout.setAlignment(QtCore.Qt.AlignTop)


class componentSettings(MayaQWidgetDockableMixin, guide.componentMainSettings):

    def __init__(self, parent=None):
        self.toolName = TYPE
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
        self.resize(280, 350)

    def create_componentControls(self):
        return

    def populate_componentControls(self):
        """Populate Controls

        Populate the controls values from the custom attributes of the
        component.

        """
        # populate tab
        self.tabs.insertTab(1, self.settingsTab, "Component Settings")

        # populate component settings
        self.populateCheck(self.settingsTab.neutral_pose_cb,
                "neutralpose")
        self.populateCheck(self.settingsTab.override_cb,
                "overrideNegate")
        self.populateCheck(self.settingsTab.joint_cb,
                "addJoints")

    def create_componentLayout(self):

        self.settings_layout = QtWidgets.QVBoxLayout()
        self.settings_layout.addWidget(self.tabs)
        self.settings_layout.addWidget(self.close_button)

        self.setLayout(self.settings_layout)

    def create_componentConnections(self):

        self.settingsTab.neutral_pose_cb.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.neutral_pose_cb,
                    "neutralpose"))

        self.settingsTab.override_cb.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.override_cb,
                    "overrideNegate"))

        self.settingsTab.joint_cb.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.joint_cb,
                    "addJoints"))

    def dockCloseEventTriggered(self):
        pyqt.deleteInstances(self, MayaQDockWidget)