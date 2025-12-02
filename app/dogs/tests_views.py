"""
Unit tests for dogs views.

Tests cover basic dog functionality.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from userbase.models import Doggy, Owner
from .forms import DoggyForm


class DogsViewsTests(TestCase):
    """Test suite for dogs views."""

    def setUp(self):
        """Set up test data."""
        self.owner_user = User.objects.create_user(
            username='testowner', email='owner@test.com', password='testpass'
        )
        self.regular_user = User.objects.create_user(
            username='regular', email='regular@test.com', password='testpass'
        )

        self.owner = Owner.objects.create(
            user=self.owner_user, address='123 Test St', phone_number='555-1234'
        )

        self.dog = Doggy.objects.create(
            dog_name='TestDog', breed='Mixed', temperament='FRIENDLY',
            energy_level='MEDIUM', weight=25.0, age=3, owner=self.owner
        )

    def test_dog_list_requires_login(self):
        """Test dog list requires authentication."""
        response = self.client.get(reverse('dog_list'))
        self.assertEqual(response.status_code, 302)

    def test_dog_list_non_owner(self):
        """Test non-owner sees empty list."""
        self.client.login(username='regular', password='testpass')
        response = self.client.get(reverse('dog_list'))
        self.assertEqual(response.status_code, 200)

    def test_create_dog_requires_login(self):
        """Test create dog requires authentication."""
        response = self.client.get(reverse('create_dog'))
        self.assertEqual(response.status_code, 302)

    def test_create_dog_get(self):
        """Test create dog form displays."""
        self.client.login(username='testowner', password='testpass')
        response = self.client.get(reverse('create_dog'))
        self.assertEqual(response.status_code, 200)

    def test_create_dog_post_valid(self):
        """Test creating a dog with valid data."""
        self.client.login(username='testowner', password='testpass')
        data = {
            'dog_name': 'NewDog',
            'breed': 'Poodle',
            'weight': 15.0,
            'age': 2,
            'temperament': 'PLAYFUL',
            'energy_level': 'HIGH',
        }
        response = self.client.post(reverse('create_dog'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Doggy.objects.filter(dog_name='NewDog').exists())

    def test_create_dog_post_invalid(self):
        """Test creating a dog with invalid data."""
        self.client.login(username='testowner', password='testpass')
        data = {'dog_name': '', 'breed': 'Test'}
        response = self.client.post(reverse('create_dog'), data=data)
        self.assertEqual(response.status_code, 200)

    def test_edit_dog_requires_login(self):
        """Test edit dog requires authentication."""
        response = self.client.get(reverse('edit_dog', args=[self.dog.pk]))
        self.assertEqual(response.status_code, 302)

    def test_edit_dog_success(self):
        """Test editing a dog successfully."""
        self.client.login(username='testowner', password='testpass')
        data = {
            'dog_name': 'UpdatedDog',
            'breed': 'UpdatedBreed',
            'weight': 30.0,
            'age': 4,
            'temperament': 'CALM',
            'energy_level': 'LOW',
        }
        response = self.client.post(reverse('edit_dog', args=[self.dog.pk]), data=data)
        self.assertEqual(response.status_code, 302)
        self.dog.refresh_from_db()
        self.assertEqual(self.dog.dog_name, 'UpdatedDog')

