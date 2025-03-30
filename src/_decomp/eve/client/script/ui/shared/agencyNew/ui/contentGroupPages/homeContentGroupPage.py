#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentGroupPages\homeContentGroupPage.py
import os
import blue
from carbonui import uiconst
from carbonui.control.carousel import Carousel
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import NEW_FEATURE_CONTENT_GROUP_OFFSET
from eve.client.script.ui.shared.agencyNew.contentGroups.dynamicContentGroup import DynamicContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards import contentGroupCardConstants
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards.horizontalContentGroupCard import HorizontalContentGroupCard
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards.verticalContentGroupCard import VerticalContentGroupCard
from eve.client.script.ui.shared.agencyNew.ui.contentGroupPages.baseContentGroupPage import BaseContentGroupPage
from newFeatures.newFeatureNotify import GetAvailableNewFeatures
PAD_VALUE = 20
CARD1_WIDTH = contentGroupCardConstants.HORIZONTAL_CARD_WIDTH
CARD1_HEIGHT = 98
CARD2_WIDTH = 632
CARD2_HEIGHT = 132
CARD3_WIDTH = CARD2_WIDTH
CARD3_HEIGHT = 300
CARD4_WIDTH = 220
CARD4_HEIGHT = CARD3_HEIGHT
CARD5_WIDTH = CARD2_WIDTH - CARD4_WIDTH - PAD_VALUE
CARD5_HEIGHT = CARD3_HEIGHT
CARD6_WIDTH = CARD5_WIDTH
CARD6_HEIGHT = (CARD3_HEIGHT - PAD_VALUE) / 2

class HomeContentGroupPage(BaseContentGroupPage):
    default_name = 'HomeContentGroupPage'
    contentGroupID = contentGroupConst.contentGroupHome
    default_height = 460
    default_alignMode = uiconst.TOLEFT

    def ConstructLayout(self):
        self.leftContainer = Container(name='leftContainer', parent=self, align=uiconst.TOLEFT, width=CARD1_WIDTH)
        self.rightContainer = Container(name='rightContainer', parent=self, align=uiconst.TOLEFT, width=CARD2_WIDTH, padLeft=PAD_VALUE)
        self.topRightContainer = Container(name='topRightContainer', parent=self.rightContainer, align=uiconst.TOTOP, height=CARD3_HEIGHT)
        self.bottomRightContainer = Container(name='bottomRightContainer', parent=self.rightContainer, align=uiconst.TOTOP, height=CARD2_HEIGHT, padTop=PAD_VALUE)

    def ConstructContentGroupCards(self):
        for contentGroupID in (contentGroupConst.contentGroupMissions,
         contentGroupConst.contentGroupEncounters,
         contentGroupConst.contentGroupExploration,
         contentGroupConst.contentGroupResourceHarvesting):
            self._ConstructHomeContentGroupCard(HorizontalHomeContentGroupCard, contentGroupID, self.leftContainer)

        self._ConstructHomeContentGroupCard(VerticalHomeContentGroupCard, contentGroupConst.contentGroupHelp, self.bottomRightContainer, name='HelpSectionCard')
        self.carousel = Carousel(parent=self.topRightContainer, align=uiconst.TOTOP, height=CARD3_HEIGHT, interval=8, scrollSpeed=1.0)
        self.ConstructDynamicContentGroupCards()
        self._ConstructHomeContentGroupCard(VerticalHomeContentGroupCard, contentGroupConst.contentGroupHomefrontSites, self.carousel, name='HomefrontCarouselCard', align=uiconst.TOLEFT, padBottom=0, texturePath='res:/UI/Texture/Classes/Agency/navigationCards/carousel_homefront_operations.png')
        self._ConstructHomeContentGroupCard(VerticalHomeContentGroupCard, contentGroupConst.contentGroupMissionAgentsHeraldry, self.carousel, name='HeraldryCarouselCard', align=uiconst.TOLEFT, padBottom=0, texturePath='res:/UI/Texture/Classes/Agency/navigationCards/carousel_AgentsHeraldry.png')
        self._ConstructHomeContentGroupCard(VerticalHomeContentGroupCard, contentGroupConst.contentGroupCorp, self.carousel, name='CorpCarouselCard', align=uiconst.TOLEFT, padBottom=0)
        self.carousel.InitializeButtons()

    def _ConstructHomeContentGroupCard(self, cls, contentGroupID, parent, name = None, contentGroup = None, align = uiconst.TOTOP, padBottom = PAD_VALUE, texturePath = None):
        if not contentGroup:
            contentGroup = self.contentGroup.GetContentGroup(contentGroupID)
        cardContainer = cls(name=name if name else cls.default_name, parent=parent, contentGroup=contentGroup, contentGroupID=contentGroupID, align=align, padBottom=padBottom, texturePath=texturePath)
        self.cards.append(cardContainer)

    def ConstructDynamicContentGroupCards(self):
        featuresToHighlight = [ x for x in GetAvailableNewFeatures() if x.GetCallToActionMethod() and x.availableToAgency ]
        for feature in featuresToHighlight:
            contentGroupID = NEW_FEATURE_CONTENT_GROUP_OFFSET + feature.featureID

            def GetCallToActionCmd(f):
                if f.GetCallToActionMethod():
                    return f.ExecuteCallToAction

            texturePath = feature.GetAgencyTexturePath()
            dynamicGroup = DynamicContentGroup(contentGroupID, groupName=feature.GetName(), groupDesc=feature.GetDescription(), texturePath=texturePath, callback=GetCallToActionCmd(feature), opensInAgency=feature.CallToActionOpensInAgency())
            self._ConstructHomeContentGroupCard(VerticalHomeContentGroupCard, contentGroupID, self.carousel, contentGroup=dynamicGroup, align=uiconst.TOLEFT, padBottom=0)


class HorizontalHomeContentGroupCard(HorizontalContentGroupCard):
    default_name = 'HorizontalHomeContentGroupCard'
    default_width = CARD1_WIDTH
    default_height = CARD1_HEIGHT
    descriptionWidth = 170

    def ConstructDescriptionCont(self):
        super(HorizontalHomeContentGroupCard, self).ConstructDescriptionCont()
        self.descriptionCont.opacity = 0.0
        self.descriptionBG.opacity = 0.0

    def OnMouseEnter(self, *args):
        super(HorizontalHomeContentGroupCard, self).OnMouseEnter(*args)
        animations.FadeTo(self.descriptionCont, self.descriptionCont.opacity, 1.0, duration=0.3)
        animations.FadeTo(self.descriptionBG, self.descriptionBG.opacity, 0.5, duration=0.3)

    def OnMouseExit(self, *args):
        super(HorizontalHomeContentGroupCard, self).OnMouseExit(*args)
        animations.FadeTo(self.descriptionCont, self.descriptionCont.opacity, 0.0, duration=0.2)
        animations.FadeTo(self.descriptionBG, self.descriptionBG.opacity, 0.0, duration=0.2)


class VerticalHomeContentGroupCard(VerticalContentGroupCard):
    default_name = 'VerticalHomeContentGroupCard'
    default_width = CARD2_WIDTH
    default_height = CARD2_HEIGHT
    descriptionHeight = 60

    def ConstructDescriptionCont(self):
        super(VerticalHomeContentGroupCard, self).ConstructDescriptionCont()
        self.descriptionCont.opacity = 0.0
        self.descriptionBG.opacity = 0.0

    def OnMouseEnter(self, *args):
        super(VerticalHomeContentGroupCard, self).OnMouseEnter(*args)
        animations.FadeTo(self.descriptionCont, self.descriptionCont.opacity, 1.0, duration=0.3)
        animations.FadeTo(self.descriptionBG, self.descriptionBG.opacity, 0.5, duration=0.3)

    def OnMouseExit(self, *args):
        super(VerticalHomeContentGroupCard, self).OnMouseExit(*args)
        animations.FadeTo(self.descriptionCont, self.descriptionCont.opacity, 0.0, duration=0.2)
        animations.FadeTo(self.descriptionBG, self.descriptionBG.opacity, 0.0, duration=0.2)


class ContentGroupCard3(VerticalHomeContentGroupCard):
    default_width = CARD3_WIDTH
    default_height = CARD3_HEIGHT
    bgScalingCenter = (0.5, 0.2)


class ContentGroupCard4(VerticalHomeContentGroupCard):
    default_width = CARD4_WIDTH
    default_height = CARD4_HEIGHT
    bgScalingCenter = (0.5, 0.5)


class ContentGroupCard5(VerticalHomeContentGroupCard):
    default_width = CARD5_WIDTH
    default_height = CARD5_HEIGHT
    bgScalingCenter = (0.5, 0.2)


class ContentGroupCard6(HorizontalHomeContentGroupCard):
    default_width = CARD6_WIDTH
    default_height = CARD6_HEIGHT
    bgScalingCenter = (0.5, 0.2)
