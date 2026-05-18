from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date

from .models import Client, Product, Review, UserProfile


class ClientRegistrationForm(forms.ModelForm):
    username = forms.CharField(label='Логин', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    role = forms.ChoiceField(
        choices=[('buyer', 'Покупатель'), ('employee', 'Сотрудник')],
        label='Роль',
        initial='buyer'
    )

    class Meta:
        model = Client
        fields = ['full_name', 'phone', 'email', 'birth_date', 'city', 'address']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким логином уже существует.")
        return username

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if not birth_date:
            raise ValidationError("Укажите дату рождения.")
        today = date.today()
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )
        if age < 18:
            raise ValidationError("Вам должно быть не менее 18 лет.")
        return birth_date

    def save(self, commit=True):
        # Создаём User
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email']
        )
        # Создаём Client
        client = super().save(commit=False)
        if commit:
            client.save()

        # Создаём UserProfile (OneToOne)
        UserProfile.objects.create(
            user=user,
            role=self.cleaned_data.get('role', 'buyer'),
            client=client
        )
        return user


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'unit', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Например: Помидоры'}),
            'price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise ValidationError("Цена не может быть отрицательной.")
        return price


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш отзыв...'}),
            'rating': forms.Select(choices=[(i, f"{i} ★") for i in range(1, 6)]),
        }