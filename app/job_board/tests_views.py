"""
Unit tests for job_board views.

Tests cover basic job functionality.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from userbase.models import Job, Owner, Walker, Doggy
from .forms import JobForm


class JobBoardViewsTests(TestCase):
    """Test suite for job_board views."""

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

        self.dog = Doggy.objects.create(
            dog_name='TestDog', breed='Mixed', temperament='FRIENDLY',
            energy_level='MEDIUM', weight=30.0, age=3, owner=self.owner
        )

        self.job = Job.objects.create(
            title='Test Job', description='Test description',
            owner=self.owner, dog=self.dog, status='OPEN'
        )

    def test_job_list_requires_login(self):
        """Test job list requires authentication."""
        response = self.client.get(reverse('job_board:job_list'))
        self.assertEqual(response.status_code, 302)

    def test_job_list_owner(self):
        """Test owner can see their jobs."""
        self.client.login(username='testowner', password='testpass')
        response = self.client.get(reverse('job_board:job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('owner_jobs', response.context)

    def test_job_list_walker(self):
        """Test walker can see available jobs."""
        self.client.login(username='testwalker', password='testpass')
        response = self.client.get(reverse('job_board:job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['role'], 'walker')

    def test_job_detail_owner_access(self):
        """Test owner can access their job details."""
        self.client.login(username='testowner', password='testpass')
        response = self.client.get(reverse('job_board:job_detail', args=[self.job.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['job'], self.job)

    def test_job_detail_walker_access_open_job(self):
        """Test walker can access open job details."""
        self.client.login(username='testwalker', password='testpass')
        response = self.client.get(reverse('job_board:job_detail', args=[self.job.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['job'], self.job)

    def test_job_detail_unauthorized_access(self):
        """Test unauthorized users cannot access job details."""
        # Create a different owner and job
        other_owner_user = User.objects.create_user(
            username='otherowner', email='other@test.com', password='testpass'
        )
        other_owner = Owner.objects.create(
            user=other_owner_user, address='456 Other St', phone_number='402-555-9999'
        )
        other_job = Job.objects.create(
            title='Other Job', description='Other description',
            owner=other_owner, dog=self.dog, status='OPEN'
        )

        # Try to access other owner's job
        self.client.login(username='testowner', password='testpass')
        response = self.client.get(reverse('job_board:job_detail', args=[other_job.pk]))
        self.assertEqual(response.status_code, 302)  # Should redirect to job list

    def test_job_create_get(self):
        """Test job create form displays for authenticated users."""
        self.client.login(username='testowner', password='testpass')
        response = self.client.get(reverse('job_board:job_create'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], JobForm)

    def test_job_create_post_valid(self):
        """Test creating a job with valid data."""
        self.client.login(username='testowner', password='testpass')
        data = {
            'title': 'New Job',
            'description': 'New job description',
            'dog': self.dog.pk,
            'location': 'Test Park',
            'scheduled_date': '2024-01-01',
            'scheduled_time': '10:00',
            'recurrence': 'NONE',
            'duration': '60',
        }
        response = self.client.post(reverse('job_board:job_create'), data=data)
        self.assertEqual(response.status_code, 302)
        job = Job.objects.get(title='New Job')
        self.assertEqual(job.owner, self.owner)  # Owner should be set automatically

    def test_job_create_post_invalid(self):
        """Test creating a job with invalid data."""
        self.client.login(username='testowner', password='testpass')
        data = {'title': '', 'description': 'Test'}
        response = self.client.post(reverse('job_board:job_create'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())

    def test_accept_job_requires_login(self):
        """Test accept job requires login."""
        response = self.client.post(reverse('job_board:accept_job', args=[self.job.pk]))
        self.assertEqual(response.status_code, 302)

    def test_accept_job_success(self):
        """Test walker can accept a job."""
        self.client.login(username='testwalker', password='testpass')
        response = self.client.post(reverse('job_board:accept_job', args=[self.job.pk]))
        self.assertEqual(response.status_code, 302)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, 'WAITING FOR APPROVAL')

    def test_decline_job_success(self):
        """Test walker can decline an assigned job."""
        self.job.walker = self.walker
        self.job.status = 'ASSIGNED'
        self.job.save()

        self.client.login(username='testwalker', password='testpass')
        response = self.client.post(reverse('job_board:decline_job', args=[self.job.pk]))
        self.assertEqual(response.status_code, 302)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, 'OPEN')
        self.assertIsNone(self.job.walker)

    def test_job_delete_get_shows_confirmation(self):
        """Test job delete GET shows confirmation page."""
        self.client.login(username='testowner', password='testpass')
        response = self.client.get(reverse('job_board:job_delete', args=[self.job.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['job'], self.job)

    def test_job_delete_owner_access(self):
        """Test owner can delete their job."""
        self.client.login(username='testowner', password='testpass')
        response = self.client.post(reverse('job_board:job_delete', args=[self.job.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Job.objects.filter(pk=self.job.pk).exists())

    def test_job_delete_unauthorized_access(self):
        """Test unauthorized users cannot delete jobs."""
        # Create a different owner and job
        other_owner_user = User.objects.create_user(
            username='otherowner', email='other@test.com', password='testpass'
        )
        other_owner = Owner.objects.create(
            user=other_owner_user, address='456 Other St', phone_number='402-555-9999'
        )
        other_job = Job.objects.create(
            title='Other Job', description='Other description',
            owner=other_owner, dog=self.dog, status='OPEN'
        )

        # Try to delete other owner's job
        self.client.login(username='testowner', password='testpass')
        response = self.client.post(reverse('job_board:job_delete', args=[other_job.pk]))
        self.assertEqual(response.status_code, 302)  # Should redirect to job list
        self.assertTrue(Job.objects.filter(pk=other_job.pk).exists())  # Job should still exist
