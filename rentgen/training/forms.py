from django import forms

class ImageUploadForm(forms.Form):
    image_file = forms.FileField(label='File for recognition')
    # image_file1 = forms.FileField(label='File for recognition')

class EditAndCheckForm(forms.Form):
    text_input = forms.CharField(label='Edit Field', max_length=100, required=False)
    checkbox = forms.BooleanField(label='Human recognition', required=False)
    unrecognizable = forms.BooleanField(label='Unrecognizable', required=False)