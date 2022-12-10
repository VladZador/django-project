from django.core.mail import send_mail
from django.conf import settings

from config.models import Config
from mystore.celery import app


@app.task
def send_contact_form(email: str, text: str):
    send_mail(
        subject=settings.EMAIL_SUBJECT_PREFIX + "Contact form",
        message=f"From: {email}\n{text}",
        from_email=settings.SERVER_EMAIL,
        recipient_list=[Config.load().contact_form_email]
    )
