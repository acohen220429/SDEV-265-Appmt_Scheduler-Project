from django import forms
from django.contrib.auth.models import User


class SimpleRegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def save(self):
        username = self.cleaned_data["username"]
        password = self.cleaned_data["password"]
        return User.objects.create_user(username=username, password=password)
