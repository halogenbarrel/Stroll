from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
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
        choices=TEMPERAMENT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,  # temporary fix
    )
    energy_level = forms.MultipleChoiceField(
        choices=ENERGY_LEVEL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,  # temporary fix
    )
    weight_range = forms.MultipleChoiceField(
        choices=WEIGHT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,  # temporary fix
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
            "weight_range",
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
            for field in ("temperament", "energy_level", "weight_range"):
                if not cleaned_data.get(field):
                    self.add_error(field, "This field is required for walkers.")

        # if owner, make owner fields required
        if is_owner:
            for field in ("address", "phone_number"):
                if not cleaned_data.get(field):
                    self.add_error(field, "This field is required for owners.")

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    """
    Form for editing user profiles. Allows updating user information
    and associated walker/owner profiles without requiring password changes.
    """
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
        choices=TEMPERAMENT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    energy_level = forms.MultipleChoiceField(
        choices=ENERGY_LEVEL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    weight_range = forms.MultipleChoiceField(
        choices=WEIGHT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    # Owner fields
    address = forms.CharField(widget=forms.Textarea, required=False)
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "is_walker",
            "is_owner",
            "bio",
            "address",
            "phone_number",
            "energy_level",
            "temperament",
            "weight_range",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Populate form with existing profile data
            try:
                walker = self.instance.walker_profile
                self.fields['is_walker'].initial = True
                self.fields['bio'].initial = walker.bio
                self.fields['temperament'].initial = walker.temperament
                self.fields['energy_level'].initial = walker.energy_level
                self.fields['weight_range'].initial = walker.weight_range
            except Walker.DoesNotExist:
                self.fields['is_walker'].initial = False

            try:
                owner = self.instance.owner_profile
                self.fields['is_owner'].initial = True
                self.fields['address'].initial = owner.address
                self.fields['phone_number'].initial = owner.phone_number
            except Owner.DoesNotExist:
                self.fields['is_owner'].initial = False

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        is_walker = cleaned_data.get("is_walker")
        is_owner = cleaned_data.get("is_owner")

        # For profile editing, roles are optional (unlike registration)
        # But if a role is selected, make sure required fields are filled
        if is_walker:
            for field in ("temperament", "energy_level", "weight_range"):
                if not cleaned_data.get(field):
                    self.add_error(field, "This field is required for walkers.")

        if is_owner:
            for field in ("address", "phone_number"):
                if not cleaned_data.get(field):
                    self.add_error(field, "This field is required for owners.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()

            # Handle walker profile
            is_walker = self.cleaned_data.get('is_walker', False)
            if is_walker:
                # Create or update walker profile
                walker, created = Walker.objects.get_or_create(
                    user=user,
                    defaults={
                        'bio': self.cleaned_data.get('bio'),
                        'temperament': self.cleaned_data.get('temperament', []),
                        'energy_level': self.cleaned_data.get('energy_level', []),
                        'weight_range': self.cleaned_data.get('weight_range', []),
                    }
                )
                if not created:
                    walker.bio = self.cleaned_data.get('bio')
                    walker.temperament = self.cleaned_data.get('temperament', [])
                    walker.energy_level = self.cleaned_data.get('energy_level', [])
                    walker.weight_range = self.cleaned_data.get('weight_range', [])
                    walker.save()

                # Add walker permissions
                from django.contrib.auth.models import Permission
                perms = Permission.objects.filter(
                    codename__in=["can_accept_jobs", "can_complete_jobs"]
                )
                user.user_permissions.add(*perms)
            else:
                # Remove walker profile if it exists and walker role is unchecked
                try:
                    walker = user.walker_profile
                    walker.delete()
                    # Remove walker permissions
                    from django.contrib.auth.models import Permission
                    perms = Permission.objects.filter(
                        codename__in=["can_accept_jobs", "can_complete_jobs"]
                    )
                    user.user_permissions.remove(*perms)
                except Walker.DoesNotExist:
                    pass

            # Handle owner profile
            is_owner = self.cleaned_data.get('is_owner', False)
            if is_owner:
                # Create or update owner profile
                owner, created = Owner.objects.get_or_create(
                    user=user,
                    defaults={
                        'address': self.cleaned_data.get('address'),
                        'phone_number': self.cleaned_data.get('phone_number'),
                    }
                )
                if not created:
                    owner.address = self.cleaned_data.get('address')
                    owner.phone_number = self.cleaned_data.get('phone_number')
                    owner.save()

                # Add owner permissions
                from django.contrib.auth.models import Permission
                perms = Permission.objects.filter(
                    codename__in=["can_create_jobs", "can_manage_dogs"]
                )
                user.user_permissions.add(*perms)
            else:
                # Remove owner profile if it exists and owner role is unchecked
                try:
                    owner = user.owner_profile
                    owner.delete()
                    # Remove owner permissions
                    from django.contrib.auth.models import Permission
                    perms = Permission.objects.filter(
                        codename__in=["can_create_jobs", "can_manage_dogs"]
                    )
                    user.user_permissions.remove(*perms)
                except Owner.DoesNotExist:
                    pass

        return user
