try:
    from uiContainer import uic
except:
    from PyQt4 import uic

import os.path as osp
from PyQt4.QtGui import QPixmap, QLabel, QFrame
from PyQt4.QtCore import Qt, pyqtSignal, QObject

try:
    # cui is imported in login, so put it under try
    import app.util as util
    reload(util)
except:
    pass

from threading import Lock

rootPath = osp.dirname(osp.dirname(__file__))
uiPath = osp.join(rootPath, 'ui')
iconPath = osp.join(rootPath, 'icons')

class _Label(object):
    __red_path__ = osp.join(iconPath, 'RED')
    __green_path__ = osp.join(iconPath, 'GREEN')
    kCURR  = 0b00000001
    kNEW   = 0b00000010
    kVLESS = 0b00000100
    kPAIR  = 0b00001000
    kSYNC  = 0b00010000
    kPUB   = 0b00100000
    kLIVE  = 0b01000000

    @classmethod
    def everything(cls):
        mask = 0
        for member in dir(cls):
            if member.startswith('k'):
                mask |= getattr(cls, member)
        return mask

    @classmethod
    def current_versionless(cls):
        return cls.kCURR | cls.kVLESS

    @classmethod
    def latest_versionless(cls):
        return cls.kNEW | cls.kVLESS

    @classmethod
    def get_path(cls, mask, label_type=1):
        label_type = bool(label_type)
        for member in dir(cls):
            if member.startswith('k'):
                if getattr(cls, member) & mask:
                    if label_type:
                        path = cls.__green_path__
                    else:
                        path = cls.__red_path__
                    return osp.join( path, member[1:]+'.png' )

    @classmethod
    def all_labels(cls):
        return [getattr(cls, member) for member in dir(cls) if
                member.startswith('k')]

class DeferredItemJob(QObject):
    jobDone = pyqtSignal()

    class Status:
        kFailed = -1
        kWaiting = 0
        kSuccess = 1
        kBusy = 2

    def __init__(self, parent):
        super(DeferredItemJob, self).__init__(parent=parent)
        self._status = self.Status.kWaiting
        self._statusLock = Lock()

        self.retries = 0
        self.traceback = None
        self.error = None
        self._parent = parent
        self.jobDone.connect(self.update)

    def setSuccess(self):
        with self._statusLock:
            self._status = self.Status.kSuccess

    def setFailure(self):
        if self.retries > 0:
            self.retries-=1
            self.setWaiting()
        with self._statusLock:
            self._status = self.status.kFailed

    def setBusy(self):
        with self._statusLock:
            self._status = self.Status.kBusy

    def setWaiting(self):
        with self._statusLock:
            self._status = self.Status.kWaiting

    def getStatus(self):
        with self._statusLock:
            return self._status

    def doAsync(self):
        #perform IO Bound operation
        #self.jobDone.emit()
        pass

    def update(self):
        pass

class GetIcon(DeferredItemJob, QObject):
    thumbPath = ''

    def doAsync(self):
        try:
            util_copy = util.create_new()
            self.thumbPath = util_copy.get_icon(self._parent.objectName())
            self.setSuccess()
            self.jobDone.emit()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print type(e), e
            raise e

    def update(self):
        if not self.thumbPath:
            self.thumbPath = osp.join(iconPath, 'no_preview.png')
        pix = QPixmap(self.thumbPath)
        pix = pix.scaled(100, 100, Qt.KeepAspectRatio)
        self._parent.thumbLabel.setPixmap(pix)
        self.status = 1

Form1, Base1 = uic.loadUiType(osp.join(uiPath, 'item.ui'))
class Item(Form1, Base1):
    kLabel = _Label
    jobs = []

    def __init__(self, parent=None):
        super(Item, self).__init__()
        self.setupUi(self)
        self.thumb_added = False
        # TODO: fix the poor variable names
        self.ttl = ''
        self.subTtl = ''
        self.thirdTtl = ''
        self.item_type = ''
        self.__labels = {}
        self.__labelDisplayMask = 0
        self.__labelStatusMask = 0
        self.thumbThread = None
        #self.thumbFetched.connect(self.setThumb)
        self.jobs = [GetIcon(self)]

    def __updateLabels(self):
        for label in list(self.__labels.keys()):
            widget = self.__labels.pop(label)
            widget.deleteLater()

        for label in self.kLabel.all_labels():
            if label & self.__labelDisplayMask:
                path = self.kLabel.get_path(label, label & self.__labelStatusMask)
                widget = QLabel(self)
                widget.setPixmap(QPixmap(path).scaled(15, 15,
                    Qt.KeepAspectRatioByExpanding))
                self.labelLayout.addWidget(widget)
                self.__labels[label] = widget

    def setLabelDisplay(self, val):
        self.__labelDisplayMask = val
        self.__updateLabels()
    def getLabelDisplay(self):
        return self.__labelDisplayMask
    labelDisplay = property(getLabelDisplay, setLabelDisplay)

    def setLabelStatus(self, val):
        self.__labelStatusMask = val
        self.__updateLabels()
    def getLabelStatus(self):
        return self.__labelStatusMask
    labelStatus = property(getLabelStatus, setLabelStatus)

    def get_title(self):
        return self.ttl

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
        if not thumbPath:
            thumbPath = osp.join(iconPath, 'no_preview.png')
        pix = QPixmap(thumbPath)
        pix = pix.scaled(100, 100, Qt.KeepAspectRatio)
        self.thumbLabel.setPixmap(pix)
        self.thumb_added = True

    def setType(self, item_type):
        self.item_type = item_type

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

    def addLabel(self):
        pass

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

class SObjectItem(Item):
    pass

class ContextItem(Item):
    pass

class TaskItem(Item):
    pass

class GetSnapshotInfo(DeferredItemJob):

    def __init__(self, parent):
        super(GetSnapshotInfo, self).__init__(parent)
        self.snapshot = None
        self.publish_targets = None
        self.compatibles = None
        self.retries = 1

    def doAsync(self):
        try:
            util_copy = util.create_new()
            snapshot = util_copy.get_snapshot_info(self._parent.objectName())
            self.publish_targets = util_copy.get_all_publish_targets(snapshot)
            self.compatibles = util_copy.get_cache_compatible_objects(snapshot)
            self.setSuccess()
            self.jobDone.emit()
        except Exception as e:
            self.setFailure()
            import traceback
            traceback.print_exc()
            print type(e), e
            raise e

    def update(self):
        if self.publish_targets:
            self._parent.labelStatus |= self._parent.kLabel.kPUB
            self._parent.labelDisplay |= self._parent.kLabel.kPUB
        if self.compatibles:
            self._parent.labelStatus |= self._parent.kLabel.kPAIR
        self._parent.labelDisplay |= self._parent.kLabel.kPAIR

class SnapshotItem(Item):
    def __init__(self, parent=None):
        super(SnapshotItem, self).__init__(parent=parent)
        self.jobs.append(GetSnapshotInfo(self))
FileItem = SnapshotItem
