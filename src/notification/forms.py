from django import forms
from notification.models import NotificationInfo


class NotificationForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 4, 'cols': 40}), label='Message')

    class Meta:
        model = NotificationInfo
        fields = ['message', 'type']

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
