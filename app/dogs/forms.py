from django import forms
from userbase.models import Doggy
from .models import Temperament

class DoggyForm(forms.ModelForm):
    class Meta:
        model = Doggy
        
        fields = ['dog_name', 'age', 'weight', 'photo', 'breed', 'temperaments']
        widgets = {
            'temperaments': forms.CheckboxSelectMultiple()
        }

