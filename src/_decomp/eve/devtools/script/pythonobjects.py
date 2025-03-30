#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\pythonobjects.py
import gc
import weakref
import sys
import pprint
import blue
import log
import stackless
from carbon.common.script.sys.serviceConst import ROLE_QA
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.htmlwriter import Swing
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.base import Base
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from pympler import asizeof

def srepr(obj):
    try:
        return pprint.saferepr(obj)
    except:
        try:
            t = 'for type ' + type(obj).__name__
        except:
            t = "couldn't even get the typename!"

        return '[srepr failed %s]' % t


def FindObjectByID(obID):
    obID = int(obID)
    objs = gc.get_objects()
    blue_objs = blue.classes.GetWrapperList()
    ob = None
    try:
        for ob in objs:
            if id(ob) == obID:
                return (ob,)

        for ob in blue_objs:
            if id(ob) == obID:
                return (ob,)

        return ()
    finally:
        del objs
        del ob
        del blue_objs


def GetClassName(object):
    typeOrClass = type(object)
    if not isinstance(object, weakref.ProxyType):
        try:
            typeOrClass = object.__class__
        except (AttributeError, ReferenceError):
            sys.exc_clear()

    objectName = '%s.%s' % (typeOrClass.__module__, typeOrClass.__name__)
    return objectName


class PythonObjectsMonitor(Window):
    default_caption = 'Python objects'
    default_windowID = 'pythonobjectsmonitor'
    default_minSize = (500, 400)

    def ApplyAttributes(self, attributes):
        self._ready = False
        Window.ApplyAttributes(self, attributes)
        self.settingsContainer = Container(parent=self.sr.main, align=uiconst.TOTOP, top=8, height=16, padding=8)
        self.filterEdit = SingleLineEditText(parent=self.settingsContainer, align=uiconst.TOLEFT, width=150, label='Filter:', OnReturn=self.PopulateScroll)
        Button(parent=self.settingsContainer, label='Reset', align=uiconst.TORIGHT, func=self.Reset, padRight=8)
        Button(parent=self.settingsContainer, label='Refresh', align=uiconst.TORIGHT, func=self.PopulateScroll, padRight=8)
        self.onlyUiCheckbox = Checkbox(parent=self.settingsContainer, text='Only UI  ', align=uiconst.TORIGHT, callback=self.PopulateScroll, padRight=20)
        self.scroll = Scroll(parent=self.sr.main, id='pythonobjectscroll', align=uiconst.TOALL)
        self.Reset()
        self._ready = True

    def Reset(self, *args):
        wnd = PythonObjectClassDetails.GetIfOpen()
        if wnd:
            wnd.Close()
        self.peakCount = {}
        self.baseCount = {}
        self.filterEdit.SetText('')
        self.PopulateScroll()

    def GetLabelForEntry(self, key, value):
        peak = self.peakCount.get(key, 0)
        delta = value - self.baseCount.get(key, 0)
        if delta < 0:
            color = '0xffff0000'
        else:
            color = '0xff00ff00'
        label = '%s<t><color=%s>%d</color><t>%d<t>%d' % (key,
         color,
         delta,
         value,
         peak)
        return (label, delta)

    def RebuildScrollContents(self, objects, filter, onlyShowUI):
        contentList = []
        newObjects = {}
        for k, v in objects.iteritems():
            if filter and filter not in k.lower():
                continue
            newObjects[k] = v

        if onlyShowUI:
            isUiByClassName = self.GetIsUiDict(newObjects)
        else:
            isUiByClassName = {}
        for key, value in newObjects.iteritems():
            if onlyShowUI:
                if not isUiByClassName[key]:
                    continue
            label, delta = self.GetLabelForEntry(key, value)
            listEntry = ScrollEntryNode(decoClass=SE_GenericCore, id=id, name=key, label=label, OnDblClick=self.ClassEntryDetails, OnGetMenu=self.EntryMenu)
            listEntry.Set('sort_Delta', delta)
            contentList.append(listEntry)

        self.scroll.Load(contentList=contentList, headers=['Name',
         'Delta',
         'Count',
         'Peak'])

    def GetIsUiDict(self, objects):
        activeObjects = gc.get_objects()
        myDict = {}
        for activeObject in activeObjects:
            objectName = GetClassName(activeObject)
            if objectName not in objects or objectName in myDict:
                continue
            myDict[objectName] = isinstance(activeObject, Base)

        return myDict

    def EntryMenu(self, entry):
        if not session.role and ROLE_QA:
            return []
        m = [('Open Details', self.ClassEntryDetails, (entry,))]
        return m

    def ClassEntryDetails(self, entry, *args):
        if not session.role and ROLE_QA:
            return
        wnd = PythonObjectClassDetails.GetIfOpen()
        if wnd:
            wnd.SwitchItemClass(entry.name)
            wnd.Maximize()
        else:
            PythonObjectClassDetails.Open(itemClass=entry.name)

    def PopulateScroll(self, *args):
        objectsByType = {}
        for object in gc.get_objects():
            tp = type(object)
            if not isinstance(object, weakref.ProxyType):
                try:
                    tp = object.__class__
                except (AttributeError, ReferenceError):
                    sys.exc_clear()

            objectsByType[tp] = objectsByType.get(tp, 0) + 1

        objectsByModuleAndType = {}
        for k, v in objectsByType.iteritems():
            name = k.__module__ + '.' + k.__name__
            objectsByModuleAndType[name] = objectsByModuleAndType.get(name, 0) + v

        for key, value in objectsByModuleAndType.iteritems():
            peak = self.peakCount.get(key, 0)
            if value > peak:
                self.peakCount[key] = value
            if key not in self.baseCount:
                self.baseCount[key] = value

        filter = self.filterEdit.text.lower()
        onlyShowUi = self.onlyUiCheckbox.GetValue()
        self.RebuildScrollContents(objectsByModuleAndType, filter, onlyShowUi)


class PythonObjectClassDetails(Window):
    default_caption = 'Python Object Class Details'
    default_windowID = 'pythonobjectclassdetails'
    default_minSize = (500, 400)

    def ApplyAttributes(self, attributes):
        self._ready = False
        Window.ApplyAttributes(self, attributes)
        self.maxLen = 250
        self.collectTimestamp = None
        self.itemClass = attributes.itemClass
        self.classDetailsContainer = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, padding=8)
        Button(parent=self.sr.main, label='GC and Refresh', align=uiconst.TOPRIGHT, func=self.GarbageCollectAndRefresh, padRight=8)
        self.scroll = Scroll(parent=self.sr.main, id='pythonobjectclassdetailscroll', align=uiconst.TOALL)
        self.ShowObjectDetail()
        self._ready = True

    def Close(self, setClosed = False, *args, **kwds):
        wnd = PythonObjectDetails.GetIfOpen()
        if wnd:
            wnd.Close()
        self.scroll = None
        self.classDetailsContainer = None
        Window.Close(self, setClosed, *args, **kwds)

    def GarbageCollectAndRefresh(self, *args):
        import gc
        self.scroll.Clear()
        self.classDetailsContainer.Flush()
        print 'cleaned up: ', gc.collect()
        self.Refresh()

    def Refresh(self):
        self.scroll.Clear()
        self.classDetailsContainer.Flush()
        self.ShowObjectDetail()

    def SwitchItemClass(self, itemClass):
        if not self._ready:
            return
        wnd = PythonObjectDetails.GetIfOpen()
        if wnd:
            wnd.Close()
        self.itemClass = itemClass
        self._ready = False
        self.Refresh()
        self._ready = True

    def PopulateScroll(self, objectData, destroyedCountLabel):
        contentList = []
        destroyedCount = 0
        for i, obj in enumerate(objectData):
            objectName = self.GetObjectName(obj)
            parentName = getattr(getattr(obj, 'parent', None), 'name', '-')
            debugDisplayName = getattr(obj, 'debugDisplayName', None)
            if not debugDisplayName:
                debugDisplayName = getattr(obj, 'name', ' - ')
            isDestroyed = getattr(obj, 'destroyed', 'N/A')
            if isDestroyed is True:
                destroyedCount += 1
            label = '%s<t>%s<t>%s<t>%s' % (objectName,
             debugDisplayName,
             isDestroyed,
             parentName)
            listEntry = ScrollEntryNode(decoClass=SE_GenericCore, id=objectName, label=label, OnDblClick=self.EntryDetails, OnGetMenu=self.EntryMenu, refid=id(obj))
            contentList.append(listEntry)
            if i >= self.maxLen:
                break

        self.scroll.Load(contentList=contentList, headers=['ObjectName',
         'debugDisplayName',
         'isDestroyed',
         'parentName(?)'])
        destroyedCountLabel.text = 'Destroyed count: %s' % destroyedCount

    def ShowObjectDetail(self):
        objectDetails = self.GetObjectDetails()
        classLabel = EveLabelMedium(name='classLabel', parent=self.classDetailsContainer, text='module.class: %s' % self.itemClass, align=uiconst.TOTOP)
        timeStamp = EveLabelMedium(name='timestamp', parent=self.classDetailsContainer, text='Collected at %s' % FmtDate(self.collectTimestamp), align=uiconst.TOTOP)
        oCount = len(objectDetails)
        countText = '%s Objects' % oCount
        if oCount > self.maxLen:
            countText += ', only first %s displayed' % self.maxLen
        objectCount = EveLabelMedium(name='oCount', parent=self.classDetailsContainer, text=countText, align=uiconst.TOTOP)
        destroyedCount = EveLabelMedium(name='destroyedCount', parent=self.classDetailsContainer, text='-', align=uiconst.TOTOP)
        self.PopulateScroll(objectDetails, destroyedCount)

    def EntryMenu(self, entry):
        m = [('Open Details', self.EntryDetails, (entry,))]
        return m

    def EntryDetails(self, entry):
        wnd = PythonObjectDetails.GetIfOpen()
        if wnd:
            wnd.Switch(entry.sr.node.refid)
            wnd.Maximize()
        else:
            PythonObjectDetails.Open(refid=entry.sr.node.refid)

    def GetObjectDetails(self):
        self.collectTimestamp = startTime = blue.os.GetWallclockTimeNow()
        activeObjects = gc.get_objects()
        blueObjects = blue.classes.GetWrapperList()
        objectDetails = []
        for activeObject in activeObjects:
            objectName = GetClassName(activeObject)
            if objectName == self.itemClass:
                objectDetails.append(activeObject)

        for activeBlueObject in blueObjects:
            if activeBlueObject.__bluetype__ == self.itemClass:
                objectDetails.append(activeBlueObject)

        endTime = blue.os.GetWallclockTimeNow()
        log.LogInfo('Finished fetching object details in %s Ms' % blue.os.TimeDiffInMs(startTime, endTime))
        return objectDetails

    def GetObjectName(self, object):
        try:
            className = object.__class__
        except AttributeError:
            className = object.__bluetype__

        objectName = '%s at 0x%.8x' % (className, id(object))
        objectName = '%s - Ref Count = %s - Size: %s' % (objectName, sys.getrefcount(object) - 4, asizeof.asizeof(object, limit=3))
        objectName = Swing(objectName)
        return objectName


class PythonObjectDetails(Window):
    default_caption = 'Python Object Details'
    default_windowID = 'pythonobjectdetails'
    default_minSize = (400, 400)

    def ApplyAttributes(self, attributes):
        self._ready = False
        Window.ApplyAttributes(self, attributes)
        self.subWindow = None
        self.errorMessage = None
        self.objectRefID = attributes.refid
        self.object = self.GetObject()
        self.classDetailsContainer = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, padding=8)
        self.main = Container(name='main', parent=self.sr.main, align=uiconst.TOALL)
        self.ShowObjectDetail()
        self._ready = True

    def Close(self, setClosed = False, *args, **kwds):
        self.object = None
        wnd = PythonObjectDetails.GetIfOpen(windowID='pythonobjectdetails_sub_%s' % id(self.object))
        if wnd:
            wnd.Close()
        Window.Close(self, setClosed, *args, **kwds)

    def Refresh(self):
        self.scroll.Clear()
        self.classDetailsContainer.Flush()
        self.main.Flush()
        self.ShowObjectDetail()

    def Switch(self, refid):
        if not self._ready:
            return
        windowID = 'pythonobjectdetails_sub_%s' % id(self.object)
        wnd = PythonObjectDetails.GetIfOpen(windowID=windowID)
        if wnd:
            wnd.Close()
        self.errorMessage = None
        self.objectRefID = refid
        self.object = self.GetObject()
        self.Refresh()
        self._ready = True

    def ShowObjectDetail(self):
        self.listCont = Container(name='listCont', parent=self.main, align=uiconst.TOBOTTOM, height=140, padding=8)
        self.objRepr = Container(name='objRepr', parent=self.main, align=uiconst.TOALL, height=20, padding=8)
        className = GetClassName(self.object)
        objectName = self.GetObjectName(self.object)
        objectRepr = self.GetObjectRepr(self.object)
        objectSizes = self.GetObjectSizes(self.object)
        EveLabelMedium(parent=self.classDetailsContainer, text='Class name: %s' % className, align=uiconst.TOTOP, height=15)
        EveLabelMedium(parent=self.classDetailsContainer, text='Object name: %s' % objectName, align=uiconst.TOTOP, height=15)
        EveLabelMedium(parent=self.classDetailsContainer, text='Sizes: %s' % objectSizes, align=uiconst.TOTOP, height=20)
        EveLabelMedium(parent=self.objRepr, text='Repr: %s' % objectRepr, align=uiconst.TOALL)
        EveLabelMedium(parent=self.listCont, text='Incoming Refs:', align=uiconst.TOTOP, height=16)
        self.scroll = Scroll(parent=self.listCont, id='pythonobjectrefereesscroll', align=uiconst.TOALL)
        self.PopulateScroll()

    def GetObject(self):
        ob = FindObjectByID(self.objectRefID)
        if not ob:
            log.LogWarn('This Object could not be found %s' % self.objectRefID)
            return
        return ob[0]

    def GetObjectName(self, object):
        try:
            className = object.__class__
        except AttributeError:
            className = object.__bluetype__

        objectName = '%s at 0x%.8x' % (className, id(object))
        objectName = '%s - Ref Count = %s  - %s' % (objectName, sys.getrefcount(object) - 4, getattr(object, 'destroyed', 'N/A'))
        objectName = Swing(objectName)
        return objectName

    def GetObjectRepr(self, object):
        objectRepr = Swing(srepr(object))
        if len(objectRepr) < 1001:
            return objectRepr
        return objectRepr[:1000]

    def GetObjectSizes(self, object):
        sizes = [ asizeof.asizeof(object, limit=l) for l in range(8) ]
        return sizes

    def PopulateScroll(self):
        contentList = self.GetReferees()
        self.scroll.Load(contentList=contentList)

    def GetReferees(self):
        refList = []
        referrers = gc.get_referrers(self.object)
        known = [gc.garbage,
         stackless.getcurrent().frame,
         self.object,
         self.scroll,
         self.__dict__]
        for ref in referrers:
            if ref not in known:
                try:
                    objectName = self.GetObjectName(ref)
                    refid = id(ref)
                    listEntry = ScrollEntryNode(decoClass=SE_GenericCore, id=id, name=objectName, label=objectName, OnDblClick=self.EntryDetails, OnGetMenu=self.EntryMenu, refid=refid)
                    refList.append(listEntry)
                except Exception:
                    log.LogException('Invalid reference')

        return refList

    def EntryMenu(self, entry):
        m = [('Open Details', self.EntryDetails, (entry,))]
        return m

    def EntryDetails(self, entry):
        windowID = 'pythonobjectdetails_sub_%s' % id(self.object)
        wnd = PythonObjectDetails.GetIfOpen(windowID=windowID)
        if wnd:
            wnd.Switch(entry.sr.node.refid)
            wnd.Maximize()
        else:
            PythonObjectDetails.Open(refid=entry.sr.node.refid, windowID=windowID)
