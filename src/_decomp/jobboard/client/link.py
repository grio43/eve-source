#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\link.py
import evelink
import localization
SCHEME = 'opportunity'

def get_job_link(job):
    return evelink.Link(url=format_url(job.job_id), text=localization.GetByLabel('UI/Opportunities/ChatLinkLabel', title=job.link_title))


def register_link_handlers(registry):
    registry.register(SCHEME, _handle_link, hint=_get_link_hint)


def _handle_link(url):
    from jobboard.client import get_job_board_service
    job_id = _parse_url(url)
    get_job_board_service().open_job(job_id)


def _get_link_hint(url):
    return localization.GetByLabel('UI/Opportunities/ChatLinkHint')


def format_url(job_id):
    return u'{}:{}'.format(SCHEME, job_id)


def _parse_url(url):
    start = url.index(':') + 1
    return url[start:]
