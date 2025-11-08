# job_board/forms.py
from django import forms
from userbase.models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'owner', 'dog', 'walker',
            'scheduled_date', 'scheduled_time', 'duration',
            'location', 'recurrence', 'status'
        ]
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'type': 'time'}),
        }
