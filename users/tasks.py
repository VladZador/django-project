from django.conf import settings

from mystore.celery import app
from mystore.helpers import send_html_mail


@app.task
def send_confirmation_mail(email: str, context: dict):
    send_html_mail(
        subject_template_name='emails/registration/registration_confirm_subject.txt',  # noqa E501
        email_template_name='emails/registration/registration_confirm_email.html',  # noqa E501
        from_email=settings.SERVER_EMAIL,
        to_email=email,
        context=context,
    )


@app.task
def send_sms(phone: str, code: int):
    print(f"{phone}: {code}")
