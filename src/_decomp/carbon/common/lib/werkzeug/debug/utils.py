#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\werkzeug\debug\utils.py
from os.path import join, dirname
from werkzeug.templates import Template

def get_template(filename):
    return Template.from_file(join(dirname(__file__), 'templates', filename))


def render_template(template_filename, **context):
    return get_template(template_filename).render(**context)
