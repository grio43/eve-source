#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\activities\window.py
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.color import Color
from carbonui.control.window import Window
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.line import Line
from eve.client.script.ui.shared.activities.activitiesUIConst import ACTIVITIES_ICON_PATH, ACTIVITIES_WINDOW_ID, BG_HEIGHT, BG_WIDTH, EDGE_FRAME_SIZE, FOOTER_HEIGHT, HEADER_HEIGHT, HEIGHT, MAIN_SPRITE_HEIGHT, MAIN_SPRITE_WIDTH, WIDTH
from eve.client.script.ui.shared.activities.activityListCont import ActivityListCont
from eve.client.script.ui.shared.activities.activityInfoPanel import ActivityInfoPanel
from eve.client.script.ui.structure import ChangeSignalConnect
from localization import GetByLabel

class ActivitiesWindow(Window):
    __guid__ = 'form.ActivitiesWindow'
    default_windowID = ACTIVITIES_WINDOW_ID
    default_fixedWidth = WIDTH
    default_fixedHeight = HEIGHT
    default_isLightBackgroundConfigurable = False
    default_isStackable = False
    default_iconNum = ACTIVITIES_ICON_PATH
    close_button_texture_path = 'res:/UI/Texture/activities/WindowCloseUp.png'
    minimize_button_texture_path = 'res:/UI/Texture/activities/WindowMinimize.png'
    default_headerHeight = HEADER_HEIGHT
    default_header_button_width = 14
    default_header_button_height = 14
    default_header_button_left_padding = 8
    default_header_button_top_padding = 8

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.service = sm.GetService('activities')
        self.service.LoadActivities()
        self.SetCaption(GetByLabel('UI/NewActivitiesWindow/ActivitiesTitle'))
        self.SetMinSize([640, 323])
        self.SetScope(uiconst.SCOPE_INGAME)
        self.ConstructLayout()

    def ConstructLayout(self):
        self.ConstructHeader()
        self.ConstructMain()
        self.ConstructFooter()
        self.ConstructExternal()

    def ConstructHeader(self):
        self.iconLabelContainer = Container(name='iconAndLabelContainer', parent=self.sr.headerParent, align=uiconst.TOLEFT_PROP, width=0.3, padding=(5, 0, 0, 0))
        self.iconSprite = Sprite(name='iconSprite', parent=Container(name='iconContainer', parent=self.iconLabelContainer, align=uiconst.TOLEFT, width=HEADER_HEIGHT), padTop=EDGE_FRAME_SIZE, width=HEADER_HEIGHT, height=HEADER_HEIGHT, align=uiconst.CENTER, texturePath=ACTIVITIES_ICON_PATH)

    def ConstructFooter(self):
        self.footerContainer = Container(parent=self.mainCont, name='buttonContainerContainer', align=uiconst.TOBOTTOM, bgColor=Color.BLACK, height=FOOTER_HEIGHT)
        self.checkbox = Checkbox(parent=self.footerContainer, align=uiconst.CENTERRIGHT, left=20, prefstype=('char', 'ui'), checked=self.service.GetStatus(), callback=self.OnCheckboxSelected, text=GetByLabel('UI/NewActivitiesNotify/LoginNoLongerPrompt'), wrapLabel=False)

    def OnCheckboxSelected(self, checkbox):
        self.service.OnStatusChanged(checkbox.checked)

    def OnSetCheckBoxState(self, state):
        self.checkbox.SetChecked(state)

    def ConstructMain(self):
        self.mainCont = Container(name='mainCont', parent=self.sr.main, align=uiconst.CENTER, state=uiconst.UI_NORMAL, height=BG_HEIGHT, width=BG_WIDTH, opacity=1, idx=-1, clipChildren=True)
        self.activityListCont = ActivityListCont(name='activityListCont', parent=self.mainCont, align=uiconst.CENTERTOP, height=MAIN_SPRITE_HEIGHT, width=MAIN_SPRITE_WIDTH, idx=-1)
        self.ChangeSignalConnection(connect=True)
        self.activityListCont.ShowFirst()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.service.OnAfterExecution, self.AfterExecute),
         (self.service.OnSetPopState, self.OnSetCheckBoxState),
         (self.service.OnOpenActivityInfo, self.OnOpenActivityInfo),
         (self.service.OnCloseActivityInfo, self.OnCloseActivityInfo)]
        ChangeSignalConnect(signalAndCallback, connect)

    def AfterExecute(self, needWindowClosed):
        if not needWindowClosed:
            return
        self.CloseByUser()

    def ConstructExternal(self):
        self.activityInfoPanel = ActivityInfoPanel(name='activityInfoPanel', parent=self.mainCont, align=uiconst.CENTER, state=uiconst.UI_HIDDEN, idx=0, height=BG_HEIGHT, width=BG_WIDTH)

    def OnOpenActivityInfo(self, info):
        self.activityInfoPanel.state = uiconst.UI_PICKCHILDREN
        self.activityInfoPanel.Enable()
        self.activityInfoPanel.left = BG_WIDTH
        self.activityInfoPanel.UpdateHTML(info)
        uicore.animations.MoveTo(obj=self.activityInfoPanel, startPos=(BG_WIDTH, 0), endPos=(0, 0), duration=0.6, loops=1)

    def OnHideActivityInfo(self):
        self.activityInfoPanel.UpdateHTML('<html><head></head><body><body></html>')
        self.activityInfoPanel.state = uiconst.UI_HIDDEN
        self.activityInfoPanel.Disable()

    def OnCloseActivityInfo(self):
        uicore.animations.MoveTo(callback=self.OnHideActivityInfo, obj=self.activityInfoPanel, startPos=(0, 0), endPos=(-BG_WIDTH, 0), duration=0.6, loops=1)

    @classmethod
    def Open(cls, *args, **kwargs):
        sm.GetService('audio').SendUIEvent('news_window_open_play')
        return super(ActivitiesWindow, cls).Open(*args, **kwargs)

    def Close(self, *args, **kwargs):
        sm.GetService('audio').SendUIEvent('news_window_close_play')
        self.service.Reset()
        self.ChangeSignalConnection(connect=False)
        super(ActivitiesWindow, self).Close(*args, **kwargs)

    def CloseByUser(self, *args):
        self.killable = True
        super(ActivitiesWindow, self).CloseByUser(*args)
