#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\eveEdit.py
import utillib
from carbon.common.script.util import commonutils
from carbonui import uiconst
from carbonui.control.edit import EditCore
from carbonui.uicore import uicore
from eve.client.script.ui.util import searchOld, uix
import evetypes
import localization
import log
from eve.client.script.ui.control.eveEdit_Parser import ParserBase

class Edit(EditCore):
    __guid__ = 'uicontrols.Edit'
    default_align = uiconst.TOALL
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0

    def UpdateUIScaling(self, value, oldValue):
        super(Edit, self).UpdateUIScaling(value, oldValue)
        if not self.destroyed:
            self.DoContentResize()

    def OnDropDataDelegate(self, node, nodes):
        EditCore.OnDropDataDelegate(self, node, nodes)
        if self.readonly:
            return
        log.LogException('Nowadays, this old edit field is only be used for read only, but is being used to edit text?')

    def ApplyGameSelection(self, what, data, changeObjs):
        if what == 6 and len(changeObjs):
            key = {}
            if data:
                key['link'] = data['link']
                t = self.DoSearch(key['link'], data['text'])
                if not t:
                    return
            else:
                format = [{'type': 'checkbox',
                  'label': '_hide',
                  'text': 'http://',
                  'key': 'http://',
                  'required': 1,
                  'setvalue': 1,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': localization.GetByLabel('UI/Common/Character'),
                  'key': 'char',
                  'required': 1,
                  'setvalue': 0,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': localization.GetByLabel('UI/Common/Corporation'),
                  'key': 'corp',
                  'required': 1,
                  'setvalue': 0,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': localization.GetByLabel('UI/Common/ItemType'),
                  'key': 'type',
                  'required': 1,
                  'setvalue': 0,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': localization.GetByLabel('UI/Common/SolarSystem'),
                  'key': 'solarsystem',
                  'required': 1,
                  'setvalue': 0,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': localization.GetByLabel('UI/Common/Station'),
                  'key': 'station',
                  'required': 1,
                  'setvalue': 0,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'push'},
                 {'type': 'edit',
                  'label': localization.GetByLabel('UI/Common/HtmlLink'),
                  'text': 'http://',
                  'labelwidth': 100,
                  'required': 1,
                  'key': 'txt'},
                 {'type': 'push'}]
                key = self.AskLink(localization.GetByLabel('UI/Common/EnterLink'), format, width=400)
            anchor = -1
            if key:
                link = key['link']
                if link == None:
                    return
                if link in ('char', 'corp', 'alliance', 'solarsystem', 'station', 'type'):
                    if not self.typeID:
                        t = self.DoSearch(link, key['txt'])
                        if not t:
                            return
                    anchor = 'showinfo:' + str(self.typeID)
                    if self.itemID:
                        anchor += '//' + str(self.itemID)
                elif link == 'fleet':
                    anchor = 'fleet:' + str(self.itemID)
                elif link == 'http://':
                    if key['txt'].startswith(key['link']) or key['txt'].startswith('https://'):
                        anchor = ''
                    else:
                        anchor = key['link']
                    anchor += key['txt']
                else:
                    anchor = key['link'] + key['txt']
            return anchor
        return -1

    def OnLinkTypeChange(self, chkbox, *args):
        if chkbox.GetValue():
            self.itemID = self.typeID = 0
            self.key = chkbox.data['key']
            text = chkbox.GetChild('text')
            wnd = chkbox.FindParentByName(localization.GetByLabel('UI/Common/GenerateLink'))
            if not wnd:
                return
            editParent = wnd.FindChild('editField')
            if editParent is not None:
                label = editParent.FindChild('label')
                label.text = text.text
                edit = editParent.FindChild('edit_txt')
                edit.SetValue('')
                self.sr.searchbutt = editParent.FindChild('button')
                if self.key in ('char', 'corp', 'type', 'solarsystem', 'station'):
                    if self.sr.searchbutt == None:
                        from carbonui.control.button import Button
                        self.sr.searchbutt = Button(parent=editParent, label=localization.GetByLabel('UI/Common/SearchForItemType'), func=self.OnSearch, btn_default=0, align=uiconst.TOPRIGHT)
                    else:
                        self.sr.searchbutt.state = uiconst.UI_NORMAL
                    edit.width = 55
                elif self.sr.searchbutt != None:
                    self.sr.searchbutt.state = uiconst.UI_HIDDEN
                    edit.width = 0

    def OnSearch(self, *args):
        wnd = self.sr.searchbutt.FindParentByName(localization.GetByLabel('UI/Common/GenerateLink'))
        if not wnd:
            return
        editParent = wnd.FindChild('editField')
        edit = editParent.FindChild('edit_txt')
        val = edit.GetValue().strip().lower()
        name = self.DoSearch(self.key, val)
        if name is not None:
            edit.SetValue(name)

    def DoSearch(self, key, val):
        self.itemID = None
        self.typeID = None
        id = None
        name = ''
        if key == 'type':
            if getattr(self, 'markettypes', None) == None:
                from eve.client.script.util.contractutils import GetMarketTypes
                self.markettypes = GetMarketTypes()
            itemTypes = []
            for t in self.markettypes:
                if t.typeName.lower().find(val.lower()) >= 0:
                    itemTypes.append((evetypes.GetName(t.typeID), None, t.typeID))

            if not itemTypes:
                eve.Message('NoItemTypesFound')
                return
            id = uix.ListWnd(itemTypes, 'item', localization.GetByLabel('UI/Common/SelectItemType'), None, 1)
        else:
            group = None
            hideNPC = 0
            if key == 'solarsystem':
                group = const.groupSolarSystem
            elif key == 'station':
                group = const.groupStation
            elif key == 'char':
                group = const.groupCharacter
            elif key == 'corp':
                group = const.groupCorporationOwner
            elif key == 'alliance':
                group = const.groupAlliance
            id = searchOld.Search(val, group, hideNPC=hideNPC, listType='Generic')
        name = ''
        if id:
            self.itemID = id
            self.typeID = 0
            if key in ('char', 'corp', 'alliance'):
                o = cfg.eveowners.Get(id)
                self.typeID = o.typeID
                name = o.name
            elif key == 'solarsystem':
                l = cfg.evelocations.Get(id)
                self.typeID = l.typeID
                name = l.name
            elif key == 'station':
                self.typeID = sm.GetService('ui').GetStationStaticInfo(id).stationTypeID
                l = cfg.evelocations.Get(id)
                name = l.name
            elif key == 'type':
                self.typeID = id[2]
                self.itemID = None
                name = id[0]
        return name

    def AskLink(self, label = '', lines = [], width = 280):
        icon = uiconst.QUESTION
        format = [{'type': 'text',
          'text': label}] + lines
        retval = uix.HybridWnd(format, caption=localization.GetByLabel('UI/Common/GenerateLink'), windowID='askLink', modal=1, buttons=uiconst.OKCANCEL, minW=width, minH=110, icon=icon)
        if retval:
            return retval
        else:
            return None

    def AddLink(self, text, link = None):
        self.SetSelectionRange(None, None)
        text = commonutils.StripTags(text, stripOnly=['localized'])
        shiftCursor = len(text)
        node, obj, npos = self.GetNodeAndTextObjectFromGlobalCursor()
        if obj.letters:
            orgString = obj.letters
            orgIndex = node.stack.index(obj)
            obj.letters = orgString[:npos]
            firstSpaceObj = self.GetTextObject(' ')
            firstSpaceObj.a = None
            node.stack.insert(orgIndex + 1, firstSpaceObj)
            newObject = self.GetTextObject(' ')
            newObject.a = None
            node.stack.insert(orgIndex + 2, newObject)
            restObj = obj.Copy()
            restObj.letters = orgString[npos:]
            if restObj.letters:
                node.stack.insert(orgIndex + 3, restObj)
        else:
            newObject = obj
            newObject.a = None
        newObject.letters = text
        if link is not None:
            anchor = link
            attr = utillib.KeyVal()
            attr.href = anchor
            attr.alt = anchor
            newObject.a = attr
        endSpaceObj = newObject.Copy()
        endSpaceObj.letters = ' '
        endSpaceObj.a = None
        node.stack.insert(node.stack.index(newObject) + 1, endSpaceObj)
        self._OnResize(0)
        self.SetCursorPosAtObjectEnd(newObject)
        uicore.registry.SetFocus(self)


from carbonui.control.edit import EditCoreOverride
EditCoreOverride.__bases__ = (Edit,)
