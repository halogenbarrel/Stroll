from django import forms
from userbase.models import Doggy

class DoggyForm(forms.ModelForm):
    class Meta:
        model = Doggy
        exclude = ['owner']
