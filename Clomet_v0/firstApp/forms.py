from django import forms

class UrlForm(forms.Form):
    urldata = forms.CharField(label='urldata', max_length=100, required=True)

class UploadForm(forms.Form):
    localdata = forms.FileField(label='local')
