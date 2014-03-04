import site
site.addsitedir(r"R:\Pipe_Repo\Users\Qurban\utilities")
from uiContainer import uic

import os.path as osp
import sys

rootPath = osp.dirname(osp.dirname(__file__))
uiPath = osp.join(rootPath, 'ui')

class Item(uic.loadUiType(osp.join(uiPath, 'item.ui'))):

    def __init__(self, parent=None):
        super(Item, self).__init__()
        self.setupUi(self)

class Scroller(uic.loadUiType(osp.join(uiPath, 'scroller.ui'))):
    
    def __init__(self, parent=None):
        super(Scroller, self).__init__(parent)
        self.setupUi(self)