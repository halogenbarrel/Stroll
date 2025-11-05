from django.shortcuts import render
from userbase.models import Doggy

def testValues(request):
    dog_list = Doggy.objects.all()
    context = {"dog_list": dog_list}
    return render(request, "test_values.html", context)
