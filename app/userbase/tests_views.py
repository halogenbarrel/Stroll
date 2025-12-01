"""
Unit tests for userbase views.

Tests cover view functionality including user registration,
profile management, and protected view access control.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from userbase.models import Walker, Owner
from userbase.forms import StrollUserCreationForm


class UserbaseViewsTests(TestCase):
    """
    Test suite for userbase views including registration and profile management.

    Tests cover:
    - User registration with walker/owner profile creation
    - Form validation and error handling
    - Permission assignment
    - Authentication and redirects
    - Protected view access control
    """

    def test_register_walker_success(self):
        """
        Test successful walker registration creates user and walker profile.
        """
        form_data = {
            'username': 'testwalker',
            'email': 'walker@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': True,
            'is_owner': False,
            'bio': 'I love walking dogs!',
            'temperament': ['FRIENDLY', 'PLAYFUL'],
            'energy_level': ['MEDIUM', 'HIGH'],
            'weight_range': ['0-20', '21-50'],
        }

        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Verify user was created
        user = User.objects.get(username='testwalker')
        self.assertEqual(user.email, 'walker@test.com')
        self.assertTrue(user.check_password('testpass123'))

        # Verify walker profile was created
        walker = Walker.objects.get(user=user)
        self.assertEqual(walker.bio, 'I love walking dogs!')
        self.assertEqual(walker.temperament, ['FRIENDLY', 'PLAYFUL'])
        self.assertEqual(walker.energy_level, ['MEDIUM', 'HIGH'])

        # Verify user is logged in
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_register_owner_success(self):
        """
        Test successful owner registration creates user and owner profile.
        """
        form_data = {
            'username': 'testowner',
            'email': 'owner@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': False,
            'is_owner': True,
            'address': '123 Main St, Anytown, USA',
            'phone_number': '555-123-4567',
        }

        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Verify user was created
        user = User.objects.get(username='testowner')
        self.assertEqual(user.email, 'owner@test.com')

        # Verify owner profile was created
        owner = Owner.objects.get(user=user)
        self.assertEqual(owner.address, '123 Main St, Anytown, USA')
        self.assertEqual(owner.phone_number, '555-123-4567')

    def test_register_both_walker_and_owner(self):
        """
        Test registration as both walker and owner creates both profiles.
        """
        form_data = {
            'username': 'bothuser',
            'email': 'both@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': True,
            'is_owner': True,
            'bio': 'I walk and own dogs!',
            'temperament': ['FRIENDLY'],
            'energy_level': ['MEDIUM'],
            'weight_range': ['21-50'],
            'address': '456 Oak St, Somewhere, USA',
            'phone_number': '555-987-6543',
        }

        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username='bothuser')

        # Verify both profiles were created
        walker = Walker.objects.get(user=user)
        owner = Owner.objects.get(user=user)

        self.assertEqual(walker.bio, 'I walk and own dogs!')
        self.assertEqual(owner.address, '456 Oak St, Somewhere, USA')

    def test_register_form_validation_errors(self):
        """
        Test form validation errors are handled properly.
        """
        # Test missing required role
        form_data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': False,
            'is_owner': False,
        }

        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 200)  # Stay on form
        self.assertFormError(response.context['form'], None,
                           'You must select at least one role (Walker or Owner)')

        # Test missing walker required fields
        form_data_walker_incomplete = {
            'username': 'testwalker2',
            'email': 'walker2@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': True,
            'is_owner': False,
            # Missing temperament, energy_level, weight_range
        }

        response = self.client.post(reverse('register'), data=form_data_walker_incomplete)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'temperament', 'This field is required for walkers.')

    def test_register_duplicate_username(self):
        """
        Test duplicate username is rejected.
        """
        # Create first user
        User.objects.create_user(username='duplicate', password='pass123', email='dup@test.com')

        form_data = {
            'username': 'duplicate',  # Same username
            'email': 'different@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'is_walker': True,
            'is_owner': False,
            'temperament': ['FRIENDLY'],
            'energy_level': ['MEDIUM'],
            'weight_range': ['21-50'],
        }

        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'username', 'A user with that username already exists.')

    def test_owner_settings_requires_login(self):
        """
        Test owner_settings view requires authentication.
        """
        response = self.client.get(reverse('userbase:owner_settings'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Should redirect to login page
        self.assertIn('/login/', response['Location'])

    def test_owner_settings_authenticated(self):
        """
        Test owner_settings view works for authenticated users.
        """
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        response = self.client.get(reverse('userbase:owner_settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userbase/owner_settings.html')

    def test_edit_profile_requires_login(self):
        """
        Test edit_profile view requires authentication.
        """
        response = self.client.get(reverse('userbase:edit_profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_edit_profile_get(self):
        """
        Test GET request to edit_profile shows form with current user data.
        """
        user = User.objects.create_user(
            username='edituser',
            email='edit@test.com',
            password='testpass'
        )
        self.client.login(username='edituser', password='testpass')

        response = self.client.get(reverse('userbase:edit_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userbase/edit_profile.html')

        # Check form is populated with user data
        form = response.context['form']
        self.assertEqual(form.instance, user)

    def test_edit_profile_post_success(self):
        """
        Test successful profile editing updates user data.
        """
        user = User.objects.create_user(
            username='edituser',
            email='edit@test.com',
            password='testpass'
        )
        self.client.login(username='edituser', password='testpass')

        form_data = {
            'username': 'edituser',  # Keep same username
            'email': 'updated@test.com',  # Change email
            'password1': '',  # Empty password means no change
            'password2': '',
            'is_walker': False,
            'is_owner': False,
        }

        response = self.client.post(reverse('userbase:edit_profile'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Verify user data was updated
        user.refresh_from_db()
        self.assertEqual(user.email, 'updated@test.com')

    def test_edit_profile_comprehensive_functionality(self):
        """
        Test comprehensive edit_profile functionality including:
        - Role changes (adding/removing walker/owner profiles)
        - Permission management
        - Profile data updates
        - Form validation
        """
        from userbase.models import Walker, Owner
        from django.contrib.auth.models import Permission

        # Create a user with both walker and owner profiles
        user = User.objects.create_user(
            username='comprehensive_user',
            email='comprehensive@test.com',
            password='testpass123'
        )

        # Create walker and owner profiles
        walker = Walker.objects.create(
            user=user,
            bio='Original bio',
            temperament=['FRIENDLY'],
            energy_level=['MEDIUM'],
            weight_range=['21-50']
        )
        owner = Owner.objects.create(
            user=user,
            address='123 Original St',
            phone_number='555-0123'
        )

        self.client.login(username='comprehensive_user', password='testpass123')

        # Test 1: GET request should show form with existing data
        response = self.client.get(reverse('userbase:edit_profile'))
        self.assertEqual(response.status_code, 200)
        form = response.context['form']

        # Verify form is pre-populated with existing data
        self.assertEqual(form.fields['is_walker'].initial, True)
        self.assertEqual(form.fields['is_owner'].initial, True)
        self.assertEqual(form.fields['bio'].initial, 'Original bio')
        self.assertEqual(form.fields['address'].initial, '123 Original St')
        self.assertEqual(form.fields['phone_number'].initial, '555-0123')
        self.assertEqual(form.fields['temperament'].initial, ['FRIENDLY'])
        self.assertEqual(form.fields['energy_level'].initial, ['MEDIUM'])
        self.assertEqual(form.fields['weight_range'].initial, ['21-50'])

        # Test 2: Update profile data and remove owner role
        form_data = {
            'username': 'comprehensive_user',
            'email': 'updated@test.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'is_walker': True,  # Keep walker role
            'is_owner': False,  # Remove owner role
            'bio': 'Updated bio for walker',
            'temperament': ['FRIENDLY', 'PLAYFUL'],
            'energy_level': ['HIGH'],
            'weight_range': ['21-50', '51-100'],
            # Owner fields not needed since we're removing owner role
        }

        response = self.client.post(reverse('userbase:edit_profile'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Verify user data was updated
        user.refresh_from_db()
        self.assertEqual(user.email, 'updated@test.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')

        # Verify walker profile was updated
        walker.refresh_from_db()
        self.assertEqual(walker.bio, 'Updated bio for walker')
        self.assertEqual(walker.temperament, ['FRIENDLY', 'PLAYFUL'])
        self.assertEqual(walker.energy_level, ['HIGH'])
        self.assertEqual(walker.weight_range, ['21-50', '51-100'])

        # Verify owner profile was deleted
        with self.assertRaises(Owner.DoesNotExist):
            user.owner_profile

        # Verify permissions were updated (walker permissions should remain, owner permissions removed)
        walker_perms = Permission.objects.filter(
            codename__in=["can_accept_jobs", "can_complete_jobs"]
        )
        owner_perms = Permission.objects.filter(
            codename__in=["can_create_jobs", "can_manage_dogs"]
        )

        for perm in walker_perms:
            self.assertTrue(user.user_permissions.filter(pk=perm.pk).exists())

        for perm in owner_perms:
            self.assertFalse(user.user_permissions.filter(pk=perm.pk).exists())

        # Test 3: Add owner role back and update both profiles
        form_data = {
            'username': 'comprehensive_user',
            'email': 'final@test.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'is_walker': True,  # Keep walker
            'is_owner': True,   # Add owner back
            'bio': 'Final walker bio',
            'temperament': ['CALM'],
            'energy_level': ['LOW'],
            'weight_range': ['0-20'],
            'address': '456 Final Ave',
            'phone_number': '555-9876',
        }

        response = self.client.post(reverse('userbase:edit_profile'), data=form_data)
        self.assertEqual(response.status_code, 302)

        # Verify final state
        user.refresh_from_db()
        self.assertEqual(user.email, 'final@test.com')
        self.assertEqual(user.last_name, 'Smith')

        # Verify walker profile
        walker.refresh_from_db()
        self.assertEqual(walker.bio, 'Final walker bio')
        self.assertEqual(walker.temperament, ['CALM'])

        # Verify owner profile was recreated
        owner = user.owner_profile
        self.assertEqual(owner.address, '456 Final Ave')
        self.assertEqual(owner.phone_number, '555-9876')

        # Verify all permissions are present
        for perm in walker_perms:
            self.assertTrue(user.user_permissions.filter(pk=perm.pk).exists())
        for perm in owner_perms:
            self.assertTrue(user.user_permissions.filter(pk=perm.pk).exists())
