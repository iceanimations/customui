
try:
    from uiContainer import uic
except:
    from PyQt4 import uic

from PyQt4.QtGui import qApp

import os.path as osp
from multiprocessing.pool import ThreadPool

from . import item
reload(item)


rootPath = osp.dirname(osp.dirname(__file__))
uiPath = osp.join(rootPath, 'ui')
iconPath = osp.join(rootPath, 'icons')

Form2, Base2 = uic.loadUiType(osp.join(uiPath, 'scroller.ui'))
class Scroller(Form2, Base2):
    Item = item.Item()

    def __init__(self, parent=None):
        super(Scroller, self).__init__(parent)
        self.setupUi(self)
        self.itemsList = []
        self.searchBox.textChanged.connect(self.searchItems)
        self.searchBox.returnPressed.connect(lambda: self.searchItems(self.searchBox.text()))

        self.scrollArea.verticalScrollBar().setFixedWidth(12)
        self.scrollArea.horizontalScrollBar().setFixedHeight(12)

        path = osp.join(iconPath, 'search.png').replace('\\', '/')
        style = ("padding-left: 15px; background-image: url(%s); "+
        "background-repeat: no-repeat; background-position: center left; "+
        "border-width: 1px; border-style: inset; border-color: #535353; "+
        "border-radius: 9px; padding-bottom: 1px;")%path
        self.searchBox.setStyleSheet(style)
        self.pool = None
        self.reinitializeThreadPool()

        self.versionsButton.clicked.connect(self.toggleShowVersions)

    def reinitializeThreadPool(self):
        if self.pool:
            self.pool.terminate()
        self.pool = ThreadPool(processes=4)

    def toggleShowVersions(self):
        for i in range(len(self.itemsList) - 1):
            self.itemsList[i+1].setVisible(self.versionsButton.isChecked())

    def scrolled(self, value):
        for _item in self.itemsList:
            if not _item.visibleRegion().isEmpty():
                for job in _item.jobs:
                    if job.getStatus() == job.Status.kWaiting:
                        job.setBusy()
                        self.pool.apply_async(job.doAsync)
                #if not item.thumbAdded():
                    #self.pool.apply_async(item.get_icon_async)
        qApp.processEvents()

    def setTitle(self, title):
        self.titleLabel.setText(title)

    def getTitle(self):
        return str(self.titleLabel.text())

    def createItem(self, title, subTitle, thirdTitle, detail):

        if not title:
            title = 'No title'

        _item = self.Item()
        _item.setTitle(title)
        _item.setSubTitle(subTitle)
        _item.setThirdTitle(thirdTitle)
        _item.setDetail(detail)
        _item.setToolTip(detail)
        return _item

    def addItem(self, item):
        self.itemLayout.addWidget(item)
        self.itemsList.append(item)

    def removeItemsON(self, items):
        removed = []
        for _item in self.itemsList:
            for itm in items:
                if str(item.objectName()) == itm:
                    item.deleteLater()
                    removed.append(item)
                    break
        for rmd in removed:
            self.itemsList.remove(rmd)
        return removed

    def removeItems(self, items):
        for _item in items:
            item.deleteLater()
            self.itemsList.remove(item)

    def items(self):
        return self.itemsList

    def searchItems(self, text):
        if self.getTitle() == 'Files':
            self.versionsButton.setChecked(True)
        sources = str(text).split()
        for _item in self.itemsList:
            target = [item.title(), item.thirdTitle(), item.subTitle()]
            target = filter(None, target)
            tar = " ".join(target).lower()
            if not sources or any([True if src.lower() in tar
                                   else False for src in sources]):
                item.show()
            else: item.hide()

    def clearItems(self):
        for _item in self.itemsList:
            item.deleteLater()
        self.itemsList[:] = []
        self.reinitializeThreadPool()

class SObjectScroller(Scroller):
    Item = item.SObjectItem

class ContextScroller(Scroller):
    Item = item.ContextItem

class SnapshotScroller(Scroller):
    Item = item.SnapshotItem

