from . import explorer

reload(explorer)

from .scroller import (Scroller, ContextScroller, SObjectScroller,
        SnapshotScroller)
from .explorer import Explorer
from .item import Item, DeferredItemJob

from PyQt4.QtGui import QMessageBox
#from PyQt4.QtCore import Qt, pyqtSignal, QObject

import os.path as osp

rootPath = osp.dirname(osp.dirname(__file__))
uiPath = osp.join(rootPath, 'ui')
iconPath = osp.join(rootPath, 'icons')

class MessageBox(QMessageBox):
    def __init__(self, parent=None):
        super(MessageBox, self).__init__(parent)

    def closeEvent(self, event):
        self.deleteLater()
        del self

    def hideEvent(self, event):
        self.deleteLater()
        del self


def showMessage(parent, title = 'MessageBox', msg = 'Message', btns = QMessageBox.Ok,
       icon = None, ques = None, details = None):

    if msg:
        mBox = MessageBox(parent)
        mBox.setWindowTitle(title)
        mBox.setText(msg)
        if ques:
            mBox.setInformativeText(ques)
        if icon:
            mBox.setIcon(icon)
        if details:
            mBox.setDetailedText(details)
        mBox.setStandardButtons(btns)
        buttonPressed = mBox.exec_()
        return buttonPressed

