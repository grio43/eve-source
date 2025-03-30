#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageHelp.py
import logging
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.icon import IconEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveCaptionMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from carbonui.control.section import Section
from eve.client.script.ui.shared.subtitles import GetSubtitlePathForVideo
from eve.client.script.ui.shared.videowindow import VideoPlayer
from eveui import Sprite
from localization import GetByLabel, GetByMessageID
PADDING_BETWEEN_SECTIONS = 20
logger = logging.getLogger(__name__)

class ContentPageHelp(Container):
    default_name = 'ContentPageHelp'
    default_padding = 20

    def ApplyAttributes(self, attributes):
        super(ContentPageHelp, self).ApplyAttributes(attributes)
        self.openOnVideoID = attributes.get('videoID', None)
        self._contentProvider = None
        self.agencySvc = None
        self.descriptionEntry = None
        self._ConstructVideoBrowser()
        self._ConstructVideoSection()
        self.PopulateScroll()
        if self.openOnVideoID:
            self.SelectVideoByID(self.openOnVideoID)

    @property
    def contentProvider(self):
        if not self._contentProvider:
            self._contentProvider = sm.GetService('agencyNew').GetContentProvider(contentGroupConst.contentGroupHelp)
        return self._contentProvider

    def _ConstructVideoBrowser(self):
        videoBrowser = Section(name='VideoBrowser', parent=self, align=uiconst.TOLEFT_PROP, width=0.3, headerText=GetByLabel('UI/Agency/HelpVideos/BrowserHeader'))
        self.searchBar = QuickFilterEdit(name='videoSearchBar', parent=videoBrowser, align=uiconst.TOTOP, height=24)
        self.searchBar.ReloadFunction = self.PopulateScroll
        self.videoBrowserScroll = Scroll(name='VideoBrowserScroll', parent=videoBrowser, top=5, multiSelect=False)
        self.videoBrowserScroll.OnSelectionChange = self.DisplayVideo

    def SelectVideoByID(self, videoID):
        scrollNodes = self.videoBrowserScroll.GetNodes()
        for scrollNode in scrollNodes:
            if scrollNode.decoClass != VideoScrollEntry:
                continue
            if scrollNode['id'] == videoID:
                self.videoBrowserScroll.SelectNode(scrollNode)

    def SelectNextEntry(self):
        self.videoBrowserScroll.OnDown()
        if self.descriptionEntry:
            self.videoBrowserScroll.OnDown()

    def SelectPreviousEntry(self):
        self.videoBrowserScroll.OnUp()

    def OnGroupToggle(self):
        selected = self.videoBrowserScroll.GetSelected()
        if not selected:
            return
        self.DisplayVideo(selected)

    def DisplayVideo(self, selectedVideoEntry):
        if not selectedVideoEntry:
            return
        selectedVideoEntry = selectedVideoEntry[0]
        if selectedVideoEntry.decoClass != VideoScrollEntry:
            return
        self.videoPlayer.Show()
        self.videoSection.SetText(selectedVideoEntry.label)
        self.noVideoSelectedMessage.Hide()
        self.AddDescriptionEntry(selectedVideoEntry)
        subtitlePath = GetSubtitlePathForVideo(selectedVideoEntry.path, session.languageID)
        self.videoPlayer.SetVideoPath(selectedVideoEntry.path, subtitles=subtitlePath, videoLoop=True)
        self.SetVideoSequence(selectedVideoEntry)

    def AddDescriptionEntry(self, selectedVideoEntry):
        if self.descriptionEntry:
            self.videoBrowserScroll.RemoveNodes(self.descriptionEntry)
        descriptionEntryData = self.GetDescriptionEntryData(selectedVideoEntry)
        self.descriptionEntry = self.videoBrowserScroll.AddNodes(selectedVideoEntry.idx + 1, [GetFromClass(DescriptionEntry, descriptionEntryData)], parentNode=selectedVideoEntry)

    def GetDescriptionEntryData(self, selectedVideoEntry):
        return {'label': selectedVideoEntry.description,
         'maxLines': 0,
         'sublevel': 1.75,
         'labelMaxWidth': 250}

    def SetVideoSequence(self, selectedVideoEntry):
        videoIDs = self.GetVideosInGroup(selectedVideoEntry.videoGroupID)
        videoPaths = [ self.contentProvider.GetVideo(videoID).path for videoID in videoIDs ]
        self.videoPlayer.SetVideoSequence(videoPaths)

    def GetVideosInGroup(self, videoGroupID):
        group = self.contentProvider.GetVideoGroup(videoGroupID)
        if not group:
            return
        return group.videos

    def _ConstructVideoSection(self):
        self.videoSection = Section(name='VideoSection', parent=self, align=uiconst.TOALL, padLeft=PADDING_BETWEEN_SECTIONS, headerText=GetByLabel('UI/Agency/HelpVideos/NoVideoSelected'))
        self.noVideoSelectedMessage = EveCaptionMedium(parent=self.videoSection, align=uiconst.CENTER, text='<center>%s</center>' % GetByLabel('UI/Agency/HelpVideos/EntryMessage'), maxWidth=200)
        self.videoPlayer = VideoPlayer(parent=self.videoSection, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, sendAnalytics=True)
        self.videoPlayer.OnNextButtonClicked = self.SelectNextEntry
        self.videoPlayer.OnPreviousButtonClicked = self.SelectPreviousEntry

    def PopulateScroll(self):
        self.videoBrowserScroll.Clear()
        scrollList = self.GetScrollEntries()
        self.videoBrowserScroll.Load(contentList=scrollList)

    def _GetVideoGroupSubContent(self, data, *args):
        scrollList = []
        for video in data.videos:
            selected = video.path == self.videoPlayer.video.path
            scrollList.append(GetFromClass(VideoScrollEntry, {'id': video.id,
             'label': GetByMessageID(video.nameID),
             'icon': 'res:/UI/Texture/classes/agency/helpSection/menuPlay_Icon.png',
             'iconsize': 16,
             'height': 25,
             'iconoffset': 8,
             'labeloffset': 8,
             'description': GetByMessageID(video.descriptionID),
             'path': video.path,
             'videoGroupID': data.videoGroupID,
             'isSelected': selected,
             'selected': selected}))

        return scrollList

    def _FilterVideos(self, videos, searchText):
        matching_videos = []
        for videoID in videos:
            video = self.contentProvider.GetVideo(videoID)
            if searchText in GetByMessageID(video.nameID).lower():
                matching_videos.append(video)

        return matching_videos

    def GetScrollEntries(self):
        scrollList = []
        videoGroups = self.contentProvider.GetVideoGroups()
        searchText = self.searchBar.GetValue().lower()
        for videoGroupID, videoGroup in videoGroups.iteritems():
            if len(searchText) >= 3:
                videos = self._FilterVideos(videoGroup.videos, searchText)
            else:
                videos = [ self.contentProvider.GetVideo(videoID) for videoID in videoGroup.videos ]
            if not videos:
                logger.warn('Agency Help Section: Encountered empty group, skipping.')
                continue
            scrollList.append(GetFromClass(ListGroup, {'GetSubContent': self._GetVideoGroupSubContent,
             'label': GetByMessageID(videoGroup.nameID),
             'id': ('videoGroup', videoGroupID),
             'videos': videos,
             'showlen': False,
             'contentProvider': self.contentProvider,
             'showicon': 'hide',
             'videoGroupID': videoGroupID,
             'onToggle': self.OnGroupToggle,
             'BlockOpenWindow': True}))

        return scrollList


class VideoScrollEntry(IconEntry):
    __guid__ = 'listentry.AgencyHelpVideoEntry'
    default_name = 'VideoScrollEntry'
    default_hint = GetByLabel('UI/Agency/HelpVideos/VideoLinkHelp')
    HIGHLIGHT_COLOR = (0.18, 0.54, 0.64, 1.0)

    def ApplyAttributes(self, attributes):
        super(VideoScrollEntry, self).ApplyAttributes(attributes)
        self.MakeDragObject()
        self.EnableDrag()

    def ConstructIcon(self):
        self.icon = Sprite(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, opacity=0.75)
        self.icon.OnMouseEnter = self.HighlightIcon
        self.icon.OnMouseExit = self.UnHighlightIcon

    def Select(self, animate = True):
        super(VideoScrollEntry, self).Select(animate)
        self.SetIconColor(self.HIGHLIGHT_COLOR)

    def Deselect(self, animate = True):
        super(VideoScrollEntry, self).Deselect(animate)
        self.SetIconColor(Color.WHITE)

    def SetIconColor(self, color):
        self.icon.SetRGBA(*color)

    def HighlightIcon(self, *args):
        animations.FadeTo(self.icon, startVal=0.75, duration=0.225)

    def UnHighlightIcon(self, *args):
        animations.FadeTo(self.icon, startVal=1.0, endVal=0.75, duration=0.225)

    def GetDragData(self, *args):
        return [self.sr.node]


class DescriptionEntry(Generic):

    def OnMouseHover(self, *args):
        pass

    def OnClick(self, *args):
        pass

    def OnMouseExit(self, *args):
        pass

    def OnMouseEnter(self, *args):
        pass

    def OnDblClick(self, *args):
        pass
