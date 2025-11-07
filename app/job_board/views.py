from django.shortcuts import render, get_object_or_404, redirect
from userbase.models import Job
from .forms import JobForm

def job_detail(request, job_id):
    """
    Display details for a specific job
    """
    job = get_object_or_404(Job, id=job_id)
    context = {"job": job}
    return render(request, 'job_board/job_detail.html', context)


def job_list(request):
    """
    Display all jobs from database
    TODO: only display jobs per owner/walker privilages
    """
    jobs = Job.objects.filter(status__in=["OPEN","ASSIGNED"]) #shows all active jobs and excludes completed/cancelled jobs
    return render(request, 'job_board/job_list.html', {'jobs': jobs})



def job_create(request):
    """
    Create a new job posting
    """
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('job_list')
    else:
        form = JobForm()
    return render(request, 'job_board/create_job.html', {'form': form})


