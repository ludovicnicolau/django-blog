from django.contrib.auth.forms import UserCreationForm, UsernameField, AuthenticationForm
from django import forms
from django.forms import TextInput, PasswordInput
from django.utils.translation import gettext_lazy as _

from .models import CustomUser

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('username'),
        }),
        label=_('Username'),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('password'),
        }),
        label=_('Password'),
    )


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override password fields CSS
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control rounded password-field',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control rounded password-confirm',
        })

    class Meta:
        model = CustomUser
        fields = ('username',)
        field_classes = {'username': UsernameField,}
        widgets = {
            'username': TextInput(attrs={'class': 'form-control'}),
            'password1': PasswordInput(attrs={'class': 'form-control'}),
            'password2': PasswordInput(attrs={'class': 'form-control'}),
        }


class BiographyUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('biography',)
        widgets = {
            'biography': forms.Textarea(attrs={'class': 'form-control'}),
        }