#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\accessGroups\searchCont.py
import math
from carbonui import fontconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.transform import Transform
from carbonui.control.buttonIcon import ButtonIcon
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import Label
from localization import GetByLabel
from carbonui.uicore import uicore
from bannedwords.client import bannedwords
hintText = GetByLabel('UI/Structures/AccessGroups/SearchFieldHint')

class SearchCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        texturePath = 'res:/UI/Texture/WindowIcons/peopleandplaces.png'
        searchIconHint = GetByLabel('UI/Structures/AccessGroups/SearchButtonHint')
        self.searchIcon = ButtonIcon(name='searchIcon', parent=self, align=uiconst.CENTERRIGHT, pos=(2, 0, 24, 24), iconSize=24, texturePath=texturePath, func=self.OnSearchBtnClicked, hint=searchIconHint)
        arrowTexturePath = 'res:/UI/Texture/Icons/1_16_99.png'
        self.arrowCont = Transform(name='arrowCont', parent=self, pos=(24, 0, 16, 16), align=uiconst.CENTERRIGHT, rotation=self.GetRotation())
        self.expandArrow = ButtonIcon(name='expandArrow', parent=self.arrowCont, pos=(0, 0, 16, 16), iconSize=16, texturePath=arrowTexturePath, func=self.OnExpanderClicked)
        self.searchField = SingleLineEditText(parent=self, align=uiconst.CENTERRIGHT, pos=(40,
         0,
         self.GetWidth(),
         0), OnReturn=self.DoSearch, hintText=hintText, isCharCorpOrAllianceField=True, maxLength=100)
        self.searchField.OnClearButtonClick = self.OnClearingSearchField
        self.searchField.ShowClearButton(hint=GetByLabel('UI/Inventory/Clear'))
        self.memberNamesByMemberID = {}
        self.height = max(self.searchField.height, self.searchIcon.height)
        self.collapsedWidth = 10 + self.searchField.left + self.searchField.width
        self.width = self.collapsedWidth

    def OnSearchBtnClicked(self, *args):
        if settings.user.ui.Get('accessGroup_searchExpanded', False):
            self.DoSearch()
        else:
            self.OnExpanderClicked()

    def OnExpanderClicked(self, *args):
        isExpandedNow = settings.user.ui.Get('accessGroup_searchExpanded', False)
        settings.user.ui.Set('accessGroup_searchExpanded', not isExpandedNow)
        newRotation = self.GetRotation()
        newWidth = self.GetWidth()
        uicore.animations.MorphScalar(self.arrowCont, 'rotation', self.arrowCont.rotation, newRotation, duration=0.35)
        uicore.animations.MorphScalar(self.searchField, 'width', startVal=self.searchField.width, endVal=newWidth, duration=0.35)
        self.width = self.collapsedWidth + newWidth
        if not isExpandedNow:
            self.PrimeMembers()

    def GetRotation(self):
        if settings.user.ui.Get('accessGroup_searchExpanded', False):
            return math.pi
        return 0

    def GetWidth(self):
        if settings.user.ui.Get('accessGroup_searchExpanded', False):
            width, _ = Label.MeasureTextSize(text=hintText, fontsize=fontconst.EVE_MEDIUM_FONTSIZE)
            return max(200, width + 10)
        return 0

    def DoSearch(self, *args):
        searchString = self.searchField.GetValue().lower()
        if len(searchString) < 3:
            self.controller.SetCurrentSearchResults(None)
            return
        bannedwords.check_search_words_allowed(searchString)
        allMemberInfo = self.PrimeMembers()
        groupsWithMatchedMembers = set()
        matchedMembers = set()
        for groupID, membersDict in allMemberInfo.iteritems():
            for eachMemberID in membersDict.iterkeys():
                memberName = self.GetMemberName(eachMemberID)
                if memberName.find(searchString) > -1:
                    groupsWithMatchedMembers.add(groupID)
                    matchedMembers.add(eachMemberID)

        searchResults = (matchedMembers, groupsWithMatchedMembers)
        self.controller.SetCurrentSearchResults(searchResults)

    def PrimeMembers(self):
        allMemberInfo, allMemberIDs = self.controller.GetAllMyMemberIDs()
        cfg.eveowners.Prime(allMemberIDs)
        return allMemberInfo

    def GetMemberName(self, memberID):
        memberName = self.memberNamesByMemberID.get(memberID)
        if memberName:
            return memberName
        memberName = cfg.eveowners.Get(memberID).name.lower()
        self.memberNamesByMemberID[memberID] = memberName
        return memberName

    def OnClearingSearchField(self):
        SingleLineEditText.OnClearButtonClick(self.searchField)
        self.DoSearch()
