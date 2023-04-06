from django.forms import ModelForm
from .models import FirewallRule

class FirewallRuleForm(ModelForm):
    class Meta:
        model = FirewallRule
        fields = '__all__'
