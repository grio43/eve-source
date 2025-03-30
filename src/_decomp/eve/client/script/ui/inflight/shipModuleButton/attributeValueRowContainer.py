#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipModuleButton\attributeValueRowContainer.py
import dogma.data as dogma_data
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelSmall
import carbonui.const as uiconst
from eve.client.script.ui.shared.info.infoUtil import GetAttributeTooltipTitleAndDescription, GetColoredText, PrepareInfoTextForAttributeHint
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
import mathext

class AttributeValueRowContainer(Container):
    default_iconSize = 24
    default_align = uiconst.TOTOP
    default_height = 30

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.iconSize = attributes.get('iconSize', self.default_iconSize)
        self.attributeValues = attributes.attributeValues
        self.doWidthAdjustments = attributes.get('doWidthAdjustments', False)
        loadOnStartup = attributes.get('loadOnStartup', True)
        self.hasAdjustedWidth = False
        self.innerContainers = {}
        if loadOnStartup:
            self.Load(self.attributeValues)

    def Load(self, attributeValues, mouseExitFunc = None, onClickFunc = None, modifiedAttributesDict = {}, itemID = None):
        if not attributeValues:
            return
        self.attributeValues = attributeValues
        self.innerContainers = {}
        self.Flush()
        numDecimals = self.FindNumberOfDecimals({x[1] for x in attributeValues})
        containerPercentage = 1.0 / len(attributeValues)
        for attributeID, value in attributeValues:
            innerCont = Container(parent=self, name='container_%s' % attributeID, width=containerPercentage, align=uiconst.TOLEFT_PROP, clipChildren=True)
            self.innerContainers[attributeID] = innerCont
            iconCont = Container(parent=innerCont, name='iconCont', width=self.iconSize, align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN)
            icon = Icon(parent=iconCont, pos=(0,
             0,
             self.iconSize,
             self.iconSize), align=uiconst.CENTERLEFT, idx=0, ignoreSize=True, state=uiconst.UI_NORMAL)
            if mouseExitFunc:
                icon.OnMouseExit = mouseExitFunc
            if onClickFunc:
                icon.OnClick = (onClickFunc, attributeID)
            labelText = value or '-'
            modifiedAttributeInfo = modifiedAttributesDict.get(attributeID)
            if not isinstance(labelText, basestring):
                labelText = FmtAmt(labelText, showFraction=numDecimals)
            if modifiedAttributeInfo:
                labelText = GetColoredText(modifiedAttributeInfo, labelText)
            innerCont.label = EveLabelSmall(parent=innerCont, text=labelText, align=uiconst.CENTERLEFT, left=self.iconSize)
            PrepareInfoTextForAttributeHint(innerCont.label, modifiedAttributeInfo, itemID)
            attributeInfo = dogma_data.get_attribute(attributeID)
            iconID = attributeInfo.iconID
            icon.LoadIcon(iconID, ignoreSize=True)
            icon.hint = dogma_data.get_attribute_display_name(attributeID)
            tooltipTitleText, tooltipDescriptionText = GetAttributeTooltipTitleAndDescription(attributeID)
            if tooltipDescriptionText:
                SetTooltipHeaderAndDescription(targetObject=icon, headerText=tooltipTitleText, descriptionText=tooltipDescriptionText)

        self._AdjustSizes()

    def FindNumberOfDecimals(self, values):
        numDecimals = None
        for each in values:
            if isinstance(each, (float, int)):
                parts = unicode(each).split('.', 1)
                if len(parts) > 1:
                    numDecimals = mathext.clamp(max(numDecimals, len(parts[1])), 0, 5)

        return numDecimals

    def _OnResize(self, *args):
        self._AdjustSizes()

    def _AdjustSizes(self):
        if not self.attributeValues or not self.doWidthAdjustments:
            return
        emptyAttributes = [ attributeID for attributeID, value in self.attributeValues if value is None ]
        nonEmptyAttributes = [ attributeID for attributeID, value in self.attributeValues if value is not None ]
        if not emptyAttributes or not nonEmptyAttributes:
            return
        absWidth = self.absoluteRight - self.absoluteLeft
        containerPercentage = 1.0 / len(self.attributeValues)
        defaultGivenWidth = containerPercentage * absWidth
        extraNeeded = 0
        for attributeID in nonEmptyAttributes:
            cont = self.innerContainers.get(attributeID)
            extraNeeded = max(extraNeeded, cont.label.textwidth + cont.label.left - defaultGivenWidth)

        if not extraNeeded and not self.hasAdjustedWidth:
            return
        percentageNeeded = extraNeeded / float(absWidth)
        noneEmptyWidth = containerPercentage + percentageNeeded
        emptyWidth = (1.0 - noneEmptyWidth * len(nonEmptyAttributes)) / len(emptyAttributes)
        self.SetContWidth(nonEmptyAttributes, noneEmptyWidth)
        self.SetContWidth(emptyAttributes, emptyWidth)
        if extraNeeded:
            self.hasAdjustedWidth = True
        else:
            self.hasAdjustedWidth = False

    def SetContWidth(self, attributeIDs, newValue):
        for attributeID in attributeIDs:
            cont = self.innerContainers.get(attributeID, None)
            if not cont:
                continue
            cont.width = newValue
