from django import forms
from userbase.models import Doggy

class DoggyForm(forms.ModelForm):
    class Meta:
        model = Doggy
        fields = ['dog_name', 'breed', 'weight', 'age', 'temperament', 'photo']
        help_texts = {
            'weight': 'Enter weight in pounds (lbs).',
            'photo': 'Upload a photo of your dog (optional).',
        }