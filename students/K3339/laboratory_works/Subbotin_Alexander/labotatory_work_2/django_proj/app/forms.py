from django import forms
from .models import Reservation, Review
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ('guests', 'notes')

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = Review
        fields = ('text', 'rating')

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

