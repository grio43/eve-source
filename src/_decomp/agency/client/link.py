#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agency\client\link.py


def get_help_video_link(video_id):
    from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst, contentGroupProvider
    contentGroup = contentGroupProvider.GetContentGroup(contentGroupConst.contentGroupHelp)
    return contentGroup.GetNameWithLink(videoID=video_id)
