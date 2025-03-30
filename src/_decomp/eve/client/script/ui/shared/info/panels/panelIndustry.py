#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelIndustry.py
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.color import Color
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control.entries.button import ButtonEntry
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.control.toggleButtonGroupButton import ToggleButtonGroupButtonIcon
from eve.client.script.ui.shared.cloneGrade import ORIGIN_INDUSTRY
from eve.client.script.ui.shared.cloneGrade.omegaRestrictedEntry import OmegaRestrictedEntry
from eve.client.script.ui.shared.industry import industryUIConst
from eve.client.script.ui.shared.industry.activitySelectionButtons import ActivityToggleButtonGroupButton
from eve.common.lib import appConst as const
import evetypes
import industry
import localization
from carbonui.primitives.container import Container
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold
from eve.client.script.ui.control.eveScroll import Scroll
from shipfitting.multiBuyUtil import BuyMultipleTypesWithQty

class PanelIndustry(Container):
    __notifyevents__ = ['OnSubscriptionChanged']

    def ApplyAttributes(self, attributes):
        sm.RegisterNotify(self)
        Container.ApplyAttributes(self, attributes)
        self.bpData = attributes.bpData

    def Load(self):
        self.Flush()
        topCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, padding=(0, 2, 0, 2))
        btnGroup = ToggleButtonGroup(parent=topCont, align=uiconst.CENTER, height=38, width=248, callback=self.LoadActivity, btnClass=ToggleButtonGroupButtonIcon)
        for activityID in industry.ACTIVITIES:
            isDisabled = activityID not in self.bpData.activities
            color = industryUIConst.GetActivityColor(activityID)
            color = Color(*color).SetBrightness(0.5).GetRGBA()
            btnGroup.AddButton(activityID, iconPath=industryUIConst.ACTIVITY_ICONS_LARGE[activityID], iconSize=26, colorSelected=color, isDisabled=isDisabled, btnClass=ActivityToggleButtonGroupButton, activityID=activityID)

        self.activityNameLabel = EveLabelMediumBold(name='label', parent=self, align=uiconst.TOTOP, padding=(6, 0, 0, 0))
        self.omegaEntry = OmegaRestrictedEntry(parent=self, align=uiconst.TOTOP, height=30, state=uiconst.UI_HIDDEN, padding=(4, 2, 4, 0), origin=ORIGIN_INDUSTRY)
        self.scroll = Scroll(parent=self, padding=const.defaultPadding)
        activityID = self.GetSelectedActivityID(activityID)
        btnGroup.SelectByID(activityID)

    def GetSelectedActivityID(self, activityID):
        activityID = settings.char.ui.Get('blueprintShowInfoActivityID', 0)
        if activityID not in self.bpData.activities:
            activityID = sorted(self.bpData.activities.keys())[0]
        return activityID

    def LoadActivity(self, activityID, *args):
        settings.char.ui.Set('blueprintShowInfoActivityID', activityID)
        self.job = industry.Job(self.bpData, activityID)
        self.activityNameLabel.text = self.job.activity.GetHint()
        self.UpdateOmegaEntry(activityID)
        entries = []
        entries.append(GetFromClass(LabelTextSides, {'line': 1,
         'label': localization.GetByLabel('UI/Industry/TimePerRun'),
         'text': self.job.GetJobTimeLeftLabel()}))
        if self.job.activityID == industry.COPYING:
            entries.append(GetFromClass(LabelTextSides, {'line': 1,
             'label': localization.GetByLabel('UI/Industry/MaxRunsPerCopy'),
             'text': self.bpData.maxProductionLimit}))
        if self.job.activityID == industry.INVENTION:
            entries.append(GetFromClass(LabelTextSides, {'line': 1,
             'label': localization.GetByLabel('UI/Industry/JobSuccessProbability'),
             'text': '%s%%' % (self.job.probability * 100)}))
        entries.append(GetFromClass(ListGroup, {'GetSubContent': self.LoadOutcome,
         'label': self.GetOutcomeCaption(),
         'groupItems': self.job.products,
         'id': 'outcome',
         'showicon': 'hide',
         'showlen': False,
         'state': 'locked',
         'BlockOpenWindow': True}))
        entries.append(GetFromClass(ListGroup, {'GetSubContent': self.LoadSkills,
         'label': localization.GetByLabel('UI/Industry/RequiredSkills'),
         'groupItems': [ (skill.typeID, skill.level, skill.GetHint()) for skill in self.job.required_skills ],
         'id': 'skills',
         'showicon': 'hide',
         'noItemText': localization.GetByLabel('UI/Common/None'),
         'state': 'locked',
         'BlockOpenWindow': True}))
        entries.append(GetFromClass(ListGroup, {'GetSubContent': self.LoadMaterialGroups,
         'label': localization.GetByLabel('UI/Industry/RequiredInputMaterials'),
         'groupItems': self.job.GetMaterialsByGroups(),
         'id': 'materialGroups',
         'showicon': 'hide',
         'noItemText': localization.GetByLabel('UI/Common/None'),
         'state': 'locked',
         'BlockOpenWindow': True}))
        self.scroll.Load(contentList=entries)

    def UpdateOmegaEntry(self, activityID):
        if self.bpData.activities[activityID].IsOmegaActivity() and not sm.GetService('cloneGradeSvc').IsOmega():
            self.omegaEntry.Show()
        else:
            self.omegaEntry.Hide()

    def GetOutcomeCaption(self):
        if len(self.job.products) > 1:
            if self.job.activityID == industry.INVENTION:
                return localization.GetByLabel('UI/Industry/OutcomeOptions')
        return localization.GetByLabel('UI/Industry/Outcome')

    def LoadOutcome(self, nodedata, *args):
        scrolllist = []
        if self.job.activityID in (industry.MANUFACTURING, industry.REACTION):
            for product in nodedata.groupItems:
                scrolllist.append(GetFromClass(Item, {'itemID': None,
                 'typeID': product.typeID,
                 'label': product.GetHint(),
                 'getIcon': 1}))

        elif self.job.activityID == industry.RESEARCH_MATERIAL:
            label = localization.GetByLabel('UI/Industry/StepMaterialEfficiency', stepSize=industry.STEP_MATERIAL_EFFICIENCY)
            scrolllist.append(GetFromClass(Generic, {'label': label,
             'sublevel': 1}))
        elif self.job.activityID == industry.RESEARCH_TIME:
            label = localization.GetByLabel('UI/Industry/StepTimeEfficiency', stepSize=industry.STEP_TIME_EFFICIENCY)
            scrolllist.append(GetFromClass(Generic, {'label': label,
             'sublevel': 1}))
        elif self.job.activityID == industry.COPYING:
            typeID = self.bpData.blueprintTypeID
            label = evetypes.GetName(typeID)
            entry = GetFromClass(Item, {'itemID': None,
             'typeID': typeID,
             'label': label,
             'getIcon': 1,
             'isCopy': True})
            scrolllist.append(entry)
        elif self.job.activityID == industry.INVENTION:
            for product in nodedata.groupItems:
                entry = GetFromClass(Item, {'itemID': None,
                 'typeID': product.typeID,
                 'label': product.GetName(),
                 'getIcon': 1,
                 'isCopy': True})
                scrolllist.append(entry)

        return scrolllist

    def LoadSkills(self, nodedata, *args):
        scrolllist = []
        infoSvc = sm.GetService('info')
        skills = []
        for typeID, level, hint in nodedata.groupItems:
            skills.append((typeID, level))

        if skills:
            skills = sorted(skills)
            skillScrollList = infoSvc.GetReqSkillInfo(None, skills)
            scrolllist += skillScrollList
        return scrolllist

    def LoadMaterialGroups(self, nodeData, *args):
        scrollList = []
        for industryGroupID, materials in nodeData.groupItems:
            label = industryUIConst.LABEL_BY_INDUSTRYGROUP.get(industryGroupID, None)
            scrollList.append(GetFromClass(ListGroup, {'GetSubContent': self.LoadMaterialGroup,
             'label': localization.GetByLabel(label),
             'groupItems': [ (material.typeID, material.quantity, material.GetHint()) for material in materials ],
             'id': 'materials_%s' % industryGroupID,
             'sublevel': 1,
             'iconID': industryUIConst.ICON_BY_INDUSTRYGROUP[industryGroupID],
             'hint': localization.GetByLabel(industryUIConst.HINT_BY_INDUSTRYGROUP[industryGroupID]),
             'state': 'locked',
             'BlockOpenWindow': True}))

        if self.job.materials:
            scrollList.append(GetFromClass(ButtonEntry, {'label': '',
             'caption': localization.GetByLabel('UI/Market/MarketQuote/BuyAll'),
             'OnClick': self.BuyMultipleTypes}))
        if self.job.materials and eve.session.role & ROLE_GML == ROLE_GML:
            items = [ (material.typeID, material.quantity) for material in self.job.materials ]
            infoSvc = sm.GetService('info')
            scrollList.append(GetFromClass(ButtonEntry, {'label': 'GM: Give me these materials',
             'caption': 'Give',
             'OnClick': infoSvc.DoCreateMaterials,
             'args': (items, '', 10)}))
        return scrollList

    def LoadMaterialGroup(self, nodedata, *args):
        scrolllist = []
        for typeID, quantity, hint in nodedata.groupItems:
            entry = GetFromClass(Item, {'itemID': None,
             'typeID': typeID,
             'label': hint,
             'getIcon': 1,
             'sublevel': 2})
            scrolllist.append((typeID, entry))

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def BuyMultipleTypes(self, *args):
        buyDict = {material.typeID:material.quantity for material in self.job.materials}
        BuyMultipleTypesWithQty(buyDict)

    def OnSubscriptionChanged(self):
        self.Load()
