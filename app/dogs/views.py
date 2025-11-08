from django.shortcuts import render, get_object_or_404, redirect
from userbase.models import Doggy
from django.contrib.auth.decorators import login_required
from .forms import DoggyForm

def dog_list(request):
    dogs = Doggy.objects.all()
    return render(request, 'dogs/dog_list.html', {'dogs': dogs})

def dog_detail(request, dog_id):
    dog = get_object_or_404(Doggy, id=dog_id)
    return render(request, 'dogs/dog_detail.html', {'dog': dog})

@login_required
def create_dog(request):
    if request.method == 'POST':
        form = DoggyForm(request.POST, request.FILES)
        if form.is_valid():
            dog = form.save(commit=False)
            dog.owner = request.user.owner  # assuming Owner is linked to User
            dog.save()
            form.save_m2m()
            return redirect('dog_detail', dog.id)
    else:
        form = DoggyForm()
    return render(request, 'dogs/dog_create.html', {'form': form})

@login_required
def edit_dog(request, dog_id):
    dog = get_object_or_404(Doggy, id=dog_id, owner=request.user.owner)
    if request.method == 'POST':
        form = DoggyForm(request.POST, request.FILES, instance=dog)
        if form.is_valid():
            form.save()
            return redirect('dog_detail', dog.id)
    else:
        form = DoggyForm(instance=dog)
    return render(request, 'dogs/edit_dog.html', {'form': form, 'dog': dog})

@login_required
def owner_dashboard(request):
    dogs = Doggy.objects.filter(owner=request.user.owner)
    return render(request, 'dogs/owner_dashboard.html', {'dogs': dogs})


