import maya.cmds as cmds
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omUI
from PySide2 import QtWidgets, QtGui, QtCore


class OptionBoxDialog(QtWidgets.QMainWindow):
    
    def __init__(self, function_to_call, function_arguments, parent=None):
        """
        Creates the OptionBox dialog for use by menus
        :param function_to_call: The function we want this option box to call with the options set in
        :type function_to_call: callable
        :param function_arguments: A dict of dicts that contains all the parameters this box needs to show
        :type function_arguments: dict
        :return: Nothing
        :rtype: None
        """
        super(OptionBoxDialog, self).__init__(parent=parent)

        self.function_to_call = function_to_call if callable(function_to_call) else None

        window_palette = QtGui.QPalette()
        window_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(30, 30, 30))
        self.setPalette(window_palette)

        # Top Menu bar
        menubar = QtWidgets.QMenuBar()
        editbar = QtWidgets.QMenu('Edit')
        save_action = editbar.addAction('Save Settings')  # type: QtWidgets.QAction
        save_action.triggered.connect(self.save_settings)
        reset_action = editbar.addAction('Reset Settings')  # type: QtWidgets.QAction
        reset_action.triggered.connect(self.reset_settings)
        menubar.addMenu(editbar)
        self.setMenuBar(menubar)

        central_widget = QtWidgets.QWidget()
        central_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(central_layout)

        tool_frame = QtWidgets.QFrame()
        tool_frame.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Plain)
        tool_frame.setLineWidth(1)
        tool_frame.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding))
        central_layout.addWidget(tool_frame)

        #  Bottom Buttons that are common to all option boxes
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setAlignment(QtCore.Qt.AlignBottom)
        button_layout.setSpacing(8)
        self.add_button = QtWidgets.QPushButton('Add')
        self.apply_button = QtWidgets.QPushButton('Apply')
        self.cancel_button = QtWidgets.QPushButton('Cancel')
        self.cancel_button.pressed.connect(self.cancel)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        central_layout.addLayout(button_layout)

        self.setCentralWidget(central_widget)

        self.setWindowTitle(function_arguments.get('name', 'Option Box'))
        self.resize(800, 500)

    def save_settings(self):
        raise NotImplementedError

    def reset_settings(self):
        raise NotImplementedError

    def add(self):
        raise NotImplementedError

    def apply(self):
        raise NotImplementedError

    def cancel(self):
        self.destroy()


def create_option_box(function_to_call, function_arguments):
    """
    Creates an OptionBoxDialog object
    :param function_to_call: The function we want to bind to the option box dialog
    :type function_to_call: callable
    :param function_arguments: A dict of dicts that contains all the parameters to pass to the option box dialog
    :type function_arguments: dict
    :return: Nothing
    :rtype: None
    """
    main_window = omUI.MQtUtil.mainWindow()
    maya_window = wrapInstance(long(main_window), QtWidgets.QMainWindow)
    ob_dialog = OptionBoxDialog(function_to_call, function_arguments, parent=maya_window)
    ob_dialog.show()


