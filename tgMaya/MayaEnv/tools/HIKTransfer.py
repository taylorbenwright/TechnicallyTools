
import maya.cmds as cmds
import os
import shutil
import MayaEnv.utils.hikUtils as hik_utils
from MayaEnv.tools import BaseDialog
from widgets import ps2_BoxLayoutSeparator
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from PySide2 import QtWidgets
from PySide2.QtCore import Qt


class HIKTransferDialog(MayaQWidgetBaseMixin, QtWidgets.QDialog):

    _instance = None

    def __init__(self, parent=None):
        super(HIKTransferDialog, self).__init__(parent=parent)

        self.setWindowTitle('XSense HIK Transfer')
        self.generate_ui()
        self.setFixedSize(850, self.sizeHint().height())

    def generate_ui(self):
        main_layout = QtWidgets.QVBoxLayout()

        target_source_layout = QtWidgets.QGridLayout()
        hik_label = QtWidgets.QLabel('HIK Base File:')
        self.hik_line = QtWidgets.QLineEdit()
        self.hik_line.setPlaceholderText('Path to HIK Base file...')
        hik_browse_but = QtWidgets.QPushButton('...')
        hik_browse_but.clicked.connect(self.base_hik_browse_pressed)
        hik_bindpose_label = QtWidgets.QLabel('HIK Base Name:')
        self.hik_bindpose_name = QtWidgets.QLineEdit()

        anim_source_label = QtWidgets.QLabel('Anim source folder: ')
        self.anim_source_line = QtWidgets.QLineEdit()
        self.anim_source_line.setPlaceholderText('Path to anim source files...')
        anim_source_browse_but = QtWidgets.QPushButton('...')
        anim_source_browse_but.clicked.connect(self.base_anim_source_browse_pressed)

        target_label = QtWidgets.QLabel('Target HIK File:')
        self.target_line = QtWidgets.QLineEdit()
        self.target_line.setPlaceholderText('Path to Target HIK file...')
        target_browse_but = QtWidgets.QPushButton('...')
        target_browse_but.clicked.connect(self.target_hik_browse_pressed)
        target_bindpose_label = QtWidgets.QLabel('Target Name:')
        self.target_bindpose_name = QtWidgets.QLineEdit()

        baked_label = QtWidgets.QLabel('Output Folder:     ')
        self.baked_line = QtWidgets.QLineEdit()
        self.baked_line.setPlaceholderText('Path to baked HIK files...')
        baked_browse_but = QtWidgets.QPushButton('...')
        baked_browse_but.clicked.connect(self.output_browse_pressed)

        target_source_layout.addWidget(hik_label, 0, 0)
        target_source_layout.addWidget(self.hik_line, 0, 1)
        target_source_layout.addWidget(hik_browse_but, 0, 2)
        target_source_layout.addWidget(hik_bindpose_label, 1, 0)
        target_source_layout.addWidget(self.hik_bindpose_name, 1, 1)
        target_source_layout.addWidget(anim_source_label, 2, 0)
        target_source_layout.addWidget(self.anim_source_line, 2, 1)
        target_source_layout.addWidget(anim_source_browse_but, 2, 2)
        target_source_layout.addWidget(ps2_BoxLayoutSeparator.BoxLayoutSeparator(QtWidgets.QFrame.HLine), 3, 0)
        target_source_layout.addWidget(ps2_BoxLayoutSeparator.BoxLayoutSeparator(QtWidgets.QFrame.HLine), 3, 1)
        target_source_layout.addWidget(ps2_BoxLayoutSeparator.BoxLayoutSeparator(QtWidgets.QFrame.HLine), 3, 2)
        target_source_layout.addWidget(target_label, 4, 0)
        target_source_layout.addWidget(self.target_line, 4, 1)
        target_source_layout.addWidget(target_browse_but, 4, 2)
        target_source_layout.addWidget(target_bindpose_label, 5, 0)
        target_source_layout.addWidget(self.target_bindpose_name, 5, 1)
        target_source_layout.addWidget(ps2_BoxLayoutSeparator.BoxLayoutSeparator(QtWidgets.QFrame.HLine), 6, 0)
        target_source_layout.addWidget(ps2_BoxLayoutSeparator.BoxLayoutSeparator(QtWidgets.QFrame.HLine), 6, 1)
        target_source_layout.addWidget(ps2_BoxLayoutSeparator.BoxLayoutSeparator(QtWidgets.QFrame.HLine), 6, 2)
        target_source_layout.addWidget(baked_label, 7, 0)
        target_source_layout.addWidget(self.baked_line, 7, 1)
        target_source_layout.addWidget(baked_browse_but, 7, 2)

        go_btn = QtWidgets.QPushButton('Execute')
        go_btn.clicked.connect(self.go_clicked)

        main_layout.addLayout(target_source_layout)
        main_layout.addWidget(ps2_BoxLayoutSeparator.BoxLayoutSeparator(QtWidgets.QFrame.HLine))
        main_layout.addWidget(go_btn)
        main_layout.setAlignment(Qt.AlignTop)

        self.setLayout(main_layout)

    def dialog_opened(self):
        return

    def dialog_closed(self):
        HIKTransferDialog._instance = None

    def base_hik_browse_pressed(self):
        """
        Opens a file dialog to browse to the base HIK file
        :return: Nothing
        :rtype: None
        """
        hik_base_file, _filter = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption="Find Base HIK File",
                                                                       dir=".", filter="Maya Scenes (*.ma *.mb)")
        self.hik_line.setText(hik_base_file)
        if hik_base_file is not None:
            file_path, file_name = os.path.split(hik_base_file)
            baked_anims_folder_name = file_path + "/baked/"

            self.baked_line.setText(baked_anims_folder_name)

    def base_anim_source_browse_pressed(self):
        """
        Opens a file dialog to browse to where all the source animations are
        :return: Nothing
        :rtype: None
        """
        directory = QtWidgets.QFileDialog.getExistingDirectory(parent=self, caption="Source Animation Directory")
        self.anim_source_line.setText(directory)

    def target_hik_browse_pressed(self):
        hik_base_file, _filter = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption="Find Target HIK File",
                                                                       dir=".", filter="Maya Scenes (*.ma *.mb)")
        self.target_line.setText(hik_base_file)

    def output_browse_pressed(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(parent=self, caption="Choose Output Directory")
        self.baked_line.setText(directory)

    def go_clicked(self):
        if self.hik_line.text() is None:
            cmds.warning('Must give a valid HIK Base file.')
            return

        cmds.refresh(suspend=True)

        cancelled = False
        ind_val = 0

        fbx_animation_files = [fbx_file for fbx_file in os.listdir(self.anim_source_line.text()) if fbx_file.endswith('.fbx')]
        num_files = len(fbx_animation_files) * 2

        progress_bar = QtWidgets.QProgressDialog("Transfer HIK Animations...", "Abort", 0, num_files, parent=self)
        progress_bar.setWindowModality(Qt.WindowModal)

        int_path = os.path.split(self.hik_line.text())[0] + '/_intermediate/'

        # Import animation FBXs onto the Base HIK character
        cmds.file(self.hik_line.text(), force=True, options='v=0;', ignoreVersion=True, type='mayaAscii', open=True)
        for ind, fbx_file in enumerate(fbx_animation_files):
            if cancelled:
                return

            print('Import FBX animation file: {}'.format(fbx_file))

            progress_bar.setLabelText('Importing animation: {}'.format(fbx_file))
            progress_bar.setValue(ind_val)
            ind_val += 1

            full_path = self.anim_source_line.text() + '/' + fbx_file
            self.import_animation_and_save(full_path, int_path)

            if progress_bar.wasCanceled():
                cancelled = True

        intermediary_files = [ma_file for ma_file in os.listdir(int_path) if ma_file.endswith('.ma')]

        # Move animations onto Target character and bake
        for ind, ma_file in enumerate(intermediary_files):
            if cancelled:
                return
            cmds.file(self.target_line.text(), force=True, options='v=0;', ignoreVersion=True, type='mayaAscii', open=True)

            print('Referencing and baking animation file: {}'.format(ma_file))

            progress_bar.setLabelText('Baking animation: {}'.format(ma_file))
            progress_bar.setValue(ind_val)
            ind_val += 1

            full_path = int_path + ma_file
            source_name = ma_file.split('.')[0]
            source_name = source_name + ':' + self.hik_bindpose_name.text()
            source_name = source_name.replace('-', '_')

            self.reference_animation(full_path)
            self.bake_anim_to_HIK_character(self.target_bindpose_name.text(), source_name)

            save_path = self.baked_line.text()
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            cmds.file(full_path, removeReference=True)

            file_name = ma_file.split('.')[0]
            cmds.file(rename=save_path + "/" + file_name + '_' + self.target_bindpose_name.text())
            cmds.file(s=True, typ='mayaAscii', force=True)

            if progress_bar.wasCanceled():
                cancelled = True

        progress_bar.setValue(num_files)
        shutil.rmtree(int_path)
        cmds.refresh(suspend=False)

    def import_animation_and_save(self, import_path, save_path):
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        file_path, file_name = os.path.split(import_path)
        file_name = file_name.split('.')[0]
        cmds.file(import_path, i=True, type="FBX", ignoreVersion=True, renameAll=True, mergeNamespacesOnClash=False,
                  namespace=file_name.replace('-', '_'), options="v=0;p=17;f=0", pr=True, importTimeRange="override")
        cmds.file(rename=save_path + "/" + file_name + ".ma")
        cmds.file(s=True, typ='mayaAscii', force=True)

    def reference_animation(self, anim_path):
        file_path, file_name = os.path.split(anim_path)
        file_name = file_name.split('.')[0]
        truncated_name = file_name.replace('-', '_')
        cmds.file(file_path + "/" + file_name + ".ma", r=True, typ='mayaAscii', gl=True,
                  mergeNamespacesOnClash=False, namespace=truncated_name, options='v=0')
        keyframe_range = cmds.keyframe('{}:Hips'.format(truncated_name), q=True)
        cmds.playbackOptions(min=int(keyframe_range[0]), max=int(keyframe_range[-1]))

    def bake_anim_to_HIK_character(self, target_name, source_name):
        hik_utils.set_source_on_character(target_name, source_name)
        hik_utils.bake_current_character()

    def unreference_animation(self, anim_path):
        cmds.file(anim_path, removeReference=True)


def create_dialog(*args):
    if not HIKTransferDialog._instance:
        HIKTransferDialog._instance = HIKTransferDialog()
    HIKTransferDialog._instance.show()
    HIKTransferDialog._instance.raise_()
