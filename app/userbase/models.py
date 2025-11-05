from django.db import models

# please note that django provides a user paradigm already. (im not looking up how to spell that.)


class Walker(models.Model):
    """
    Extension of the User model that already exists within django
    This should carry the permissions that an walker would have on top,
    as well as any additional needed info, such as location
    """

    class Meta:
        permissions = [("", "")]


class Owner(models.Model):
    """
    Extension of the User model that already exists within django
    This should carry the permissions that an owner would have on top,
    as well as any additional needed info.
    """

    class Meta:
        permissions = [("", "")]


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
    weight = models.PositiveFloat()
    age = models.PositiveInt()
    # TODO Fill in second field
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)


class WalkJob(models.Model):
    scheduled_time = models.DateTimeField()
    scheduled_dog = models.ForeignKey(Doggy, on_delete=models.CASCADE)
