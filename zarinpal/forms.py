from django.forms import ModelForm

from zarinpal.models import TopUp


class TopUpForm(ModelForm):
    class Meta:
        model = TopUp
        fields = ['profile', 'amount', 'description']
