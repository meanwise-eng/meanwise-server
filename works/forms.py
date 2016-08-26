from django import forms

from .models import Work, Workitem


class WorkForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Work
        exclude = []


class WorkItemForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Workitem
        exclude = []


class WorkCoverPictureUploadForm(forms.Form):
    picture = forms.ImageField()
