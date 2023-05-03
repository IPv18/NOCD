from django.forms import ModelForm
from .models import TCPolicy

class TCPolicyForm(ModelForm):
    class Meta:
        model = TCPolicy
        fields = ["name", "description", "config", "enabled", "startup"]
