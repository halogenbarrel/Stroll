from django.db import models
from django.contrib.auth.models import User

# please note that django provides a user paradigm already. (im not looking up how to spell that.)


class Walker(models.Model):
    """
    Extension of the User model that already exists within django
    This should carry the permissions that an walker would have on top,
    as well as any additional needed info, such as location.
    A user can be both a walker and an owner.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='walker_profile')
    bio = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Walker: {self.user.username}"

    class Meta:
        permissions = [
            ("can_accept_jobs", "Can accept walking jobs"),
            ("can_complete_jobs", "Can mark jobs as completed")
        ]


class Owner(models.Model):
    """
    Extension of the User model that already exists within django
    This should carry the permissions that an owner would have on top,
    as well as any additional needed info.
    A user can be both an owner and a walker.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_profile')
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"Owner: {self.user.username}"

    class Meta:
        permissions = [
            ("can_create_jobs", "Can create walking jobs"),
            ("can_manage_dogs", "Can manage dogs")
        ]


class Doggy(models.Model):
    """
    Stores a name, charfield of len 50
    Stores an owner, a foreign key. When owner deleted, all "Doggy" as well
    FIXME Store weight :: cap weight and verify type. Cap to one decimal
    FIXME Store age :: cap age and verify type.
    TODO Store an list of temperments
    like permissions but more
    maybe in the form ( lazy, True or False ) as a tuple?
    """

    dog_name = models.CharField(max_length=50)
    weight = models.FloatField(default=0.0)
    age = models.FloatField(default=0.0)
    # TODO Fill in second field
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True)

class Job(models.Model):
    """
    Represents a dog walking job listing
    """
    title = models.CharField(max_length=100)
    description = models.TextField()
    walker = models.ForeignKey(Walker, on_delete=models.SET_NULL, null=True, blank=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    dog = models.ForeignKey(Doggy, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('OPEN', 'Open'),
            ('ASSIGNED', 'Assigned'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled')
        ],
        default='OPEN'
    )

    def __str__(self):
        return f"{self.title} - {self.scheduled_time}"