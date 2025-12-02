#!/usr/bin/env python
"""
Cleanup script to delete test data created by Selenium tests.
This script should be run after all tests complete to clean up the database.
"""
import os
import sys
import django

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoproject.settings')
django.setup()

from django.contrib.auth.models import User
from userbase.models import Owner, Walker, Doggy, Job

def cleanup_test_data():
    """Delete all test data created by Selenium tests."""
    print("Cleaning up test data...")
    
    # Delete test jobs
    test_job_titles = ["New Job!", "See me!"]
    jobs_deleted = 0
    for title in test_job_titles:
        jobs = Job.objects.filter(title=title)
        count = jobs.count()
        jobs.delete()
        jobs_deleted += count
        if count > 0:
            print(f"  Deleted {count} job(s) with title '{title}'")
    
    # Delete test dogs
    test_dog_names = ["Carl", "MEME"]
    dogs_deleted = 0
    for name in test_dog_names:
        dogs = Doggy.objects.filter(dog_name=name)
        count = dogs.count()
        dogs.delete()
        dogs_deleted += count
        if count > 0:
            print(f"  Deleted {count} dog(s) named '{name}'")
    
    # Delete test users and their associated profiles
    test_usernames = ["Owner", "Walker"]
    users_deleted = 0
    for username in test_usernames:
        try:
            user = User.objects.get(username=username)
            # Delete associated profiles first
            if hasattr(user, 'owner_profile'):
                user.owner_profile.delete()
            if hasattr(user, 'walker_profile'):
                user.walker_profile.delete()
            # Delete the user
            user.delete()
            users_deleted += 1
            print(f"  Deleted user '{username}' and associated profiles")
        except User.DoesNotExist:
            pass
    
    print(f"\nCleanup complete:")
    print(f"  - {jobs_deleted} job(s) deleted")
    print(f"  - {dogs_deleted} dog(s) deleted")
    print(f"  - {users_deleted} user(s) deleted")

if __name__ == '__main__':
    cleanup_test_data()

