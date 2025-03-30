#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overviewSettings\statesPanel.py
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.parklife import states as stateFlagcConst
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.inflight.overviewSettings.overviewSettingEntries import StateOverviewEntry
from globalConfig import IsPlayerBountyHidden
from overviewPresets import overviewSettingsConst

class StatesPanel(Container):
    default_name = 'StatesPanel'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.presetSvc = sm.GetService('overviewPresetSvc')
        self.presetName = attributes.presetName
        self.initialized = False

    def SetPresetName(self, presetName):
        self.presetName = presetName

    def CreateIfNeeded(self):
        if self.initialized:
            return
        self.initialized = True
        self.iconCont = Container(parent=self, name='iconCont', align=uiconst.TOTOP, height=20, state=uiconst.UI_PICKCHILDREN)
        showSprite = Sprite(parent=self.iconCont, pos=(64, 0, 16, 16), name='showSprite', state=uiconst.UI_NORMAL, texturePath='res:/ui/texture/icons/generic/visible_default_16.png', align=uiconst.CENTERRIGHT, hint=localization.GetByLabel('UI/Overview/FilterStateAlwaysShowLong'))
        showSprite.SetRGBA(0.1, 1.0, 0.1, 0.75)
        showSprite.OnClick = (self.OnIconClicked, 'alwaysShow')
        hideSprite = Sprite(parent=self.iconCont, pos=(34, 0, 16, 16), name='hideSprite', state=uiconst.UI_NORMAL, texturePath='res:/ui/texture/icons/generic/visible_dontshow_16.png', align=uiconst.CENTERRIGHT, hint=localization.GetByLabel('UI/Overview/FilterStateFilterOutLong'))
        hideSprite.OnClick = (self.OnIconClicked, 'filterOut')
        hideSprite.SetRGBA(1.0, 0.05, 0.05, 0.75)
        neutralSprite = Sprite(parent=self.iconCont, pos=(4, 0, 16, 16), name='neutralSprite', state=uiconst.UI_NORMAL, texturePath='res:/ui/texture/icons/generic/visible_matchstate_16.png', align=uiconst.CENTERRIGHT, hint=localization.GetByLabel('UI/Overview/FilterStateNotFilterOutLong'))
        neutralSprite.SetRGBA(0.2, 0.4, 0.6, 0.75)
        neutralSprite.OnClick = (self.OnIconClicked, 'unfiltered')

        def ChangeOpaacity(sprite, opacity):
            sprite.opacity = opacity

        for sprite in (showSprite, hideSprite, neutralSprite):
            sprite.OnMouseEnter = (ChangeOpaacity, sprite, 1.2)
            sprite.OnMouseExit = (ChangeOpaacity, sprite, 1.0)

        self.statesScroll = Scroll(name='statesScroll', parent=self)

    def Load(self):
        self.CreateIfNeeded()
        includedList = []
        allFlagsAndProps = sm.GetService('stateSvc').GetStateProps()
        alwaysShow = self.presetSvc.GetAlwaysShownStates(presetName=self.presetName) or []
        filtered = self.presetSvc.GetFilteredStates(presetName=self.presetName) or []
        playerBountyHidden = IsPlayerBountyHidden(sm.GetService('machoNet'))
        for flag, props in allFlagsAndProps.iteritems():
            if flag == stateFlagcConst.flagForcedOn:
                continue
            if flag == stateFlagcConst.flagIsWanted and playerBountyHidden:
                continue
            entry = GetFromClass(StateOverviewEntry, {'label': props.text,
             'isAlwaysShow': flag in alwaysShow,
             'isFilterOut': flag in filtered,
             'flag': flag,
             'hint': props.hint,
             'props': props,
             'onChangeFunc': self.OnFilteredStatesChange})
            includedList.append(entry)

        includedList = localization.util.Sort(includedList, key=lambda x: x.label)
        self.statesScroll.Load(contentList=includedList, keepPosition=True)
        self.AdjustIcons()

    def _OnResize(self, *args):
        Container._OnResize(self)
        self.AdjustIcons()

    def OnIconClicked(self, configName, *args):
        self.OnFilteredStatesChange(None, configName)

    def AdjustIcons(self):
        scroll = getattr(self, 'statesScroll', None)
        if not scroll:
            return
        if scroll._scrollbar_vertical.display:
            self.iconCont.padRight = 24
        else:
            self.iconCont.padRight = 8

    def OnFilteredStatesChange(self, node, configToChange, *args):
        if node:
            selected = self.statesScroll.GetSelectedNodes(node)
        else:
            selected = self.statesScroll.GetSelected()
        flags = [ x.flag for x in selected ]
        addAlwaysShow = False
        addFilterOut = False
        if configToChange == 'alwaysShow':
            addAlwaysShow = True
        elif configToChange == 'filterOut':
            addFilterOut = True
        changeList = [(overviewSettingsConst.PRESET_SETTINGS_FILTERED_STATES, flags, addFilterOut), (overviewSettingsConst.PRESET_SETTINGS_ALWAYS_SHOWN_STATES, flags, addAlwaysShow)]
        self.presetSvc.ChangeSettings(changeList=changeList, presetName=self.presetName)
