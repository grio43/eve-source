#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overviewSettings\overviewBracketLabelPreview.py
import evetypes
from carbonui import const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label
from carbonui.fontconst import EVE_SMALL_FONTSIZE
from eve.client.script.ui.inflight.bracketsAndTargets.bracketNameFormatting import TagWithUnderLine, TagWithBold, TagWithColor, TagWithSize, TagWithItalic
from eve.client.script.ui.inflight.overview.overviewConst import LABEL_TYPE_SHIP_TYPE, LABEL_TYPE_PILOT, LABEL_TYPE_CORP, LABEL_TYPE_ALLIANCE, LABEL_TYPE_SHIP_NAME, LABEL_STATE, LABEL_TYPE, PRE, POST, LABEL_UNDERLINE, LABEL_BOLD, LABEL_TYPE_NONE, LABEL_COLOR, LABEL_SIZE, LABEL_TYPE_LINEBREAK, CHAR_BR, LABEL_ITALIC
from eve.common.script.sys.idCheckers import IsNPC
from carbonui.uicore import uicore
from localization import GetByLabel

class OverviewBracketLabelPreview(ContainerAutoSize):
    __notifyevents__ = ['OnShipLabelsUpdated', 'OnOverviewLabelOrderChanged', 'OnReloadingOverviewProfile']
    default_name = 'overviewBracketLabelPreview'
    default_align = uiconst.TOBOTTOM
    default_height = 50
    default_alignMode = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.lineBreakFunc = attributes.lineBreakFunc
        text = GetByLabel('UI/Overview/AddLinebreak')
        btn = Button(parent=self, label=text, func=self.lineBreakFunc, align=uiconst.CENTERTOP)
        textTop = btn.height + 10
        text = GetByLabel('UI/Overview/LabelPreview')
        EveLabelMedium(parent=self, text=text, align=uiconst.TOTOP, padding=(10,
         textTop,
         10,
         2))
        textCont = ContainerAutoSize(name='textCont', parent=self, align=uiconst.TOTOP, padding=(10, 2, 10, 10), alignMode=uiconst.TOTOP, maxHeight=100, clipChildren=True)
        Frame(bgParent=textCont, opacity=0.1)
        self.exampleText = Label(parent=textCont, align=uiconst.TOTOP, padding=4, fontsize=EVE_SMALL_FONTSIZE)
        self.LoadText()
        sm.RegisterNotify(self)

    def LoadText(self):
        shipLabels = sm.GetService('stateSvc').GetShipLabels()
        exampleTextDict = self.GetExampleLabels()
        textList = []
        for label in shipLabels:
            labelType = label[LABEL_TYPE]
            isVisible = label[LABEL_STATE]
            if not isVisible and labelType != LABEL_TYPE_LINEBREAK:
                continue
            pre = label[PRE]
            post = label[POST]
            if labelType is LABEL_TYPE_NONE:
                textList.append(pre)
                continue
            elif labelType == LABEL_TYPE_LINEBREAK:
                if not textList or textList[-1] != CHAR_BR:
                    textList.append(CHAR_BR)
                continue
            if labelType == LABEL_TYPE_CORP:
                labelText = exampleTextDict[LABEL_TYPE_CORP]
            elif labelType == LABEL_TYPE_ALLIANCE:
                labelText = exampleTextDict[LABEL_TYPE_ALLIANCE]
            elif labelType == LABEL_TYPE_PILOT:
                labelText = exampleTextDict[LABEL_TYPE_PILOT]
            elif labelType == LABEL_TYPE_SHIP_TYPE:
                labelText = exampleTextDict[LABEL_TYPE_SHIP_TYPE]
            elif labelType == LABEL_TYPE_SHIP_NAME:
                labelText = exampleTextDict[LABEL_TYPE_SHIP_NAME]
            else:
                continue
            labelsForType = [labelText]
            isBold = label.get(LABEL_BOLD, False)
            isUnderlined = label.get(LABEL_UNDERLINE, False)
            isItalic = label.get(LABEL_ITALIC, False)
            labelsForType = TagWithBold(labelsForType, isBold)
            labelsForType = TagWithUnderLine(labelsForType, isUnderlined)
            labelsForType = TagWithItalic(labelsForType, isItalic)
            labelsForType.insert(0, pre)
            labelsForType.append(post)
            color = label.get(LABEL_COLOR, None)
            fontsize = label.get(LABEL_SIZE)
            labelsForType = TagWithColor(labelsForType, color)
            labelsForType = TagWithSize(labelsForType, fontsize)
            textList += labelsForType

        text = ''.join(textList)
        self.exampleText.text = text

    def GetExampleLabels(self):
        try:
            shipTypeName = evetypes.GetName(uicore.layer.shipui.controller.GetTypeID())
        except StandardError:
            shipTypeName = GetByLabel('UI/Overview/ShipTypeExample')

        try:
            shipName = cfg.evelocations.Get(session.shipid).name
        except StandardError:
            shipName = GetByLabel('UI/Overview/ShipNameExample')

        corpTicker = GetByLabel('UI/Overview/CorpTickerExample')
        try:
            if not IsNPC(session.corpid):
                corpTicker = cfg.corptickernames.Get(session.corpid).tickerName
        except StandardError:
            pass

        allianceTicker = GetByLabel('UI/Overview/AllianceTickerExample')
        try:
            if session.allianceid:
                allianceTicker = cfg.allianceshortnames.Get(session.allianceid).shortName
        except StandardError:
            pass

        example = {LABEL_TYPE_SHIP_TYPE: shipTypeName,
         LABEL_TYPE_PILOT: cfg.eveowners.Get(session.charid).name,
         LABEL_TYPE_CORP: corpTicker,
         LABEL_TYPE_ALLIANCE: allianceTicker,
         LABEL_TYPE_SHIP_NAME: shipName}
        return example

    def OnShipLabelsUpdated(self):
        self.LoadText()

    def OnOverviewLabelOrderChanged(self):
        self.LoadText()

    def OnReloadingOverviewProfile(self):
        self.LoadText()
