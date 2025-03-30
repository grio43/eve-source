#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agency\client\custom_content.py
import logging
logger = logging.getLogger(__name__)

def get_remote_agency_provider_service():
    return sm.RemoteSvc('custom_agency_provider')


def get_custom_content():
    content_data = get_remote_agency_provider_service().get_content_data()
    logger.debug('Returning %s pieces of custom agency content from the server', len(content_data))
    return content_data


def get_custom_content_by_content_type(content_type):
    content_data_collection = get_custom_content()
    filtered_content_data = [ data for data in content_data_collection if data.content_type == content_type ]
    logger.debug('Returning %s pieces of custom agency content of type %s from the server', len(filtered_content_data), content_type)
    return filtered_content_data
