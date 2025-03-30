#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\imageserver\validate\mappingchange.py
import os
from itertoolsext.Enum import Enum
_confluenceIconSize = 128

@Enum

class MappingChangeType(object):
    ENTRY_ADDED = 'Entry Added'
    ENTRY_DELETED = 'Entry Deleted'
    ICON_TYPE_ADDED = 'Icon Type Added'
    ICON_TYPE_DELETED = 'Icon Type Deleted'
    ICON_NAME_CHANGED = 'Icon Name Changed'
    ICON_CHANGED = 'Icon Changed'


class MappingChange(object):

    def __init__(self, mappingName, type, id, oldFolder = None, oldValue = None, newFolder = None, newValue = None, iconType = None, diffData = None):
        self.mappingName = mappingName
        self.changeType = type
        self.ids = set()
        self.ids.add(id)
        self.oldValue = oldValue
        self.newValue = newValue
        self.oldFolder = oldFolder
        self.newFolder = newFolder
        self.iconType = iconType
        self.diffData = diffData

    def ToDict(self):
        result = {}
        result['ids'] = ','.join(self.ids)
        result['iconType'] = self.iconType
        result['oldValuePath'] = self._GetOldIconPath()
        result['newValuePath'] = self._GetNewIconPath()
        result['diffData'] = self.diffData.GetReport() if self.diffData else None
        return result

    def ToHtmlConfluenceTableRow(self, confluence, pageID, outputFolder):
        showOld = self.changeType in [MappingChangeType.ICON_CHANGED, MappingChangeType.ICON_NAME_CHANGED]
        showNew = self.changeType in [MappingChangeType.ICON_CHANGED,
         MappingChangeType.ENTRY_ADDED,
         MappingChangeType.ICON_TYPE_ADDED,
         MappingChangeType.ICON_NAME_CHANGED]

        def _BuildName(originalName, suffix):
            name, ext = os.path.splitext(os.path.basename(originalName))
            if len(self.ids) > 10:
                newName = '%s_and_too_many_others' % iter(self.ids).next()
            else:
                newName = str('_'.join(self.ids))
            if self.iconType:
                newName += '_%s' % self.iconType
            newName += '_%s%s' % (suffix, ext)
            return newName

        s = 512 if self.iconType == 'render' else 64
        s = min(_confluenceIconSize, s)
        embeddedImages = ''
        if showOld:
            fileName = _BuildName(self._GetOldIconPath(), 'old')
            confluence.AddOrUpdateImageAttachment(pageID, self._GetOldIconPath(), fileName)
            contentType = confluence.GetImageContentType(fileName)
            embeddedImages += confluence.InsertAttachmentAsImagePreview(pageID, contentType, fileName, s)
            if showNew:
                embeddedImages += '&nbsp;'
        if showNew:
            fileName = _BuildName(self._GetNewIconPath(), 'new')
            confluence.AddOrUpdateImageAttachment(pageID, self._GetNewIconPath(), fileName)
            contentType = confluence.GetImageContentType(fileName)
            embeddedImages += confluence.InsertAttachmentAsImagePreview(pageID, contentType, fileName, s)
            if self.diffData:
                embeddedImages += '&nbsp;'
        if self.diffData:
            diffPath = self._GetDiffImagePath(outputFolder)
            fileName = os.path.basename(diffPath)
            confluence.AddOrUpdateImageAttachment(pageID, diffPath, fileName)
            contentType = confluence.GetImageContentType(fileName)
            embeddedImages += confluence.InsertAttachmentAsImagePreview(pageID, contentType, fileName, s)
        return self._ToHtmlTableRow(embeddedImages)

    def _ToHtmlTableRow(self, embeddedImagesHtml):
        tableStr = '<tr>'
        tableStr += '<td>%s</td>' % ', '.join(self.ids)
        tableStr += '<td>%s</td>' % self.changeType
        tableStr += '<td>%s</td>' % self._GetChangeValueString(True)
        tableStr += '<td>%s</td>' % embeddedImagesHtml
        tableStr += '</tr>'
        return tableStr

    def _GetChangeValueString(self, html = False):
        result = ''
        if self.iconType:
            result += "'%s': " % self.iconType
            if html:
                result = '<b>%s</b><br/>' % result
        if self.changeType in [MappingChangeType.ENTRY_ADDED, MappingChangeType.ICON_TYPE_ADDED, MappingChangeType.ICON_CHANGED]:
            result += str(self.newValue)
        elif self.changeType in [MappingChangeType.ENTRY_DELETED, MappingChangeType.ICON_TYPE_DELETED]:
            result += str(self.oldValue)
        elif self.changeType == MappingChangeType.ICON_NAME_CHANGED:
            result += 'from %s %sto %s' % (self.oldValue, '<br/>' if html else '', self.newValue)
        return result

    def GetDiffString(self):
        if self.diffData:
            return self.diffData.GetReport()
        return ''

    def Matches(self, type, oldFolder, oldValue, newFolder, newValue, iconType):
        return type == self.changeType and oldFolder == self.oldFolder and oldValue == self.oldValue and newFolder == self.newFolder and newValue == self.newValue and iconType == self.iconType

    def AddId(self, id):
        self.ids.add(id)

    def _GetOldIconPath(self):
        if self.oldValue:
            return os.path.join(self.oldFolder, self.oldValue)
        else:
            return None

    def _GetNewIconPath(self):
        if self.newValue:
            return os.path.join(self.newFolder, self.newValue)
        else:
            return None

    def _GetDiffImagePath(self, outputFolder):
        if self.diffData:
            if len(self.ids) > 10:
                name = '%s_and_too_many_others' % iter(self.ids).next()
            else:
                name = '_'.join(self.ids)
            if self.iconType:
                name += '_%s' % self.iconType
            name += '_diff.png'
            path = os.path.join(outputFolder, name)
            self.diffData.SaveDiffImage(path)
            return path
        else:
            return None
