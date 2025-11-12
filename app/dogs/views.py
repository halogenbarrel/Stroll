from django.shortcuts import render, get_object_or_404, redirect
from userbase.models import Doggy
from django.contrib.auth.decorators import login_required
from .forms import DoggyForm

@login_required
def dog_list(request):
    if not hasattr(request.user, 'owner_profile'):
        # Redirect non-owners to an appropriate page or show an error message
        return render(request, 'dogs/dog_list.html', {
            'dogs': [],
            'error_message': 'You must be registered as an owner to view dogs.'
        })
    
    dogs = Doggy.objects.filter(owner=request.user.owner_profile)
    return render(request, 'dogs/dog_list.html', {'dogs': dogs})

def dog_detail(request, dog_id):
    dog = get_object_or_404(Doggy, id=dog_id)
    return render(request, 'dogs/dog_detail.html', {'dog': dog})

@login_required
def create_dog(request):
    if not hasattr(request.user, 'owner_profile'):
        return redirect('dog_list')
        
    if request.method == 'POST':
        form = DoggyForm(request.POST, request.FILES)
        if form.is_valid():
            dog = form.save(commit=False)
            dog.owner = request.user.owner_profile
            dog.save()
            form.save_m2m()  # Save the many-to-many relationships (temperaments)
            return redirect('dog_list')
    else:
        form = DoggyForm()
    return render(request, 'dogs/dog_create.html', {'form': form})

@login_required
def edit_dog(request, dog_id):
    dog = get_object_or_404(Doggy, id=dog_id, owner=request.user.owner_profile)
    if request.method == 'POST':
        form = DoggyForm(request.POST, request.FILES, instance=dog)
        if form.is_valid():
            form.save()
            return redirect('dog_detail', dog.id) # type: ignore
    else:
        form = DoggyForm(instance=dog)
    return render(request, 'dogs/dog_edit.html', {'form': form, 'dog': dog})

@login_required
def owner_dashboard(request):
    dogs = Doggy.objects.filter(owner=request.user.owner_profile)
    return render(request, 'dogs/owner_dashboard.html', {'dogs': dogs})


