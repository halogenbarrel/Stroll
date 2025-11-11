from django.shortcuts import render, get_object_or_404, redirect
from userbase.models import Job
from userbase.models import Walker
from .forms import JobForm


def job_detail(request, job_id):
    """
    Display details for a specific job
    """
    job = get_object_or_404(Job, id=job_id)
    context = {"job": job}
    return render(request, "job_board/job_detail.html", context)


def job_list(request):
    """
    Display all jobs from database
    TODO: only display jobs per owner/walker privilages
    """
    user = request.user
    jobs = Job.objects.filter(
        status__in=["OPEN", "ASSIGNED"]
    )  # shows all active jobs and excludes completed/cancelled jobs
    filter_on = request.GET.get("filter") == "on"

    # Predetermined filter (example: only show user’s assigned jobs)
    if filter_on and user.is_authenticated:
        user_preference = getattr(user.walker_profile, "temper")
        jobs = Job.objects.filter(dog__temper__in=user_preference)

    return render(request, "job_board/job_list.html", {"jobs": jobs})


def job_create(request):
    """
    Create a new job posting
    """
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("job_board:job_list")
    else:
        form = JobForm()
    return render(request, "job_board/job_create.html", {"form": form})
