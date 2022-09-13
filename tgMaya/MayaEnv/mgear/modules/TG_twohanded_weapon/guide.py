"""
Guide for the two-handed weapon module
"""

from functools import partial
from PySide2 import QtWidgets, QtCore

from mgear.shifter.component import guide
from mgear.core import transform, pyqt

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.general.mayaMixin import MayaQDockWidget


# guide info
AUTHOR = "TB Wright"
URL = "www.tbwrightartist.com"
EMAIL = "tbwrightartist@gmail.com"
VERSION = [1, 0, 0]
TYPE = "TG_twohanded_weapon"
NAME = "twohandedweapon"
DESCRIPTION = "Module for two-handed weapons. Assumes that the right hand is the dominant hand. Creates one joint"  \
              "at the mid locator."
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

    connectors = ["orientation"]

    # =====================================================
    ##
    # @param self
    def postInit(self):
        self.save_transform = ["root", 'top', 'mid', 'bottom']

    # =====================================================
    # Add more object to the object definition list.
    # @param self
    def addObjects(self):

        self.root = self.addRoot()
        self.top = self.addLoc('top', self.root, transform.getOffsetPosition(self.root, [0, 0, 0]))
        self.mid = self.addLoc('mid', self.root, transform.getOffsetPosition(self.root, [0, -5, 0]))
        self.bottom = self.addLoc('bottom', self.root, transform.getOffsetPosition(self.mid, [0, -5, 0]))

        self.disp_crv = self.addDispCurve('crv', [self.top, self.mid, self.bottom])

    # =====================================================
    # Add more parameter to the parameter definition list.
    # @param self
    def addParameters(self):

        self.top_ikref_array = self.addParam('top_ikref_array', 'string', '')

        self.top_joint = self.addParam('top_joint', 'bool', False)
        self.mid_joint = self.addParam('mid_joint', 'bool', False)
        self.bot_joint = self.addParam('bot_joint', 'bool', False)

        self.top_RotOrder = self.addParam("top_rotorder", "long", 0, 0, 5)
        self.mid_RotOrder = self.addParam("mid_rotorder", "long", 0, 0, 5)
        self.bot_RotOrder = self.addParam("bot_rotorder", "long", 0, 0, 5)

        self.pUseIndex = self.addParam("useIndex", "bool", False)
        self.pParentJointIndex = self.addParam(
            "parentJointIndex", "long", -1, None, None)

        return

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
        self.resize(733, 550)
        main_layout = QtWidgets.QVBoxLayout(self)

        top_groupbox = QtWidgets.QGroupBox()
        top_layout = QtWidgets.QVBoxLayout(top_groupbox)

        top_hbox = QtWidgets.QHBoxLayout()
        self.top_joint_chx = QtWidgets.QCheckBox('Top Joint')
        self.top_ro_cmb = QtWidgets.QComboBox()
        self.top_ro_cmb.addItems(ro_list)
        top_hbox.addWidget(self.top_joint_chx)
        top_hbox.addWidget(self.top_ro_cmb)

        mid_hbox = QtWidgets.QHBoxLayout()
        self.mid_joint_chx = QtWidgets.QCheckBox('Middle Joint')
        self.mid_ro_cmb = QtWidgets.QComboBox()
        self.mid_ro_cmb.addItems(ro_list)
        mid_hbox.addWidget(self.mid_joint_chx)
        mid_hbox.addWidget(self.mid_ro_cmb)

        bot_hbox = QtWidgets.QHBoxLayout()
        self.bot_joint_chx = QtWidgets.QCheckBox('Bottom Joint')
        self.bot_ro_cmb = QtWidgets.QComboBox()
        self.bot_ro_cmb.addItems(ro_list)
        bot_hbox.addWidget(self.bot_joint_chx)
        bot_hbox.addWidget(self.bot_ro_cmb)

        top_ikref_groupbox = QtWidgets.QGroupBox('IK Reference Array')
        top_ikref_layout = QtWidgets.QHBoxLayout(top_ikref_groupbox)
        self.ikref_list = QtWidgets.QListWidget()
        self.ikref_list.setDragDropOverwriteMode(True)
        self.ikref_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.ikref_list.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.ikref_list.setAlternatingRowColors(True)
        self.ikref_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.ikref_list.setSelectionRectVisible(False)
        top_ikref_layout.addWidget(self.ikref_list)

        top_ikbuts_layout = QtWidgets.QVBoxLayout()
        self.ikref_add_but = QtWidgets.QPushButton('<<')
        self.ikref_remove_but = QtWidgets.QPushButton('<<')
        top_ikref_but_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        top_ikbuts_layout.addWidget(self.ikref_add_but)
        top_ikbuts_layout.addWidget(self.ikref_remove_but)
        top_ikbuts_layout.addItem(top_ikref_but_spacer)
        top_ikref_layout.addLayout(top_ikbuts_layout)

        top_layout.addLayout(top_hbox)
        top_layout.addLayout(mid_hbox)
        top_layout.addLayout(bot_hbox)
        top_layout.addWidget(top_ikref_groupbox)

        main_layout.addWidget(top_groupbox)


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

        self.populateCheck(self.settingsTab.top_joint_chx, "top_joint")
        self.populateCheck(self.settingsTab.mid_joint_chx, "mid_joint")
        self.populateCheck(self.settingsTab.bot_joint_chx, "bot_joint")

        self.settingsTab.top_ro_cmb.setCurrentIndex(self.root.attr("top_rotorder").get())
        self.settingsTab.mid_ro_cmb.setCurrentIndex(self.root.attr("mid_rotorder").get())
        self.settingsTab.bot_ro_cmb.setCurrentIndex(self.root.attr("bot_rotorder").get())

        ik_ref_array_items = self.root.attr("top_ikref_array").get().split(",")
        for item in ik_ref_array_items:
            self.settingsTab.ikref_list.addItem(item)

    def create_componentLayout(self):
        self.settings_layout = QtWidgets.QVBoxLayout()
        self.settings_layout.addWidget(self.tabs)
        self.settings_layout.addWidget(self.close_button)

        self.setLayout(self.settings_layout)

    def create_componentConnections(self):
        self.settingsTab.top_joint_chx.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.top_joint_chx,
                    'top_joint'))

        self.settingsTab.mid_joint_chx.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.mid_joint_chx,
                    'mid_joint'))

        self.settingsTab.bot_joint_chx.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.bot_joint_chx,
                    'bot_joint'))

        self.settingsTab.top_ro_cmb.currentIndexChanged.connect(
            partial(self.updateComboBox,
                    self.settingsTab.top_ro_cmb,
                    "top_rotorder"))

        self.settingsTab.mid_ro_cmb.currentIndexChanged.connect(
            partial(self.updateComboBox,
                    self.settingsTab.mid_ro_cmb,
                    "mid_rotorder"))

        self.settingsTab.bot_ro_cmb.currentIndexChanged.connect(
            partial(self.updateComboBox,
                    self.settingsTab.bot_ro_cmb,
                    "bot_rotorder"))

        self.settingsTab.ikref_add_but.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.ikref_list,
                    "top_ikref_array"))
        self.settingsTab.ikref_add_but.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.ikref_list,
                    "top_ikref_array"))
        self.settingsTab.ikref_list.installEventFilter(self)

    def eventFilter(self, sender, event):
        if event.type() == QtCore.QEvent.ChildRemoved:
            if sender == self.settingsTab.ikref_list:
                self.updateListAttr(sender, 'top_ikref_array')
            return True
        else:
            return QtWidgets.QDialog.eventFilter(self, sender, event)

    def dockCloseEventTriggered(self):
        pyqt.deleteInstances(self, MayaQDockWidget)
