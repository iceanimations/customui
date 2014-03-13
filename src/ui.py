from uiContainer import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt

import os.path as osp
import sys

rootPath = osp.dirname(osp.dirname(__file__))
uiPath = osp.join(rootPath, 'ui')
iconPath = osp.join(rootPath, 'icons')

Form1, Base1 = uic.loadUiType(osp.join(uiPath, 'item.ui'))
class Item(Form1, Base1):

    def __init__(self, parent=None):
        super(Item, self).__init__()
        self.setupUi(self)
        pix = QPixmap(100, 100)
        pix.load(osp.join(iconPath, 'no_preview.png'))
        self.thumbLabel.setPixmap(pix)
        self.ttl = ''
        self.ast = ''
        self.proj = ''
        
    def setTitle(self, title):
        self.ttl = title
        self.titleLabel.setText(title)
    
    def setAssetName(self, name):
        self.ast = name
        self.assetLabel.setText(name)
        
    def setProjectName(self, name):
        self.proj = name
        self.projectLabel.setText(name)
    
    def setDetail(self, detail):
        self.detailLabel.setText(detail)
        
    def setThumb(self, thumbPath):
        pix = QPixmap(thumbPath)
        pix = pix.scaled(100, 100, Qt.KeepAspectRatio)
        self.thumbLabel.setPixmap(pix)
        
    def title(self):
        if self.ttl == 'No Title':
            return ''
        return self.ttl
    
    def asset(self):
        return self.ast
    
    def project(self):
        return self.proj
        
    def enterEvent(self, event):
        '''
        handles when the mouse cursor enters the label
        '''
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(3)
    
    def leaveEvent(self, event):
        '''
        handles when the mouse cursor leaves the label
        '''
        self.setFrameStyle(QFrame.StyledPanel)
        self.setLineWidth(1)

Form2, Base2 = uic.loadUiType(osp.join(uiPath, 'scroller.ui'))
class Scroller(Form2, Base2):
    
    def __init__(self, parent=None):
        super(Scroller, self).__init__(parent)
        self.setupUi(self)
        
        self.itemsList = []
        self.searchBox.textChanged.connect(self.searchItems)
        
        self.scrollArea.verticalScrollBar().setFixedWidth(12)
        self.scrollArea.horizontalScrollBar().setFixedHeight(12)
        
        path = osp.join(iconPath, 'search.png').replace('\\', '/')
        style = ("padding-left: 15px; background-image: url(%s); "+
        "background-repeat: no-repeat; background-position: center left; "+
        "border-width: 1px; border-style: inset; border-color: #535353; "+
        "border-radius: 9px; padding-bottom: 1px;")%path
        self.searchBox.setStyleSheet(style)
        
    def setTitle(self, title):
        self.titleLabel.setText(title)
        
    def addItem(self, item):
        self.itemLayout.addWidget(item)
        self.itemsList.append(item)
        
    def removeItems(self, items):
        for item in items:
            item.deleteLater()
            self.itemsList.remove(item)
        
    def items(self):
        return self.itemsList
        
    def searchItems(self, text):
        sources = str(text).split()
        result = []
        for item in self.itemsList:
            target = [item.title(), item.project(), item.asset()]
            tar = " ".join(target).lower()
            if not sources or any([True if src.lower() in tar 
                                   else False for src in sources]):
                item.show()
            else: item.hide()
    def clearItems(self):
        self.itemsList[:] = []