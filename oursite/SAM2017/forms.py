from django import forms
from SAM2017.models import *
import datetime
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext as _
from django.contrib.auth import password_validation
from django.forms.models import ModelForm
from django.contrib.admin import widgets
from datetime import datetime, date, time, timedelta

class PaperForm(forms.ModelForm):
    class Meta:
        model = Paper
        fields = ('title','description','file')
		
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Email", max_length=30)
    password = forms.CharField(label="Password", max_length=30, min_length=8, widget=forms.PasswordInput())
    
    class Meta:
        model = SAMUser

class UserCreationForm(UserCreationForm):
    username = forms.EmailField(label=_("Email"), widget=forms.EmailInput)
    first_name = forms.CharField(label=_("First Name"), widget=forms.TextInput)
    last_name = forms.CharField(label=_("Last Name"), widget=forms.TextInput)
    address = forms.CharField(label=_("Address"), widget=forms.Textarea)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = forms.CharField(validators=[phone_regex], label=_("Phone Number"))
    
    class Meta:
        model = SAMUser
        fields = ("username",)
    
    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        # copy the submitted cleaned form-data to the user's properties
        user.set_password(self.cleaned_data["password1"])
        user.username = self.cleaned_data["username"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.address = self.cleaned_data["address"]
        user.phone_number = self.cleaned_data["phone_number"]
        if commit:
            # save the user properties to the db fields
            user.save()
        return user

class ReviewRateForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ('review','rating')