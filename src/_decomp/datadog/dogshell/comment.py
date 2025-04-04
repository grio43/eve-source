#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\dogshell\comment.py
import sys
from datadog import api
from datadog.dogshell.common import report_errors, report_warnings
from datadog.util.compat import json

class CommentClient(object):

    @classmethod
    def setup_parser(cls, subparsers):
        parser = subparsers.add_parser('comment', help='Post, update, and delete comments.')
        verb_parsers = parser.add_subparsers(title='Verbs', dest='verb')
        verb_parsers.required = True
        post_parser = verb_parsers.add_parser('post', help='Post comments.')
        post_parser.add_argument('--handle', help='handle to post as. if unset, posts as the owner of the application key used to authenticate')
        post_parser.add_argument('comment', help='comment message to post. if unset, reads from stdin.', nargs='?')
        post_parser.set_defaults(func=cls._post)
        update_parser = verb_parsers.add_parser('update', help='Update existing comments.')
        update_parser.add_argument('comment_id', help='comment to update (by id)')
        update_parser.add_argument('--handle', help='handle to post as. if unset, posts as the owner of the application key used to authenticate')
        update_parser.add_argument('comment', help='comment message to post. if unset, reads from stdin.', nargs='?')
        update_parser.set_defaults(func=cls._update)
        reply_parser = verb_parsers.add_parser('reply', help='Reply to existing comments.')
        reply_parser.add_argument('comment_id', help='comment to reply to (by id)')
        reply_parser.add_argument('--handle', help='handle to post as. if unset, posts as the owner of the application key used to authenticate')
        reply_parser.add_argument('comment', help='comment message to post. if unset, reads from stdin.', nargs='?')
        reply_parser.set_defaults(func=cls._reply)
        show_parser = verb_parsers.add_parser('show', help='Show comment details.')
        show_parser.add_argument('comment_id', help='comment to show')
        show_parser.set_defaults(func=cls._show)
        delete_parser = verb_parsers.add_parser('delete', help='Delete comments.')
        delete_parser.add_argument('comment_id', help='comment to delete (by id)')
        delete_parser.set_defaults(func=cls._delete)

    @classmethod
    def _post(cls, args):
        api._timeout = args.timeout
        handle = args.handle
        comment = args.comment
        format = args.format
        if comment is None:
            comment = sys.stdin.read()
        res = api.Comment.create(handle=handle, message=comment)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            message = res['comment']['message']
            lines = message.split('\n')
            message = '\n'.join([ '    ' + line for line in lines ])
            print 'id\t\t' + str(res['comment']['id'])
            print 'url\t\t' + res['comment']['url']
            print 'resource\t' + res['comment']['resource']
            print 'handle\t\t' + res['comment']['handle']
            print 'message\n' + message
        elif format == 'raw':
            print json.dumps(res)
        else:
            print 'id\t\t' + str(res['comment']['id'])
            print 'url\t\t' + res['comment']['url']
            print 'resource\t' + res['comment']['resource']
            print 'handle\t\t' + res['comment']['handle']
            print 'message\t\t' + res['comment']['message'].__repr__()

    @classmethod
    def _update(cls, args):
        handle = args.handle
        comment = args.comment
        id = args.comment_id
        format = args.format
        if comment is None:
            comment = sys.stdin.read()
        res = api.Comment.update(id, handle=handle, message=comment)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            message = res['comment']['message']
            lines = message.split('\n')
            message = '\n'.join([ '    ' + line for line in lines ])
            print 'id\t\t' + str(res['comment']['id'])
            print 'url\t\t' + res['comment']['url']
            print 'resource\t' + res['comment']['resource']
            print 'handle\t\t' + res['comment']['handle']
            print 'message\n' + message
        elif format == 'raw':
            print json.dumps(res)
        else:
            print 'id\t\t' + str(res['comment']['id'])
            print 'url\t\t' + res['comment']['url']
            print 'resource\t' + res['comment']['resource']
            print 'handle\t\t' + res['comment']['handle']
            print 'message\t\t' + res['comment']['message'].__repr__()

    @classmethod
    def _reply(cls, args):
        api._timeout = args.timeout
        handle = args.handle
        comment = args.comment
        id = args.comment_id
        format = args.format
        if comment is None:
            comment = sys.stdin.read()
        res = api.Comment.create(handle=handle, message=comment, related_event_id=id)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            message = res['comment']['message']
            lines = message.split('\n')
            message = '\n'.join([ '    ' + line for line in lines ])
            print 'id\t\t' + str(res['comment']['id'])
            print 'url\t\t' + res['comment']['url']
            print 'resource\t' + res['comment']['resource']
            print 'handle\t\t' + res['comment']['handle']
            print 'message\n' + message
        elif format == 'raw':
            print json.dumps(res)
        else:
            print 'id\t\t' + str(res['comment']['id'])
            print 'url\t\t' + res['comment']['url']
            print 'resource\t' + res['comment']['resource']
            print 'handle\t\t' + res['comment']['handle']
            print 'message\t\t' + res['comment']['message'].__repr__()

    @classmethod
    def _show(cls, args):
        api._timeout = args.timeout
        id = args.comment_id
        format = args.format
        res = api.Event.get(id)
        report_warnings(res)
        report_errors(res)
        if format == 'pretty':
            message = res['event']['text']
            lines = message.split('\n')
            message = '\n'.join([ '    ' + line for line in lines ])
            print 'id\t\t' + str(res['event']['id'])
            print 'url\t\t' + res['event']['url']
            print 'resource\t' + res['event']['resource']
            print 'message\n' + message
        elif format == 'raw':
            print json.dumps(res)
        else:
            print 'id\t\t' + str(res['event']['id'])
            print 'url\t\t' + res['event']['url']
            print 'resource\t' + res['event']['resource']
            print 'message\t\t' + res['event']['text'].__repr__()

    @classmethod
    def _delete(cls, args):
        api._timeout = args.timeout
        id = args.comment_id
        res = api.Comment.delete(id)
        if res is not None:
            report_warnings(res)
            report_errors(res)
