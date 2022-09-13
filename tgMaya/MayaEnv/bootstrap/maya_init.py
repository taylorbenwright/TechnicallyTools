"""
This is the main entrypoint into the Maya toolset
"""

import sys
import os
from pathlib import Path
import maya.cmds as cmds

sys.dont_write_bytecode = True

ENTRY_POINT__ = Path(__file__)
ENTRY_ROOT__ = ENTRY_POINT__.parent.absolute()
DEV_ROOT__ = ENTRY_POINT__.parent.parent.parent.absolute()
PYSIDE2WIDGETS_ROOT__ = str(DEV_ROOT__.parent.absolute()) + '\\PySide2Widgets'
AGNOSTIC_ROOT__ = str(DEV_ROOT__.parent.absolute()) + '\\agnostic'
DEV_ROOT__ = str(DEV_ROOT__)
PYSIDE2WIDGETS_ROOT__ = str(PYSIDE2WIDGETS_ROOT__)
AGNOSTIC_ROOT__ = str(AGNOSTIC_ROOT__)


def bootstrap():

    print("Technically Games Maya tools starting... ")

    initialize()

    import MayaEnv.startup as startup
    startup.execute()

    print("Technically Games Maya loaded!")


def initialize():
    """
    Initializes the Maya tool environment
    """
    if DEV_ROOT__ not in sys.path:
        sys.path.append(DEV_ROOT__)
    if AGNOSTIC_ROOT__ not in sys.path:
        sys.path.append(AGNOSTIC_ROOT__)
    if PYSIDE2WIDGETS_ROOT__ not in sys.path:
        sys.path.append(PYSIDE2WIDGETS_ROOT__)


# if __name__ == '__main__':
cmds.evalDeferred(bootstrap, lp=True)
