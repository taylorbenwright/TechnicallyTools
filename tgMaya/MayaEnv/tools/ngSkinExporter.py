"""
An ngSkin mass exporter that keeps track of the objects in the scene and exports those to json files
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om2
from ngSkinTools2 import api as ngst_api
from PySide2 import QtWidgets
from PySide2.QtCore import Qt, Signal
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

EXPORT_PATH_ATTR_NAME = 'exportPath'


class ngSkinTool(object):

    @staticmethod
    def get_ngskinned_mesh(ngskin_name):
        """
        Given the name of a ngst2SkinLayerData node, walks the chain and returns the name of the mesh associated with it
        :param ngskin_name: the name of the ngst2SkinLayerData noe
        :type ngskin_name: str
        :return: the name of the associated mesh
        :rtype: str
        """
        try:
            skin_cluster = cmds.listConnections('{}.skinCluster'.format(ngskin_name), s=True)[0]
            mesh = cmds.listConnections('{}.outputGeometry'.format(skin_cluster), d=True)[0]
            return mesh
        except TypeError:
            print("Skipping ngst2SkinLayerData '{}'. It may be invalid.".format(ngskin_name))

    def __init__(self, force_refresh_callable):
        self._after_scene_open_callback_id = None
        self._node_added_callback_id = None
        self._node_removed_callback_ids = []
        self._node_renamed_callback_ids = []
        self._node_connection_callback_ids = []
        self._export_path = cmds.optionVar(q='ngSkinExporter_Path') if cmds.optionVar(exists='ngSkinExporter_Path') else ''
        self._layer_datum = dict()
        self.reload_ngskinned_objects()
        self.force_refresh_signal = force_refresh_callable  # type: callable

    @property
    def export_path(self):
        """
        The directory path to export skins to
        :return: The absolute export path
        :rtype: str
        """
        return self._export_path

    @export_path.setter
    def export_path(self, value):
        cmds.optionVar(sv=('ngSkinExporter_Path', value))
        self._export_path = value

    @property
    def layer_datum(self):
        """
        Returns the layer data information in the exporter
        :return: a dict of mesh: layerdata names
        :rtype: dict
        """
        return self._layer_datum

    @layer_datum.setter
    def layer_datum(self, new_data):
        """
        Sets the layer data dict on the tool
        :param new_data: A dict of mesh: layerdata names
        :type new_data: dict
        :return: Nothing
        :rtype: None
        """
        self._layer_datum = new_data

    def load_callbacks(self):
        """
        Loads the callbacks that keep the dialog up-to-date
        :return: Nothing.
        :rtype: None
        """
        try:
            self._after_scene_open_callback_id = om2.MSceneMessage.addCallback(om2.MSceneMessage.kAfterOpen, self.after_scene_opened_callback)
            self._node_added_callback_id = om2.MDGMessage.addNodeAddedCallback(self.ngskin_node_added_callback, 'ngst2SkinLayerData')
            for layerdata in self.layer_datum.values():
                mobj = (om2.MSelectionList().add(layerdata)).getDependNode(0)
                self._node_removed_callback_ids.append(
                    om2.MNodeMessage.addNodePreRemovalCallback(mobj, self.ngskin_node_removed_callback))
        except RuntimeError:
            print('Please initiate ngSkin and then reopen dialog.')

    def remove_all_callbacks(self):
        """
        Removes all the valid callbacks that have been added while the dialog is open
        :return: Nothing
        :rtype: None
        """
        if self._after_scene_open_callback_id is not None:
            om2.MMessage.removeCallback(self._after_scene_open_callback_id)
        if self._node_added_callback_id is not None:
            om2.MMessage.removeCallback(self._node_added_callback_id)
        for callback in self._node_removed_callback_ids:
            try:
                om2.MMessage.removeCallback(callback)
            except RuntimeError:
                continue
        for callback in self._node_renamed_callback_ids:
            try:
                om2.MMessage.removeCallback(callback)
            except RuntimeError:
                continue
        for callback in self._node_connection_callback_ids:
            try:
                om2.MMessage.removeCallback(callback)
            except RuntimeError:
                continue

    def after_scene_opened_callback(self, *args):
        self.reload_and_send()

    def ngskin_node_added_callback(self, *args):
        """
        We need to register a name-change callback for newly added objects to properly capture them.
        :param args: args[0] is the original name of the new node
        :type args: str
        :return: Nothing
        :rtype: None
        """
        self._node_renamed_callback_ids.append(om2.MNodeMessage.addNameChangedCallback(args[0], self.ngskin_node_renamed_callback))
        self._node_removed_callback_ids.append(om2.MNodeMessage.addNodePreRemovalCallback(args[0], self.ngskin_node_removed_callback))

    def ngskin_node_renamed_callback(self, *args):
        """
        Now that the new node has been renamed, we just need to refresh
        :return: Nothing
        :rtype: None
        """
        mobj = (om2.MSelectionList().add(args[0]).getDependNode(0))
        self._node_connection_callback_ids.append(om2.MNodeMessage.addAttributeChangedCallback(mobj, self.ngskin_node_connection_callback))

    def ngskin_node_removed_callback(self, *args):
        """
        Captures the name of the node about to be deleted then pop it from out list before forcing a refresh on the UI
        :param args: args[0] is the name of the object queued for deletion
        :type args: str
        :return: Nothing
        :rtype: None
        """
        mesh_name = self.get_ngskinned_mesh(om2.MFnDependencyNode(args[0]).absoluteName())
        self.layer_datum.pop(mesh_name)
        self.force_refresh_signal()

    def ngskin_node_connection_callback(self, *args):
        if not bool(args[0] & om2.MNodeMessage.kConnectionMade):
            pass
        if bool(args[0] | om2.MNodeMessage.kConnectionBroken):
            pass
        self.reload_ngskinned_objects()
        self.force_refresh_signal()
        om2.MMessage.removeCallback(self._node_connection_callback_ids[-1])

    def get_ngskinned_objects(self):
        """
        Gathers all the ngst2SkinLayerData nodes in the scene and then returns all their meshed
        :return: A list of all the mesh names that use ngSkin in the scene
        :rtype: list
        """
        new_datum = dict()
        ngskin_nodes = cmds.ls(type='ngst2SkinLayerData')
        for layerdata in ngskin_nodes:
            mesh_name = self.get_ngskinned_mesh(layerdata)
            if mesh_name is not None:
                new_datum[mesh_name] = layerdata
        return new_datum

    def reload_ngskinned_objects(self):
        """
        Regather all the ngSkinned meshes in the scene
        :return: Nothing
        :rtype: None
        """
        self.layer_datum = self.get_ngskinned_objects()

    def reload_and_send(self):
        """
        Regathers all the ngSKinned meshes in the scene and then forced a UI refresh
        :return: Nothing
        :rtype: None
        """
        self.reload_ngskinned_objects()
        self.force_refresh_signal()

    def export_skin(self, mesh_name):
        """
        Exports a named ngSkin mesh to a json file at the designated export path
        :param mesh_name: The name of the mesh to export
        :type mesh_name: str
        :return: Nothing
        :rtype: None
        """
        if self.export_path == '':
            print('Please select an export path before exporting.')
            return

        ngst_api.export_json(mesh_name, file='{}/{}.json'.format(self.export_path, mesh_name))
        print("ngSkin '{}' exported successively.".format(mesh_name))

    def export_all(self):
        """
        Exports all the ngSkin meshes in the scene
        :return: Nothing
        :rtype: None
        """
        for mesh in self.layer_datum:
            self.export_skin(mesh)


class SkinEntry(QtWidgets.QFrame):

    export_pressed_signal = Signal(str)

    def __init__(self, current_mesh, parent=None):
        """
        Creates a widget for a skin entry into the tool
        :param current_mesh: The current mesh this entry is set to
        :type current_mesh: str
        """
        super(SkinEntry, self).__init__(parent=parent)
        self._current_mesh = current_mesh

        self.setLineWidth(1)
        self.setMinimumWidth(500)
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        main_layout = QtWidgets.QVBoxLayout()
        skin_layout = QtWidgets.QHBoxLayout()

        cluster_label = QtWidgets.QLabel('Skin:    ')
        self.cluster_le = QtWidgets.QLineEdit()
        self.cluster_le.setText(self._current_mesh)
        self.cluster_le.setReadOnly(True)
        self.cluster_le.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        export_but = QtWidgets.QPushButton('Export')
        export_but.clicked.connect(self.export_pressed)

        skin_layout.addWidget(cluster_label)
        skin_layout.addWidget(self.cluster_le)
        skin_layout.addWidget(export_but)

        main_layout.addLayout(skin_layout)

        self.setLayout(main_layout)

    def export_pressed(self):
        """
        Send the name of this entry up the chain to be exported
        :return: Nothing
        :rtype: None
        """
        self.export_pressed_signal.emit(self._current_mesh)


class NGSkinExporter(MayaQWidgetBaseMixin, QtWidgets.QDialog):

    instance = None

    def __init__(self, parent=None):
        """
        Creates the main dialog for the tool
        """
        super(NGSkinExporter, self).__init__(parent=parent)

        self.tool = None
        self.items = []

        self.generate_ui()

        self.setFixedWidth(550)
        self.setObjectName('ngskin_exporter')
        self.setWindowTitle('ngSkin Exporter')
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def generate_ui(self):
        """
        Sets up the ui
        :return: Nothing
        :rtype: None
        """
        main_layout = QtWidgets.QVBoxLayout()
        scrollbox = QtWidgets.QScrollArea()
        scrollbox.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scrollbox_widget = QtWidgets.QWidget()
        self.scrollbox_layout = QtWidgets.QVBoxLayout()

        self.scrollbox_layout.setAlignment(Qt.AlignTop)
        self.scrollbox_layout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.scrollbox_layout.setSpacing(3)
        scrollbox_widget.setLayout(self.scrollbox_layout)
        scrollbox_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        scrollbox.setWidget(scrollbox_widget)

        bottom_layout = QtWidgets.QVBoxLayout()

        path_layout = QtWidgets.QHBoxLayout()
        path_label = QtWidgets.QLabel('Path:    ')
        self.path_le = QtWidgets.QLineEdit()
        self.path_le.editingFinished.connect(self.path_le_edited)
        path_browse = QtWidgets.QPushButton('...')
        path_browse.setFixedWidth(35)
        path_browse.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        path_browse.clicked.connect(self.browse_pressed)
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_le)
        path_layout.addWidget(path_browse)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setAlignment(Qt.AlignRight)
        export_all_but = QtWidgets.QPushButton('Export All')
        export_all_but.clicked.connect(self.export_all_pressed)
        button_layout.addWidget(export_all_but)

        bottom_layout.addLayout(path_layout)
        bottom_layout.addLayout(button_layout)

        main_layout.addWidget(scrollbox)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def add_item(self, mesh):
        """
        Adds an item entry to the scrollbox layout and connect to its export signal
        :param mesh: The name of the mesh to put on this SkinEntry
        :type mesh: str
        :return: Nothing
        :rtype: None
        """
        new_item = SkinEntry(mesh)
        new_item.export_pressed_signal.connect(self.item_export_pressed)
        self.scrollbox_layout.addWidget(new_item)
        self.items.append(new_item)

    def clear_items(self):
        """
        Clears out the scrollbox layout
        :return: Nothing
        :rtype: None
        """
        num_children = self.scrollbox_layout.count()
        for ind in reversed(range(num_children)):
            item = self.scrollbox_layout.takeAt(ind)  # type: QtWidgets.QLayoutItem
            self.items.pop(ind)
            item.widget().deleteLater()

    def load_items(self):
        """
        Loads all items saved on the tool and refresh the export path
        :return: Nothing
        :rtype: None
        """
        self.path_le.setText(self.tool.export_path)
        for mesh, layerdata in sorted(self.tool.layer_datum.items()):
            self.add_item(mesh)

    def refresh_items(self):
        """
        Refresh the dialog
        :return: Nothing
        :rtype: None
        """
        self.clear_items()
        self.load_items()

    def item_export_pressed(self, skin_name):
        """
        Signal to pass on to the tool from an individual SkinEntry
        :param skin_name: the name of the mesh to export
        :type skin_name: str
        :return: Nothing
        :rtype: None
        """
        self.tool.export_skin(skin_name)

    def export_all_pressed(self):
        """
        Signal to the tool to export all meshes
        :return: Nothing
        :rtype: None
        """
        self.tool.export_all()

    def showEvent(self, *args):
        """
        Event to fire when the dialog is shown. Load callbacks, set up items, set export path
        :return: Nothing
        :rtype: None
        """
        self.tool = ngSkinTool(self.refresh_items)
        self.tool.load_callbacks()
        self.clear_items()
        self.load_items()

    def closeEvent(self, *args):
        """
        Event to fire when the dialog is closed. We just need to unload all callbacks here
        :return: Nothing
        :rtype: None
        """
        self.tool.remove_all_callbacks()
        self.tool = None
        NGSkinExporter.instance = None

    def browse_pressed(self):
        """
        Open a file dialog and gather the chosen directory, then set the path line edit
        :return: Nothing
        :rtype: None
        """
        directory = QtWidgets.QFileDialog.getExistingDirectory(parent=self, caption='Export Directory')
        self.path_le.setText(directory)
        self.path_le.editingFinished.emit()

    def path_le_edited(self):
        """
        Set the export path on the tool based on what's in the line edit. We did this to capture when the use has
        manually typed something into the field.
        :return: Nothing
        :rtype: None
        """
        self.tool.export_path = self.path_le.text()


def create_dialog(*args):
    if NGSkinExporter.instance is None:
        NGSkinExporter.instance = NGSkinExporter()
    NGSkinExporter.instance.show()
    NGSkinExporter.instance.raise_()
