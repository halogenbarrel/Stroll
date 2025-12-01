"""
Unit tests for job_board forms.

Tests cover JobForm validation and saving.
"""

from django.test import TestCase
from userbase.models import Job, Owner, Doggy
from django.contrib.auth.models import User
from .forms import JobForm


class JobBoardFormsTests(TestCase):
    """Test suite for JobForm functionality."""

    def setUp(self):
        """Set up test data."""
        self.owner_user = User.objects.create_user(
            username='testowner', email='owner@test.com', password='testpass'
        )
        self.owner = Owner.objects.create(
            user=self.owner_user, address='123 Test St', phone_number='402-555-1234'
        )
        self.dog = Doggy.objects.create(
            dog_name='TestDog', breed='Mixed', temperament='FRIENDLY',
            energy_level='MEDIUM', weight=25.0, age=3, owner=self.owner
        )

    def test_job_form_valid(self):
        """Test JobForm accepts valid data."""
        form_data = {
            'title': 'Test Job',
            'description': 'Test job description',
            'dog': self.dog.pk,
            'scheduled_date': '2024-01-01',
            'scheduled_time': '10:00',
            'duration': '60',
            'location': 'Test Park',
            'recurrence': 'NONE',
        }
        form = JobForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_job_form_invalid(self):
        """Test JobForm rejects invalid data."""
        form_data = {'title': '', 'description': 'Test'}
        form = JobForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_job_form_save(self):
        """Test JobForm saves correctly."""
        form_data = {
            'title': 'Test Job',
            'description': 'Test description',
            'dog': self.dog.pk,
            'scheduled_date': '2024-01-01',
            'scheduled_time': '10:00',
            'duration': '60',
            'location': 'Test Park',
            'recurrence': 'NONE',
        }
        form = JobForm(data=form_data)
        self.assertTrue(form.is_valid())
        # Set owner before saving since it's required by the model
        job = form.save(commit=False)
        job.owner = self.owner
        job.save()
        self.assertEqual(job.title, 'Test Job')
        self.assertEqual(job.dog, self.dog)
        self.assertEqual(job.owner, self.owner)

    def test_job_form_user_filtering(self):
        """Test JobForm filters dog queryset based on user."""
        # Create another owner and dog
        other_owner_user = User.objects.create_user(
            username='otherowner', email='other@test.com', password='testpass'
        )
        other_owner = Owner.objects.create(
            user=other_owner_user, address='456 Other St', phone_number='402-555-5678'
        )
        other_dog = Doggy.objects.create(
            dog_name='OtherDog', breed='Labrador', temperament='FRIENDLY',
            energy_level='HIGH', weight=30.0, age=2, owner=other_owner
        )

        # Form without user should include all dogs
        form_all = JobForm()
        self.assertIn(self.dog, form_all.fields['dog'].queryset)
        self.assertIn(other_dog, form_all.fields['dog'].queryset)

        # Form with owner user should only show their dogs
        form_filtered = JobForm(user=self.owner_user)
        self.assertIn(self.dog, form_filtered.fields['dog'].queryset)
        self.assertNotIn(other_dog, form_filtered.fields['dog'].queryset)
