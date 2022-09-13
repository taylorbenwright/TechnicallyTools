"""
Tool for the Matrix Constraint tool.
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om2
from MayaEnv.tools import BaseDialog
from widgets import ps2_BoxLayoutSeparator
from PySide2 import QtWidgets, QtGui
from PySide2.QtCore import Qt, QModelIndex, Signal
from MayaEnv.utils.riggingUtils import matrix_constraint


class MatrixConstraintDialog(BaseDialog.BaseMayaDialog):

    _instance = None

    def __init__(self, parent=None):
        super(MatrixConstraintDialog, self).__init__(parent=parent)

        self.setWindowTitle('Matrix Constraint')
        self.setFixedSize(823, 525)

        self.generate_ui()

    def generate_ui(self):
        self.menu_bar = QtWidgets.QMenuBar()
        self.edit_menu = self.menu_bar.addMenu('Edit')
        self.save_settings_action = self.edit_menu.addAction('Save Settings')
        self.reset_settings_action = self.edit_menu.addAction('Reset Settings')
        self.save_settings_action.triggered.connect(self.save_settings)
        self.reset_settings_action.triggered.connect(self.reset_settings)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setMenuBar(self.menu_bar)

        grp_layout = QtWidgets.QVBoxLayout()
        top_grid = QtWidgets.QGridLayout()
        top_grid.setColumnStretch(0, 1)
        top_grid.setColumnStretch(1, 2)

        top_grid.addWidget(QtWidgets.QLabel('Maintain Offset:  '), 0, 0, alignment=Qt.AlignRight)
        self.maintain_offset_chx = QtWidgets.QCheckBox()
        top_grid.addWidget(self.maintain_offset_chx, 0, 1)

        grp_layout.addLayout(top_grid)
        grp_layout.addWidget(ps2_BoxLayoutSeparator.BoxLayoutSeparator(QtWidgets.QFrame.HLine))

        constraint_frame = QtWidgets.QLabel('Constraint Axes: ')
        constraint_frame.setStyleSheet('font-weight: bold;')
        constraint_frame.setFrameStyle(QtWidgets.QFrame.Plain)
        constraint_frame.setAlignment(Qt.AlignLeft)
        constraint_frame.setLineWidth(2)
        constraint_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        constraint_frame.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        constraint_frame.setBackgroundRole(QtGui.QPalette.Button)
        constraint_frame.setAutoFillBackground(True)

        grp_layout.addWidget(constraint_frame)

        bottom_grid = QtWidgets.QGridLayout()
        bottom_grid.setColumnMinimumWidth(1, 300)
        bottom_grid.setColumnStretch(0, 1)
        bottom_grid.setColumnStretch(1, 2)

        self.translate_all_chx = QtWidgets.QCheckBox('All')
        self.translate_all_chx.setChecked(True)
        self.translate_all_chx.pressed.connect(self.checkbox_checked)
        translate_btngrp = QtWidgets.QHBoxLayout()
        self.translate_x_chx = QtWidgets.QCheckBox('X')
        self.translate_x_chx.pressed.connect(self.checkbox_checked)
        self.translate_y_chx = QtWidgets.QCheckBox('Y')
        self.translate_y_chx.pressed.connect(self.checkbox_checked)
        self.translate_z_chx = QtWidgets.QCheckBox('Z')
        self.translate_z_chx.pressed.connect(self.checkbox_checked)
        translate_btngrp.addWidget(self.translate_x_chx)
        translate_btngrp.addWidget(self.translate_y_chx)
        translate_btngrp.addWidget(self.translate_z_chx)

        bottom_grid.addWidget(QtWidgets.QLabel('Translate:  '), 0, 0, alignment=Qt.AlignRight)
        bottom_grid.addWidget(self.translate_all_chx, 0, 1)
        bottom_grid.addLayout(translate_btngrp, 1, 1)

        self.rotate_all_chx = QtWidgets.QCheckBox('All')
        self.rotate_all_chx.setChecked(True)
        self.rotate_all_chx.pressed.connect(self.checkbox_checked)
        rotate_btngrp = QtWidgets.QHBoxLayout()
        self.rotate_x_chx = QtWidgets.QCheckBox('X')
        self.rotate_x_chx.pressed.connect(self.checkbox_checked)
        self.rotate_y_chx = QtWidgets.QCheckBox('Y')
        self.rotate_y_chx.pressed.connect(self.checkbox_checked)
        self.rotate_z_chx = QtWidgets.QCheckBox('Z')
        self.rotate_z_chx.pressed.connect(self.checkbox_checked)
        rotate_btngrp.addWidget(self.rotate_x_chx)
        rotate_btngrp.addWidget(self.rotate_y_chx)
        rotate_btngrp.addWidget(self.rotate_z_chx)

        bottom_grid.addWidget(QtWidgets.QLabel('Rotate:  '), 2, 0, alignment=Qt.AlignRight)
        bottom_grid.addWidget(self.rotate_all_chx, 2, 1)
        bottom_grid.addLayout(rotate_btngrp, 3, 1)

        self.scale_all_chx = QtWidgets.QCheckBox('All')
        self.scale_all_chx.setChecked(True)
        self.scale_all_chx.pressed.connect(self.checkbox_checked)
        scale_btngrp = QtWidgets.QHBoxLayout()
        self.scale_x_chx = QtWidgets.QCheckBox('X')
        self.scale_x_chx.pressed.connect(self.checkbox_checked)
        self.scale_y_chx = QtWidgets.QCheckBox('Y')
        self.scale_y_chx.pressed.connect(self.checkbox_checked)
        self.scale_z_chx = QtWidgets.QCheckBox('Z')
        self.scale_z_chx.pressed.connect(self.checkbox_checked)
        scale_btngrp.addWidget(self.scale_x_chx)
        scale_btngrp.addWidget(self.scale_y_chx)
        scale_btngrp.addWidget(self.scale_z_chx)

        bottom_grid.addWidget(QtWidgets.QLabel('Scale:  '), 4, 0, alignment=Qt.AlignRight)
        bottom_grid.addWidget(self.scale_all_chx, 4, 1)
        bottom_grid.addLayout(scale_btngrp, 5, 1)

        grp_layout.addLayout(bottom_grid)

        but_layout = QtWidgets.QHBoxLayout()
        add_but = QtWidgets.QPushButton('Add')
        add_but.pressed.connect(self.add_but_pressed)
        apply_but = QtWidgets.QPushButton('Apply')
        apply_but.pressed.connect(self.apply_but_pressed)
        close_but = QtWidgets.QPushButton('Close')
        close_but.pressed.connect(self.close_but_pressed)
        but_layout.addWidget(add_but)
        but_layout.addWidget(apply_but)
        but_layout.addWidget(close_but)

        grp_layout.setStretch(0, 1)
        grp_layout.setStretch(1, 3)
        grp_layout.setStretch(2, 3)
        grp_layout.setStretch(3, 4)

        main_layout.addLayout(grp_layout)
        main_layout.addStretch()
        main_layout.addWidget(ps2_BoxLayoutSeparator.BoxLayoutSeparator(QtWidgets.QFrame.HLine))

        main_layout.addLayout(but_layout)

        self.setLayout(main_layout)

        self.load_prefs()

    def save_settings(self, *args):
        self.save_prefs()

    def reset_settings(self, *args):
        cmds.optionVar(iv=('matrixConstraint_maintainOffset', 0))
        cmds.optionVar(iv=('matrixConstraint_translateAll', 1))
        cmds.optionVar(iv=('matrixConstraint_translateX', 0))
        cmds.optionVar(iv=('matrixConstraint_translateY', 0))
        cmds.optionVar(iv=('matrixConstraint_translateZ', 0))
        cmds.optionVar(iv=('matrixConstraint_rotateAll', 1))
        cmds.optionVar(iv=('matrixConstraint_rotateX', 0))
        cmds.optionVar(iv=('matrixConstraint_rotateY', 0))
        cmds.optionVar(iv=('matrixConstraint_rotateZ', 0))
        cmds.optionVar(iv=('matrixConstraint_scaleAll', 1))
        cmds.optionVar(iv=('matrixConstraint_scaleX', 0))
        cmds.optionVar(iv=('matrixConstraint_scaleY', 0))
        cmds.optionVar(iv=('matrixConstraint_scaleZ', 0))
        self.load_prefs()

    def add_but_pressed(self, *args):
        self.constrain_objects()
        self.save_prefs()
        self.close()

    def apply_but_pressed(self, *args):
        self.constrain_objects()

    def close_but_pressed(self, *args):
        self.close()

    def checkbox_checked(self, *args):
        translate_boxes = [self.translate_x_chx, self.translate_y_chx, self.translate_z_chx]
        rotate_boxes = [self.rotate_x_chx, self.rotate_y_chx, self.rotate_z_chx]
        scale_boxes = [self.scale_x_chx, self.scale_y_chx, self.scale_z_chx]
        sender = self.sender()
        if sender == self.translate_all_chx:
            for box in translate_boxes:
                box.setChecked(False)
        elif sender == self.rotate_all_chx:
            for box in rotate_boxes:
                box.setChecked(False)
        elif sender == self.scale_all_chx:
            for box in scale_boxes:
                box.setChecked(False)
        elif sender in translate_boxes:
            self.translate_all_chx.setChecked(False)
        elif sender in rotate_boxes:
            self.rotate_all_chx.setChecked(False)
        elif sender in scale_boxes:
            self.scale_all_chx.setChecked(False)

    def constrain_objects(self):
        sel = cmds.ls(sl=True)
        if len(sel) < 2:
            cmds.warning('Unable to constrain. Please select at least two DAG objects.')
            return
        target = sel[-1]
        sources = sel[:-1]

        bools = [False] * 9
        if self.translate_all_chx.isChecked():
            bools[0], bools[1], bools[2] = True, True, True
        else:
            bools[0] = True if self.translate_x_chx.isChecked() else False
            bools[1] = True if self.translate_y_chx.isChecked() else False
            bools[2] = True if self.translate_z_chx.isChecked() else False
        if self.rotate_all_chx.isChecked():
            bools[3], bools[4], bools[5] = True, True, True
        else:
            bools[3] = True if self.rotate_x_chx.isChecked() else False
            bools[4] = True if self.rotate_y_chx.isChecked() else False
            bools[5] = True if self.rotate_z_chx.isChecked() else False
        if self.scale_all_chx.isChecked():
            bools[6], bools[7], bools[8] = True, True, True
        else:
            bools[6] = True if self.scale_x_chx.isChecked() else False
            bools[7] = True if self.scale_y_chx.isChecked() else False
            bools[8] = True if self.scale_z_chx.isChecked() else False

        matrix_constraint(target, sources, maintain_offset=self.maintain_offset_chx.isChecked(),
                          translate_x=bools[0], translate_y=bools[1], translate_z=bools[2],
                          rotate_x=bools[3], rotate_y=bools[4], rotate_z=bools[5],
                          scale_x=bools[6], scale_y=bools[7], scale_z=bools[8])

    def save_prefs(self):
        cmds.optionVar(iv=('matrixConstraint_maintainOffset', int(self.maintain_offset_chx.isChecked())))
        cmds.optionVar(iv=('matrixConstraint_translateAll', int(self.translate_all_chx.isChecked())))
        cmds.optionVar(iv=('matrixConstraint_translateX', int(self.translate_x_chx.isChecked())))
        cmds.optionVar(iv=('matrixConstraint_translateY', int(self.translate_y_chx.isChecked())))
        cmds.optionVar(iv=('matrixConstraint_translateZ', int(self.translate_z_chx.isChecked())))
        cmds.optionVar(iv=('matrixConstraint_rotateAll', int(self.rotate_all_chx.isChecked())))
        cmds.optionVar(iv=('matrixConstraint_rotateX', int(self.rotate_x_chx.isChecked())))
        cmds.optionVar(iv=('matrixConstraint_rotateY', int(self.rotate_y_chx.isChecked())))
        cmds.optionVar(iv=('matrixConstraint_rotateZ', int(self.rotate_z_chx.isChecked())))
        cmds.optionVar(iv=('matrixConstraint_scaleAll', int(self.scale_all_chx.isChecked())))
        cmds.optionVar(iv=('matrixConstraint_scaleX', int(self.scale_x_chx.isChecked())))
        cmds.optionVar(iv=('matrixConstraint_scaleY', int(self.scale_y_chx.isChecked())))
        cmds.optionVar(iv=('matrixConstraint_scaleZ', int(self.scale_z_chx.isChecked())))

    def load_prefs(self):
        self.maintain_offset_chx.setChecked(bool(cmds.optionVar(q='matrixConstraint_maintainOffset')))
        self.translate_all_chx.setChecked(bool(cmds.optionVar(q='matrixConstraint_translateAll')))
        self.translate_x_chx.setChecked(bool(cmds.optionVar(q='matrixConstraint_translateX')))
        self.translate_y_chx.setChecked(bool(cmds.optionVar(q='matrixConstraint_translateY')))
        self.translate_z_chx.setChecked(bool(cmds.optionVar(q='matrixConstraint_translateZ')))
        self.rotate_all_chx.setChecked(bool(cmds.optionVar(q='matrixConstraint_rotateAll')))
        self.rotate_x_chx.setChecked(bool(cmds.optionVar(q='matrixConstraint_rotateX')))
        self.rotate_y_chx.setChecked(bool(cmds.optionVar(q='matrixConstraint_rotateY')))
        self.rotate_z_chx.setChecked(bool(cmds.optionVar(q='matrixConstraint_rotateZ')))
        self.scale_all_chx.setChecked(bool(cmds.optionVar(q='matrixConstraint_scaleAll')))
        self.scale_x_chx.setChecked(bool(cmds.optionVar(q='matrixConstraint_scaleX')))
        self.scale_y_chx.setChecked(bool(cmds.optionVar(q='matrixConstraint_scaleY')))
        self.scale_z_chx.setChecked(bool(cmds.optionVar(q='matrixConstraint_scaleZ')))

    def dialog_opened(self):
        return

    def dialog_closed(self):
        MatrixConstraintDialog._instance = None


def create_dialog(*args):
    if not MatrixConstraintDialog._instance:
        MatrixConstraintDialog._instance = MatrixConstraintDialog()
    MatrixConstraintDialog._instance.show()
    MatrixConstraintDialog._instance.raise_()
