#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\attributesPanel.py
from carbonui.primitives.container import Container
from dogma.attributes.format import GetFormattedAttributeAndValue
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.neocom.attributes import AttributeRespecEntry
from eve.common.lib import appConst as const
from eve.common.script.sys.dbrow import LookupConstValue
from localization import GetByLabel

class AttributesPanel(Container):
    default_name = 'AttributesPanel'
    __notifyevents__ = ['OnAttribute', 'OnAttributes', 'OnRespecInfoUpdated']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.scroll = Scroll(parent=self, padding=(0, 4, 0, 4))
        self.scroll.sr.id = 'charsheet_myattributes'

    def LoadPanel(self, *args):
        self.scroll.Load(fixedEntryHeight=32, contentList=self.GetScrollList(), noContentHint=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/NoAttributesFound'))

    def GetScrollList(self):
        attributeIDs = (const.attributePerception,
         const.attributeMemory,
         const.attributeWillpower,
         const.attributeIntelligence,
         const.attributeCharisma)
        scrollList = [ self.GetEntry(attributeID) for attributeID in attributeIDs ]
        respecInfo = sm.GetService('skills').GetRespecInfo()
        self.respecEntry = GetFromClass(AttributeRespecEntry, {'nextTimedRespec': respecInfo['nextTimedRespec'],
         'freeRespecs': respecInfo['freeRespecs']})
        scrollList.append(self.respecEntry)
        return scrollList

    def GetEntry(self, attributeID):
        value = sm.GetService('skills').GetCharacterAttributes()[attributeID]
        formatInfo = GetFormattedAttributeAndValue(attributeID, value)
        if not formatInfo:
            return None
        return GetFromClass(LabelTextSides, {'attributeID': attributeID,
         'label': formatInfo.displayName,
         'text': formatInfo.value,
         'iconID': formatInfo.iconID,
         'typeID': formatInfo.infoTypeID,
         'itemID': session.charid,
         'OnClick': lambda : sm.GetService('info').OnAttributeClick(attributeID, session.charid)})

    def UpdateInline(self, attributeID):
        for entry in self.scroll.GetNodes():
            if entry.attributeID == attributeID:
                value = sm.GetService('skills').GetCharacterAttributes()[attributeID]
                entry.text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/Points', skillPoints=int(value))
                if entry.panel:
                    entry.panel.sr.text.text = entry.text
                    entry.panel.hint = entry.text.replace('<t>', '  ')

    def OnAttribute(self, attributeName, item, value):
        if not self.display:
            return
        if attributeName in ('memory', 'intelligence', 'willpower', 'perception', 'charisma'):
            self.UpdateInline(LookupConstValue('attribute%s' % attributeName.capitalize(), 0))

    def OnAttributes(self, changes):
        for attributeName, item, value in changes:
            self.OnAttribute(attributeName, item, value)

    def OnRespecInfoUpdated(self):
        if self.display:
            self.LoadPanel()
