"""
Unit tests for dogs forms.

Tests cover DoggyForm validation and saving.
"""

from django.test import TestCase
from userbase.models import Doggy, Owner
from django.contrib.auth.models import User
from .forms import DoggyForm


class DogsFormsTests(TestCase):
    """Test suite for DoggyForm functionality."""

    def setUp(self):
        """Set up test data."""
        self.owner_user = User.objects.create_user(
            username='testowner', email='owner@test.com', password='testpass'
        )
        self.owner = Owner.objects.create(
            user=self.owner_user, address='123 Test St', phone_number='555-1234'
        )

    def test_doggy_form_valid(self):
        """Test DoggyForm accepts valid data."""
        form_data = {
            'dog_name': 'Buddy',
            'breed': 'Golden Retriever',
            'weight': 65.5,
            'age': 3,
            'temperament': 'FRIENDLY',
            'energy_level': 'HIGH',
        }
        form = DoggyForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_doggy_form_invalid(self):
        """Test DoggyForm rejects invalid data."""
        form_data = {'dog_name': '', 'breed': 'Test'}
        form = DoggyForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_doggy_form_save(self):
        """Test DoggyForm saves correctly."""
        form_data = {
            'dog_name': 'Max',
            'breed': 'Labrador',
            'weight': 70.0,
            'age': 5,
            'temperament': 'FRIENDLY',
            'energy_level': 'MEDIUM',
        }
        form = DoggyForm(data=form_data)
        self.assertTrue(form.is_valid())
        dog = form.save(commit=False)
        dog.owner = self.owner
        dog.save()
        self.assertEqual(dog.dog_name, 'Max')
        self.assertEqual(dog.owner, self.owner)
