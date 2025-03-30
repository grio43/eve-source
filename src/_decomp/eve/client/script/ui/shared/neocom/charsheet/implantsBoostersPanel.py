#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\implantsBoostersPanel.py
import dogma.data
import evetypes
from carbonui.primitives.container import Container
from carbonui.util.sortUtil import SortListOfTuples
from dogma.const import attributeNonDiminishingSkillInjectorUses
from eve.client.script.ui.control.entries.divider import DividerEntry
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.icon import IconEntry
from eve.client.script.ui.control.entries.implant import ImplantEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.common.lib import appConst as const
from fsdBuiltData.common.iconIDs import GetIconFile
from localization import GetByLabel
import blue

class ImplantsBoostersPanel(Container):
    default_name = 'ImplantsBoostersPanel'
    __notifyevents__ = ['OnGodmaItemChange',
     'OnBoosterUpdated',
     'OnImplantsChanged',
     'OnNonDiminishingInjectionsChanged']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.scroll = Scroll(parent=self, padding=(0, 4, 0, 4))

    def LoadPanel(self, *args):
        mygodma = self.GetMyGodmaItem(session.charid)
        if not mygodma:
            return
        implants = mygodma.implants
        boosters = mygodma.boosters
        godma = sm.GetService('godma')
        implants = SortListOfTuples([ (getattr(godma.GetType(implant.typeID), 'implantness', None), implant) for implant in implants ])
        boosters = SortListOfTuples([ (getattr(godma.GetType(booster.boosterTypeID), 'boosterness', None), booster) for booster in boosters ])
        scrolllist = []
        if implants:
            scrolllist.append(GetFromClass(Header, {'label': GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Augmentations/Implants', implantCount=len(implants))}))
            for booster in implants:
                scrolllist.append(GetFromClass(ImplantEntry, {'implant_booster': booster,
                 'label': evetypes.GetName(booster.typeID)}))

            if boosters:
                scrolllist.append(GetFromClass(DividerEntry))
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        staticMgr = dogmaLocation.dogmaStaticMgr
        if boosters:
            scrolllist.append(GetFromClass(Header, {'label': GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Augmentations/Boosters', boosterCount=len(boosters))}))
            for booster in boosters:
                scrolllist.append(GetFromClass(ImplantEntry, {'implant_booster': booster,
                 'label': evetypes.GetName(booster.boosterTypeID)}))
                boosterEffects = staticMgr.GetPassiveFilteredEffectsByType(booster.boosterTypeID)
                for effectID in boosterEffects:
                    eff = dogma.data.get_effect(effectID)
                    chanceAttributeID = staticMgr.effects[effectID].fittingUsageChanceAttributeID
                    if chanceAttributeID and effectID in booster.sideEffectIDs:
                        effectDisplayName = dogma.data.get_effect_display_name(effectID)
                        scrolllist.append(GetFromClass(IconEntry, {'line': 1,
                         'hint': effectDisplayName,
                         'text': None,
                         'label': effectDisplayName,
                         'icon': GetIconFile(eff.iconID),
                         'selectable': 0,
                         'iconoffset': 32,
                         'iconsize': 22,
                         'linecolor': (1.0, 1.0, 1.0, 0.125)}))

                self._AddNonDiminishingSkillInjectorUses(staticMgr, booster, scrolllist)
                scrolllist.append(GetFromClass(DividerEntry))

        self.scroll.sr.id = 'charsheet_implantandboosters'
        self.scroll.Load(fixedEntryHeight=32, contentList=scrolllist, noContentHint=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Augmentations/NoImplantOrBoosterInEffect'))

    def _AddNonDiminishingSkillInjectorUses(self, staticMgr, booster, scrolllist):
        hasNonDiminishingSkillInjectorUses = staticMgr.GetTypeAttribute(booster.typeID, attributeNonDiminishingSkillInjectorUses, defaultValue=0)
        if hasNonDiminishingSkillInjectorUses:
            timesRemaining = sm.GetService('nonDiminishingInjection').GetRemaining()
            iconID = evetypes.GetIconID(const.typeSkillInjector)
            scrolllist.append(GetFromClass(IconEntry, {'line': 1,
             'hint': evetypes.GetName(booster.typeID),
             'text': None,
             'label': GetByLabel('UI/Skills/NonDiminishingInjectionsRemainingForBooster', timesRemaining=int(timesRemaining)),
             'icon': GetIconFile(iconID),
             'selectable': 0,
             'iconoffset': 32,
             'iconsize': 22,
             'linecolor': (1.0, 1.0, 1.0, 0.125)}))

    def GetMyGodmaItem(self, itemID):
        ret = sm.GetService('godma').GetItem(itemID)
        while ret is None and not self.destroyed:
            blue.pyos.synchro.SleepWallclock(500)
            ret = sm.GetService('godma').GetItem(itemID)

        return ret

    def OnGodmaItemChange(self, item, change):
        if const.ixLocationID in change and item.categoryID == const.categoryImplant and item.flagID in [const.flagBooster, const.flagImplant]:
            self.LoadPanel()

    def OnBoosterUpdated(self):
        if self.display:
            self.LoadPanel()

    def OnImplantsChanged(self):
        if self.display:
            self.LoadPanel()

    def OnNonDiminishingInjectionsChanged(self):
        if self.display:
            self.LoadPanel()
