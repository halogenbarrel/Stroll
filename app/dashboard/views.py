from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def dashboard(request):
    """
    Main dashboard view that displays navigation to different features
    """
    return render(request, 'dashboard/dashboard.html')
