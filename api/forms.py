from django import forms


class Identity(forms.Form):
    name = forms.CharField(max_length=255)
