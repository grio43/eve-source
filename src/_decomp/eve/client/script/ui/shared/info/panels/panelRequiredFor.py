#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelRequiredFor.py
import eveformat
import evetypes
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.listgroup import ListGroup
from evetypes.skills import get_required_skills_index

class RequiredForScrollController:

    def __init__(self):
        self.skillSvc = sm.GetService('skills')

    def GetRequiredForScrollList(self, typeID, skillLevel):
        typeIndex = get_required_skills_index().get(typeID, {})
        typesByMarketAndMetaGroups = typeIndex.get(skillLevel, {})
        marketGroupIDs = [ marketGroupID for marketGroupID in typesByMarketAndMetaGroups.iterkeys() ]
        return self._GetScrollList(marketGroupIDs, skillLevel, typeID)

    def _GetScrollList(self, marketGroupIDs, skillLevel, typeID):
        scrolllist = []
        for marketGroupID in marketGroupIDs:
            marketGroup = cfg.GetMarketGroup(marketGroupID)
            scrolllist.append(GetFromClass(ListGroup, data={'GetSubContent': self._GetRequiredForLevelGroupSubContent,
             'label': marketGroup.marketGroupName,
             'skillLevel': int(skillLevel),
             'sublevel': 0,
             'showlen': False,
             'typeID': typeID,
             'marketGroupID': marketGroupID,
             'id': ('skillGroups_group', marketGroupID),
             'state': 'locked',
             'iconID': marketGroup.iconID,
             'openByDefault': True}))

        return scrolllist

    def GetUnlockTypeIDsByMarketGroup(self, typeID, skillLevel):
        ret = {}
        typesByMarketAndMetaGroupID = self.skillSvc.GetTypesUnlockedByTrainingToLevel(typeID, skillLevel)
        for marketGroupID, typesByMetaGroupID in typesByMarketAndMetaGroupID.iteritems():
            ret[marketGroupID] = self.GetRequiredForTypeIDs(typesByMetaGroupID)

        return ret

    def _GetRequiredForLevelGroupSubContent(self, data, *args):
        skillTypeID = data['typeID']
        skillLevel = data['skillLevel']
        skillMarketGroup = data['marketGroupID']
        typeIndex = get_required_skills_index().get(skillTypeID, {})
        typesByMetaGroupID = typeIndex.get(skillLevel, {})[skillMarketGroup]
        typeIDs = self.GetRequiredForTypeIDs(typesByMetaGroupID)
        return self.GetTypeScrollList(typeIDs, subLevel=1)

    def GetTypeScrollList(self, typeIDs, subLevel = 0):
        scrollList = []
        for typeID in typeIDs:
            scrollList.append(GetFromClass(Item, {'label': evetypes.GetName(typeID),
             'sublevel': subLevel,
             'typeID': typeID,
             'showinfo': True,
             'getIcon': True,
             'showTooltip': False,
             'disableIcon': sm.GetService('cloneGradeSvc').IsRestrictedForAlpha(typeID)}))

        return scrollList

    def GetRequiredForTypeIDs(self, typesByMetaGroupID):
        requiredForTypeIDs = []
        for metaGroupID, typeIDs in sorted(typesByMetaGroupID.iteritems(), key=lambda x: x[0]):
            for typeID in typeIDs:
                if not evetypes.IsPublished(typeID):
                    continue
                requiredForTypeIDs.append(typeID)

        return requiredForTypeIDs


class PanelRequiredFor(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.controller = RequiredForScrollController()
        self.skillSvc = sm.GetService('skills')

    def Load(self):
        self.Flush()
        toggleButtonCont = Container(name='btnGroupCont', parent=self, align=uiconst.TOTOP, height=35)
        btnGroup = ToggleButtonGroup(parent=toggleButtonCont, align=uiconst.CENTER, height=toggleButtonCont.height, width=300, padding=(10, 4, 10, 3), callback=self.LoadRequiredForLevel)
        for level in xrange(1, 6):
            hint = localization.GetByLabel('UI/InfoWindow/RequiredForLevelButtonHint', skillName=evetypes.GetName(self.typeID), level=level)
            typeIndex = get_required_skills_index().get(self.typeID, {})
            typesByMarketAndMetaGroupID = typeIndex.get(level, {})
            isDisabled = not bool(typesByMarketAndMetaGroupID)
            btnGroup.AddButton(btnID=level, label=eveformat.number_roman(level), hint=hint, isDisabled=isDisabled)

        self.scroll = Scroll(name='scroll', parent=self, padding=uiconst.defaultPadding)
        btnGroup.SelectFirst()

    def LoadRequiredForLevel(self, level, *args):
        scrolllist = self.controller.GetRequiredForScrollList(self.typeID, level)
        self.scroll.Load(fixedEntryHeight=27, contentList=scrolllist)
