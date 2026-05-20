from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(label='ФИО', max_length=255, required=False)
    email = forms.EmailField(label='Email', required=False)

    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()
            user.profile.full_name = self.cleaned_data.get('full_name', '')
            user.profile.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
