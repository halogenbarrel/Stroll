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
            'owner': self.owner.pk,
            'dog': self.dog.pk,
            'location': 'Test Park',
            'scheduled_date': '2024-01-01',
            'scheduled_time': '10:00',
            'recurrence': 'NONE',
            'duration': 60,
            'price': 30.0,
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
            'owner': self.owner.pk,
            'dog': self.dog.pk,
            'location': 'Test Park',
            'scheduled_date': '2024-01-01',
            'scheduled_time': '10:00',
            'recurrence': 'NONE',
            'duration': 60,
            'price': 30.0,
        }
        form = JobForm(data=form_data)
        self.assertTrue(form.is_valid())
        job = form.save()
        self.assertEqual(job.title, 'Test Job')
        self.assertEqual(job.owner, self.owner)
