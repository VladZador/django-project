import re
from django import forms

from .models import Feedback


class FeedbackModelForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ("text", "user", "rating")

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['user'].initial = user.id

    def clean_text(self) -> str:
        """
        Cleans text field. Only alphanumeric characters along with some
        punctuation characters are left
        :return: string with cleaned text
        """
        return re.sub("[^A-Za-z0-9-,.'\"!? ]", "", self.cleaned_data["text"])

    def save(self, commit=True):
        super().save()
        self.instance.delete_cache()
