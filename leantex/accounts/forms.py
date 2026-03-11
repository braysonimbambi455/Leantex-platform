from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )
    
    # Phone number validation
    phone_number = forms.CharField(
        max_length=15, 
        required=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in format: '+254700000000'"
        )],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0712345678 or +254712345678'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create or get profile (in case it doesn't exist)
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data['phone_number']
            profile.save()
        
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                'This account is inactive.',
                code='inactive',
            )

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email exists for other users
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Check if username exists for other users
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

class ProfileUpdateForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in format: '+254700000000'"
        )],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0712345678'
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your physical address'
        })
    )
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your city'
        })
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    email_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    sms_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'city', 'profile_picture', 
                 'email_notifications', 'sms_notifications']

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Check file size (max 5MB)
            if profile_picture.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image file too large ( > 5MB )')
            
            # Check file extension
            import os
            ext = os.path.splitext(profile_picture.name)[1]
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if not ext.lower() in valid_extensions:
                raise forms.ValidationError('Unsupported file extension. Allowed: .jpg, .jpeg, .png, .gif')
        
        return profile_picture

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password'
        })
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class AdminUserCreationForm(UserCreationForm):
    """Form for creating new users in admin panel"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    role = forms.ChoiceField(choices=Profile.USER_ROLES, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data['phone_number']
            profile.role = self.cleaned_data['role']
            profile.save()
        
        return user