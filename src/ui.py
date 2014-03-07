import site
site.addsitedir(r"R:\Pipe_Repo\Users\Qurban\utilities")
from uiContainer import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt

import os.path as osp
import sys

rootPath = osp.dirname(osp.dirname(__file__))
uiPath = osp.join(rootPath, 'ui')

Form1, Base1 = uic.loadUiType(osp.join(uiPath, 'item.ui'))
class Item(Form1, Base1):

    def __init__(self, parent=None):
        super(Item, self).__init__()
        self.setupUi(self)
        
    def setTitle(self, title):
        self.titleLabel.setText(title)
    
    def setAssetName(self, name):
        self.assetLabel.setText(name)
        
    def setProjectName(self, name):
        self.projectLabel.setText(name)
    
    def setDetail(self, detail):
        self.detailLabel.setText(detail)
        
    def setThumb(self, thumbPath):
        pix = QPixmap(thumbPath)
        pix = pix.scaled(100, 100, Qt.KeepAspectRatio)
        self.thumbLabel.setPixmap(pix)

Form2, Base2 = uic.loadUiType(osp.join(uiPath, 'scroller.ui'))
class Scroller(Form2, Base2):
    
    def __init__(self, parent=None):
        super(Scroller, self).__init__(parent)
        self.setupUi(self)
        self.typeLabel.hide()
        
    def setTitle(self, title):
        self.titleLabel.setText(title)
        
    def setType(self, typ):
        self.typeLabel.setText(typ)
        
    def addItem(self, item):
        self.itemLayout.addWidget(item)