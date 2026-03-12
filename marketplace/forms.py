from django import forms
from marketplace.models import User,UserProfile,Product,Review,Tag
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ["username","email","password"]
        help_texts = {
        'username': '',
        }
    
    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                raise forms.ValidationError(e.messages)
        return password

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