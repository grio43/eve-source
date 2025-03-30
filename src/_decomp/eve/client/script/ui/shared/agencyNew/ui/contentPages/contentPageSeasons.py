#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageSeasons.py
import math
import mathext
import trinity
from carbonui import fontconst, TextColor, uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.moreIcon import DescriptionIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelMediumBold, Label, EveCaptionLarge
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupSeasons
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.agencyUIConst import OPACITY_DESCRIPTION_LABEL
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards import contentGroupCardConstants
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards.contentGroupCardConstants import CLIPPING_PARENT_HEIGHT, EDGE_GRADIENT_HEIGHT, EDGE_GRADIENT_WIDTH, MAX_VISIBLE_VERTICAL_CARDS, VERTICAL_CARD_BOTTOM_CONTAINER_HEIGHT, VERTICAL_CARD_WIDTH
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards.verticalContentGroupCard import HEADER_CONT_TOP
from eve.client.script.ui.shared.agencyNew.ui.contentGroupPages.contentScroller import ContentScroller
from carbonui.control.section import Section
from eve.client.script.ui.shared.agencyNew import agencySignals
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.ui.contentPages.baseContentPage import BaseContentPage
from eve.client.script.ui.control.simpleTextTooltip import SimpleTextTooltip
from eveexceptions import ExceptionEater
from localization import GetByLabel, GetByMessageID
from seasons.client.challengeEntry import ChallengeEntry, ENTRY_WIDTH
from seasons.client.seasonprogressbar import RewardsBar
from seasons.client.uiutils import CHALLENGE_BACKGROUND_COLOR_ACTIVE
import logging
import uthread2
stdlog = logging.getLogger(__name__)
CURRENT_EVENT_BACKGROUND_COLOR = (0, 0, 0)
CURRENT_EVENT_REWARDS_BACKGROUND_OPACITY = 0.5
ICON_BACKGROUND_COLOR = (0.05, 0.05, 0.05, 0.9)
COMPLETED_CHALLENGE_FADE_OUT_DURATION = 1.0
PROGRESS_BAR_HEIGHT = 114
CHALLENGES_HEIGHT = 378
PADDING_PROGRESS_BAR_TO_CHALLENGES = 10
MAIN_CONTAINER_HEIGHT = PROGRESS_BAR_HEIGHT + CHALLENGES_HEIGHT + PADDING_PROGRESS_BAR_TO_CHALLENGES
MAX_VISIBLE_CARDS = 8
CUSTOM_THIN_CARD_WIDTH = 125
CUSTOM_THIN_CARD_HEIGHT = 333

class ContentPageSeasons(BaseContentPage):
    default_name = 'ContentPageSeasons'
    default_align = uiconst.TOTOP
    default_padTop = 14

    def __init__(self, *args, **kwargs):
        super(ContentPageSeasons, self).__init__(*args, **kwargs)
        self.ConstructSeasonPanel()

    def SelectFirstCard(self):
        pass

    def ShouldConstructLeftContainer(self):
        return False

    def OnCardSelected(self, selectedCard):
        super(ContentPageSeasons, self).OnCardSelected(selectedCard)
        agencySignals.on_content_group_selected(contentGroupConst.contentGroupSeasons, itemID=selectedCard.contentPiece.solarSystemID)

    def ConstructSeasonPanel(self):
        if sm.GetService('seasonService').is_selection_needed():
            SeasonSelectionContent(parent=self, height=500, align=uiconst.TOTOP, top=10)
        else:
            SeasonContent(parent=self, height=500, align=uiconst.TOTOP)


class SeasonSelectionContent(Container):
    default_name = 'SeasonSelectionContent'
    default_align = uiconst.CENTER
    default_alignMode = uiconst.CENTERTOP
    mainContHeight = CLIPPING_PARENT_HEIGHT
    extraSlotWidth = 130
    default_minWidth = 400
    default_minHeight = 400
    clippingParentTop = 27

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.cards = []
        self.contentScroller = None
        self.ConstructLayout()
        self.ConstructSeasonCards()
        self.AnimateAllCards()

    def AnimateAllCards(self):
        for i, child in enumerate(self.cards):
            child.AnimEnter(self.GetOffsetValue(i))

    def ConstructSeasonCards(self):
        seasonSelection = sm.GetService('seasonService').get_season_selection()
        numAvailableSeasons = len(seasonSelection)
        self.mainCont.columns = numAvailableSeasons
        for index, season in enumerate(seasonSelection):
            cardContainer = CustomGroupCardContainer(parent=self.mainCont, index=index, season=season)
            self.cards.append(cardContainer)

        if numAvailableSeasons > MAX_VISIBLE_CARDS:
            self.AdjustForScrolling(numAvailableSeasons)

    def ConstructLayout(self):
        self.ConstructMainContainer()

    def ConstructMainContainer(self):
        padding = 16
        self.clippingParent = ContainerAutoSize(name='clippingParent', parent=self, align=uiconst.CENTERTOP, height=self.mainContHeight, maxWidth=MAX_VISIBLE_CARDS * (CUSTOM_THIN_CARD_WIDTH + padding), clipChildren=True)
        self.mainCont = LayoutGrid(parent=self.clippingParent, align=uiconst.TOLEFT, cellSpacing=(0, 50), cellPadding=(padding / 2, 20), top=self.clippingParentTop)
        self.scrollIndicator = Fill(parent=self, frameConst=uiconst.FRAME_BORDER1_CORNER9, pos=(0, 40, 0, 6), align=uiconst.BOTTOMLEFT, opacity=0.05)
        self.scrollIndicator.baseOpacity = 0.05
        self.scrollIndicator.display = False
        self.ConstructSelctionHeader(padding)

    def ConstructSelctionHeader(self, padding):
        selectionDescriptionContainer = Container(name='selectionDescriptionContainer', parent=self, maxWidth=MAX_VISIBLE_CARDS * (CUSTOM_THIN_CARD_WIDTH + padding), align=uiconst.CENTERTOP, state=uiconst.UI_PICKCHILDREN, height=30, width=MAX_VISIBLE_CARDS * (CUSTOM_THIN_CARD_WIDTH + padding) - 14)
        eventInformationCont = ContainerAutoSize(parent=selectionDescriptionContainer, align=uiconst.CENTERLEFT)
        DescriptionIcon(parent=eventInformationCont, align=uiconst.CENTERLEFT, tooltipPanelClassInfo=SimpleTextTooltip(text=sm.GetService('seasonService').get_navigation_tooltip()))
        EveLabelMedium(parent=eventInformationCont, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, text=GetByLabel('UI/Seasons/MultipleSeasonsTexts/eventInfoLabel'), padLeft=36)
        EveCaptionLarge(parent=selectionDescriptionContainer, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, text=sm.GetService('seasonService').get_season_selection_large_title())

    def GetOffsetValue(self, idx):
        numChildren = len(self.cards)
        return math.fabs((numChildren - 1) / 2.0 - idx)

    def AdjustForScrolling(self, numAvailableChildren):
        padding = 23
        numFullCards = MAX_VISIBLE_VERTICAL_CARDS - 1
        self.clippingParent.maxWidth = numFullCards * (VERTICAL_CARD_WIDTH + padding) + self.extraSlotWidth
        self.clippingParent.alignMode = uiconst.CENTERLEFT
        self.clippingParent.minHeight = EDGE_GRADIENT_HEIGHT
        self.mainCont.cellPadding = (padding / 2, self.mainCont.cellPadding[1])
        self.mainCont.align = uiconst.CENTERLEFT
        self.mainCont.top = 10
        self.mainCont.state = uiconst.UI_NORMAL
        self.contentScroller = ContentScroller(contentGroupSeasons, self.mainCont, numAvailableCards=numAvailableChildren, numVisibleCards=numFullCards, slotSize=VERTICAL_CARD_WIDTH + padding, extraSlotWidth=self.extraSlotWidth, scrollIndicator=self.scrollIndicator)
        self.contentScroller.onUpdate.connect(self.UpdateFade)
        for each in [self.mainCont] + [ x.card for x in self.cards ]:
            each.OnMouseDown = (self.contentScroller.OnMouseDown, each)
            each.OnMouseUp = self.contentScroller.OnMouseUp
            each.OnMouseWheel = self.contentScroller.OnMouseWheel

        self.ConstructGradients()

    def ConstructGradients(self):
        if not getattr(self, 'leftFadeCont', None) or self.leftFadeCont.destroyed:
            self.leftFadeCont = Container(name='leftFadeCont', parent=self.clippingParent, align=uiconst.TOLEFT_NOPUSH, width=EDGE_GRADIENT_WIDTH, clipChildren=True, idx=0)
            self.leftFade = Sprite(name='scrollGradientLeft', parent=self.leftFadeCont, align=uiconst.CENTERLEFT, pos=(0,
             0,
             EDGE_GRADIENT_WIDTH,
             EDGE_GRADIENT_HEIGHT), rotation=mathext.pi, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/agency/scrollGradient3.png', idx=0, color=(0, 0, 0, 1))
            self.leftFade.display = False
        if not getattr(self, 'rightFadeCont', None) or self.rightFadeCont.destroyed:
            self.rightFadeCont = Container(name='rightFadeCont', parent=self.clippingParent, align=uiconst.TORIGHT_NOPUSH, width=EDGE_GRADIENT_WIDTH, clipChildren=True, idx=0)
            self.rightFade = Sprite(name='scrollGradientRight', parent=self.rightFadeCont, align=uiconst.CENTERRIGHT, pos=(0,
             0,
             EDGE_GRADIENT_WIDTH,
             EDGE_GRADIENT_HEIGHT), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/agency/scrollGradient3.png', idx=0, color=(0, 0, 0, 1))
            self.rightFade.display = False

    def UpdateFade(self, newLeft, firstIdx, lastIdx, cardWidth):
        animations.StopAnimation(self.mainCont, 'left')
        self.mainCont.left = newLeft
        currentLeftOffSet = self.clippingParent.absoluteLeft - self.mainCont.absoluteLeft
        correction = int(currentLeftOffSet + newLeft)
        showLeft = showRight = False
        for cardContainer in self.cards:
            if cardContainer.card.index == firstIdx:
                cardLeft = cardContainer.absoluteLeft
                fromEdge = self.clippingParent.absoluteLeft - cardLeft - correction
                showLeft = fromEdge > -10
                diff = cardWidth - fromEdge
                self.leftFadeCont.width = diff - 10 if diff < EDGE_GRADIENT_WIDTH else EDGE_GRADIENT_WIDTH
            if cardContainer.card.index == lastIdx:
                cardRight = cardContainer.absoluteRight
                fromEdge = cardRight - self.clippingParent.absoluteRight + correction
                diff = cardWidth - fromEdge
                self.rightFadeCont.width = diff - 10 if diff < EDGE_GRADIENT_WIDTH else EDGE_GRADIENT_WIDTH
                showRight = fromEdge > -10

        self.leftFade.display = showLeft
        self.rightFade.display = showRight

    def Close(self):
        with ExceptionEater('Killing SeasonContentScroller'):
            if self.contentScroller:
                self.contentScroller.onUpdate.disconnect(self.UpdateFade)
                self.contentScroller.Cleanup()
        ContainerAutoSize.Close(self)


class CustomGroupCardContainer(ContainerAutoSize):
    default_name = 'CustomGroupCardContainer'
    default_align = uiconst.CENTERTOP
    default_width = CUSTOM_THIN_CARD_WIDTH

    def ApplyAttributes(self, attributes):
        super(CustomGroupCardContainer, self).ApplyAttributes(attributes)
        self.season = attributes.season
        self.index = attributes.index
        self.ConstructLayout()

    def ConstructLayout(self):
        self.ConstructContentGroupCard()
        self.ConstructCustomGroupInfoContainer()
        self.ConstructDescriptionIcon()

    def ConstructCustomGroupInfoContainer(self):
        self.customGroupInfoContainer = Container(name='ConstructCustomGroupInfoContainer', parent=self, align=uiconst.TOTOP, height=VERTICAL_CARD_BOTTOM_CONTAINER_HEIGHT)

    def ConstructDescriptionIcon(self):
        self.descriptionIcon = DescriptionIcon(parent=self.customGroupInfoContainer, align=uiconst.CENTERLEFT, tooltipPanelClassInfo=SimpleTextTooltip(text=GetByMessageID(self.season.agency_card_hint)))

    def ConstructContentGroupCard(self):
        self.card = CustomContentGroupCard(parent=self, index=self.index, seasonID=self.season.season_id, texturePath=self.season.navigation_card_picture_path, cardTitleID=self.season.agency_card_title, agencyCardDescriptionID=self.season.agency_card_description)

    def AnimEnter(self, offsetValue):
        self.card.AnimEnter(offsetValue)
        self.descriptionIcon.AnimEnter(offsetValue)


class CustomContentGroupCard(Container):
    default_name = 'CustomContentGroupCard'
    default_state = uiconst.UI_NORMAL
    default_opacity = 0.0
    default_align = uiconst.TOTOP
    default_width = CUSTOM_THIN_CARD_WIDTH
    default_height = CUSTOM_THIN_CARD_HEIGHT
    descriptionHeight = contentGroupCardConstants.VERTICAL_CARD_FOOTER_CONTAINER_HEIGHT
    scaleDistance = 20
    bgScalingCenter = (0.0, 0.5)
    maskTexture = 'res:/UI/Texture/classes/Agency/navMask.png'
    baselineBackgroundScaleX = 1.0
    baselineBackgroundScaleY = 1.0

    def ApplyAttributes(self, attributes):
        super(CustomContentGroupCard, self).ApplyAttributes(attributes)
        self.seasonID = attributes.seasonID
        self.texturePath = attributes.texturePath
        self.cardTitleID = attributes.cardTitleID
        self.agencyCardDescriptionID = attributes.agencyCardDescriptionID
        self.titleFrame = None
        self.descriptionLabel = None
        self.index = attributes.index
        self.ConstructBaseLayout()

    def ConstructBaseLayout(self):
        self.contNoTransform = Container(name='contNoTransform', parent=self)
        self.transform = Transform(parent=self, align=uiconst.TOALL, scalingCenter=(0.5, 0.5))
        self.ConstructMainContainer()
        self.ConstructHeader()
        self.ConstructBackground()
        if self.agencyCardDescriptionID:
            self.ConstructDescriptionCont()

    def ConstructMainContainer(self):
        self.mainCont = Container(name='mainCont', parent=self.transform)

    def ConstructHeader(self):
        self.headerCont = Container(name='headerContainer', parent=self.contNoTransform, align=uiconst.TOTOP, height=55, top=HEADER_CONT_TOP)
        self.ConstructLabelCont(self.width)

    def ConstructDescriptionCont(self):
        self.descriptionCont = ContainerAutoSize(name='descriptionCont', parent=self.contNoTransform, align=uiconst.TOBOTTOM, minHeight=self.descriptionHeight, padding=(1, 1, 1, 1), state=uiconst.UI_DISABLED)
        self.descriptionLabel = EveLabelMedium(name='descriptionLabel', parent=self.descriptionCont, align=uiconst.CENTER, width=self.width - 30, text='<center>%s</center>' % GetByMessageID(self.agencyCardDescription), color=Color.WHITE, opacity=OPACITY_DESCRIPTION_LABEL, state=uiconst.UI_DISABLED, padding=(0, 4, 0, 16))
        self.descriptionCont.SetSizeAutomatically()
        self.descriptionBG = Frame(name='descriptionBackground', parent=self.mainCont, align=uiconst.TOBOTTOM, height=self.descriptionCont.height, padding=1, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, color=agencyUIConst.COLOR_BG_DARK, state=uiconst.UI_DISABLED)

    def ConstructBackground(self):
        self.bgContainer = Container(name='bgContainer', align=uiconst.TOALL, state=uiconst.UI_DISABLED, parent=self.transform)
        self.ConstructBackgroundTextured()

    def ConstructBackgroundTextured(self):
        StretchSpriteHorizontal(name='navButtonTopSprite', parent=self.bgContainer, texturePath='res:/UI/Texture/classes/Agency/navButtonTop.png', align=uiconst.TOTOP_NOPUSH, height=9, rightEdgeSize=10, leftEdgeSize=10, padding=(1, 1, 1, 1))
        self.strokeFrame = Frame(name='strokeFrame', parent=self.bgContainer, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Stroke.png', opacity=0.1, cornerSize=9)
        self.backgroundSprite = Frame(name='bgSprite', parent=self.bgContainer, align=uiconst.TOALL, opacity=0.9, textureSecondaryPath=self.texturePath, texturePath=self.maskTexture, spriteEffect=trinity.TR2_SFX_MODULATE, cornerSize=10)
        self.backgroundSprite.textureSecondary.scale = (self.baselineBackgroundScaleX, self.baselineBackgroundScaleY)
        self.backgroundSprite.textureSecondary.scalingCenter = self.bgScalingCenter
        self.backgroundSprite.textureSecondary.useTransform = True

    def AnimEnter(self, offsetValue):
        timeOffset = 0.05 * offsetValue
        duration = 0.3
        animations.Tr2DScaleTo(self.transform, (0.9, 0.9), (1.0, 1.0), duration=duration, timeOffset=timeOffset)
        animations.FadeIn(self, duration=2 * duration, timeOffset=timeOffset)

    def OnClick(self, *args):
        if eve.Message('seasonSelectionWarning', buttons=uiconst.YESNO) == uiconst.ID_YES:
            sm.GetService('seasonService').select_season(self.seasonID)

    def OnMouseEnter(self, *args):
        super(CustomContentGroupCard, self).OnMouseEnter(*args)
        animations.MorphScalar(self.headerCont, 'left', self.headerCont.left, -self.GetScaleOffsetX(), duration=0.1, curveType=uiconst.ANIM_LINEAR)
        if self.descriptionLabel:
            animations.FadeTo(self.descriptionLabel, self.descriptionLabel.opacity, 1.0, duration=0.1)
        animations.FadeTo(self.strokeFrame, self.strokeFrame.opacity, 0.2, duration=0.1)
        endVal = (self.baselineBackgroundScaleX * 0.9, self.baselineBackgroundScaleY * 0.9)
        animations.MorphVector2(self.backgroundSprite.textureSecondary, 'scale', self.backgroundSprite.textureSecondary.scale, endVal, duration=3.0, curveType=uiconst.ANIM_LINEAR)
        scale = self._GetScaleFactor()
        animations.Tr2DScaleTo(self.transform, self.transform.scale, (scale, scale), duration=0.1, curveType=uiconst.ANIM_LINEAR)

    def OnMouseExit(self, *args):
        super(CustomContentGroupCard, self).OnMouseExit(*args)
        newLeft = getattr(self.headerCont, 'originalLeft', 0)
        animations.MorphScalar(self.headerCont, 'left', self.headerCont.left, newLeft, duration=0.2, curveType=uiconst.ANIM_LINEAR)
        if self.descriptionLabel:
            animations.FadeTo(self.descriptionLabel, self.descriptionLabel.opacity, OPACITY_DESCRIPTION_LABEL, duration=0.1)
        animations.FadeTo(self.strokeFrame, self.strokeFrame.opacity, 0.1, duration=0.1)
        endVal = (self.baselineBackgroundScaleX * 1.0, self.baselineBackgroundScaleY * 1.0)
        animations.MorphVector2(self.backgroundSprite.textureSecondary, 'scale', self.backgroundSprite.textureSecondary.scale, endVal, duration=0.2, curveType=uiconst.ANIM_LINEAR)
        animations.Tr2DScaleTo(self.transform, self.transform.scale, (1.0, 1.0), duration=0.2, curveType=uiconst.ANIM_LINEAR)

    def _GetScaleFactor(self):
        x = self.width
        scale = (x + self.scaleDistance) / float(x)
        return scale

    def GetScaleOffsetX(self):
        return int(self.width * (self._GetScaleFactor() - 1.0) / 2.0)

    def GetScaleOffsetY(self):
        return int(self.height * (self._GetScaleFactor() - 1.0) / 2.0)

    def ConstructLabelCont(self, maxWidth = CUSTOM_THIN_CARD_WIDTH):
        labelCont = ContainerAutoSize(name='labelCont', parent=self.headerCont, align=uiconst.CENTERLEFT, top=-5, left=1, minHeight=50, alignMode=uiconst.TOPLEFT)
        self.titleFrame = Frame(name='topContFrame', bgParent=labelCont, texturePath='res:/UI/Texture/classes/Agency/navButtonTitleBar.png', cornerSize=26, color=eveColor.CRYO_BLUE)
        titleCont = ContainerAutoSize(name='titleCont', parent=labelCont, align=uiconst.TOPLEFT, top=22, padding=(15, 4, 10, 4))
        Label(parent=titleCont, align=uiconst.TOPLEFT, text=GetByMessageID(self.cardTitleID), fontsize=17, fontStyle=fontconst.STYLE_HEADER, color=TextColor.NORMAL, maxWidth=maxWidth - 40, padRight=15)


class SeasonContent(Container):
    contentType = agencyConst.CONTENTTYPE_AGENCY
    __notifyevents__ = ['OnChallengeProgressUpdateInClient',
     'OnChallengeCompletedInClient',
     'OnChallengeRewardsGrantedInClient',
     'OnChallengeExpiredInClient']

    def ApplyAttributes(self, attributes):
        super(SeasonContent, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.alphaChallenges = None
        self.challengeEntries = dict()
        self.seasonSvc = sm.GetService('seasonService')
        self.ConstructContent()

    def ConstructContent(self):
        mainContainer = Container(name='mainContainer', parent=self, align=uiconst.TOTOP, height=MAIN_CONTAINER_HEIGHT)
        self.progressBarContainer = Container(name='progressBarContainer', parent=mainContainer, align=uiconst.TOTOP, height=PROGRESS_BAR_HEIGHT)
        self.DrawRewardsBar()
        self.challengesCont = Container(name='challengesCont', parent=mainContainer, align=uiconst.TOTOP, height=CHALLENGES_HEIGHT, padding=(12,
         PADDING_PROGRESS_BAR_TO_CHALLENGES,
         12,
         4))
        self.LoadChallenges()
        self.DrawChallengesContainer()
        self.DrawChallengeCards()
        self.DrawSeasonInfo()

    def LoadChallenges(self):
        self.alphaChallenges = self.seasonSvc.get_active_challenges_by_character_id()

    def DrawRewardsBar(self):
        self.progressBar = RewardsBar(name='progressBar', parent=self.progressBarContainer, align=uiconst.TOTOP, height=self.progressBarContainer.height)

    def DrawChallengesContainer(self):
        self.lines = len(self.alphaChallenges)
        self.extraChallengeContainer = Section(parent=self.challengesCont, align=uiconst.TOLEFT, height=CHALLENGES_HEIGHT, width=735, headerText=GetByLabel('UI/Agency/Seasons/ChallengesSectionHeader', count=self.lines), textAlign=uiconst.CENTERLEFT, insidePadding=(10, 10, 10, 0))
        self.challengeScrollContainer = ScrollContainer(parent=self.extraChallengeContainer, align=uiconst.TOLEFT, height=self.extraChallengeContainer.height, width=self.extraChallengeContainer.width - 20)
        self.challengeGridContainer = Container(name='alphaChallengesGridCont', parent=self.challengeScrollContainer, align=uiconst.TOTOP, padLeft=2)

    def DrawChallengeCards(self):
        tempEntries = self.challengeEntries.copy()
        for challenge_id, challenge_entry in tempEntries.iteritems():
            if challenge_id not in self.alphaChallenges:
                challengeEntry = self.challengeEntries.pop(challenge_id, None)
                if challengeEntry:
                    challengeEntry.Close()

        for challenge in self.alphaChallenges.itervalues():
            if self.seasonSvc.challenge_is_dormant(challenge.challenge_id):
                continue
            if not self.challengeEntries.has_key(challenge.challenge_id) or self.seasonSvc.challenge_is_dormant(challenge.challenge_id):
                idx = self.alphaChallenges.keys().index(challenge.challenge_id)
                entry = ChallengeEntry(name='challengeentry_%s' % challenge.challenge_id, parent=self.challengeGridContainer, challenge=challenge, challengeWidth=ENTRY_WIDTH, padding=(0, 2, 12, 8), opacity=0.0, idx=idx, align=uiconst.TOTOP)
                self.challengeEntries[challenge.challenge_id] = entry
                self.challengeEntries[challenge.challenge_id].idx = idx
                Fill(bgParent=entry, color=CHALLENGE_BACKGROUND_COLOR_ACTIVE)

        self.AdjustHeight()

    def AdjustHeight(self):
        height = 0
        for challenge in self.alphaChallenges.itervalues():
            if self.seasonSvc.challenge_is_dormant(challenge.challenge_id):
                continue
            if self.challengeEntries.has_key(challenge.challenge_id):
                entry = self.challengeEntries[challenge.challenge_id]
                height += entry.GetHeight() + entry.padTop + entry.padBottom

        self.challengeGridContainer.height = height

    def OnChallengeProgressUpdateInClient(self, challenge_id, new_progress):
        try:
            self.challengeEntries[challenge_id].UpdateChallengeProgress(new_progress)
        except KeyError:
            stdlog.exception('Update challenge failed for challenge: %s, character: %s', challenge_id, session.charid)
            self._RefreshChallenges()

    def OnChallengeCompletedInClient(self, old_challenge_id):
        try:
            self.challengeEntries[old_challenge_id].CompleteChallenge()
        except (KeyError, AttributeError):
            stdlog.exception('Complete challenge failed for challenge: %s, character: %s', old_challenge_id, session.charid)
        finally:
            if old_challenge_id is None:
                return
            uthread2.start_tasklet(self._HideCompletedChallenge, old_challenge_id, COMPLETED_CHALLENGE_FADE_OUT_DURATION)

    def OnChallengeRewardsGrantedInClient(self, challenge_id):
        challengeEntry = self.challengeEntries[challenge_id]
        if hasattr(challengeEntry, 'progressBar'):
            challengeEntry.progressBar.update_challenge(challengeEntry.challenge.max_progress)
            challengeEntry.UpdateClaimButton()

    def OnChallengeExpiredInClient(self, old_challenge_id):
        uthread2.start_tasklet(self._HideCompletedChallenge, old_challenge_id, COMPLETED_CHALLENGE_FADE_OUT_DURATION, False)

    def _HideCompletedChallenge(self, challengeID, fadeOutTime, shouldDelay = False):
        challengeEntry = self.challengeEntries.get(challengeID, None)
        if challengeEntry:
            uicore.animations.FadeOut(challengeEntry, duration=COMPLETED_CHALLENGE_FADE_OUT_DURATION)
        if shouldDelay:
            uthread2.call_after_wallclocktime_delay(self._RefreshChallenges, fadeOutTime)
        else:
            uthread2.start_tasklet(self._RefreshChallenges)

    def _RefreshChallenges(self):
        self.LoadChallenges()
        self.DrawChallengeCards()

    def DrawSeasonInfo(self):
        self.contentContainer = Container(parent=self.challengesCont, align=uiconst.TOPRIGHT, width=400, height=420)
        self.imageContainer = Container(parent=self.contentContainer, align=uiconst.TOPRIGHT, height=200, width=326)
        Sprite(parent=self.imageContainer, align=uiconst.TOALL, texturePath=self.seasonSvc.get_content_card_picture_path())
        self.textContainer = Container(parent=self.contentContainer, align=uiconst.BOTTOMRIGHT, height=self.contentContainer.height - self.imageContainer.height, width=326, padTop=10, padBottom=45, headerText=self.seasonSvc.GetSeasonName())
        fromDateTime = self.seasonSvc.get_start_time()
        toDateTime = self.seasonSvc.get_end_time()
        EveLabelMediumBold(parent=self.textContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Seasons/EventDates', fromDate=fromDateTime, toDate=toDateTime))
        descriptionContainer = ScrollContainer(parent=self.textContainer, align=uiconst.TOALL)
        EveLabelMedium(parent=descriptionContainer, align=uiconst.TOTOP, padTop=10, text=self.seasonSvc.get_season_news())
