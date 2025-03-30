#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\contextMenu\menuEntryData.py
import caching
import signals
from eve.client.script.ui import menuUtil
from eve.client.script.ui.inflight import actionConst
from menu import MenuLabel

class BaseMenuEntryData(object):
    __on_enabled_changed = None

    def __init__(self, text = None, menuGroupID = None, hint = None, menuEntryViewClass = None, internalName = '', isEnabled = True, disabledHint = None, quantity = None, uniqueUiName = None):
        super(BaseMenuEntryData, self).__init__()
        if isinstance(text, MenuLabel):
            self._menuLabel = text
            self.text = self._menuLabel.GetText()
        else:
            self._menuLabel = None
            self.text = text
        self.menuGroupID = menuGroupID or menuUtil.GetMenuGroup(self.GetLabelPath())
        self.hint = hint
        self.menuClass = menuEntryViewClass
        self.internalName = internalName
        self._enabled = isEnabled
        self.disabledHint = disabledHint
        self.quantity = quantity
        self.uniqueUiName = uniqueUiName

    @property
    def on_enabled_changed(self):
        if self.__on_enabled_changed is None:
            self.__on_enabled_changed = signals.Signal('{}.on_enabled_changed'.format(self.__class__.__name__))
        return self.__on_enabled_changed

    @property
    def isEnabled(self):
        return self._enabled

    @isEnabled.setter
    def isEnabled(self, value):
        if self._enabled != value:
            self._enabled = value
            if self.__on_enabled_changed is not None:
                self.__on_enabled_changed(self)

    def GetMenuLabel(self):
        return self._menuLabel

    def GetLabelPath(self):
        if self._menuLabel:
            return self._menuLabel.labelPath

    def GetActionID(self):
        return self.GetLabelPath()

    def GetLabelKeywords(self):
        if self._menuLabel:
            return self._menuLabel.labelKeywords
        return {}

    def GetText(self):
        if self._menuLabel:
            text = self._menuLabel.GetText()
        else:
            text = self.text
        if self.quantity is not None:
            text += ' (%s)' % self.quantity
        return text

    def GetTextDescriptive(self):
        return self.GetText()

    def IsEnabled(self):
        return self.isEnabled

    def GetDisabledHint(self):
        return self.disabledHint

    def GetPrimaryMenuGroupID(self):
        if isinstance(self.menuGroupID, tuple):
            return self.menuGroupID[0]
        else:
            return self.menuGroupID

    def HasIcon(self):
        return bool(self.GetIcon())

    def HasGroupIcon(self):
        return self.menuGroupID and self.menuGroupID in menuUtil.ICON_DATA_BY_MENUGROUPID

    def GetGroupIconData(self):
        return menuUtil.GetGroupIconData(self.menuGroupID)

    def GetIcon(self):
        if self.GetActionID() in actionConst.MENU_ICON_BLACKLIST:
            return None
        return actionConst.ICON_BY_ACTIONID.get(self.GetActionID(), None)

    def GetHint(self):
        return self.hint

    def HasSubMenuData(self):
        return False

    def HasFunction(self):
        return False

    def __repr__(self):
        return '{}(internalName={}, text={!r})'.format(self.__class__.__name__, self.internalName, self.text)


class MenuEntryDataCaption(BaseMenuEntryData):

    def IsEnabled(self):
        return False


class MenuEntryDataLabel(BaseMenuEntryData):

    def IsEnabled(self):
        return False


class MenuEntryData(BaseMenuEntryData):

    def __init__(self, text, func = None, subMenuData = None, texturePath = None, menuGroupID = None, menuEntryViewClass = None, internalName = '', typeID = None, **kwargs):
        super(MenuEntryData, self).__init__(text=text, menuGroupID=menuGroupID, menuEntryViewClass=menuEntryViewClass, internalName=internalName, **kwargs)
        self.func = func
        self._subMenuData = subMenuData
        self.texturePath = texturePath
        self.typeID = typeID

    def IsSubMenuDynamic(self):
        return callable(self._subMenuData)

    def GetSubMenuData(self):
        if self.IsSubMenuDynamic():
            return self._GetSubMenuDataDynamic()
        if isinstance(self._subMenuData, (tuple, list)):
            from carbonui.control.contextMenu import menuDataFactory
            self._subMenuData = menuDataFactory.CreateMenuDataFromRawTuples(self._subMenuData)
        return self._subMenuData

    @caching.Memoize(minutes=1 / 120.0)
    def _GetSubMenuDataDynamic(self):
        from carbonui.control.contextMenu import menuDataFactory
        return menuDataFactory.CreateMenuDataFromRawTuples(self._subMenuData())

    def HasSubMenuData(self):
        if self.IsSubMenuDynamic():
            return True
        else:
            return bool(self._subMenuData)

    def GetIcon(self):
        if self.texturePath:
            return self.texturePath
        else:
            return super(MenuEntryData, self).GetIcon()

    def HasFunction(self):
        return bool(self.func)

    def ExecuteFunction(self):
        self.func()


class MenuEntryDataCheckbox(BaseMenuEntryData):

    def __init__(self, text, setting, **kwargs):
        super(MenuEntryDataCheckbox, self).__init__(text=text, **kwargs)
        self.setting = setting

    def HasIcon(self):
        return True


class MenuEntryDataRadioButton(BaseMenuEntryData):

    def __init__(self, text, value, setting, **kwargs):
        super(MenuEntryDataRadioButton, self).__init__(text=text, **kwargs)
        self.value = value
        self.setting = setting

    def HasIcon(self):
        return True


class MenuEntryDataSlider(BaseMenuEntryData):

    def __init__(self, text, setting, min_label = None, max_label = None, isInteger = False, **kwargs):
        super(MenuEntryDataSlider, self).__init__(text=text, **kwargs)
        self.setting = setting
        self.min_label = min_label
        self.max_label = max_label
        self.isInteger = isInteger

    def HasFunction(self):
        return False
