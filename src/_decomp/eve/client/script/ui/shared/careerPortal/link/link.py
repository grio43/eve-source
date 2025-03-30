#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\link\link.py
import uuid
import evelink.client
SCHEME_CAREER_PROGRAM_NODE = 'careerProgramNode'

def register_link_handlers(registry):
    registry.register(SCHEME_CAREER_PROGRAM_NODE, handle_node_link, hint='UI/CareerPortal/NodeLinkHint')


def handle_node_link(url):
    careerID, activityID, goalID = parse_node_url(url)
    from eve.client.script.ui.shared.careerPortal.careerPortalWnd import CareerPortalDockablePanel
    wnd = CareerPortalDockablePanel.GetIfOpen()
    if wnd and not wnd.destroyed:
        wnd.Maximize()
    else:
        wnd = CareerPortalDockablePanel.Open()
    if wnd:
        wnd.navigate_to_node(careerID, activityID, goalID)


def parse_node_url(url):
    _, careerID, activityID, goalID = url.split(':')
    try:
        careerID = int(careerID)
    except ValueError:
        careerID = None

    try:
        activityID = int(activityID)
    except ValueError:
        activityID = None

    try:
        goalID = uuid.UUID(goalID)
    except ValueError:
        goalID = None

    return (careerID, activityID, goalID)


def format_node_url(careerID, activityID, goalID):
    return u'{}:{}:{}:{}'.format(SCHEME_CAREER_PROGRAM_NODE, careerID, activityID, goalID)


def node_link(careerID, activityID, goalID, name):
    return evelink.Link(url=format_node_url(careerID, activityID, goalID), text=name)
