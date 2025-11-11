from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from userbase.models import Doggy, Walker, Owner
from django.db.models import Count
from .forms import StrollUserCreationForm
from django.contrib.auth.models import Permission


def register(request):
    if request.method == 'POST':
        form = StrollUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create Walker profile if selected
            if form.cleaned_data['is_walker']:
                Walker.objects.create(
                    user=user,
                    bio=form.cleaned_data['bio']
                )
            
            #keaghons code to add permissions
            perms = Permission.objects.filter(codename__in=['can_accept_jobs', 'can_complete_jobs'])
            user.user_permissions.add(*perms)

            # Create Owner profile if selected
            if form.cleaned_data['is_owner']:
                Owner.objects.create(
                    user=user,
                    address=form.cleaned_data['address'],
                    phone_number=form.cleaned_data['phone_number']
                )

                #keaghons code to add permissions
                perms = Permission.objects.filter(codename__in=['can_create_jobs', 'can_manage_dogs'])
                user.user_permissions.add(*perms)

            login(request, user)
            return redirect('/')
    else:
        form = StrollUserCreationForm()
    
    return render(request, 'userbase/register.html', {'form': form})


@login_required
def owner_settings(request):
    '''
    adding settings page if you click on the welcome <username>! in nav bar
    '''
    return render(request, 'userbase/owner_settings.html')

@login_required
def edit_owner_profile(request):
    return render(request, 'userbase/edit_owner_profile.html')


'''
MOVING TO DOGS app

def dog_list(request):
    # Pull from database
    name_lookup = request.GET.get("name", None)
    # grab all dogs
    dog = Doggy.objects.all()

    if name_lookup:
        dog = dog.filter(user__name=name_lookup)

    user_with_dog = Doggy.objects.values("dog_name").annotate(num_posts=Count("id"))
    total_posts = Doggy.objects.count()

    # Extract the username from user_with_dog
    owner = [user_with_dog["user_name"] for user_with_dog in user_with_dog]

    return render(
        request,
        "post.html",
        {
            "dog name": dog,
            "owner": owner,
            "user_with_dog": user_with_dog,
            "total_posts": total_posts,
        },
    )

'''