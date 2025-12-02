from django import forms
from .models import Reservation, Review, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re


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
    first_name = forms.CharField(max_length=150, required=True, label='Имя')
    last_name = forms.CharField(max_length=150, required=True, label='Фамилия')
    date_of_birth = forms.DateField(required=True, label='Дата рождения', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "date_of_birth", "password1", "password2"]

    def clean_password1(self):
        pw = self.cleaned_data.get('password1')
        if not pw:
            raise ValidationError('Введите пароль.')
        pw_regex = re.compile(r'^(?=.{8,}$)(?=.*[A-Z])(?=.*[@.\+\-_])[A-Za-z0-9@.\+\-_]+$')
        if not pw_regex.match(pw):
            raise ValidationError('Пароль должен содержать минимум 8 символов, как минимум одну заглавную букву, состоять только из латинских букв, цифр и одного из символов @ . + - _.')
        return pw

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'date_of_birth': self.cleaned_data.get('date_of_birth')}
            )
        return user

