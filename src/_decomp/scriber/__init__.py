#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\scriber\__init__.py
__version__ = (1, 3, 0, 0)
import types
import os
import sys
import traceback
import json
import jinja2
from jinja2 import exceptions
from scriber import filters
from scriber import utils
from scriber.const import *
import logging
log = logging.getLogger(__name__)
local_mode = False

class _SingletonEnvironment(object):
    jinja_environment = None

    @classmethod
    def get_environment(cls):
        if not _SingletonEnvironment.jinja_environment:
            raise RuntimeError('Scriber has not been initialized yet!')
        return _SingletonEnvironment.jinja_environment

    @classmethod
    def init(cls, template_dir_list = '', force_reload = False):
        log.debug('scriber::_SingletonEnvironment.init()')
        if not _SingletonEnvironment.jinja_environment or force_reload:
            if not isinstance(template_dir_list, list):
                template_dir_list = list(template_dir_list)
            _SingletonEnvironment.jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir_list), undefined=utils.ScriberUndefined)
            _load_filters()


def init(template_dir_list = '', force_reload = False):
    _SingletonEnvironment.init(template_dir_list, force_reload)


def get_environment():
    return _SingletonEnvironment.get_environment()


def _load_filters():
    for name, item in filters.__dict__.iteritems():
        if isinstance(item, types.FunctionType):
            filter_name = utils.get_filter_name(item)
            _SingletonEnvironment.jinja_environment.filters[filter_name] = item


def scribe_json(**kwargs):
    return json.dumps(kwargs)


def scribe_compact_json(**kwargs):
    return json.dumps(kwargs, separators=(',', ':'))


def scribe(template, *args, **kwargs):
    try:
        template = get_environment().get_template(template)
        return template.render(*args, **kwargs)
    except jinja2.TemplateNotFound as ex:
        log.exception('Template not found - template=%s' % template)
        log.error('Templates: %s' % get_environment().list_templates())


def scribe_str(template_str, *args, **kwargs):
    template = get_environment().from_string(template_str)
    return template.render(*args, **kwargs)


def template_exists(template):
    if template.startswith('/'):
        template = template[1:]
    return template in get_environment().list_templates()


def error(message, details = ''):
    if details:
        if isinstance(details, BaseException):
            details = traceback.format_exc()
        elif not isinstance(details, basestring):
            details = '%r' % details
    return scribe('/pages/error.html', message=message, details=details)
