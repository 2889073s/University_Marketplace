from django import forms
from marketplace.models import *

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ["username","email","password"]

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["profile_picture"]

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name","description","price","image","tag"]

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating"]

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["tag_name"]