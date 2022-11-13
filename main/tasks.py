from django.core.mail import send_mail

from config.models import Config
from mystore import settings
from mystore.celery import app


@app.task
def send_contact_form(email, text):
    send_mail(
        subject="Contact form",
        message=f"From: {email}\n{text}",
        from_email=settings.SERVER_EMAIL,
        recipient_list=[Config.load()]
    )
