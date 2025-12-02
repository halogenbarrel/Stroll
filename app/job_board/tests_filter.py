"""
Unit tests for job_board filtering functionality.

Tests the walker job filtering toggle feature.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from userbase.models import Job, Owner, Walker, Doggy


class JobFilteringTests(TestCase):
    """Test suite for job filtering functionality."""

    def setUp(self):
        """Set up test data."""
        self.owner_user = User.objects.create_user(
            username='testowner', email='owner@test.com', password='testpass'
        )
        self.walker_user = User.objects.create_user(
            username='testwalker', email='walker@test.com', password='testpass'
        )

        self.owner = Owner.objects.create(
            user=self.owner_user, address='123 Test St', phone_number='402-555-1234'
        )
        self.walker = Walker.objects.create(
            user=self.walker_user, bio='I love walking dogs',
            temperament=['FRIENDLY'], energy_level=['MEDIUM'], weight_range=['21-50']
        )

        # Create dogs - one that matches walker preferences, one that doesn't
        self.matching_dog = Doggy.objects.create(
            dog_name='MatchingDog', breed='Labrador', temperament='FRIENDLY',
            energy_level='MEDIUM', weight=25.0, age=3, owner=self.owner
        )
        self.non_matching_dog = Doggy.objects.create(
            dog_name='NonMatchingDog', breed='Poodle', temperament='SHY',
            energy_level='HIGH', weight=15.0, age=5, owner=self.owner
        )

        # Create jobs
        self.matching_job = Job.objects.create(
            title='Matching Job', description='Matches preferences',
            owner=self.owner, dog=self.matching_dog, status='OPEN'
        )
        self.non_matching_job = Job.objects.create(
            title='Non-Matching Job', description='Does not match preferences',
            owner=self.owner, dog=self.non_matching_dog, status='OPEN'
        )

    def test_filtering_enabled_by_default(self):
        """Test that filtering is enabled by default for walkers."""
        self.client.login(username='testwalker', password='testpass')
        response = self.client.get(reverse('job_board:job_list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('filtering_disabled', response.context)
        self.assertFalse(response.context['filtering_disabled'])
        # Should only show matching jobs
        available_jobs = response.context['available_jobs']
        self.assertIn(self.matching_job, available_jobs)
        self.assertNotIn(self.non_matching_job, available_jobs)

    def test_filtering_disabled_via_url(self):
        """Test that filtering can be disabled via URL parameter."""
        self.client.login(username='testwalker', password='testpass')
        response = self.client.get(reverse('job_board:job_list') + '?filtering=disabled')

        self.assertEqual(response.status_code, 200)
        self.assertIn('filtering_disabled', response.context)
        self.assertTrue(response.context['filtering_disabled'])
        # Should show all jobs when filtering is disabled
        available_jobs = response.context['available_jobs']
        self.assertIn(self.matching_job, available_jobs)
        self.assertIn(self.non_matching_job, available_jobs)

    def test_filtering_toggle_button_text(self):
        """Test that the toggle button shows correct text in each state."""
        self.client.login(username='testwalker', password='testpass')

        # Test enabled state (default)
        response = self.client.get(reverse('job_board:job_list'))
        self.assertContains(response, 'Disable Filtering')
        self.assertNotContains(response, 'Enable Filtering')

        # Test disabled state
        response = self.client.get(reverse('job_board:job_list') + '?filtering=disabled')
        self.assertContains(response, 'Enable Filtering')
        self.assertNotContains(response, 'Disable Filtering')

    def test_filtering_status_text(self):
        """Test that status text is correct for each filtering state."""
        self.client.login(username='testwalker', password='testpass')

        # Test enabled state
        response = self.client.get(reverse('job_board:job_list'))
        self.assertContains(response, 'Showing jobs that match your preferences')

        # Test disabled state
        response = self.client.get(reverse('job_board:job_list') + '?filtering=disabled')
        self.assertContains(response, 'Filtering disabled - showing all available jobs')

    def test_filtering_unaffected_by_invalid_params(self):
        """Test that invalid filtering parameters default to enabled."""
        self.client.login(username='testwalker', password='testpass')

        # Test with invalid parameter
        response = self.client.get(reverse('job_board:job_list') + '?filtering=invalid')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['filtering_disabled'])
        # Should show only matching jobs
        available_jobs = response.context['available_jobs']
        self.assertIn(self.matching_job, available_jobs)
        self.assertNotIn(self.non_matching_job, available_jobs)
