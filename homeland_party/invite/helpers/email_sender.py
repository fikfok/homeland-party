import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

from homeland_party.const import SENDER_EMAIL, SMTP_SERVER, SMTP_PORT, SENDER_PASSWORD
from invite.models import Invite


class EmailSender:
    """
    Отправляет email с приглашением
    """
    def __init__(self, email: str, request):
        self.receiver_email = email
        self.request = request
        self.author = request.user

    def send_email(self):
        invite = Invite.objects.create(author=self.author, email=self.receiver_email)
        url = self.request.build_absolute_uri(
            reverse('invite:activate_invite', kwargs={'invite_code': str(invite.code)})
        )

        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = self.receiver_email
        msg['Subject'] = "Приглашение"

        template_context = {
            'home_url': self.request.build_absolute_uri(reverse('home')),
            'url': url,
            'author': self.author,
            'url_lifetime_period_hours': int(Invite.EXPIRE_PERIOD_HOURS.total_seconds()/3600)
        }

        msg_html = render_to_string('invite_email_template.html', context=template_context)
        msg_plain = strip_tags(msg_html)

        part1 = MIMEText(msg_html, 'html')
        part2 = MIMEText(msg_plain, 'plain')

        msg.attach(part2)
        msg.attach(part1)

        smtp_context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=smtp_context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, self.receiver_email, msg.as_string())
