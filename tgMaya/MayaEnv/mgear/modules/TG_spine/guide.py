from functools import partial

from mgear.shifter.component import guide
from mgear.core import transform, pyqt, vector
from PySide2 import QtWidgets, QtCore

from MayaEnv.mgear.utils import ik_reference_groubox

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.general.mayaMixin import MayaQDockWidget

# guide info
AUTHOR = "TBWright"
URL = "www.tbwrightartist.com"
EMAIL = "tbwrightartist@gmail.com"
VERSION = [1, 0, 0]
TYPE = "TG_spine"
NAME = "spine"
DESCRIPTION = "Spine module based on the EPIC_Spine module. Allows IK parenting."

##########################################################
# CLASS
##########################################################


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
        self.save_transform = ["root",
                               "spineBase",
                               "tan0",
                               "tan1",
                               "spineTop",
                               "chest"]
        self.save_blade = ["blade"]

    def addObjects(self):
        """Add the Guide Root, blade and locators"""

        self.root = self.addRoot()
        vTemp = transform.getOffsetPosition(self.root, [0, 0, .5])
        self.spineBase = self.addLoc("spineBase", self.root, vTemp)
        vTemp = transform.getOffsetPosition(self.root, [0, 0, 4])
        self.spineTop = self.addLoc("spineTop", self.spineBase, vTemp)
        vTemp = transform.getOffsetPosition(self.root, [0, 0, 5])
        self.chest = self.addLoc("chest", self.spineTop, vTemp)

        vTan0 = vector.linearlyInterpolate(
            self.spineBase.getTranslation(space="world"),
            self.spineTop.getTranslation(space="world"),
            0.3333
        )
        self.tan0 = self.addLoc("tan0", self.spineBase, vTan0)

        vTan1 = vector.linearlyInterpolate(
            self.spineTop.getTranslation(space="world"),
            self.spineBase.getTranslation(space="world"),
            0.3333
        )
        self.tan1 = self.addLoc("tan1", self.spineTop, vTan1)

        self.blade = self.addBlade("blade", self.root, self.spineTop)

        # spine curve
        self.disp_crv_hip = self.addDispCurve(
            "crvHip", [self.root, self.spineBase])
        self.disp_crv_chst = self.addDispCurve(
            "crvChest", [self.spineTop, self.chest])
        centers = [self.spineBase, self.tan0, self.tan1, self.spineTop]
        self.dispcrv = self.addDispCurve("crv", centers, 3)
        self.dispcrv.attr("lineWidth").set(5)

        # tangent handles
        self.disp_tancrv0 = self.addDispCurve(
            "crvTan0", [self.spineBase, self.tan0])
        self.disp_tancrv1 = self.addDispCurve(
            "crvTan1", [self.spineTop, self.tan1])

    def addParameters(self):
        """Add the configurations settings"""

        # Default values
        self.pPosition = self.addParam("position", "double", 0, 0, 1)
        self.pMaxStretch = self.addParam("maxstretch", "double", 1.5, 1)
        self.pMaxSquash = self.addParam("maxsquash", "double", .5, 0, 1)
        self.pSoftness = self.addParam("softness", "double", 0, 0, 1)
        self.pLockOriPelvis = self.addParam(
            "lock_ori_pelvis", "double", 1, 0, 1)
        self.pLockOriChest = self.addParam("lock_ori_chest", "double", 1, 0, 1)

        # Options
        self.pDivision = self.addParam("division", "long", 4, 2)
        self.pAutoBend = self.addParam("autoBend", "bool", True)
        self.pCentralTangent = self.addParam("centralTangent", "bool", True)
        self.pIKWorldOri = self.addParam("IKWorldOri", "bool", True)

        # FCurves
        self.pSt_profile = self.addFCurveParam(
            "st_profile", [[0, 0], [.5, -1], [1, 0]])

        self.pSq_profile = self.addFCurveParam(
            "sq_profile", [[0, 0], [.5, 1], [1, 0]])

        self.pUseIndex = self.addParam("useIndex", "bool", False)

        self.pParentJointIndex = self.addParam(
            "parentJointIndex", "long", -1, None, None)

        self.spine_ikref_array = self.addParam('spine_ikref_array', 'string', '', niceName='Spine Space')

    def get_divisions(self):
        """ Returns correct segments divisions """

        self.divisions = self.root.division.get()

        return self.divisions


##########################################################
# Setting Page
##########################################################

class settingsTab(QtWidgets.QDialog):
    """The Component settings UI"""

    def __init__(self, parent=None):
        super(settingsTab, self).__init__(parent)

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        ctl_gridbox = QtWidgets.QGridLayout()

        softness_label = QtWidgets.QLabel('Softness')
        position_label = QtWidgets.QLabel('Position')
        lock_orient_p_label = QtWidgets.QLabel('Lock Orient Pelvis')
        lock_orient_c_label = QtWidgets.QLabel('Lock Orient Chest')
        max_stretch_label = QtWidgets.QLabel('Max Stretch')
        max_squash_label = QtWidgets.QLabel('Max Squash')
        divisions_label = QtWidgets.QLabel('Divisons')
        auto_bend_label = QtWidgets.QLabel('Auto Bend Control')
        ik_ctl_world_label = QtWidgets.QLabel('IK CTL World Ori')
        central_t_label = QtWidgets.QLabel('Central Tangent')

        self.softness_spinbox = QtWidgets.QSpinBox()
        self.softness_spinbox.setRange(0, 100)
        self.softness_spinbox.setSingleStep(10)
        self.softness_spinbox.setValue(0)

        self.position_spinbox = QtWidgets.QSpinBox()
        self.position_spinbox.setRange(0, 100)
        self.position_spinbox.setSingleStep(10)
        self.position_spinbox.setValue(0)

        self.lock_orient_p_spinbox = QtWidgets.QSpinBox()
        self.lock_orient_p_spinbox.setRange(0, 100)
        self.lock_orient_p_spinbox.setSingleStep(10)
        self.lock_orient_p_spinbox.setValue(0)

        self.lock_orient_c_spinbox = QtWidgets.QSpinBox()
        self.lock_orient_c_spinbox.setRange(0, 100)
        self.lock_orient_c_spinbox.setSingleStep(10)
        self.lock_orient_c_spinbox.setValue(0)

        self.max_stretch_spinbox = QtWidgets.QDoubleSpinBox()
        self.max_stretch_spinbox.setRange(1.0, 99.99)
        self.max_stretch_spinbox.setDecimals(2)
        self.max_stretch_spinbox.setSingleStep(.1)
        self.max_stretch_spinbox.setValue(1.5)

        self.max_squash_spinbox = QtWidgets.QDoubleSpinBox()
        self.max_squash_spinbox.setRange(.1, 1.0)
        self.max_squash_spinbox.setDecimals(2)
        self.max_squash_spinbox.setSingleStep(.1)
        self.max_squash_spinbox.setValue(.5)

        self.divisions_spinbox = QtWidgets.QSpinBox()
        self.divisions_spinbox.setRange(0, 100)
        self.divisions_spinbox.setSingleStep(10)
        self.divisions_spinbox.setValue(4)

        self.auto_bend_cb = QtWidgets.QCheckBox()
        self.auto_bend_cb.setChecked(False)
        self.ik_ctl_world_cb = QtWidgets.QCheckBox()
        self.ik_ctl_world_cb.setChecked(False)
        self.central_t_cb = QtWidgets.QCheckBox()
        self.central_t_cb.setChecked(False)

        ctl_gridbox.addWidget(softness_label, 0, 0)
        ctl_gridbox.addWidget(self.softness_spinbox, 0, 1)
        ctl_gridbox.addWidget(position_label, 1, 0)
        ctl_gridbox.addWidget(self.position_spinbox, 1, 1)
        ctl_gridbox.addWidget(lock_orient_p_label, 2, 0)
        ctl_gridbox.addWidget(self.lock_orient_p_spinbox, 2, 1)
        ctl_gridbox.addWidget(lock_orient_c_label, 3, 0)
        ctl_gridbox.addWidget(self.lock_orient_c_spinbox, 3, 1)
        ctl_gridbox.addWidget(max_stretch_label, 4, 0)
        ctl_gridbox.addWidget(self.max_stretch_spinbox, 4, 1)
        ctl_gridbox.addWidget(max_squash_label, 5, 0)
        ctl_gridbox.addWidget(self.max_squash_spinbox, 5, 1)
        ctl_gridbox.addWidget(divisions_label, 6, 0)
        ctl_gridbox.addWidget(self.divisions_spinbox, 6, 1)
        ctl_gridbox.addWidget(auto_bend_label, 7, 0)
        ctl_gridbox.addWidget(self.auto_bend_cb, 7, 1)
        ctl_gridbox.addWidget(ik_ctl_world_label, 8, 0)
        ctl_gridbox.addWidget(self.ik_ctl_world_cb, 8, 1)
        ctl_gridbox.addWidget(central_t_label, 9, 0)
        ctl_gridbox.addWidget(self.central_t_cb, 9, 1)

        self.squash_and_stretch_profile = QtWidgets.QPushButton('Squash and Stretch Profile')

        ik_groupbox = QtWidgets.QGroupBox('IK Ref: ')
        ik_layout = QtWidgets.QVBoxLayout(ik_groupbox)
        ik_ikref_grpbox, self.ikref_list, self.ikref_add_but, self.ikref_remove_but = ik_reference_groubox()
        ik_layout.addWidget(ik_ikref_grpbox)

        main_layout.addLayout(ctl_gridbox)
        main_layout.addWidget(self.squash_and_stretch_profile)
        main_layout.addWidget(ik_groupbox)


class componentSettings(MayaQWidgetDockableMixin, guide.componentMainSettings):
    """Create the component setting window"""

    def __init__(self, parent=None):
        self.toolName = TYPE
        # Delete old instances of the componet settings window.
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
        self.resize(280, 360)

    def create_componentControls(self):
        return

    def populate_componentControls(self):
        """Populate the controls values.

        Populate the controls values from the custom attributes of the
        component.

        """
        # populate tab
        self.tabs.insertTab(1, self.settingsTab, "Component Settings")

        # populate component settings

        self.settingsTab.position_spinbox.setValue(
            int(self.root.attr("position").get() * 100))

        self.settingsTab.lock_orient_p_spinbox.setValue(
            int(self.root.attr("lock_ori_pelvis").get() * 100))

        self.settingsTab.lock_orient_c_spinbox.setValue(
            int(self.root.attr("lock_ori_chest").get() * 100))

        self.settingsTab.softness_spinbox.setValue(
            int(self.root.attr("softness").get() * 100))

        self.settingsTab.max_stretch_spinbox.setValue(
            self.root.attr("maxstretch").get())

        self.settingsTab.max_squash_spinbox.setValue(
            self.root.attr("maxsquash").get())

        self.settingsTab.divisions_spinbox.setValue(
            self.root.attr("division").get())

        self.populateCheck(self.settingsTab.auto_bend_cb, "autoBend")
        self.populateCheck(self.settingsTab.ik_ctl_world_cb, "IKWorldOri")
        self.populateCheck(self.settingsTab.central_t_cb,
                           "centralTangent")

        spine_ikref_array_items = self.root.attr("spine_ikref_array").get().split(",")
        for item in spine_ikref_array_items:
            self.settingsTab.ikref_list.addItem(item)

    def create_componentLayout(self):

        self.settings_layout = QtWidgets.QVBoxLayout()
        self.settings_layout.addWidget(self.tabs)
        self.settings_layout.addWidget(self.close_button)

        self.setLayout(self.settings_layout)

    def create_componentConnections(self):
        self.settingsTab.softness_spinbox.valueChanged.connect(
            partial(self.updateSpinBox,
                    self.settingsTab.softness_spinbox,
                    "softness"))

        self.settingsTab.position_spinbox.valueChanged.connect(
            partial(self.updateSpinBox,
                    self.settingsTab.position_spinbox,
                    "position"))

        self.settingsTab.lock_orient_p_spinbox.valueChanged.connect(
            partial(self.updateSpinBox,
                    self.settingsTab.lock_orient_p_spinbox,
                    "lock_ori_pelvis"))

        self.settingsTab.lock_orient_c_spinbox.valueChanged.connect(
            partial(self.updateSpinBox,
                    self.settingsTab.lock_orient_c_spinbox,
                    "lock_ori_chest"))

        self.settingsTab.max_stretch_spinbox.valueChanged.connect(
            partial(self.updateSpinBox,
                    self.settingsTab.max_stretch_spinbox,
                    "maxstretch"))

        self.settingsTab.max_squash_spinbox.valueChanged.connect(
            partial(self.updateSpinBox,
                    self.settingsTab.max_squash_spinbox,
                    "maxsquash"))

        self.settingsTab.divisions_spinbox.valueChanged.connect(
            partial(self.updateSpinBox,
                    self.settingsTab.divisions_spinbox,
                    "division"))

        self.settingsTab.auto_bend_cb.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.auto_bend_cb,
                    "autoBend"))

        self.settingsTab.ik_ctl_world_cb.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.ik_ctl_world_cb,
                    "IKWorldOri"))

        self.settingsTab.central_t_cb.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.central_t_cb,
                    "centralTangent"))

        self.settingsTab.ikref_add_but.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.ikref_list,
                    "spine_ikref_array"))

        self.settingsTab.ikref_remove_but.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.ikref_list,
                    "spine_ikref_array"))

        self.settingsTab.squash_and_stretch_profile.clicked.connect(
            self.setProfile)

        self.settingsTab.ikref_list.installEventFilter(self)

    def eventFilter(self, sender, event):
        if event.type() == QtCore.QEvent.ChildRemoved:
            if sender == self.settingsTab.ikref_list:
                self.updateListAttr(sender, 'spine_ikref_array')
            return True
        else:
            return QtWidgets.QDialog.eventFilter(self, sender, event)

    def dockCloseEventTriggered(self):
        pyqt.deleteInstances(self, MayaQDockWidget)
