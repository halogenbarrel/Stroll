# job_board/forms.py
from django import forms
from userbase.models import Job

class JobForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'owner_profile'):
            self.fields['dog'].queryset = user.owner_profile.doggy_set.all()

    class Meta:
        model = Job
        fields = [
            'title', 'description', 'dog',
            'scheduled_date', 'scheduled_time', 'duration',
            'location', 'recurrence'
        ]
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'type': 'time'}),
        }
