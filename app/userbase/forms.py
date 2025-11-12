from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Walker, Owner


class StrollUserCreationForm(UserCreationForm):
    is_walker = forms.BooleanField(required=False, label="Register as Walker")
    is_owner = forms.BooleanField(required=False, label="Register as Owner")

    # Walker fields
    bio = forms.CharField(widget=forms.Textarea, required=False)
    TEMPERAMENT_CHOICES = [
        ("FRIENDLY", "Friendly"),
        ("SHY", "Shy"),
        ("ENERGETIC", "Energetic"),
        ("CALM", "Calm"),
        ("PROTECTIVE", "Protective"),
        ("PLAYFUL", "Playful"),
        ("INDEPENDENT", "Independent"),
        ("SOCIAL", "Social"),
    ]

    ENERGY_LEVEL_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]

    temperament = forms.ChoiceField(choices=TEMPERAMENT_CHOICES)
    energy_level = forms.ChoiceField(choices=ENERGY_LEVEL_CHOICES)

    # Owner fields
    address = forms.CharField(widget=forms.Textarea, required=False)
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "is_walker",
            "is_owner",
            "bio",
            "address",
            "phone_number",
            "energy_level",
            "temperament",
        )

    def clean(self):
        cleaned_data = super().clean()
        is_walker = cleaned_data.get("is_walker")
        is_owner = cleaned_data.get("is_owner")

        if not is_walker and not is_owner:
            raise forms.ValidationError(
                "You must select at least one role (Walker or Owner)"
            )

        return cleaned_data
