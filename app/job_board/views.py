from django.shortcuts import render, get_object_or_404, redirect
from userbase.models import Job, Owner, Walker
from .forms import JobForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone


def job_detail(request, job_id):
    """
    Display details for a specific job
    """
    job = get_object_or_404(Job, id=job_id)
    context = {"job": job}
    return render(request, "job_board/job_detail.html", context)


@login_required
def job_list(request):
    """
    Display jobs from database depending on profile type
    Walkers can view only open or assigned jobs
    Owners can only see jobs they have created
    """
    user = request.user
    context = {}

    if hasattr(user, "owner_profile"):
        # Owner: show all their jobs theyve posted
        owner = user.owner_profile
        jobs = Job.objects.filter(owner=owner).order_by("-created_at")
        context["role"] = "owner"
        context["owner_jobs"] = jobs

    elif hasattr(user, "walker_profile"):
        walker = user.walker_profile

        # Handle empty or malformed weight_range
        try:
            min_weight = walker.weight_range[0]
            max_weight = walker.weight_range[1]
        except (IndexError, TypeError):
            min_weight = 0
            max_weight = 300

        # Walker: show assigned + matching open jobs
        assigned_jobs = Job.objects.filter(walker=walker).order_by(
            "scheduled_date", "scheduled_time"
        )
        available_jobs = (
            Job.objects.filter(
                status="OPEN",
                dog__temperament__in=walker.temperament,
                dog__energy_level__in=walker.energy_level,
                dog__weight__gte=min_weight,
                dog__weight__lte=max_weight,
            )
            .exclude(walker__isnull=False)
            .order_by("created_at")
        )

        context["role"] = "walker"
        context["assigned_jobs"] = assigned_jobs
        context["available_jobs"] = available_jobs

    return render(request, "job_board/job_list.html", context)


@login_required
def accept_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, status="OPEN")
    job.status = "ASSIGNED"
    job.walker = request.user.walker_profile
    job.scheduled_date = timezone.now().date()
    job.scheduled_time = timezone.now().time()
    job.save()
    return redirect("job_list")


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
