#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\activities\activityListCont.py
import uthread2
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import StreamingVideoSprite
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from carbonui.window.underlay import WindowUnderlay
from eve.client.script.ui.shared.activities.activitiesUIConst import ACTIVITY_COUNT_LAYER_COLOR, ACTIVITY_ENTRY_HEIGHT, BANNER_SPRITE_HEIGHT, BANNER_SPRITE_WIDTH, LABEL_ACTIVITY_COUNT, SCROLL_ELEMENT_BOTTOM_PADDING, SCROLL_ELEMENT_LEFT_PADDING, SCROLL_ELEMENT_RIGHT_PADDING, SCROLL_HEIGHT, SCROLL_LAYER_COLOR, SCROLL_PADDING_HEIGHT, SCROLL_SECTION_HEADER_HEIGHT, SCROLL_SECTION_HEIGHT, SCROLL_SECTION_REST_HEIGHT, SCROLL_SECTION_RIGHT_PADDING, SCROLL_SECTION_WIDTH
from eve.client.script.ui.shared.activities.activityEntry import ActivityEntry
from eve.client.script.ui.structure import ChangeSignalConnect
from carbonui.control.button import Button
from eveui import Sprite
import localization

class ActivityCountHeaderCont(Container):
    default_name = 'HeaderCont'
    default_bgColor = (0.5, 0.5, 0.5, 0.3)
    default_height = SCROLL_SECTION_HEADER_HEIGHT

    def ApplyAttributes(self, attributes):
        super(ActivityCountHeaderCont, self).ApplyAttributes(attributes)
        text = attributes.text
        self.label = EveLabelLarge(parent=self, align=uiconst.CENTER, text=text)

    def SetText(self, text):
        self.label.SetText(text)


class ActivityListCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.service = sm.GetService('activities')
        self.ConstructBanner()
        self.ConstructBackground()
        self.ConstructScrollSection()
        self.ChangeSignalConnection(connect=True)
        self.LoadActivities()

    def ConstructBanner(self):
        self.bannerSprite = Sprite(name='bannerSprite', parent=self, align=uiconst.CENTERLEFT, width=BANNER_SPRITE_WIDTH, height=BANNER_SPRITE_HEIGHT, textureSecondaryPath='res:/UI/Texture/classes/newFeatureNotify/mask_Window.png')
        self.bannerVideoSprite = StreamingVideoSprite(name='bannerVideoSprite', parent=self, align=uiconst.CENTERLEFT, width=BANNER_SPRITE_WIDTH, height=BANNER_SPRITE_HEIGHT, textureSecondaryPath='res:/UI/Texture/classes/newFeatureNotify/mask_Window.png')
        self.ConstructButtons(BANNER_SPRITE_WIDTH, BANNER_SPRITE_HEIGHT)
        self.bannerSpriteColor = self.bannerSprite.GetRGBA()

    def ConstructScrollSection(self):
        self.scrollSection = Container(name='scrollSection', parent=self, state=uiconst.UI_NORMAL, align=uiconst.CENTERRIGHT, width=SCROLL_SECTION_WIDTH, height=SCROLL_SECTION_HEIGHT, left=SCROLL_SECTION_RIGHT_PADDING, idx=0)
        count = localization.formatters.FormatNumeric(self.service.GetActivityCount())
        self.headerCont = ActivityCountHeaderCont(parent=self.scrollSection, align=uiconst.TOTOP, bgColor=ACTIVITY_COUNT_LAYER_COLOR, text=localization.GetByLabel(LABEL_ACTIVITY_COUNT, count=count))
        self.bottomSection = Container(name='bottomSection', parent=self.scrollSection, align=uiconst.TOBOTTOM, height=SCROLL_SECTION_REST_HEIGHT, bgColor=SCROLL_LAYER_COLOR)
        self.scrollCont = Container(name='scrollCont', parent=self.bottomSection, padTop=SCROLL_PADDING_HEIGHT, align=uiconst.TOTOP, height=SCROLL_HEIGHT)
        self.contentScroll = ScrollContainer(parent=self.scrollCont)

    def ConstructBackground(self):
        self.underlay = WindowUnderlay(parent=self)
        self.underlay.SetState(uiconst.UI_DISABLED)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.service.OnActivitySelected, self.ActivitySelected)]
        ChangeSignalConnect(signalAndCallback, connect)

    def ConstructButtons(self, mainSpriteWidth, mainSpriteHeight):
        callToActionButton = Button(name='callToActionButton', parent=self, align=uiconst.CENTERLEFT, func=self.OnBannerClicked, opacity=0, idx=0)
        callToActionButton.width = mainSpriteWidth
        callToActionButton.height = mainSpriteHeight

    def OnBannerClicked(self, *args):
        self.service.OnBannerClicked()

    def ShowFirst(self):
        self.service.SelectActivity()

    def ActivitySelected(self, activity):
        self._UpdateCardSelectedState(activity)
        self.ShowBanner(activity)

    def ShowBanner(self, activity):
        uthread2.start_tasklet(self._OnShow, activity)

    def _OnShow(self, activity):
        self._UpdateSpriteAndVideoSprite(activity)

    def _UpdateSpriteAndVideoSprite(self, activity):
        if activity.IsVideo():
            self.bannerVideoSprite.SetVideoPath(activity.GetTexturePath(), videoLoop=True)
        else:
            self.bannerSprite.texturePath = activity.GetTexturePath()
        self.bannerSprite.display = not activity.IsVideo()
        self.bannerVideoSprite.display = activity.IsVideo()

    def _UpdateCardSelectedState(self, activity):
        for entry in self.activityEntrys:
            if entry.GetActivity() == activity:
                entry.Select()
            else:
                entry.Deselect()

    def LoadActivities(self, **args):
        datas = self.service.GetActivities()
        if not datas:
            return
        self.activityEntrys = [ ActivityEntry(parent=self.contentScroll, data=element, padLeft=SCROLL_ELEMENT_LEFT_PADDING, padRight=SCROLL_ELEMENT_RIGHT_PADDING, padBottom=SCROLL_ELEMENT_BOTTOM_PADDING, align=uiconst.TOTOP, opacity=1.0, height=ACTIVITY_ENTRY_HEIGHT) for element in datas ]

    def Close(self):
        self.ChangeSignalConnection(connect=False)
        Container.Close(self)
