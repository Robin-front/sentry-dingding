# coding: utf-8

import json

import requests
from sentry.plugins.bases.notify import NotificationPlugin

import sentry_dingding
from .forms import DingDingOptionsForm

DingTalk_API = "https://oapi.dingtalk.com/robot/send?access_token={token}"


class DingDingPlugin(NotificationPlugin):
    """
    Sentry plugin to send error counts to DingDing.
    """
    author = 'robin'
    author_url = 'https://github.com/Robin-front/sentry-dingding'
    version = sentry_dingding.VERSION
    description = 'Send error counts to DingDing.'
    resource_links = [
        ('Source', 'https://github.com/Robin-front/sentry-dingding'),
        ('Bug Tracker', 'https://github.com/Robin-front/sentry-dingding/issues'),
        ('README', 'https://github.com/Robin-front/sentry-dingding/blob/master/README.md'),
    ]

    slug = 'DingDing'
    title = 'DingDing'
    conf_key = slug
    conf_title = title
    project_conf_form = DingDingOptionsForm

    def is_configured(self, project):
        """
        Check if plugin is configured.
        """
        return bool(self.get_option('access_token', project))

    def notify_users(self, group, event, *args, **kwargs):
        if self.should_notify(group, event):
            self.post_process(group, event, *args, **kwargs)
        else:
            return None
        

    def post_process(self, group, event, *args, **kwargs):
        """
        Process error.
        """
        if not self.is_configured(group.project):
            return

        if group.is_ignored():
            return

        access_token = self.get_option('access_token', group.project)
        allow_environment = self.get_option('allow_environment', group.project)
        if bool(allow_environment):
            allow_environments = allow_environment.split(',')
        else:
            allow_environments = []
            
        at_mobile = self.get_option('at_mobiles', group.project)
        if bool(at_mobile):
            at_mobiles = at_mobile.split(',')
        else:
            at_mobiles = []
        
        send_url = DingTalk_API.format(token=access_token)
        at_text = ''
        for phone in at_mobiles:
            if len(phone) > 0:
                at_text += u'@{} '.format(phone)

        title = u"来自 [{}][{}] 的异常上报".format(event.project.slug, event.get_environment().name)

        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": u"#### {title} {at_text} \n > {message} \n\n > [更多详细信息]({url}) \n\n ".format(
                    title=title,
                    message=event.title or event.data.message,
                    url=u"{}events/{}/".format(group.get_absolute_url(), event.event_id),
                    at_text=at_text
                )
            },
            "at": {
                "atMobiles": at_mobiles, 
                "isAtAll": False
            }
        }

        if not bool(len(allow_environments)) or event.get_environment().name in allow_environments:
            requests.post(
                url=send_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(data).encode("utf-8")
            )
