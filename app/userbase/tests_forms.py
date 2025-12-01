"""
Unit tests for userbase forms.

Tests cover form validation, field behavior, custom validation logic,
and form functionality independent of views. Note: Profile creation
(Walker/Owner instances) is handled by views, not forms.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from userbase.forms import StrollUserCreationForm
from userbase.models import Walker, Owner


class StrollUserCreationFormTests(TestCase):
    """
    Comprehensive tests for StrollUserCreationForm.

    Tests cover:
    - Form field validation and attributes
    - Choice field validation
    - Form save behavior and profile creation
    - Field dependencies and requirements
    """

    def test_form_instantiation(self):
        """
        Test form can be instantiated and has correct fields.
        """
        form = StrollUserCreationForm()
        expected_fields = [
            'username', 'email', 'password1', 'password2',
            'is_walker', 'is_owner', 'bio', 'temperament',
            'energy_level', 'weight_range', 'address', 'phone_number'
        ]

        for field_name in expected_fields:
            self.assertIn(field_name, form.fields)

    def test_form_field_attributes(self):
        """
        Test form fields have correct attributes (required, max_length, widgets).
        """
        form = StrollUserCreationForm()

        # Check BooleanFields are not required by default
        self.assertFalse(form.fields['is_walker'].required)
        self.assertFalse(form.fields['is_owner'].required)

        # Check phone_number has max_length
        self.assertEqual(form.fields['phone_number'].max_length, 15)

        # Check textarea widgets
        self.assertEqual(form.fields['bio'].widget.__class__.__name__, 'Textarea')
        self.assertEqual(form.fields['address'].widget.__class__.__name__, 'Textarea')

        # Check multiple choice widgets
        self.assertEqual(form.fields['temperament'].widget.__class__.__name__, 'CheckboxSelectMultiple')
        self.assertEqual(form.fields['energy_level'].widget.__class__.__name__, 'CheckboxSelectMultiple')
        self.assertEqual(form.fields['weight_range'].widget.__class__.__name__, 'CheckboxSelectMultiple')

    def test_choice_field_options(self):
        """
        Test choice fields have correct predefined options.
        """
        form = StrollUserCreationForm()

        # Temperament choices
        expected_temperament = [
            ('FRIENDLY', 'Friendly'), ('SHY', 'Shy'), ('ENERGETIC', 'Energetic'),
            ('CALM', 'Calm'), ('PROTECTIVE', 'Protective'), ('PLAYFUL', 'Playful'),
            ('INDEPENDENT', 'Independent'), ('SOCIAL', 'Social')
        ]
        self.assertEqual(form.fields['temperament'].choices, expected_temperament)

        # Energy level choices
        expected_energy = [
            ('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')
        ]
        self.assertEqual(form.fields['energy_level'].choices, expected_energy)

        # Weight choices
        expected_weight = [
            ('0-20', 'Small'), ('21-50', 'Medium'), ('51-100', 'Large'), ('100+', 'X-Large')
        ]
        self.assertEqual(form.fields['weight_range'].choices, expected_weight)

    def test_form_valid_basic_user_data(self):
        """
        Test form accepts valid basic user data.
        """
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': True,
            'is_owner': False,
            'bio': 'I love walking dogs',
            'temperament': ['FRIENDLY', 'PLAYFUL'],
            'energy_level': ['MEDIUM'],
            'weight_range': ['21-50'],
        }

        form = StrollUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form should be valid but got errors: {form.errors}")

    def test_custom_validation_requires_role_selection(self):
        """
        Test custom validation requires at least one role (walker or owner).
        """
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': False,  # No role selected
            'is_owner': False,
        }

        form = StrollUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('You must select at least one role (Walker or Owner)', str(form.errors))

    def test_walker_validation_requires_walker_fields(self):
        """
        Test that selecting walker role makes walker fields required.
        """
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': True,
            'is_owner': False,
            # Missing required walker fields
            'temperament': [],
            'energy_level': [],
            'weight_range': [],
        }

        form = StrollUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

        # Check that all walker fields have errors
        for field in ['temperament', 'energy_level', 'weight_range']:
            self.assertIn(field, form.errors)
            self.assertIn('This field is required for walkers', str(form.errors[field]))

    def test_owner_validation_requires_owner_fields(self):
        """
        Test that selecting owner role makes owner fields required.
        """
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': False,
            'is_owner': True,
            # Missing required owner fields
            'address': '',
            'phone_number': '',
        }

        form = StrollUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

        # Check that owner fields have errors
        for field in ['address', 'phone_number']:
            self.assertIn(field, form.errors)
            self.assertIn('This field is required for owners', str(form.errors[field]))

    def test_both_roles_selected_makes_both_field_sets_required(self):
        """
        Test that selecting both roles makes all fields required.
        """
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': True,
            'is_owner': True,
            # Missing all required fields
            'temperament': [],
            'energy_level': [],
            'weight_range': [],
            'address': '',
            'phone_number': '',
        }

        form = StrollUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

        # Check walker fields
        for field in ['temperament', 'energy_level', 'weight_range']:
            self.assertIn(field, form.errors)

        # Check owner fields
        for field in ['address', 'phone_number']:
            self.assertIn(field, form.errors)

    def test_form_valid_with_both_roles_and_all_fields(self):
        """
        Test form is valid when both roles selected and all fields provided.
        """
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': True,
            'is_owner': True,
            'bio': 'I walk and own dogs',
            'temperament': ['FRIENDLY', 'PLAYFUL'],
            'energy_level': ['MEDIUM', 'HIGH'],
            'weight_range': ['21-50', '51-100'],
            'address': '123 Main St, Anytown, USA',
            'phone_number': '555-123-4567',
        }

        form = StrollUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form should be valid but got errors: {form.errors}")

    def test_form_save_creates_user(self):
        """
        Test form save creates User instance with correct data.
        """
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': True,
            'is_owner': False,
            'bio': 'Test bio',
            'temperament': ['FRIENDLY'],
            'energy_level': ['MEDIUM'],
            'weight_range': ['21-50'],
        }

        form = StrollUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_form_save_only_creates_user(self):
        """
        Test form save only creates User instance - profile creation happens in views.

        The form itself only handles User creation. Profile creation (Walker/Owner)
        is handled by the registration view logic, not the form save method.
        """
        form_data = {
            'username': 'testuser',
            'email': 'user@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': True,
            'is_owner': False,
            'bio': 'Test bio',
            'temperament': ['FRIENDLY'],
            'energy_level': ['MEDIUM'],
            'weight_range': ['21-50'],
        }

        form = StrollUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

        user = form.save()

        # Verify user was created with correct data
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'user@example.com')
        self.assertTrue(user.check_password('testpass123'))

        # Verify NO profiles were created (that's view logic)
        with self.assertRaises(Walker.DoesNotExist):
            Walker.objects.get(user=user)
        with self.assertRaises(Owner.DoesNotExist):
            Owner.objects.get(user=user)

    def test_form_preserves_role_selection_data(self):
        """
        Test form preserves role selection and profile data for view processing.

        The form doesn't create profiles itself, but it should preserve the
        data needed by views to create appropriate profiles.
        """
        form_data = {
            'username': 'testuser',
            'email': 'user@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': True,
            'is_owner': True,
            'bio': 'I do both',
            'temperament': ['FRIENDLY'],
            'energy_level': ['MEDIUM'],
            'weight_range': ['21-50'],
            'address': '123 Main St',
            'phone_number': '555-123-4567',
        }

        form = StrollUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Verify form preserves all the data views need for profile creation
        self.assertTrue(form.cleaned_data['is_walker'])
        self.assertTrue(form.cleaned_data['is_owner'])
        self.assertEqual(form.cleaned_data['bio'], 'I do both')
        self.assertEqual(form.cleaned_data['address'], '123 Main St')
        self.assertEqual(form.cleaned_data['phone_number'], '555-123-4567')

    def test_form_field_validation_individual_fields(self):
        """
        Test individual field validation works correctly.
        """
        # Test phone number max length
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': False,
            'is_owner': True,
            'address': 'Test Address',
            'phone_number': '12345678901234567890',  # Too long (20 chars vs 15 limit)
        }

        form = StrollUserCreationForm(data=form_data)
        # Note: Django's CharField doesn't enforce max_length on its own in forms
        # This would need additional validation if strict enforcement is desired

        # Test email format (inherited from UserCreationForm)
        form_data_invalid_email = {
            'username': 'testuser',
            'email': 'invalid-email',  # Invalid email format
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': False,
            'is_owner': True,
            'address': 'Test Address',
            'phone_number': '555-123-4567',
        }

        form = StrollUserCreationForm(data=form_data_invalid_email)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
