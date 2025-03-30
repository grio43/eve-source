#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\client\handlers\__init__.py


def register_handlers(registry):
    from .deprecated import register_deprecated_handlers
    register_deprecated_handlers(registry)
    from .local_service import register_local_service_handlers
    register_local_service_handlers(registry)
    from .show_info import register_show_info_handler
    register_show_info_handler(registry)
    from .web import register_web_handlers
    register_web_handlers(registry)
    import raffles.client
    raffles.client.register_link_handlers(registry)
    import ownergroups.client
    ownergroups.client.register_link_handlers(registry)
    import overviewPresets.client.link as overview_link
    overview_link.register_link_handlers(registry)
    from eve.client.script.ui.shared.pointerTool import link as pointer_tool_link
    pointer_tool_link.register_link_handlers(registry)
    import sharedSettings.client
    sharedSettings.client.register_link_handlers(registry)
    import redeem.client
    redeem.client.register_link_handlers(registry)
    from eve.client.script.ui.shared import preview
    preview.register_link_handlers(registry)
    from eve.client.script.ui.shared.maps import link as map_link
    map_link.register_link_handlers(registry)
    import xmppchatclient
    xmppchatclient.register_link_handlers(registry)
    from eve.client.script.ui.shared.neocom import notepad
    notepad.register_link_handlers(registry)
    from eve.client.script.ui.shared.neocom.contracts import link as contract_link
    contract_link.register_link_handlers(registry)
    import evefleet.client
    evefleet.client.register_link_handlers(registry)
    import shipfitting.client
    shipfitting.client.register_link_handlers(registry)
    import evemail.client
    evemail.client.register_link_handlers(registry)
    import evewar.client
    evewar.client.register_link_handlers(registry)
    from eve.client.script.ui.shared.bookmarks import link as bookmark_link
    bookmark_link.register_link_handlers(registry)
    from eve.client.script.ui.shared import killReportUtil
    killReportUtil.register_link_handlers(registry)
    import eveagent.client
    eveagent.client.register_link_handlers(registry)
    import corporation.client
    corporation.client.register_link_handlers(registry)
    import characterskills.client
    characterskills.client.register_link_handlers(registry)
    import probescanning.link
    probescanning.link.register_link_handlers(registry)
    import dynamicresources.client.ui.link
    dynamicresources.client.ui.link.register_link_handlers(registry)
    from eve.client.script.ui.podGuide import link as pod_guide_link
    pod_guide_link.register_link_handlers(registry)
    from eve.client.script.ui.skillPlan import link as skill_plan_link
    skill_plan_link.register_link_handlers(registry)
    from eve.client.script.ui.shared.careerPortal.link import link as career_portal_link
    career_portal_link.register_link_handlers(registry)
    from fwwarzone.client.dashboard import link as fw_system_link
    fw_system_link.register_link_handlers(registry)
    from jobboard.client import link as job_board_link
    job_board_link.register_link_handlers(registry)
    from cosmetics.client.ships.link import ship_skin_design_link_handler
    ship_skin_design_link_handler.register_link_handlers(registry)
    from cosmetics.client.ships.link import ship_skin_listing_link_handler
    ship_skin_listing_link_handler.register_link_handlers(registry)
    from eve.client.script.ui.shared.planet.colonyTemplateWindow import register_link_handlers as PITemplateLinkHandler
    PITemplateLinkHandler(registry)
