from django.core.mail import send_mail

from config.models import Config
from mystore.settings import EMAIL_SUBJECT_PREFIX, SERVER_EMAIL
from mystore.celery import app


@app.task
def send_contact_form(email, text):
    # todo: Why is the prefix ignored?
    send_mail(
        subject=EMAIL_SUBJECT_PREFIX + "Contact form",
        message=f"From: {email}\n{text}",
        from_email=SERVER_EMAIL,
        recipient_list=[Config.load().contact_form_email]
    )
