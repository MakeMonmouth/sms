from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.forms import AuthenticationForm, UsernameField

from django import forms


class UserLoginForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = UsernameField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username', 'id': 'username'}
        )
    )
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'password',
            }
        )
    )

class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': '', 'id': 'email'}))
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '', 'id': 'first_name'}))
    last_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '', 'id': 'last_name'}))
    username = UsernameField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '', 'id': 'username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': '',
            'id': 'password1',
        }
        ))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': '',
            'id': 'password2',
        }
))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2','first_name','last_name' )
