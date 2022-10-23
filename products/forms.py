from django import forms


class CsvImportForm(forms.Form):
    csv_import = forms.FileField()
