from django import forms
from userbase.models import Doggy


class DoggyForm(forms.ModelForm):
    class Meta:
        model = Doggy

        fields = ["dog_name", "age", "weight", "photo", "breed", "temper"]
        widgets = {"temper": forms.RadioSelect()}
