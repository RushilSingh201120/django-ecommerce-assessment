from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Product, Profile, Store


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput(
                attrs={'placeholder': 'Store name'}
            ),
            'description': forms.Textarea(
                attrs={'placeholder': 'Store description'}
            ),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            'name',
            'description',
            'price',
            'stock',
        )
        widgets = {
            'name': forms.TextInput(
                attrs={'placeholder': 'Product name'}
            ),
            'description': forms.Textarea(
                attrs={'placeholder': 'Product description'}
            ),
            'price': forms.NumberInput(
                attrs={
                    'placeholder': 'Product price',
                    'step': '0.01'
                }
            ),
            'stock': forms.NumberInput(
                attrs={
                    'placeholder': 'Available stock',
                    'min': '0'
                }
            ),
        }


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('vendor', 'Vendor'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',
            'role',
        )

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            Profile.objects.create(
                user=user,
                role=self.cleaned_data['role']
            )

        return user
