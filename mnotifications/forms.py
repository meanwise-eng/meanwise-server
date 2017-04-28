from django import forms
 
class AddTopicForm(forms.Form):
    topic = forms.CharField(max_length=256)
