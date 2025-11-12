from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Walker(models.Model):
    """
    Extension of the User model that already exists within django
    This should carry the permissions that an walker would have on top,
    as well as any additional needed info, such as location.
    A user can be both a walker and an owner.
    """

    TEMPERAMENT_CHOICES = [
        ("FRIENDLY", "Friendly"),
        ("SHY", "Shy"),
        ("ENERGETIC", "Energetic"),
        ("CALM", "Calm"),
        ("PROTECTIVE", "Protective"),
        ("PLAYFUL", "Playful"),
        ("INDEPENDENT", "Independent"),
        ("SOCIAL", "Social"),
    ]

    ENERGY_LEVEL_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]
    # switching model to OneToOneField so users can only have one walker profile
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="walker_profile"
    )
    bio = models.TextField(blank=True, null=True)

    temperament = models.CharField(
        max_length=20, choices=TEMPERAMENT_CHOICES, default="FRIENDLY"
    )
    energy_level = models.CharField(
        max_length=10, choices=ENERGY_LEVEL_CHOICES, default="MEDIUM"
    )

    def __str__(self):
        return f"Walker: {self.user.username}"

    class Meta:
        permissions = [
            ("can_accept_jobs", "Can accept walking jobs"),
            ("can_complete_jobs", "Can mark jobs as completed"),
        ]


class Owner(models.Model):
    """
    Extension of the User model that already exists within django
    This should carry the permissions that an owner would have on top,
    as well as any additional needed info.
    A user can be both an owner and a walker.
    """

    # switching model to OneToOneField so users can only have one owner profile
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="owner_profile"
    )
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"Owner: {self.user.username}"

    class Meta:
        permissions = [
            ("can_create_jobs", "Can create walking jobs"),
            ("can_manage_dogs", "Can manage dogs"),
        ]


class Doggy(models.Model):
    # Predefined choices for dog temperaments
    TEMPERAMENT_CHOICES = [
        ("FRIENDLY", "Friendly"),
        ("SHY", "Shy"),
        ("ENERGETIC", "Energetic"),
        ("CALM", "Calm"),
        ("PROTECTIVE", "Protective"),
        ("PLAYFUL", "Playful"),
        ("INDEPENDENT", "Independent"),
        ("SOCIAL", "Social"),
    ]

    ENERGY_LEVEL_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]

    """
    Stores a name, charfield of len 50
    Stores dog breed, charfield len 100, optional blank
    Stores weight any value from 0 to 350 with up to one decimal 
    Stores age of any int from 0 to 35 
    Stores temperament from predefined choices
    Allows photo to be uploaded - optional with default as paw print
    Stores an owner, a foreign key. When owner deleted, all "Doggy" as well
    """
    dog_name = models.CharField(max_length=50)
    breed = models.CharField(max_length=100, blank=True)
    temperament = models.CharField(
        max_length=20, choices=TEMPERAMENT_CHOICES, default="FRIENDLY"
    )
    energy_level = models.CharField(
        max_length=10, choices=ENERGY_LEVEL_CHOICES, default="MEDIUM"
    )
    weight = models.DecimalField(
        max_digits=5,  # allow up to 999.9 lbs
        decimal_places=1,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(350.0),  # caps at 350 - heaviest dog ever recorded =343
        ],
        default=Decimal("0.0"),
    )

    age = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(35),  # oldest dog ever was 31
        ],
        default=0,
    )

    photo = models.ImageField(
        upload_to="dog_photos/",
        null=True,
        blank=True,
        default="dog_photos/default_paw.png",  # path relative to MEDIA_ROOT
    )
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.dog_name


class Job(models.Model):
    """
    Represents a dog walking job listing
    """

    # Core identifiers
    title = models.CharField(max_length=100)
    description = models.TextField()

    # Relationships
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    dog = models.ForeignKey(Doggy, on_delete=models.CASCADE)
    walker = models.ForeignKey(Walker, on_delete=models.SET_NULL, null=True, blank=True)

    # Scheduling
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)
    duration = models.CharField(
        max_length=3,
        choices=[
            ("15", "15 minutes"),
            ("30", "30 minutes"),
            ("45", "45 minutes"),
            ("60", "1 hour"),
        ],
        default="30",
    )

    # other important info
    location = models.CharField(max_length=200, blank=True)
    recurrence = models.CharField(
        max_length=10,
        choices=[
            ("NONE", "No recurrence"),
            ("DAILY", "Daily"),
            ("WEEKLY", "Weekly"),
            ("MONTHLY", "Monthly"),
        ],
        default="NONE",
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("OPEN", "Open"),
            ("ASSIGNED", "Assigned"),
            ("COMPLETED", "Completed"),
            ("CANCELLED", "Cancelled"),
        ],
        default="OPEN",
    )

    # metadata
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.scheduled_time}"
