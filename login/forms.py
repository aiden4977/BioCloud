from django import forms
from .models import JobUniversal

class JobUniversalForm(forms.ModelForm):
    class Meta:
        model = JobUniversal
        fields = ['workfolw', 'parameters', 'sampleName', 'workDir']