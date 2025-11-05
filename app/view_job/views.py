from django.shortcuts import render, get_object_or_404
from userbase.models import Job

def job_detail(request, job_id):
    """
    Display details for a specific job
    """
    job = get_object_or_404(Job, id=job_id)
    context = {"job": job}
    return render(request, 'view_job/job_detail.html', context)
