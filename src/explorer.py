try:
    from uiContainer import uic
except:
    from PyQt4 import uic

from PyQt4.QtGui import QIcon

try:
    # cui is imported in login, so put it under try
    import app.util as util
    reload(util)
except:
    pass
import imaya as mi
import os.path as osp

from . import scroller
reload(scroller)


from .scroller import Scroller

rootPath = osp.dirname(osp.dirname(__file__))
uiPath = osp.join(rootPath, 'ui')
iconPath = osp.join(rootPath, 'icons')

Form3, Base3 = uic.loadUiType(osp.join(uiPath, 'explorer.ui'))
class BaseExplorer(Form3, Base3):
    def __init__(self, parent=None, standalone=False):
        super(BaseExplorer, self).__init__(parent)
        self.setupUi(self)
        self.projectsBox.hide()
        self.episodeBox.hide()
        self.sequenceBox.hide()
        self.statusBar().hide()
        self.referenceButton.hide()
        self.proxyButton.hide()
        self.gpuCacheButton.hide()

        if standalone:
            self.openButton.hide()
            self.referenceButton.hide()
            self.setWindowIcon(QIcon(osp.join(iconPath, 'tactic.png')))

        self.standalone = standalone
        self.projects = {}

        self.refreshButton.setIcon(QIcon(osp.join(iconPath, 'refresh.png')))

        self.refreshButton.clicked.connect(self.updateWindow)

    def setProjectsBox(self):
        for project in util.get_all_projects():
            self.projects[project['title']] = project['code']
            self.projectsBox.addItem(project['title'])
        project_name = mi.pc.optionVar(q='current_project_key')
        if project_name:
            for i in range(self.projectsBox.count()):
                text = self.projectsBox.itemText(i)
                if text == project_name:
                    self.projectsBox.setCurrentIndex(i)
                    break
    
    def updateWindow(self):
        pass
    

class Explorer(BaseExplorer):
    def __init__(self, parent=None, standalone=False):
        super(Explorer, self).__init__(parent, standalone)

        self.currentContext = None
        self.currentFile = None
        self.snapshots = None
        self.checkinputDialog = None
        self.projects = {}

        self.refreshButton.setIcon(QIcon(osp.join(iconPath, 'refresh.png')))

        self.refreshButton.clicked.connect(self.updateWindow)
        self.referenceButton.clicked.connect(self.addReference)
        self.advanceButton.clicked.connect(self.handleAdvanceButton)
        
    def handleAdvanceButton(self):
        if self.advanceButton.text().lower().startswith('<<'):
            self.proxyButton.show()
            self.gpuCacheButton.show()
            self.referenceButton.show()
            self.advanceButton.setText('Less >>')
            self.advanceButton.setToolTip('Show Lesser options')
        else:
            self.proxyButton.hide()
            self.gpuCacheButton.hide()
            self.referenceButton.hide()
            self.advanceButton.setText('<< More')
            self.advanceButton.setToolTip('Show More options')

    def addReference(self):
        pass

    def clearContextsProcesses(self):
        self.contextsBox.clearItems()
        self.currentContext = None

        self.filesBox.clearItems()
        self.currentFile = None

    def addFilesBox(self):
        self.filesBox = self.createScroller('Files',
                cls=scroller.SnapshotScroller)

    def showFiles(self, context, files = None):
        # highlight the context
        if self.currentContext:
            self.currentContext.setStyleSheet("background-color: None")
        self.currentContext = context
        self.currentContext.setStyleSheet("background-color: #666666")

        objectName = str(self.currentContext.objectName())
        parts = objectName.split('>')

        index = 0
        # check if object name has sobject_key in it

        if files is None:
            # get the files
            contx = parts[index+1]
            task = parts[index]
            files = util.get_snapshots(contx, task)

        else:
            if objectName.find('?') >= 0:
                index = 1
            newFiles = {}
            pro = parts[index]
            contx = (parts[index] if len(parts) == index+1 else
                    '/'.join(parts[(index+1):]))

            for snap in files:
                if snap['process'] == pro and snap['context'] == contx:
                    try:
                        newFiles[snap['__search_key__']] = {'filename': osp.basename(util.filename_from_snap(snap)),
                                                            'latest': snap['is_latest'],
                                                            'version': snap['version'],
                                                            'description': snap['description'],
                                                            'timestamp': snap['timestamp']}
                    except IndexError:
                        continue
            files = newFiles


        # remove the showed files
        self.filesBox.clearItems()
        self.currentFile = None

        if files:
            # add the latest file to scroller
            for k in files:
                values=files[k]
                if values['latest']:
                    item = self.filesBox.createItem(values['filename'],
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
                item = self.filesBox.createItem(value['filename'],
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
                context = (self.currentContext.title().split('/')[0] +'/' +
                           str(self.checkinputDialog.newContextBox.text()))
            self.checkinputDialog.setContext(context)
        self.filesBox.toggleShowVersions()

    def selectFile(self, fil):
        if self.currentFile:
            self.currentFile.setStyleSheet("background-color: None")
        self.currentFile = fil
        self.currentFile.setStyleSheet("background-color: #666666")

    def createScroller(self, title, cls=Scroller):
        scroller = cls(self)
        scroller.setTitle(title)
        self.scrollerLayout.addWidget(scroller)
        return scroller

    def bindClickEvent(self, widget, function):
        widget.mouseReleaseEvent = lambda event: function(widget)

    def bindClickEventForFiles(self, widget, func, args):
        widget.mouseReleaseEvent = lambda event: func(widget, args)

    def updateFilesBox(self):
        if self.currentContext:
            self.showFiles(self.currentContext)

