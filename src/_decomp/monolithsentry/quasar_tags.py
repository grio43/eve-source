#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithsentry\quasar_tags.py
REQUEST_BROKER_STATE = 'quasar.req.broker_state'
REQUEST_BROKER_STREAM_ID = 'quasar.req.stream_id'
REQUEST_BROKER_CONNECTION_ID = 'quasar.req.conn_id'
REQUEST_BROKER_CHANNEL_STATE = 'quasar.req.chan_state'
REQUEST_BROKER_LAST_STREAM_ID = 'quasar.req.last_stream_id'
REQUEST_BROKER_LAST_STATUS_CODE = 'quasar.req.last_status_code'
NOTICE_CONSUMER_STATE = 'quasar.notice.consumer_state'
NOTICE_CONSUMER_STREAM_ID = 'quasar.notice.stream_id'
NOTICE_CONSUMER_CONNECTION_ID = 'quasar.notice.conn_id'
NOTICE_CONSUMER_CHANNEL_STATE = 'quasar.notice.chan_state'
NOTICE_CONSUMER_LAST_STREAM_ID = 'quasar.notice.last_stream_id'
NOTICE_CONSUMER_LAST_STATUS_CODE = 'quasar.notice.last_status_code'

def get_quasar_tags(public_gateway_svc):
    tags = {REQUEST_BROKER_STATE: 'none',
     REQUEST_BROKER_STREAM_ID: -1,
     REQUEST_BROKER_CONNECTION_ID: -1,
     REQUEST_BROKER_CHANNEL_STATE: 'none',
     REQUEST_BROKER_LAST_STREAM_ID: -1,
     REQUEST_BROKER_LAST_STATUS_CODE: -1,
     NOTICE_CONSUMER_STATE: 'none',
     NOTICE_CONSUMER_STREAM_ID: -1,
     NOTICE_CONSUMER_CONNECTION_ID: -1,
     NOTICE_CONSUMER_CHANNEL_STATE: 'none',
     NOTICE_CONSUMER_LAST_STREAM_ID: -1,
     NOTICE_CONSUMER_LAST_STATUS_CODE: -1}
    request_broker_details = public_gateway_svc.get_request_broker_details()
    if request_broker_details.get('native_broker', True) is not None:
        tags[REQUEST_BROKER_STATE] = request_broker_details['broker_state']
        tags[REQUEST_BROKER_STREAM_ID] = request_broker_details['stream_id']
        tags[REQUEST_BROKER_CONNECTION_ID] = request_broker_details['connection_id']
        tags[REQUEST_BROKER_CHANNEL_STATE] = request_broker_details['channel_state']
        tags[REQUEST_BROKER_LAST_STREAM_ID] = request_broker_details['last_status_code_stream_id']
        tags[REQUEST_BROKER_LAST_STATUS_CODE] = request_broker_details['last_status_code']
    notice_consumer_details = public_gateway_svc.get_notice_consumer_details()
    if notice_consumer_details.get('native_broker', True) is not None:
        tags[NOTICE_CONSUMER_STATE] = notice_consumer_details['consumer_state']
        tags[NOTICE_CONSUMER_STREAM_ID] = notice_consumer_details['stream_id']
        tags[NOTICE_CONSUMER_CONNECTION_ID] = notice_consumer_details['connection_id']
        tags[NOTICE_CONSUMER_CHANNEL_STATE] = notice_consumer_details['channel_state']
        tags[NOTICE_CONSUMER_LAST_STREAM_ID] = notice_consumer_details['last_status_code_stream_id']
        tags[NOTICE_CONSUMER_LAST_STATUS_CODE] = notice_consumer_details['last_status_code']
    return tags
