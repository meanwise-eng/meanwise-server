import json
import urllib

from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string


class InviteMail(EmailMultiAlternatives):
    subject = _(' Invitation Code for SQUELO!')
    bcc = ['invites@squelo.com']
    reply_to = ['hello@squelo.com']
    sendgrid_categories = ["invite"]

    def __init__(self, to, data):
        data.update({'email': to})
        url = settings.SITE_URL + '/?action=signup&' + urllib.urlencode(data)
        html_content = render_to_string('mails/invite.html', {'url': url})
        text_content = strip_tags(html_content)
        smtpapi = {'category': self.sendgrid_categories, }
        headers = {'X-SMTPAPI': json.dumps(smtpapi)}
        super(InviteMail, self).__init__(self.subject,
                                         text_content, '', [to],
                                         headers=headers)
        self.attach_alternative(html_content, 'text/html')


class PasswordChangeMail(EmailMultiAlternatives):
    subject = _('Squelo: Change your password')
    bcc = ['password@squelo.com']
    reply_to = ['hello@squelo.com']
    sendgrid_categories = ["password-change"]

    def __init__(self, to, data):
        url = "%s?%s" % (settings.RESET_PASSWORD_URL, urllib.urlencode(data))
        html_content = render_to_string('mails/password_change_mail.html',
                                        {'url': url})
        text_content = strip_tags(html_content)
        smtpapi = {'category': self.sendgrid_categories}
        headers = {'X-SMTPAPI': json.dumps(smtpapi)}
        super(PasswordChangeMail, self).__init__(self.subject,
                                                 text_content, '',
                                                 [to], headers=headers)
        self.attach_alternative(html_content, 'text/html')


class WelcomeMail(EmailMultiAlternatives):
    subject = _('Welcome to SQUELO!')
    bcc = ['welcome@squelo.com']
    reply_to = ['hello@squelo.com']
    sendgrid_categories = ["welcome"]

    def __init__(self, to, data):
        html_content = render_to_string('mails/welcome.html', data)
        text_content = strip_tags(html_content)
        smtpapi = {'category': self.sendgrid_categories}
        headers = {'X-SMTPAPI': json.dumps(smtpapi)}
        super(WelcomeMail, self).__init__(self.subject, text_content,
                                          '', [to], headers=headers)
        self.attach_alternative(html_content, 'text/html')
