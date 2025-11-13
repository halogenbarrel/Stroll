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

    WEIGHT_CHOICES = [
        ("0-20", "Small"),
        ("21-50", "Medium"),
        ("51-100", "Large"),
        ("100+", "X-Large"),
    ]

    temperament = forms.MultipleChoiceField(
        choices=TEMPERAMENT_CHOICES, widget=forms.CheckboxSelectMultiple,
        required=False # temporary fix
    )
    energy_level = forms.MultipleChoiceField(
        choices=ENERGY_LEVEL_CHOICES, widget=forms.CheckboxSelectMultiple,
        required=False # temporary fix
    )
    weight_level = forms.MultipleChoiceField(
        choices=WEIGHT_CHOICES, widget=forms.CheckboxSelectMultiple,
        required=False # temporary fix
    )

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
            "weight_level",
        )

    def clean(self):
        cleaned_data = super().clean()
        is_walker = cleaned_data.get("is_walker")
        is_owner = cleaned_data.get("is_owner")

        if not is_walker and not is_owner:
            raise forms.ValidationError(
                "You must select at least one role (Walker or Owner)"
            )

        # if walker, make walker fields required
        if is_walker:
            for field in ("temperament", "energy_level", "weight_level"):
                if not cleaned_data.get(field):
                    self.add_error(field, "This field is required for walkers.")

        # if owner, make owner fields required
        if is_owner:
            for field in ("address", "phone_number"):
                if not cleaned_data.get(field):
                    self.add_error(field, "This field is required for owners.")

        return cleaned_data
