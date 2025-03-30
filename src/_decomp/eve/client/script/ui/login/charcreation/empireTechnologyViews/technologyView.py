#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireTechnologyViews\technologyView.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.login.charcreation.technologyViewUtils import TechExampleButton
TECH_EXAMPLE_BUTTON_HEIGHT = 50
TECH_EXAMPLE_BUTTON_SEPARATION = 8
TECH_EXAMPLE_BUTTON_PAD_LEFT = 25
TECH_EXAMPLE_BUTTON_PAD_BOT = 30
TECH_EXAMPLE_BUTTON_ICON_SIZE = 32
TECH_EXAMPLE_BUTTON_ICON_TO_TEXT = 16
TECH_EXAMPLE_BUTTON_INTERNAL_PADDING = 3

class TechnologyView(Container):

    def ApplyAttributes(self, attributes):
        self.AddInternalPadding(attributes)
        Container.ApplyAttributes(self, attributes)
        self.raceID = attributes.Get('raceID', None)
        self.technology = attributes.Get('technology', None)

    def AddInternalPadding(self, attributes):
        internalPadTop = attributes.Get('internalPadTop', 0)
        internalPadBottom = attributes.Get('internalPadBottom', 0)
        height = attributes.Get('height')
        attributes.Set('height', height - internalPadTop - internalPadBottom)
        padTop = attributes.Get('padTop', 0)
        attributes.Set('padTop', padTop + internalPadTop)
        padBottom = attributes.Get('padBottom', 0)
        attributes.Set('padBottom', padBottom + internalPadBottom)


class TechnologyViewWithCentralPic(TechnologyView):

    def ApplyAttributes(self, attributes):
        TechnologyView.ApplyAttributes(self, attributes)
        mainView = self.technology.GetMainView(self.raceID)
        if mainView:
            self.AddMainView(mainView)

    def AddMainView(self, mainView):
        self.centralViewContainer = Container(name='centralViewContainer', parent=self, align=uiconst.ANCH_TOPLEFT, width=self.width, height=self.height, state=uiconst.UI_DISABLED, opacity=0.0)
        centralViewWrapper = Container(name='centralViewWrapper', parent=self.centralViewContainer, align=uiconst.TOLEFT, width=self.centralViewContainer.width, height=self.centralViewContainer.height)
        Sprite(name='centralView', parent=centralViewWrapper, align=uiconst.TOTOP, width=centralViewWrapper.width, height=centralViewWrapper.height, texturePath=mainView, useSizeFromTexture=False)

    def ShowMainView(self):
        self.centralViewContainer.opacity = 1.0


class TechnologyViewWithExampleButtons(TechnologyView):

    def ApplyAttributes(self, attributes):
        TechnologyView.ApplyAttributes(self, attributes)
        self.techExampleOrder = attributes.Get('techExampleOrder', 1)
        self.techExampleButtons = {}
        self._AddTechExampleButtons()
        self.techExampleView = None
        self.SetTechExampleView(order=self.techExampleOrder)

    def _AddTechExampleButtons(self):
        numButtons = self.technology.GetNumberOfExamples()
        if numButtons < 1:
            return
        textWidth = self.technology.GetMaxTechExampleTitleWidth(self.raceID) + 2 * TECH_EXAMPLE_BUTTON_INTERNAL_PADDING
        totalWidth = TECH_EXAMPLE_BUTTON_PAD_LEFT + TECH_EXAMPLE_BUTTON_ICON_SIZE + 2 * TECH_EXAMPLE_BUTTON_ICON_TO_TEXT + textWidth
        padBottom = TECH_EXAMPLE_BUTTON_PAD_BOT
        totalHeight = self.height - padBottom
        self.techExamplesContainer = Container(name='techExamplesContainer', align=uiconst.TOALL, parent=self, state=uiconst.UI_PICKCHILDREN)
        techExampleButtonsContainer = Container(name='techExampleButtonsContainer', align=uiconst.TOLEFT, parent=self.techExamplesContainer, width=totalWidth, height=totalHeight, padLeft=TECH_EXAMPLE_BUTTON_PAD_LEFT)
        wrapperHeight = TECH_EXAMPLE_BUTTON_HEIGHT * numButtons + TECH_EXAMPLE_BUTTON_SEPARATION * (numButtons - 1)
        techExampleButtonsWrapper = Container(name='techExampleButtonsWrapper', align=uiconst.BOTTOMLEFT, parent=techExampleButtonsContainer, width=totalWidth, height=wrapperHeight)
        numButton = 1
        for order, techExample in self.technology.GetTechExamples():
            self.techExampleButtons[order] = TechExampleButton(parent=techExampleButtonsWrapper, name='techExampleButton%d' % order, align=uiconst.TOTOP, width=totalWidth, height=TECH_EXAMPLE_BUTTON_HEIGHT, state=uiconst.UI_NORMAL, order=order, raceID=self.raceID, techExample=techExample, techExampleSetter=self.SetTechExampleView, iconSize=TECH_EXAMPLE_BUTTON_ICON_SIZE, padIconToText=TECH_EXAMPLE_BUTTON_ICON_TO_TEXT)
            numButton += 1

    def _ActivateTechExampleButton(self, order):
        for buttonOrder, button in self.techExampleButtons.iteritems():
            if buttonOrder == order:
                button.SetActive()
            else:
                button.SetInactive()

    def SetTechExampleView(self, order):
        self._ActivateTechExampleButton(order)
        self.techExampleOrder = order
