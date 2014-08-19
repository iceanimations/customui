try:
    from uiContainer import uic
except:
    from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
try:
    # cui is imported in login, so put it under try
    import app.util as util
    reload(util)
except: pass
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
        self.subTtl = ''
        self.thirdTtl = ''
        
    def setTitle(self, title):
        self.ttl = title
        self.titleLabel.setText(title)
    
    def setSubTitle(self, name):
        self.subTtl = name
        self.subTitleLabel.setText(name)
        
    def setThirdTitle(self, name):
        self.thirdTtl = name
        self.thirdTitleLabel.setText(name)
    
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
    
    def subTitle(self):
        return self.subTtl
    
    def thirdTitle(self):
        return self.thirdTtl
    
    def addWidget(self, widget):
        self.horizontalLayout.addWidget(widget)
        self.widget = widget
        
    def setChecked(self, checked):
        self.widget.setChecked(checked)
        
    def isChecked(self):
        return self.widget.isChecked()
        
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
        
    def removeItemsON(self, items):
        removed = []
        for item in self.itemsList:
            for itm in items:
                if str(item.objectName()) == itm:
                    item.deleteLater()
                    removed.append(item)
                    break
        for rmd in removed:
            self.itemsList.remove(rmd)
        return removed
        
    def removeItems(self, items):
        for item in items:
            item.deleteLater()
            self.itemsList.remove(item)
        
    def items(self):
        return self.itemsList
        
    def searchItems(self, text):
        sources = str(text).split()
        for item in self.itemsList:
            target = [item.title(), item.thirdTitle(), item.subTitle()]
            tar = " ".join(target).lower()
            if not sources or any([True if src.lower() in tar 
                                   else False for src in sources]):
                item.show()
            else: item.hide()
    def clearItems(self):
        for item in self.itemsList:
            item.deleteLater()
        self.itemsList[:] = []
        
Form3, Base3 = uic.loadUiType(osp.join(uiPath, 'explorer.ui'))
class Explorer(Form3, Base3):
    
    def __init__(self, parent=None, standalone=False):
        super(Explorer, self).__init__(parent)
        self.setupUi(self)
        self.projectsBox.hide()
        self.episodeBox.hide()
        self.sequenceBox.hide()
        self.statusBar().hide()
        
        if standalone:
            self.openButton.hide()
            self.referenceButton.hide()
            
        self.standalone = standalone
        self.currentContext = None
        self.currentFile = None
        self.snapshots = None # used in assetsExplorer
        self.checkinputDialog = None
        self.projects = {}
        
        self.refreshButton.setIcon(QIcon(osp.join(iconPath, 'refresh.png')))
        
        self.closeButton.clicked.connect(self.close)
        self.refreshButton.clicked.connect(self.updateWindow)
        self.referenceButton.clicked.connect(self.addReference)
        
    def setProjectsBox(self):
        for project in util.get_all_projects():
            self.projects[project['title']] = project['code']
            self.projectsBox.addItem(project['title'])

    def addReference(self):
        pass
    
    def clearContextsProcesses(self):
        self.contextsBox.clearItems()
        self.currentContext = None
        
        self.filesBox.clearItems()
        self.currentFile = None
        
    def addFilesBox(self):
        self.filesBox = self.createScroller('Files')
        
    def showFiles(self, context, files = None):
        # highlight the context
        if self.currentContext:
            self.currentContext.setStyleSheet("background-color: None")
        self.currentContext = context
        self.currentContext.setStyleSheet("background-color: #666666")
        
        parts = str(self.currentContext.objectName()).split('>')
        if files is None:
            # get the files
            contx = parts[0]; task = parts[1]
            files = util.get_snapshots(contx, task)
        else:
            newFiles = {}
            pro = parts[0]; contx = parts[0] if len(parts) == 1 else '/'.join(parts[1:])
            for snap in files:
                if snap['process'] == pro and snap['context'] == contx:
                    newFiles[snap['__search_key__']] = {'filename': osp.basename(util.filename_from_snap(snap)),
                                                        'latest': snap['is_latest'],
                                                        'version': snap['version'],
                                                        'description': snap['description'],
                                                        'timestamp': snap['timestamp']}
            files = newFiles

        
        # remove the showed files
        self.filesBox.clearItems()
        self.currentFile = None
        
        if files:
            # add the latest file to scroller
            for k in files:
                values=files[k]
                if values['latest']:
                    item = self.createItem(values['filename'],
                                           str(util.date_str_to_datetime(values['timestamp'])), '',
                                           values['description'])
                    self.filesBox.addItem(item)
                    item.setObjectName(k)
                    item.setToolTip(values['filename'])
                    files.pop(k)
                    break
                
            temp = {}
            for ke in files:
                temp[ke] = files[ke]['version']
                
            # show the new files
            for key in sorted(temp, key=temp.get, reverse=True):
                value = files[key]
                item = self.createItem(value['filename'],
                                       str(util.date_str_to_datetime(value['timestamp'])), '',
                                       value['description'])
                self.filesBox.addItem(item)
                item.setObjectName(key)
                item.setToolTip(value['filename'])
            
            # bind click event
            map(lambda widget: self.bindClickEvent(widget, self.selectFile), self.filesBox.items())
            
        # handle child windows
        if self.checkinputDialog:
            context = self.currentContext.title()
            if self.checkinputDialog.newContextButton.isChecked():
                context = self.currentContext.title().split('/')[0] +'/'+ str(self.checkinputDialog.newContextBox.text())
            self.checkinputDialog.setContext(context)
                
    def selectFile(self, fil):
        if self.currentFile:
            self.currentFile.setStyleSheet("background-color: None")
        self.currentFile = fil
        self.currentFile.setStyleSheet("background-color: #666666")
        
    def createScroller(self, title):
        scroller = Scroller(self)
        scroller.setTitle(title)
        self.scrollerLayout.addWidget(scroller)
        return scroller
    
    def createItem(self, title, subTitle, thirdTitle, detail):
        if not title:
            title = 'No title'
        item = Item(self)
        item.setTitle(title)
        item.setSubTitle(subTitle)
        item.setThirdTitle(thirdTitle)
        item.setDetail(detail)
        item.setToolTip(title)
        return item
    

    def checkout(self, r = False):
        if self.currentFile:
            backend.checkout(str(self.currentFile.objectName()), r = r)

    def bindClickEvent(self, widget, function):
        widget.mouseReleaseEvent = lambda event: function(widget)
        
    def bindClickEventForFiles(self, widget, func, args):
        widget.mouseReleaseEvent = lambda event: func(widget, args)
    
    def updateWindow(self):
        pass
    
    def updateFilesBox(self):
        if self.currentContext:
            self.showFiles(self.currentContext)
        
    def closeEvent(self, event):
        self.deleteLater()

def showMessage(parent, title = 'MessageBox', msg = 'Message', btns = QMessageBox.Ok,
       icon = None, ques = None, details = None):

    if msg:
        mBox = QMessageBox(parent)
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
