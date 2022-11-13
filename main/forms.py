from django.forms import Form, EmailField, CharField, Textarea


class ContactForm(Form):
    email = EmailField()
    text = CharField(widget=Textarea)
