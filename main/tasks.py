from django.core.mail import mail_managers

from mystore.celery import app


@app.task
def send_contact_form(email, text):
    mail_managers(
        subject="Contact form",
        message=f"From: {email}\n{text}"
    )
