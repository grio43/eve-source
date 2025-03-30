#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\charactercreator\client\empireSelectionTechnology.py
from carbonui.fontconst import EVE_MEDIUM_FONTSIZE, EVE_SMALL_FONTSIZE
from eve.common.lib.appConst import raceAmarr, raceMinmatar, raceGallente, raceCaldari
from eve.client.script.ui.util.uix import GetTextWidth
from localization import GetByMessageID

class TechnologyExample(object):

    def __init__(self, icons, titles, subtitles):
        self.icons = icons
        self.titles = titles
        self.subtitles = subtitles

    def GetTitle(self, raceID):
        return GetByMessageID(self.titles[raceID]).upper()

    def GetSubtitle(self, raceID):
        return GetByMessageID(self.subtitles[raceID])

    def GetIcon(self, raceID):
        return self.icons[raceID]

    def GetTextWidth(self, raceID):
        titleWidth = self._GetTitleWidth(raceID)
        subtitleWidth = self._GetSubtitleWidth(raceID)
        return max(titleWidth, subtitleWidth)

    def _GetTitleWidth(self, raceID):
        title = self.GetTitle(raceID)
        return GetTextWidth(title, EVE_MEDIUM_FONTSIZE)

    def _GetSubtitleWidth(self, raceID):
        subtitle = self.GetSubtitle(raceID)
        return GetTextWidth(subtitle, EVE_SMALL_FONTSIZE)


class Technology(object):

    def __init__(self, title, iconTexture, mainTexts, mainViews, techExamples, techStepOrder):
        self.title = title
        self.iconTexture = iconTexture
        self.mainTexts = mainTexts
        self.mainViews = mainViews
        self.techExamples = techExamples
        self.techStepOrder = techStepOrder

    def GetTechTitle(self):
        return GetByMessageID(self.title).upper()

    def GetIconTexture(self):
        return self.iconTexture

    def GetTechStepOrder(self):
        return self.techStepOrder

    def GetMainText(self, raceID):
        return GetByMessageID(self.mainTexts[raceID])

    def GetMainView(self, raceID):
        return self.mainViews[raceID]

    def GetTechExample(self, order):
        return self.techExamples[order]

    def GetNumberOfExamples(self):
        return len(self.techExamples)

    def GetTechExamples(self):
        return self.techExamples.iteritems()

    def GetTitleWidth(self):
        title = self.GetTechTitle()
        return GetTextWidth(title, fontsize=EVE_MEDIUM_FONTSIZE, uppercase=1, hspace=1)

    def GetMaxTechExampleTitleWidth(self, raceID):
        maxWidth = 0
        for techExample in self.techExamples.values():
            textWidth = techExample.GetTextWidth(raceID)
            if textWidth > maxWidth:
                maxWidth = textWidth

        return maxWidth


class TechnologyData(object):

    def __init__(self, technologyStaticData):
        self.data = {}
        self._ReadTechnologies(technologyStaticData)

    def _ReadTechnologies(self, technologyStaticData):
        techsToDisplay = {}
        for techID, techData in technologyStaticData.iteritems():
            if techData.isDisplayed:
                techsToDisplay[techData.order] = techID

        for techOrder, techStepOrder in enumerate(sorted(techsToDisplay.keys())):
            techID = techsToDisplay[techStepOrder]
            techData = technologyStaticData[techID]
            mainTexts = self._ReadMainTexts(techData)
            mainViews = self._ReadMainViews(techData)
            techExamples = self._ReadTechExamples(techData.examples)
            if techData.isDisplayed:
                self.data[techOrder + 1] = Technology(title=techData.title, iconTexture=techData.icon, mainTexts=mainTexts, mainViews=mainViews, techExamples=techExamples, techStepOrder=techStepOrder)

    def _ReadMainTexts(self, techData):
        return {raceAmarr: getattr(techData, 'mainTextAmarr', None),
         raceCaldari: getattr(techData, 'mainTextCaldari', None),
         raceGallente: getattr(techData, 'mainTextGallente', None),
         raceMinmatar: getattr(techData, 'mainTextMinmatar', None)}

    def _ReadMainViews(self, techData):
        return {raceAmarr: getattr(techData, 'mainViewAmarr', None),
         raceCaldari: getattr(techData, 'mainViewCaldari', None),
         raceGallente: getattr(techData, 'mainViewGallente', None),
         raceMinmatar: getattr(techData, 'mainViewMinmatar', None)}

    def _ReadTechExamples(self, techExamplesData):
        techExamples = {}
        for techExampleID, techExampleData in techExamplesData.iteritems():
            titles = self._ReadTechExampleTitles(techExampleData)
            subtitles = self._ReadTechExampleSubtitles(techExampleData)
            icons = self._ReadTechExampleIcons(techExampleData)
            techExamples[techExampleID] = TechnologyExample(titles=titles, subtitles=subtitles, icons=icons)

        return techExamples

    def _ReadTechExampleTitles(self, techExampleData):
        return {raceAmarr: techExampleData.titleAmarr,
         raceCaldari: techExampleData.titleCaldari,
         raceGallente: techExampleData.titleGallente,
         raceMinmatar: techExampleData.titleMinmatar}

    def _ReadTechExampleSubtitles(self, techExampleData):
        return {raceAmarr: techExampleData.subtitleAmarr,
         raceCaldari: techExampleData.subtitleCaldari,
         raceGallente: techExampleData.subtitleGallente,
         raceMinmatar: techExampleData.subtitleMinmatar}

    def _ReadTechExampleIcons(self, techExampleData):
        return {raceAmarr: techExampleData.iconAmarr,
         raceCaldari: techExampleData.iconCaldari,
         raceGallente: techExampleData.iconGallente,
         raceMinmatar: techExampleData.iconMinmatar}

    def GetNumberOfTechs(self):
        return len(self.data)

    def GetFirstOrder(self):
        return min(self.data.keys())

    def GetTechnologies(self):
        return self.data.iteritems()

    def GetTech(self, order):
        return self.data[order]

    def GetMaxTechTitleWidth(self):
        maxWidth = 0
        for tech in self.data.values():
            textWidth = tech.GetTitleWidth()
            if textWidth > maxWidth:
                maxWidth = textWidth

        return maxWidth
