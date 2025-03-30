#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\contextMenu\menuData.py
from carbonui.control.contextMenu.menuEntryData import MenuEntryData, MenuEntryDataCheckbox, MenuEntryDataRadioButton, MenuEntryDataCaption, MenuEntryDataLabel, MenuEntryDataSlider

class BaseMenuData(object):

    def __init__(self, iconSize = 16):
        self.iconSize = iconSize

    def GetEntries(self):
        raise NotImplementedError

    def GetIconSize(self):
        if self.HasIcons():
            return self.iconSize
        return 0

    def HasIcons(self):
        return any((e.HasIcon() or e.HasGroupIcon() for e in self.GetEntries() if e is not None))

    def __add__(self, other):
        from carbonui.control.contextMenu.menuDataFactory import CreateMenuDataFromRawTuples, CreateMenuDataWithEntries
        if isinstance(other, MenuData):
            entryList = other.entrylist
        elif isinstance(other, (tuple, list)):
            menuData = CreateMenuDataFromRawTuples(other)
            entryList = menuData.entrylist if menuData else []
        else:
            raise ValueError('Cannot add types %s and %s' % (type(self), type(other)))
        return CreateMenuDataWithEntries(self.GetEntries() + entryList, iconSize=self.iconSize)

    def __len__(self):
        return len(self.GetEntries())

    def __iter__(self):
        return iter(self.GetEntries())


class MenuData(BaseMenuData):

    def __init__(self, entryList = None, iconSize = 16):
        super(MenuData, self).__init__(iconSize)
        self.entrylist = entryList or []

    def AppendMenuEntryData(self, menuEntryData):
        self.entrylist.append(menuEntryData)

    def AddEntry(self, text, func = None, subMenuData = None, texturePath = None, hint = None, menuGroupID = None, menuEntryViewClass = None, internalName = '', **kwargs):
        menuEntryData = MenuEntryData(text, func=func, subMenuData=subMenuData, texturePath=texturePath, hint=hint, menuGroupID=menuGroupID, menuEntryViewClass=menuEntryViewClass, internalName=internalName, **kwargs)
        self.AppendMenuEntryData(menuEntryData)
        return menuEntryData

    def AddCaption(self, text, hint = None, internalName = ''):
        menuEntryData = MenuEntryDataCaption(text=text, hint=hint, internalName=internalName)
        self.AppendMenuEntryData(menuEntryData)
        return menuEntryData

    def AddLabel(self, text, hint = None, internalName = ''):
        menuEntryData = MenuEntryDataLabel(text=text, hint=hint, internalName=internalName)
        self.AppendMenuEntryData(menuEntryData)
        return menuEntryData

    def AddCheckbox(self, text, setting, **kwargs):
        menuEntryData = MenuEntryDataCheckbox(text=text, setting=setting, **kwargs)
        self.AppendMenuEntryData(menuEntryData)
        return menuEntryData

    def AddRadioButton(self, text, value, setting, **kwargs):
        menuEntryData = MenuEntryDataRadioButton(text=text, value=value, setting=setting, **kwargs)
        self.AppendMenuEntryData(menuEntryData)
        return menuEntryData

    def AddSlider(self, text, setting, isInteger = False, **kwargs):
        menuEntryData = MenuEntryDataSlider(text=text, setting=setting, min_label=str(setting.min_value), max_label=str(setting.max_value), isInteger=isInteger, **kwargs)
        self.AppendMenuEntryData(menuEntryData)
        return menuEntryData

    def AddSeparator(self):
        self.entrylist.append(None)

    def GetEntries(self):
        return self.entrylist

    def append(self, entry):
        self.extend(entries=[entry])

    def extend(self, entries):
        combined_menu = self + entries
        self.entrylist = combined_menu.GetEntries()
