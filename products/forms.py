from django.forms import Form, FileField


class CsvImportForm(Form):
    csv_import = FileField()
