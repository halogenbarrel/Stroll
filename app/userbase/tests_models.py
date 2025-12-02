"""
Unit tests for userbase models (Walker and Owner).

These tests verify the creation, initialization, and data persistence
of Walker and Owner model instances, which extend Django's built-in User model.
"""

from django.test import TestCase
from userbase.models import Walker, Owner, Doggy, Job
from django.contrib.auth.models import User
from django.utils import timezone


class UserbaseModelsTests(TestCase):
    """
    Test suite for Userbase models including Walker, Owner, Doggy, and Job.

    Tests cover:
    - Model instance creation with proper relationships
    - Default field values
    - Data persistence and retrieval
    - Field updates and validation
    - User-Dog relationships through Owner model
    - Job creation, assignment, and status management
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data shared across all test methods.

        Creates common users, walkers, owners, and dogs that can be reused
        in multiple test methods for efficiency.
        """
        # Create test users
        cls.walker_user = User.objects.create_user(
            username='testwalker',
            password='testpassword',
            email='walker@example.com'
        )
        cls.owner_user = User.objects.create_user(
            username='testowner',
            password='testpassword',
            email='owner@example.com'
        )

        # Create corresponding profile instances
        cls.walker = Walker.objects.create(user=cls.walker_user)  # pyright: ignore[reportAttributeAccessIssue]
        cls.owner = Owner.objects.create(user=cls.owner_user)

        # Create a test dog for the owner
        cls.dog = Doggy.objects.create(
            dog_name="Buddy",
            breed="Golden Retriever",
            temperament="FRIENDLY",
            energy_level="HIGH",
            weight=65.5,
            age=3,
            owner=cls.owner
        )

    def test_walker_creation(self):
        """
        Test Walker model creation and preference management.

        Verifies:
        - Walker instance can be created with User relationship
        - Default values for preference fields (empty lists, None for bio)
        - Preference data can be updated and persisted
        - Data integrity after database save/reload
        """
        # Use the walker instance created in setUpTestData
        user = self.walker_user
        walker = self.walker

        # Verify User model attributes are set correctly
        self.assertEqual(user.username, 'testwalker')
        self.assertTrue(user.check_password('testpassword'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.get_full_name(), '')  # No first/last name provided
        self.assertEqual(user.get_short_name(), '')  # Uses first name, which is empty
        self.assertEqual(user.email, 'walker@example.com')
        self.assertIsNotNone(user.date_joined)  # Auto-set on creation
        self.assertIsNone(user.last_login)  # None until first login

        # Verify Walker attributes start with default values
        self.assertEqual(walker.user, user)  # OneToOne relationship
        self.assertIsNone(walker.bio)  # Optional text field
        self.assertEqual(walker.temperament, [])  # JSONField defaults to empty list
        self.assertEqual(walker.energy_level, [])  # JSONField defaults to empty list
        self.assertEqual(walker.weight_range, [])  # JSONField defaults to empty list

        # Test updating Walker preferences with valid data
        walker.temperament = ["FRIENDLY", "PLAYFUL", "ENERGETIC"]  # From Doggy.TEMPERAMENT_CHOICES
        walker.energy_level = ["MEDIUM", "HIGH"]  # From Doggy.ENERGY_LEVEL_CHOICES
        walker.weight_range = [10.0, 50.0]  # Weight range in lbs (10-50 lbs)
        walker.save()

        # Refresh from database to verify persistence
        walker.refresh_from_db()

        # Verify preference data was saved correctly
        self.assertEqual(walker.temperament, ["FRIENDLY", "PLAYFUL", "ENERGETIC"])
        self.assertEqual(walker.energy_level, ["MEDIUM", "HIGH"])
        self.assertEqual(walker.weight_range, [10.0, 50.0])

    def test_owner_creation(self):
        """
        Test Owner model creation and contact information management.

        Verifies:
        - Owner instance can be created with User relationship
        - Default values for contact fields (None for optional fields)
        - Contact data can be updated and persisted
        - Data integrity after database save/reload
        """
        # Use the owner instance created in setUpTestData
        user = self.owner_user
        owner = self.owner

        # Verify User model attributes are set correctly
        self.assertEqual(user.username, 'testowner')
        self.assertTrue(user.check_password('testpassword'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.get_full_name(), '')  # No first/last name provided
        self.assertEqual(user.get_short_name(), '')  # Uses first name, which is empty
        self.assertEqual(user.email, 'owner@example.com')
        self.assertIsNotNone(user.date_joined)  # Auto-set on creation
        self.assertIsNone(user.last_login)  # None until first login

        # Verify Owner attributes start with default values
        self.assertEqual(owner.user, user)  # OneToOne relationship
        self.assertIsNone(owner.address)  # Optional text field
        self.assertIsNone(owner.phone_number)  # Optional char field

        # Test updating Owner contact information
        owner.address = "123 Main Street, Anytown, USA"
        owner.phone_number = "555-123-4567"  # Standard US phone format
        owner.save()

        # Refresh from database to verify persistence
        owner.refresh_from_db()

        # Verify contact data was saved correctly
        self.assertEqual(owner.address, "123 Main Street, Anytown, USA")
        self.assertEqual(owner.phone_number, "555-123-4567")

    def test_dog_creation_and_owner_relationship(self):
        """
        Test Doggy model creation and relationship with Owner.

        Verifies:
        - Dog instance can be created with all required fields
        - Dog can be associated with an Owner via ForeignKey
        - Default values for optional fields work correctly
        - Owner can access their dogs through the relationship
        """
        # Create a separate owner for this test to avoid conflicts with shared data
        test_owner_user = User.objects.create_user(
            username='testdogowner',
            password='testpassword',
            email='dogowner@example.com'
        )
        test_owner = Owner.objects.create(user=test_owner_user)

        # Create a dog associated with the test owner
        dog = Doggy.objects.create(
            dog_name="Buddy",
            breed="Golden Retriever",
            temperament="FRIENDLY",
            energy_level="HIGH",
            weight=65.5,  # 65.5 lbs
            age=3,
            owner=test_owner
        )

        # Verify dog attributes are set correctly
        self.assertEqual(dog.dog_name, "Buddy")
        self.assertEqual(dog.breed, "Golden Retriever")
        self.assertEqual(dog.temperament, "FRIENDLY")
        self.assertEqual(dog.energy_level, "HIGH")
        self.assertEqual(dog.weight, 65.5)
        self.assertEqual(dog.age, 3)
        self.assertEqual(dog.owner, test_owner)

        # Test that owner can access their dogs
        owner_dogs = Doggy.objects.filter(owner=test_owner)
        self.assertEqual(owner_dogs.count(), 1)
        self.assertEqual(owner_dogs.first(), dog)

        # Create another dog for the same owner
        dog2 = Doggy.objects.create(
            dog_name="Max",
            breed="",  # Optional field left blank
            temperament="PLAYFUL",
            energy_level="MEDIUM",
            weight=45.0,  # 45 lbs
            age=5,
            owner=test_owner
        )

        # Verify owner now has two dogs
        owner_dogs = Doggy.objects.filter(owner=test_owner)
        self.assertEqual(owner_dogs.count(), 2)
        dog_names = [d.dog_name for d in owner_dogs]
        self.assertIn("Buddy", dog_names)
        self.assertIn("Max", dog_names)

    def test_job_creation_and_acceptance(self):
        """
        Test Job model creation and walker acceptance workflow.

        Verifies:
        - Job can be created with owner, dog, and scheduling details
        - Job starts with OPEN status by default
        - Job can be accepted by assigning a walker
        - Job status changes to ASSIGNED when accepted
        - Walker assignment is properly recorded
        """
        from datetime import date, time

        # Use the owner and dog from setUpTestData
        owner = self.owner
        dog = self.dog

        # Create a job posting
        job = Job.objects.create(
            title="Evening Walk for Buddy",
            description="Buddy needs his daily evening walk around the neighborhood",
            owner=owner,
            dog=dog,
            scheduled_date=date.today(),
            scheduled_time=time(18, 30),  # 6:30 PM
            duration="45",  # 45 minutes
            location="Central Park",
            recurrence="NONE",
            # status defaults to "OPEN"
        )

        # Verify job was created with correct attributes
        self.assertEqual(job.title, "Evening Walk for Buddy")
        self.assertEqual(job.description, "Buddy needs his daily evening walk around the neighborhood")
        self.assertEqual(job.owner, owner)
        self.assertEqual(job.dog, dog)
        self.assertEqual(job.scheduled_date, date.today())
        self.assertEqual(job.scheduled_time, time(18, 30))
        self.assertEqual(job.duration, "45")
        self.assertEqual(job.location, "Central Park")
        self.assertEqual(job.recurrence, "NONE")
        self.assertEqual(job.status, "OPEN")  # Default status
        self.assertIsNone(job.walker)  # No walker assigned initially
        self.assertIsNotNone(job.created_at)  # Auto-set timestamp

        # Test job acceptance by assigning a walker
        walker = self.walker
        job.walker = walker
        job.status = "ASSIGNED"
        job.save()

        # Refresh from database to verify persistence
        job.refresh_from_db()

        # Verify job acceptance
        self.assertEqual(job.walker, walker)
        self.assertEqual(job.status, "ASSIGNED")

        # Verify walker can see their assigned jobs
        walker_jobs = Job.objects.filter(walker=walker, status="ASSIGNED")
        self.assertEqual(walker_jobs.count(), 1)
        self.assertEqual(walker_jobs.first(), job)