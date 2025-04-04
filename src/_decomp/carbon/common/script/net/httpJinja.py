#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\httpJinja.py
import cherrypy
import jinja2
import blue
import scriber
from carbon.common.script.net.httpSettings import TEMPLATES_DIR
scriber.init([blue.paths.ResolvePath('res:/scriber')])

def CherryPyApp():
    return cherrypy.request.app


def TemplateRender(template, **kwargs):
    context = {}
    context.update(kwargs)
    if cherrypy.request.app is not None:
        context.update({'request': cherrypy.request,
         'app_url': cherrypy.request.app.script_name})
    return scriber.scribe(template, **context)


class JinjaHandler(cherrypy.dispatch.LateParamPageHandler):

    def __init__(self, env, template_name, next_handler):
        self.env = env
        self.template_name = template_name
        self.next_handler = next_handler

    def __call__(self):
        context = {}
        try:
            r = self.next_handler()
            context.update(r)
        except ValueError as e:
            cherrypy.log('%s (handler for "%s" returned "%s")' % (e, self.template_name, repr(r)), traceback=True)

        context.update({'request': cherrypy.request,
         'app_url': cherrypy.request.app.script_name})
        return scriber.scribe(self.template_name, **context)


class JinjaLoader(object):

    def __init__(self):
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATES_DIR))

    def __call__(self, template):
        cherrypy.request.handler = JinjaHandler(self.env, template, cherrypy.request.handler)

    def add_filter(self, func):
        self.env.filters[func.__name__] = func
        return func

    def add_global(self, func):
        self.env.globals[func.__name__] = func
        return func


loader = JinjaLoader()
cherrypy.tools.jinja = cherrypy.Tool('before_handler', loader, priority=70)
